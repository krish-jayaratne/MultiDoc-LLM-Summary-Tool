"""
LLM interface for future document analysis and cross-referencing capabilities.

This module defines the interface for integrating with Large Language Models
to perform advanced document analysis, cross-referencing, and relationship
discovery between documents.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
from ..models.metadata import DocumentMetadata


class LLMInterface(ABC):
    """
    Abstract interface for LLM integration.
    
    This interface defines the contract for integrating with various LLM providers
    to enhance document analysis capabilities. Future implementations will provide
    concrete implementations for specific LLM services.
    """
    
    # Standard prompts for document analysis - shared across all LLM implementations
    DOCUMENT_ANALYSIS_SYSTEM_PROMPT = """You are a document analysis expert. Extract key information from documents and return structured data in JSON format.

For each document, extract the following information:
- document_type: Type of document (invoice, letter, report, contract, etc.)
- document_date: The actual date when this document/email/letter was written or sent (format: YYYY-MM-DD). Look for "Date:", "Sent:", email headers, or letter dates. This is different from dates mentioned within the content.
- summary: Brief 1-2 sentence summary of the document
- organizations: List of company/organization names mentioned
- people: List of people's names mentioned
- dates: List of important dates mentioned in the content (format: YYYY-MM-DD), excluding the document date
- locations: List of addresses, cities, places mentioned
- referenced_documents: List of other documents referenced
- key_information: List of important facts, numbers, or details
- properties: List of property addresses or real estate mentions
- financial_amounts: List of monetary amounts with context

Return only valid JSON. Use empty arrays [] for categories with no entries."""

    CROSS_REFERENCE_SYSTEM_PROMPT = """You are a document relationship analyst. Analyze multiple documents to find connections, relationships, and cross-references between them.

Identify:
- Direct references (one document mentions another)
- Common entities (same people, organizations, addresses appearing in multiple docs)
- Chronological relationships (sequence of events across documents)
- Subject matter relationships (documents about same topic/project)
- Contradictions or inconsistencies between documents

Return results in JSON format with:
- relationships: Array of relationship objects
- common_entities: Object with shared people, organizations, etc.
- timeline: Chronological sequence of events
- potential_issues: Any contradictions or concerns found

Return only valid JSON."""

    SUMMARY_AGGREGATION_SYSTEM_PROMPT = """You are a document summarization expert. Your task is to combine multiple partial summaries of the same document into one coherent, comprehensive summary.

Return only valid JSON."""

    SUMMARY_AGGREGATION_SYSTEM_PROMPT = """You are a document summarization expert. Your task is to combine multiple partial summaries of the same document into one coherent, comprehensive summary.

Guidelines:
1. Remove redundant information that appears in multiple summaries
2. Preserve all unique and important details from each summary
3. Create a flowing, coherent narrative that reads naturally
4. Prioritize the most important information first
5. Keep the final summary concise but comprehensive (ideally 2-4 sentences)
6. Maintain factual accuracy - don't add information not present in the source summaries

The input will be multiple summaries from different sections of the same document. Your output should be a single, well-written summary that captures the essence of the entire document.

Return only the final summary text, no additional formatting or explanation."""
    
    @abstractmethod
    def analyze_document(self, content: str, metadata: DocumentMetadata) -> Dict[str, Any]:
        """
        Perform advanced analysis on a document using LLM capabilities.
        
        Args:
            content: The raw document content
            metadata: Existing metadata extracted from the document
            
        Returns:
            Dictionary containing enhanced analysis results
        """
        pass
    
    @abstractmethod
    def cross_reference_documents(self, documents: List[DocumentMetadata]) -> Dict[str, Any]:
        """
        Cross-reference multiple documents to find relationships and connections.
        
        Args:
            documents: List of document metadata to cross-reference
            
        Returns:
            Dictionary containing relationship analysis and connections
        """
        pass
    
    def create_document_analysis_prompt(self, content: str, metadata: DocumentMetadata) -> str:
        """
        Create standardized user prompt for document analysis.
        
        Args:
            content: The raw document content
            metadata: Basic file metadata
            
        Returns:
            Formatted user prompt string
        """
        return f"""Analyze this document:

