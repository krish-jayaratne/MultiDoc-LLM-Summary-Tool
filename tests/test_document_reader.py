"""
Tests for the DocumentReader base class and TextDocumentReader implementation.
"""

import tempfile
import pytest
from datetime import datetime
from pathlib import Path

from src.document_summarizer.base.document_reader import DocumentReader, TextDocumentReader
from src.document_summarizer.models.metadata import DocumentMetadata


class TestDocumentReader:
    """Test cases for the abstract DocumentReader base class."""
    
    def test_document_reader_is_abstract(self):
        """Test that DocumentReader cannot be instantiated directly."""
        with pytest.raises(TypeError):
            DocumentReader()


class TestTextDocumentReader:
    """Test cases for the TextDocumentReader implementation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.reader = TextDocumentReader()
        self.test_content = """
        This is a test document created on January 15, 2024.
        It mentions John Smith who works at ABC Corporation.
        Please contact jane.doe@example.com for more information.
        The phone number is 555-123-4567.
        
        This document references report_2023.pdf and analysis.docx.
        Organizations mentioned include XYZ Inc and Tech Solutions LLC.
        
        People involved: Alice Johnson and Bob Wilson.
        Important dates: 12/25/2023 and 2024-03-10.
        """
    
    def test_supported_extensions(self):
        """Test that TextDocumentReader supports correct file extensions."""
        expected_extensions = {'.txt', '.md', '.rst', '.log'}
        assert self.reader.supported_extensions == expected_extensions
    
    def test_can_handle_supported_files(self):
        """Test that the reader can handle supported file types."""
        assert self.reader.can_handle("test.txt")
        assert self.reader.can_handle("readme.md")
        assert self.reader.can_handle("document.rst")
        assert self.reader.can_handle("application.log")
        assert not self.reader.can_handle("document.pdf")
        assert not self.reader.can_handle("spreadsheet.xlsx")
    
    def test_read_content_with_temp_file(self):
        """Test reading content from a temporary file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write(self.test_content)
            temp_file.flush()
            
            try:
                content = self.reader.read_content(temp_file.name)
                assert content.strip() == self.test_content.strip()
            finally:
                temp_file.close()
                Path(temp_file.name).unlink()
    
    def test_read_content_file_not_found(self):
        """Test that reading non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            self.reader.read_content("nonexistent_file.txt")
    
    def test_validate_file(self):
        """Test file validation."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write("test content")
            temp_file.flush()
            
            try:
                assert self.reader.validate_file(temp_file.name)
                assert not self.reader.validate_file("nonexistent_file.txt")
            finally:
                temp_file.close()
                Path(temp_file.name).unlink()
    
    def test_generate_description(self):
        """Test description generation from content."""
        description = self.reader._generate_description(self.test_content)
        assert len(description) <= 203  # 200 chars + "..."
        assert "This is a test document" in description
    
    def test_generate_description_short_content(self):
        """Test description generation with short content."""
        short_content = "Short document content."
        description = self.reader._generate_description(short_content)
        assert description == short_content
    
    def test_extract_metadata_complete(self):
        """Test complete metadata extraction workflow."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write(self.test_content)
            temp_file.flush()
            
            try:
                metadata = self.reader.extract_metadata(temp_file.name)
                
                # Check basic properties
                assert metadata.name == Path(temp_file.name).name
                assert len(metadata.description) > 0
                assert metadata.file_path == temp_file.name
                assert metadata.content_type == 'text/plain'
                assert metadata.file_size > 0
                assert isinstance(metadata.creation_date, datetime)
                assert isinstance(metadata.modified_date, datetime)
                
                # Check file stats
                assert len(metadata.organizations) == 0  # No entity extraction
                assert len(metadata.referenced_documents) == 0  # No entity extraction  
                assert len(metadata.document_dates) == 0  # No entity extraction
                
            finally:
                temp_file.close()
                Path(temp_file.name).unlink()
    
    def test_extract_metadata_with_provided_content(self):
        """Test metadata extraction with pre-provided content."""
        metadata = self.reader.extract_metadata("dummy_path.txt", content=self.test_content)
        
        # Should work even with dummy path since content is provided
        assert metadata.name == "dummy_path.txt"
        assert len(metadata.description) > 0
        assert len(metadata.organizations) == 0  # No entity extraction in base extract_metadata


class TestDocumentMetadataIntegration:
    """Integration tests for DocumentMetadata with DocumentReader."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.reader = TextDocumentReader()
    
    def test_metadata_summary_generation(self):
        """Test that metadata summary includes all relevant information."""
        test_content = """
        Meeting minutes from January 15, 2024.
        Attendees: John Smith (Acme Corp), Jane Doe (Tech Solutions LLC).
        Discussed project timeline and referenced project_plan.pdf.
        Next meeting scheduled for February 20, 2024.
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write(test_content)
            temp_file.flush()
            
            try:
                metadata = self.reader.extract_metadata(temp_file.name)
                summary = metadata.to_summary()
                
                assert "Document:" in summary
                assert "Description:" in summary
                assert metadata.name in summary
                
                # Check that extracted entities appear in summary
                if metadata.organizations:
                    assert "Organizations:" in summary
                if metadata.referenced_documents:
                    assert "Referenced Docs:" in summary
                if metadata.document_dates:
                    assert "Dates:" in summary
                    
            finally:
                temp_file.close()
                Path(temp_file.name).unlink()
    
    def test_metadata_entity_methods(self):
        """Test the add_* methods don't create duplicates."""
        metadata = DocumentMetadata(name="test.txt", description="Test")
        
        # Add same entity multiple times
        metadata.add_organization("Test Corp")
        metadata.add_organization("Test Corp")
        assert len(metadata.organizations) == 1
        assert "Test Corp" in metadata.organizations
        
        metadata.add_person("John Doe")
        metadata.add_person("John Doe")
        assert len(metadata.people_mentioned) == 1
        assert "John Doe" in metadata.people_mentioned
        
        metadata.add_referenced_document("doc.pdf")
        metadata.add_referenced_document("doc.pdf")
        assert len(metadata.referenced_documents) == 1
        assert "doc.pdf" in metadata.referenced_documents
        
        # Test date handling
        test_date = datetime(2024, 1, 15)
        metadata.add_date(test_date)
        metadata.add_date(test_date)
        assert len(metadata.document_dates) == 1
        assert test_date in metadata.document_dates
