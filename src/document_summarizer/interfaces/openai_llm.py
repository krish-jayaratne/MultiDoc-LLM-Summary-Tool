"""
OpenAI LLM implementation for document analysis.

This module provides a concrete implementation of the LLMInterface using OpenAI's GPT models.
"""

import os
import json
from typing import List, Dict, Any, Optional
import openai
from openai import OpenAI

from .llm_interface import LLMInterface
from ..models.metadata import DocumentMetadata


class OpenAILLM(LLMInterface):
    """OpenAI GPT implementation for document analysis."""
    
    def __init__(self, model: str = "gpt-4o", api_key: Optional[str] = None):
        """
        Initialize OpenAI LLM interface.
        
        Args:
            model: OpenAI model name (default: gpt-4o)
            api_key: OpenAI API key. If None, reads from OPENAI_KEY environment variable
        """
        self.model = model
        
        # Get API key from parameter or environment
        if api_key is None:
            api_key = os.getenv('OPENAI_KEY')
        
        if not api_key:
            raise ValueError(
                "OpenAI API key not provided. Set OPENAI_KEY environment variable or pass api_key parameter."
            )
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=api_key)
    
    def analyze_document(self, content: str, metadata: DocumentMetadata) -> Dict[str, Any]:
        """
        Analyze document content using OpenAI to extract structured information.
        Handles large documents by chunking if necessary.
        
        Args:
            content: The raw document content
            metadata: Basic file metadata (filename, type, etc.)
            
        Returns:
            Dictionary containing extracted information in structured format
        """
        
        # Check content size and chunk if necessary
        max_content_tokens = 3000  # Leave room for prompt + response
        
        if self._estimate_tokens(content) > max_content_tokens:
            return self._analyze_large_document(content, metadata)
        else:
            return self._analyze_single_chunk(content, metadata)
    
    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.
        
        Args:
            text: Text to estimate
            
        Returns:
            Estimated token count
        """
        # Rough estimation: 1 token ≈ 0.75 words ≈ 4 characters
        return len(text) // 4
    
    def _analyze_single_chunk(self, content: str, metadata: DocumentMetadata) -> Dict[str, Any]:
        """
        Analyze a single chunk of content that fits within token limits.
        
        Args:
            content: The document content
            metadata: Basic file metadata
            
        Returns:
            Analysis results
        """
        
        # Use standardized prompts from base class
        system_prompt = self.DOCUMENT_ANALYSIS_SYSTEM_PROMPT
        user_prompt = self.create_document_analysis_prompt(content, metadata)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,  # Low temperature for consistent extraction
                max_tokens=4000
            )
            
            # Parse JSON response
            analysis_text = response.choices[0].message.content.strip()
            
            # Remove any markdown formatting if present
            if analysis_text.startswith('```json'):
                analysis_text = analysis_text[7:-3]
            elif analysis_text.startswith('```'):
                analysis_text = analysis_text[3:-3]
            
            analysis_result = json.loads(analysis_text)
            
            # Add metadata about the analysis
            analysis_result['llm_model'] = self.model
            analysis_result['analysis_timestamp'] = metadata.analysis_timestamp
            analysis_result['filename'] = metadata.name
            analysis_result['file_path'] = metadata.file_path
            analysis_result['content_tokens_estimated'] = self._estimate_tokens(content)
            
            return analysis_result
            
        except json.JSONDecodeError as e:
            return {
                'error': f'Failed to parse LLM response as JSON: {str(e)}',
                'raw_response': analysis_text if 'analysis_text' in locals() else 'No response'
            }
        except Exception as e:
            return {
                'error': f'LLM analysis failed: {str(e)}',
                'filename': metadata.name,
                'file_path': metadata.file_path
            }
    
    def _analyze_large_document(self, content: str, metadata: DocumentMetadata) -> Dict[str, Any]:
        """
        Analyze large documents by chunking them into smaller pieces.
        
        Args:
            content: The full document content
            metadata: Basic file metadata
            
        Returns:
            Aggregated analysis results from all chunks
        """
        max_chunk_size = 12000  # ~3000 tokens worth of characters
        chunks = self._split_content_into_chunks(content, max_chunk_size)
        
        print(f"   📄 Large document detected: {len(content):,} chars")
        print(f"   📊 Split into {len(chunks)} chunks for analysis")
        
        all_results = []
        chunk_summaries = []  # Collect all summaries for batch aggregation
        aggregated_result = {
            'document_type': '',
            'document_date': '',
            'summary': '',
            'organizations': [],
            'people': [],
            'dates': [],
            'locations': [],
            'referenced_documents': [],
            'properties': [],
            'financial_amounts': [],
            'key_information': [],
            'chunk_count': len(chunks),
            'total_content_length': len(content),
            'analysis_method': 'chunked'
        }
        
        # Analyze each chunk
        for i, chunk in enumerate(chunks, 1):
            print(f"   🔍 Analyzing chunk {i}/{len(chunks)}...")
            
            # Create chunk metadata
            chunk_metadata = DocumentMetadata(
                name=f"{metadata.name} (chunk {i}/{len(chunks)})",
                file_path=metadata.file_path,
                file_type=metadata.file_type,
                content=chunk
            )
            
            chunk_result = self._analyze_single_chunk(chunk, chunk_metadata)
            all_results.append(chunk_result)
            
            # Aggregate results (avoid duplicates)
            if chunk_result.get('document_type') and not aggregated_result['document_type']:
                aggregated_result['document_type'] = chunk_result['document_type']
            
            if chunk_result.get('document_date') and not aggregated_result['document_date']:
                aggregated_result['document_date'] = chunk_result['document_date']
            
            # Combine lists (remove duplicates)
            for field in ['organizations', 'people', 'dates', 'locations', 
                         'referenced_documents', 'properties', 'financial_amounts', 'key_information']:
                if field in chunk_result:
                    for item in chunk_result[field]:
                        if item not in aggregated_result[field]:
                            aggregated_result[field].append(item)
            
            # Collect summary for batch aggregation
            if chunk_result.get('summary'):
                chunk_summaries.append(chunk_result['summary'])
        
        # Aggregate all summaries at once using LLM
        if chunk_summaries:
            print(f"   🤖 Aggregating {len(chunk_summaries)} summaries using LLM...")
            aggregated_result['summary'] = self.aggregate_summaries_with_llm(
                chunk_summaries, 
                metadata.name
            )
        
        # Add metadata
        aggregated_result['llm_model'] = self.model
        aggregated_result['analysis_timestamp'] = metadata.analysis_timestamp
        aggregated_result['filename'] = metadata.name
        aggregated_result['file_path'] = metadata.file_path
        aggregated_result['chunk_results'] = all_results  # Keep individual results for debugging
        
        return aggregated_result
    
    def _call_llm_for_summary_aggregation(self, summaries: List[str], document_name: str = "") -> str:
        """
        OpenAI-specific implementation of summary aggregation.
        """
        # Use the LLM to combine all summaries at once
        system_prompt = self.SUMMARY_AGGREGATION_SYSTEM_PROMPT
        user_prompt = self.create_summary_aggregation_prompt(summaries, document_name)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,  # Low temperature for consistent results
            max_tokens=500  # Increased limit for combining multiple summaries
        )
        
        combined_summary = response.choices[0].message.content.strip()
        
        # Clean up any extra formatting
        if combined_summary.startswith('"') and combined_summary.endswith('"'):
            combined_summary = combined_summary[1:-1]
        
        return combined_summary
    
    def _split_content_into_chunks(self, content: str, max_chunk_size: int) -> List[str]:
        """
        Split content into chunks while trying to preserve sentence boundaries.
        
        Args:
            content: Content to split
            max_chunk_size: Maximum characters per chunk
            
        Returns:
            List of content chunks
        """
        if len(content) <= max_chunk_size:
            return [content]
        
        chunks = []
        current_pos = 0
        
        while current_pos < len(content):
            # Calculate chunk end position
            chunk_end = min(current_pos + max_chunk_size, len(content))
            
            # If we're not at the end, try to break at a sentence boundary
            if chunk_end < len(content):
                # Look for sentence endings within the last 200 characters
                search_start = max(chunk_end - 200, current_pos)
                sentence_end = -1
                
                for punct in ['. ', '.\n', '! ', '!\n', '? ', '?\n']:
                    pos = content.rfind(punct, search_start, chunk_end)
                    if pos > sentence_end:
                        sentence_end = pos + len(punct)
                
                # If we found a good break point, use it
                if sentence_end > current_pos:
                    chunk_end = sentence_end
            
            chunk = content[current_pos:chunk_end].strip()
            if chunk:
                chunks.append(chunk)
            
            current_pos = chunk_end
        
        return chunks
    
    def cross_reference_documents(self, documents: List[DocumentMetadata]) -> Dict[str, Any]:
        """
        Cross-reference multiple documents to find relationships and connections.
        
        Args:
            documents: List of document metadata to cross-reference
            
        Returns:
            Dictionary containing relationship analysis and connections
        """
        if not documents:
            return {'relationships': [], 'error': 'No documents provided'}
        
        # Use standardized prompts from base class
        system_prompt = self.CROSS_REFERENCE_SYSTEM_PROMPT
        user_prompt = self.create_cross_reference_prompt(documents)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=4000
            )
            
            analysis_text = response.choices[0].message.content.strip()
            
            # Clean markdown formatting
            if analysis_text.startswith('```json'):
                analysis_text = analysis_text[7:-3]
            elif analysis_text.startswith('```'):
                analysis_text = analysis_text[3:-3]
            
            result = json.loads(analysis_text)
            result['document_count'] = len(documents)
            result['llm_model'] = self.model
            
            return result
            
        except json.JSONDecodeError as e:
            return {
                'error': f'Failed to parse cross-reference response: {str(e)}',
                'document_count': len(documents)
            }
        except Exception as e:
            return {
                'error': f'Cross-reference analysis failed: {str(e)}',
                'document_count': len(documents)
            }
    
    def analyze_documents_for_csv(self, documents: List[DocumentMetadata]) -> List[Dict[str, Any]]:
        """
        Analyze multiple documents and return data suitable for CSV export.
        
        Args:
            documents: List of document metadata objects
            
        Returns:
            List of dictionaries with standardized fields for CSV export
        """
        csv_data = []
        
        for doc in documents:
            try:
                # Analyze individual document
                analysis = self.analyze_document(doc.content, doc)
                
                # Convert to CSV-friendly format
                csv_row = {
                    'filename': doc.name,
                    'file_path': doc.file_path,
                    'file_type': doc.file_type,
                    'file_size_kb': round((doc.file_size or 0) / 1024, 2),
                    'document_type': analysis.get('document_type', ''),
                    'document_date': analysis.get('document_date', ''),
                    'summary': analysis.get('summary', ''),
                    'organizations': ', '.join(analysis.get('organizations', [])),
                    'people': ', '.join(analysis.get('people', [])),
                    'dates': ', '.join(analysis.get('dates', [])),
                    'locations': ', '.join(analysis.get('locations', [])),
                    'referenced_documents': ', '.join(analysis.get('referenced_documents', [])),
                    'properties': ', '.join(analysis.get('properties', [])),
                    'financial_amounts': ', '.join(analysis.get('financial_amounts', [])),
                    'key_information': ', '.join(analysis.get('key_information', [])),
                    'content_length': len(doc.content) if doc.content else 0,
                    'analysis_status': 'Success' if 'error' not in analysis else 'Error',
                    'analysis_error': analysis.get('error', ''),
                    'analysis_model': analysis.get('llm_model', self.model),
                    'analysis_timestamp': str(doc.analysis_timestamp),
                    'analysis_method': analysis.get('analysis_method', 'single'),
                    'chunk_count': analysis.get('chunk_count', 1),
                    'content_tokens_estimated': analysis.get('content_tokens_estimated', 0)
                }
                
                csv_data.append(csv_row)
                
            except Exception as e:
                # Add error row if analysis fails
                csv_data.append({
                    'filename': doc.name,
                    'file_path': doc.file_path,
                    'file_type': doc.file_type,
                    'file_size_kb': round((doc.file_size or 0) / 1024, 2) if doc.file_size else 0,
                    'document_type': '',
                    'document_date': '',
                    'summary': '',
                    'organizations': '',
                    'people': '',
                    'dates': '',
                    'locations': '',
                    'referenced_documents': '',
                    'properties': '',
                    'financial_amounts': '',
                    'key_information': '',
                    'content_length': len(doc.content) if doc.content else 0,
                    'analysis_status': 'Error',
                    'analysis_error': str(e),
                    'analysis_model': self.model,
                    'analysis_timestamp': str(doc.analysis_timestamp)
                })
        
        return csv_data