Filename: {metadata.name}
File Type: {metadata.file_type}

Content:
{content}

Please extract the structured information as specified."""
    
    def create_cross_reference_prompt(self, documents: List[DocumentMetadata]) -> str:
        """
        Create standardized user prompt for cross-referencing documents.
        
        Args:
            documents: List of document metadata to cross-reference
            
        Returns:
            Formatted user prompt string
        """
        import json
        
        # Create a summary of all documents for cross-referencing
        doc_summaries = []
        for doc in documents:
            summary = {
                'filename': doc.name,
                'type': doc.file_type,
                'description': doc.description[:200] if doc.description else '',
                'content_preview': doc.content[:500] if doc.content else ''
            }
            doc_summaries.append(summary)
        
        return f"""Analyze relationships between these {len(documents)} documents:

{json.dumps(doc_summaries, indent=2)}

Find all relationships and connections between these documents."""
    
    def create_summary_aggregation_prompt(self, summaries: List[str], document_name: str = "") -> str:
        """
        Create standardized user prompt for aggregating multiple summaries.
        
        Args:
            summaries: List of summary strings to combine
            document_name: Optional document name for context
            
        Returns:
            Formatted user prompt string
        """
        summaries_text = ""
        for i, summary in enumerate(summaries, 1):
            summaries_text += f"\nSummary {i}:\n{summary}\n"
        
        context = f" for document '{document_name}'" if document_name else ""
        
        return f"""Please combine these {len(summaries)} partial summaries{context} into one coherent summary:
{summaries_text}
Final combined summary:"""
    
    def aggregate_summaries_with_llm(self, summaries: List[str], document_name: str = "") -> str:
        """
        Use LLM to intelligently combine ALL chunk summaries at once.
        More efficient than progressive aggregation - single LLM call per document.
        
        This method should be implemented by concrete LLM classes but the logic
        is standardized here in the base class.
        
        Args:
            summaries: List of summary strings to combine
            document_name: Optional document name for context
            
        Returns:
            Combined summary string
        """
        if not summaries:
            return ""
        
        if len(summaries) == 1:
            return summaries[0]
        
        try:
            # Call the concrete implementation's LLM method
            return self._call_llm_for_summary_aggregation(summaries, document_name)
            
        except Exception as e:
            # Fallback to simple concatenation if LLM fails
            print(f"   ⚠️  LLM summary aggregation failed: {str(e)}")
            print(f"   📝 Falling back to simple concatenation")
            
            # Simple concatenation with length limit
            combined = " ".join(summaries)
            if len(combined) > 600:
                combined = combined[:600] + "..."
            return combined
    
    @abstractmethod
    def _call_llm_for_summary_aggregation(self, summaries: List[str], document_name: str = "") -> str:
        """
        Abstract method that concrete LLM implementations must provide.
        
        Args:
            summaries: List of summaries to combine
            document_name: Optional document name for context
            
        Returns:
            Combined summary from the LLM
        """
        pass


class DocumentAnalyzer:
    """
    High-level document analyzer that coordinates between document readers and LLM interfaces.
    
    This class serves as the main entry point for comprehensive document analysis,
    combining basic metadata extraction with advanced LLM-powered analysis.
    """
    
    def __init__(self, llm_interface: Optional[LLMInterface] = None):
        """
        Initialize the document analyzer.
        
        Args:
            llm_interface: Optional LLM interface for enhanced analysis
        """
        self.llm_interface = llm_interface
        self._document_cache: Dict[str, DocumentMetadata] = {}
        self._content_cache: Dict[str, str] = {}  # Cache document content as well
    
    def analyze_single_document(self, file_path: str, document_reader, 
                               use_llm: bool = True) -> Dict[str, Any]:
        """
        Perform comprehensive analysis on a single document.
        
        Args:
            file_path: Path to the document to analyze
            document_reader: DocumentReader instance to use for basic extraction
            use_llm: Whether to use LLM for enhanced analysis
            
        Returns:
            Complete analysis results
        """
        # Basic metadata extraction
        content = document_reader.read_content(file_path)
        metadata = document_reader.extract_metadata(file_path, content)
        
        # Cache both metadata and content
        self._document_cache[file_path] = metadata
        self._content_cache[file_path] = content
        
        analysis_result = {
            'basic_metadata': metadata,
            'content_preview': content[:500] + ('...' if len(content) > 500 else ''),
            'file_path': file_path,
            'analysis_timestamp': metadata.modified_date
        }
        
        # Enhanced LLM analysis if available and requested
        if use_llm and self.llm_interface:
            try:
                llm_analysis = self.llm_interface.analyze_document(content, metadata)
                analysis_result['llm_analysis'] = llm_analysis
                
            except Exception as e:
                analysis_result['llm_error'] = f"LLM analysis failed: {str(e)}"
        
        return analysis_result
    
    def cross_reference_documents(self, file_paths: List[str], 
                                 document_reader) -> Dict[str, Any]:
        """
        Cross-reference multiple documents to find relationships.
        
        Args:
            file_paths: List of document paths to cross-reference
            document_reader: DocumentReader instance to use
            
        Returns:
            Cross-reference analysis results
        """
        # Extract metadata for all documents
        documents_metadata = []
        for file_path in file_paths:
            if file_path not in self._document_cache:
                content = document_reader.read_content(file_path)
                metadata = document_reader.extract_metadata(file_path, content)
                # Cache both metadata and content
                self._document_cache[file_path] = metadata
                self._content_cache[file_path] = content
            documents_metadata.append(self._document_cache[file_path])
        
        cross_ref_result = {
            'documents_analyzed': len(documents_metadata),
            'basic_relationships': self._find_basic_relationships(documents_metadata),
            'document_summaries': [doc.to_summary() for doc in documents_metadata]
        }
        
        # Enhanced cross-referencing with LLM
        if self.llm_interface:
            try:
                llm_cross_ref = self.llm_interface.cross_reference_documents(documents_metadata)
                cross_ref_result['llm_relationships'] = llm_cross_ref
            except Exception as e:
                cross_ref_result['llm_error'] = f"LLM cross-referencing failed: {str(e)}"
        
        return cross_ref_result
    
    def _find_basic_relationships(self, documents: List[DocumentMetadata]) -> Dict[str, Any]:
        """
        Find basic relationships between documents without LLM.
        
        Args:
            documents: List of document metadata
            
        Returns:
            Basic relationship analysis
        """
        relationships = {
            'shared_people': {},
            'shared_organizations': {},
            'shared_references': {},
            'temporal_relationships': []
        }
        
        # Find shared entities
        for i, doc1 in enumerate(documents):
            for j, doc2 in enumerate(documents[i+1:], i+1):
                # Shared people
                shared_people = set(doc1.people_mentioned) & set(doc2.people_mentioned)
                if shared_people:
                    key = f"{doc1.name} <-> {doc2.name}"
                    relationships['shared_people'][key] = list(shared_people)
                
                # Shared organizations
                shared_orgs = set(doc1.organizations) & set(doc2.organizations)
                if shared_orgs:
                    key = f"{doc1.name} <-> {doc2.name}"
                    relationships['shared_organizations'][key] = list(shared_orgs)
                
                # Document references
                if doc1.name in doc2.referenced_documents or doc2.name in doc1.referenced_documents:
                    relationships['shared_references'][f"{doc1.name} <-> {doc2.name}"] = True
        
        return relationships
    
    def get_cached_metadata(self, file_path: str) -> Optional[DocumentMetadata]:
        """
        Get cached metadata for a document.
        
        Args:
            file_path: Path to the document
            
        Returns:
            Cached metadata if available, None otherwise
        """
        return self._document_cache.get(file_path)
    
    def get_cached_content(self, file_path: str) -> Optional[str]:
        """
        Get cached content for a document.
        
        Args:
            file_path: Path to the document
            
        Returns:
            Cached content if available, None otherwise
        """
        return self._content_cache.get(file_path)
    
    def clear_cache(self) -> None:
        """Clear both document metadata and content caches."""
        self._document_cache.clear()
        self._content_cache.clear()
