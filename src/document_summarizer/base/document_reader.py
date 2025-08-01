"""
Base document reader class for extensible document analysis.
"""

import os
import re
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any, Set

from ..models.metadata import DocumentMetadata


class DocumentReader(ABC):
    """
    Abstract base class for document readers.
    
    This class provides a common interface for reading and analyzing different
    types of documents. Subclasses should implement the specific logic for
    their document type while leveraging the common metadata extraction methods.
    """
    
    def __init__(self):
        """Initialize the document reader."""
        self.supported_extensions: Set[str] = set()
    
    @abstractmethod
    def read_content(self, file_path: str) -> str:
        """
        Read the content of a document.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            The text content of the document
            
        Raises:
            NotImplementedError: This method must be implemented by subclasses
        """
        pass
    
    def extract_metadata(self, file_path: str, content: Optional[str] = None) -> DocumentMetadata:
        """
        Extract comprehensive metadata from a document.
        
        Args:
            file_path: Path to the document file
            content: Optional pre-loaded content. If None, will read from file
            
        Returns:
            DocumentMetadata object containing extracted information
        """
        if content is None:
            content = self.read_content(file_path)
        
        # Create base metadata
        metadata = DocumentMetadata(
            name=Path(file_path).name,
            description=self._generate_description(content),
            file_path=file_path
        )
        
        # Add file statistics
        self._add_file_stats(metadata, file_path)
        
        return metadata
    
    def _add_file_stats(self, metadata: DocumentMetadata, file_path: str) -> None:
        """Add file statistics to metadata."""
        try:
            stat = os.stat(file_path)
            metadata.file_size = stat.st_size
            metadata.creation_date = datetime.fromtimestamp(stat.st_ctime)
            metadata.modified_date = datetime.fromtimestamp(stat.st_mtime)
            
            # Determine content type based on extension
            ext = Path(file_path).suffix.lower()
            content_type_map = {
                '.txt': 'text/plain',
                '.pdf': 'application/pdf',
                '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                '.doc': 'application/msword',
                '.md': 'text/markdown',
                '.html': 'text/html',
                '.xml': 'text/xml',
                '.json': 'application/json'
            }
            metadata.content_type = content_type_map.get(ext, 'application/octet-stream')
        except (OSError, FileNotFoundError):
            pass
    
    def _generate_description(self, content: str) -> str:
        """
        Generate a short description of the document content.
        
        Args:
            content: The document content
            
        Returns:
            A brief description of the document
        """
        content = content.strip()
        
        # If content is short enough, return as-is
        if len(content) <= 200:
            return content
        
        # For longer content, try to extract first complete sentence
        sentences = re.split(r'[.!?]+', content)
        if sentences:
            # Take first non-empty sentence, limited to 200 characters
            for sentence in sentences[:3]:
                clean_sentence = sentence.strip()
                if clean_sentence and len(clean_sentence) > 10:
                    return clean_sentence[:200] + ('...' if len(clean_sentence) > 200 else '')
        
        # Fallback to first 200 characters
        return content[:200] + ('...' if len(content) > 200 else '')
    
    def can_handle(self, file_path: str) -> bool:
        """
        Check if this reader can handle the given file.
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            True if this reader can handle the file, False otherwise
        """
        if not self.supported_extensions:
            return True  # Base class can attempt to handle any file
        
        extension = Path(file_path).suffix.lower()
        return extension in self.supported_extensions
    
    def validate_file(self, file_path: str) -> bool:
        """
        Validate that the file exists and is readable.
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            True if file is valid and readable, False otherwise
        """
        try:
            path = Path(file_path)
            return path.exists() and path.is_file() and os.access(file_path, os.R_OK)
        except (OSError, TypeError):
            return False


class TextDocumentReader(DocumentReader):
    """
    Concrete implementation for reading plain text documents.
    
    This serves as a basic implementation and example of how to extend
    the base DocumentReader class.
    """
    
    def __init__(self):
        """Initialize the text document reader."""
        super().__init__()
        self.supported_extensions = {'.txt', '.md', '.rst', '.log'}
    
    def read_content(self, file_path: str) -> str:
        """
        Read content from a text file.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            The content of the text file
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            IOError: If there's an error reading the file
        """
        if not self.validate_file(file_path):
            raise FileNotFoundError(f"File not found or not readable: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Try with different encoding if UTF-8 fails
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read()
    
