"""
PDF Document Reader implementation.

This module provides a PDF-specific document reader that inherits from the base DocumentReader class.
"""

import re
from pathlib import Path
from typing import List, Optional
import PyPDF2
from io import BytesIO

from .document_reader import DocumentReader
from ..models.metadata import DocumentMetadata


class PDFDocumentReader(DocumentReader):
    """PDF document reader that extracts text and metadata from PDF files."""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = {'.pdf'}
        self._pdf_cache = {}  # Cache for PDF readers to avoid multiple file opens
    
    def _get_pdf_reader(self, file_path: str) -> PyPDF2.PdfReader:
        """
        Get a cached PDF reader or create a new one.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            PyPDF2.PdfReader instance
        """
        # Use file path as base cache key
        file_path_obj = Path(file_path)
        
        # For tests or non-existent files, create cache key without mtime
        if not file_path_obj.exists():
            cache_key = (file_path, 0)  # Use 0 as placeholder mtime for tests
        else:
            mtime = file_path_obj.stat().st_mtime
            cache_key = (file_path, mtime)
        
        if cache_key not in self._pdf_cache:
            try:
                with open(file_path, 'rb') as file:
                    # For real files, read content into memory once
                    # For mocked files, this will be handled by the mock
                    pdf_reader = PyPDF2.PdfReader(file)
                    self._pdf_cache[cache_key] = pdf_reader
            except Exception as e:
                raise IOError(f"Failed to read PDF file {file_path}: {str(e)}")
        
        return self._pdf_cache[cache_key]
    
    def clear_cache(self):
        """Clear the PDF reader cache to free memory."""
        self._pdf_cache.clear()
    
    def read_content(self, file_path: str) -> str:
        """
        Extract text content from a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Extracted text content from all pages
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            IOError: If the file cannot be read
        """
        if not self.validate_file(file_path):
            raise FileNotFoundError(f"File not found or not readable: {file_path}")
        
        try:
            pdf_reader = self._get_pdf_reader(file_path)
            text_content = []
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                if page_text.strip():  # Only add non-empty pages
                    text_content.append(page_text)
                    
            raw_text = '\n\n'.join(text_content)
            return self._clean_extracted_text(raw_text)
            
        except FileNotFoundError:
            # Re-raise FileNotFoundError as-is
            raise
        except Exception as e:
            raise IOError(f"Error reading PDF file {file_path}: {str(e)}")
    
    def _clean_extracted_text(self, text: str) -> str:
        """
        Clean up common PDF text extraction artifacts.
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text with normalized spacing and formatting
        """
        if not text:
            return text
        
        # Replace non-breaking spaces with regular spaces
        cleaned = text.replace('\u00A0', ' ')  # Non-breaking space
        cleaned = cleaned.replace('\u2009', ' ')  # Thin space
        cleaned = cleaned.replace('\u2007', ' ')  # Figure space
        cleaned = cleaned.replace('\u202F', ' ')  # Narrow no-break space
        cleaned = cleaned.replace('\u2060', '')   # Word joiner (invisible)
        
        # Fix common PDF extraction issues
        cleaned = cleaned.replace('\r\n', '\n')   # Windows line endings
        cleaned = cleaned.replace('\r', '\n')     # Mac line endings
        
        # Remove excessive whitespace while preserving paragraph breaks
        lines = cleaned.split('\n')
        processed_lines = []
        
        for line in lines:
            # Clean up each line - remove extra spaces but keep content
            line = ' '.join(line.split())  # Normalize internal spacing
            processed_lines.append(line)
        
        # Join lines back, but remove excessive blank lines
        result = '\n'.join(processed_lines)
        
        # Remove more than 2 consecutive newlines (preserve paragraph breaks)
        import re
        result = re.sub(r'\n{3,}', '\n\n', result)
        
        # Remove trailing/leading whitespace
        result = result.strip()
        
        return result
    
    def extract_metadata(self, file_path: str, content: Optional[str] = None) -> DocumentMetadata:
        """
        Extract comprehensive metadata from a PDF document.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            DocumentMetadata object with extracted information
        """
        if not self.validate_file(file_path):
            raise FileNotFoundError(f"File not found or not readable: {file_path}")
        
        # Read the content
        content = self.read_content(file_path)
        
        # Create metadata object
        metadata = DocumentMetadata(
            name=Path(file_path).name,
            description=self._generate_description(content),
            file_path=file_path,
            file_type="PDF",
            content=content
        )
        
        # Extract PDF-specific metadata
        self._extract_pdf_metadata(file_path, metadata)
        
        return metadata
    
    def _generate_description(self, content: str) -> str:
        """
        Generate a smart description for PDF documents.
        
        Args:
            content: The document content
            
        Returns:
            A meaningful description of the PDF document
        """
        content = content.strip()
        
        # If content is empty or mostly whitespace
        if not content or len(content.replace('\n', '').replace(' ', '')) < 10:
            return "PDF document with limited extractable text (possibly image-based or formatted content)"
        
        # Clean up excessive whitespace
        cleaned_content = ' '.join(content.split())
        
        # If content is very short and seems like header/footer info
        if len(cleaned_content) <= 100 and any(indicator in cleaned_content.lower() for indicator in 
                                                ['street', 'phone', 'ph ', 'email', '@', 'letterhead', 'address']):
            return f"PDF document containing {cleaned_content[:80]}{'...' if len(cleaned_content) > 80 else ''}"
        
        # Try to extract meaningful sentences
        sentences = re.split(r'[.!?]+', cleaned_content)
        meaningful_sentences = []
        
        for sentence in sentences[:5]:  # Check first 5 sentences
            clean_sentence = sentence.strip()
            # Skip very short sentences or those that look like headers/footers
            if (len(clean_sentence) > 15 and 
                not re.match(r'^[\d\s\|\-\.]+$', clean_sentence) and  # Skip number/symbol only lines
                not all(word.istitle() or word.isupper() for word in clean_sentence.split() if word.isalpha())):  # Skip all-caps headers
                meaningful_sentences.append(clean_sentence)
        
        if meaningful_sentences:
            description = meaningful_sentences[0]
            return description[:200] + ('...' if len(description) > 200 else '')
        
        # If no meaningful sentences found, create a description based on content type
        if len(cleaned_content) <= 200:
            return f"PDF document containing: {cleaned_content}"
        else:
            # Try to find document type indicators
            doc_type_indicators = {
                'invoice': ['invoice', 'bill', 'payment', 'amount due'],
                'report': ['report', 'analysis', 'findings', 'conclusion'],
                'letter': ['dear', 'sincerely', 'regards', 'correspondence'],
                'contract': ['agreement', 'terms', 'conditions', 'parties'],
                'manual': ['instructions', 'guide', 'how to', 'steps']
            }
            
            content_lower = cleaned_content.lower()
            for doc_type, indicators in doc_type_indicators.items():
                if any(indicator in content_lower for indicator in indicators):
                    return f"PDF {doc_type} - {cleaned_content[:150]}{'...' if len(cleaned_content) > 150 else ''}"
            
            # Fallback to first 200 characters
            return cleaned_content[:200] + ('...' if len(cleaned_content) > 200 else '')
    
    def _extract_pdf_metadata(self, file_path: str, metadata: DocumentMetadata) -> None:
        """
        Extract PDF-specific metadata like title, author, subject, etc.
        
        Args:
            file_path: Path to the PDF file
            metadata: DocumentMetadata object to populate
        """
        try:
            pdf_reader = self._get_pdf_reader(file_path)
            
            if pdf_reader.metadata:
                pdf_meta = pdf_reader.metadata
                
                # Extract PDF metadata fields
                if pdf_meta.title:
                    metadata.additional_data['pdf_title'] = pdf_meta.title
                
                if pdf_meta.author:
                    metadata.additional_data['pdf_author'] = pdf_meta.author
                    # Note: Entity extraction now handled by LLM
                
                if pdf_meta.subject:
                    metadata.additional_data['pdf_subject'] = pdf_meta.subject
                
                if pdf_meta.creator:
                    metadata.additional_data['pdf_creator'] = pdf_meta.creator
                
                if pdf_meta.producer:
                    metadata.additional_data['pdf_producer'] = pdf_meta.producer
                
                if pdf_meta.creation_date:
                    metadata.additional_data['pdf_creation_date'] = str(pdf_meta.creation_date)
                    # Note: Date extraction now handled by LLM
                
                if pdf_meta.modification_date:
                    metadata.additional_data['pdf_modification_date'] = str(pdf_meta.modification_date)
                    # Note: Date extraction now handled by LLM
            
            # Add page count (always available)
            metadata.additional_data['page_count'] = len(pdf_reader.pages)
                
        except Exception as e:
            # Don't fail the entire extraction if PDF metadata extraction fails
            metadata.additional_data['pdf_metadata_error'] = str(e)
    
    def _extract_organizations(self, content: str, metadata: DocumentMetadata) -> None:
        """
        Extract organization names from PDF content.
        Enhanced for PDF-specific patterns.
        
        Args:
            content: Text co
            ntent to analyze
            metadata: DocumentMetadata object to populate
        """
        # PDF-specific patterns (often found in headers/footers)
        pdf_org_patterns = [
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]*)*)\s+(?:Inc|LLC|Corp|Ltd|Company|Co\.?)\b',
            r'\b([A-Z]{2,})\s+(?:Inc|LLC|Corp|Ltd|Company|Co\.?)\b',
            r'©\s*(?:\d+\s+)?([A-Z][a-zA-Z\s&]+?)(?:\.\s|$|\.)',  # Copyright lines with optional year
            r'Published\s+by\s+([A-Z][a-zA-Z\s&]+?)(?:\s*\.|,|$)',  # Publishing info
        ]
        
        for pattern in pdf_org_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                org_name = match.group(1).strip()
                if len(org_name) > 2 and not org_name.lower() in ['the', 'and', 'for', 'with']:
                    metadata.add_organization(org_name)
    
    def get_page_count(self, file_path: str) -> int:
        """
        Get the number of pages in the PDF.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Number of pages in the PDF
        """
        try:
            pdf_reader = self._get_pdf_reader(file_path)
            return len(pdf_reader.pages)
        except Exception:
            return 0
    
    def extract_text_from_page(self, file_path: str, page_number: int) -> str:
        """
        Extract text from a specific page.
        
        Args:
            file_path: Path to the PDF file
            page_number: Page number (0-indexed)
            
        Returns:
            Text content from the specified page
        """
        try:
            pdf_reader = self._get_pdf_reader(file_path)
            if 0 <= page_number < len(pdf_reader.pages):
                return pdf_reader.pages[page_number].extract_text()
            return ""
        except Exception:
            return ""
