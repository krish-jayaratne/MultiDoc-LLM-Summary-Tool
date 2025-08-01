"""
Tests for PDF document reader functionality.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

from src.document_summarizer.base.pdf_reader import PDFDocumentReader
from src.document_summarizer.models.metadata import DocumentMetadata


class TestPDFDocumentReader:
    """Test cases for PDFDocumentReader class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.reader = PDFDocumentReader()
    
    def test_initialization(self):
        """Test PDFDocumentReader initialization."""
        assert self.reader.supported_extensions == {'.pdf'}
    
    def test_can_handle_pdf_file(self):
        """Test that PDF files are recognized as readable."""
        assert self.reader.can_handle("document.pdf")
        assert self.reader.can_handle("path/to/file.PDF")  # Case insensitive
        assert not self.reader.can_handle("document.txt")
        assert not self.reader.can_handle("document.docx")
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('PyPDF2.PdfReader')
    def test_read_content_success(self, mock_pdf_reader, mock_file_open):
        """Test successful PDF content reading."""
        # Mock PDF reader and pages
        mock_page1 = Mock()
        mock_page1.extract_text.return_value = "Page 1 content"
        mock_page2 = Mock()
        mock_page2.extract_text.return_value = "Page 2 content"
        
        mock_reader_instance = Mock()
        mock_reader_instance.pages = [mock_page1, mock_page2]
        mock_pdf_reader.return_value = mock_reader_instance
        
        # Mock file validation
        with patch.object(self.reader, 'validate_file', return_value=True):
            content = self.reader.read_content("test.pdf")
        
        assert content == "Page 1 content\n\nPage 2 content"
        mock_file_open.assert_called_once_with("test.pdf", 'rb')
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('PyPDF2.PdfReader')
    def test_read_content_with_empty_pages(self, mock_pdf_reader, mock_file_open):
        """Test PDF content reading with empty pages."""
        # Mock PDF reader with empty and non-empty pages
        mock_page1 = Mock()
        mock_page1.extract_text.return_value = "Page 1 content"
        mock_page2 = Mock()
        mock_page2.extract_text.return_value = ""  # Empty page
        mock_page3 = Mock()
        mock_page3.extract_text.return_value = "   "  # Whitespace only
        mock_page4 = Mock()
        mock_page4.extract_text.return_value = "Page 4 content"
        
        mock_reader_instance = Mock()
        mock_reader_instance.pages = [mock_page1, mock_page2, mock_page3, mock_page4]
        mock_pdf_reader.return_value = mock_reader_instance
        
        with patch.object(self.reader, 'validate_file', return_value=True):
            content = self.reader.read_content("test.pdf")
        
        # Should only include non-empty pages
        assert content == "Page 1 content\n\nPage 4 content"
    
    def test_read_content_file_not_found(self):
        """Test read_content with non-existent file."""
        with patch.object(self.reader, 'validate_file', return_value=False):
            with pytest.raises(FileNotFoundError):
                self.reader.read_content("nonexistent.pdf")
    
    @patch('builtins.open', side_effect=IOError("Read error"))
    def test_read_content_io_error(self, mock_file_open):
        """Test read_content with IO error."""
        with patch.object(self.reader, 'validate_file', return_value=True):
            with pytest.raises(IOError, match="Error reading PDF file"):
                self.reader.read_content("test.pdf")
    
    @patch.object(PDFDocumentReader, 'read_content')
    @patch.object(PDFDocumentReader, '_extract_pdf_metadata')
    def test_extract_metadata_success(self, mock_extract_pdf, mock_read_content):
        """Test successful metadata extraction."""
        # Mock the content reading
        mock_content = """
        Sample PDF document from ACME Corporation.
        Created by John Smith on January 15, 2024.
        References Technical_Report.pdf and User_Guide.docx.
        """
        mock_read_content.return_value = mock_content
        
        # Mock file validation
        with patch.object(self.reader, 'validate_file', return_value=True):
            metadata = self.reader.extract_metadata("test.pdf")
        
        assert isinstance(metadata, DocumentMetadata)
        assert metadata.name == "test.pdf"
        assert metadata.file_type == "PDF"
        assert metadata.content == mock_content
        
        # Note: Entity extraction (organizations, people, etc.) is now handled by LLM
        # These fields will be empty in the basic PDF reader
        assert metadata.organizations == []
        assert metadata.people_mentioned == []
        
        # Verify PDF metadata extraction was called
        mock_extract_pdf.assert_called_once()
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('PyPDF2.PdfReader')
    def test_extract_pdf_metadata_success(self, mock_pdf_reader, mock_file_open):
        """Test PDF-specific metadata extraction."""
        # Mock PDF metadata
        mock_metadata = Mock()
        mock_metadata.title = "Test Document"
        mock_metadata.author = "John Doe"
        mock_metadata.subject = "Test Subject"
        mock_metadata.creator = "Test Creator"
        mock_metadata.producer = "Test Producer"
        mock_metadata.creation_date = "2024-01-15"
        mock_metadata.modification_date = "2024-01-16"
        
        mock_reader_instance = Mock()
        mock_reader_instance.metadata = mock_metadata
        mock_reader_instance.pages = [Mock(), Mock()]  # 2 pages
        mock_pdf_reader.return_value = mock_reader_instance
        
        # Create a test metadata object
        test_metadata = DocumentMetadata(
            name="test.pdf",
            description="Test PDF document for metadata extraction",
            file_path="test.pdf",
            file_type="PDF",
            content=""
        )
        
        # Extract PDF metadata
        self.reader._extract_pdf_metadata("test.pdf", test_metadata)
        
        # Verify metadata was extracted
        assert test_metadata.additional_data['pdf_title'] == "Test Document"
        assert test_metadata.additional_data['pdf_author'] == "John Doe"
        assert test_metadata.additional_data['pdf_subject'] == "Test Subject"
        assert test_metadata.additional_data['page_count'] == 2
        
        # Note: Entity extraction (people, dates) is now handled by LLM
        assert test_metadata.people_mentioned == []
        assert test_metadata.document_dates == []
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('PyPDF2.PdfReader')
    def test_extract_pdf_metadata_no_metadata(self, mock_pdf_reader, mock_file_open):
        """Test PDF metadata extraction when no metadata is available."""
        mock_reader_instance = Mock()
        mock_reader_instance.metadata = None
        mock_reader_instance.pages = [Mock()]  # 1 page
        mock_pdf_reader.return_value = mock_reader_instance
        
        test_metadata = DocumentMetadata(
            name="test.pdf",
            description="Test PDF document with no metadata",
            file_path="test.pdf",
            file_type="PDF",
            content=""
        )
        
        self.reader._extract_pdf_metadata("test.pdf", test_metadata)
        
        # Should still have page count
        assert test_metadata.additional_data['page_count'] == 1
        assert 'pdf_title' not in test_metadata.additional_data
    
    @patch('builtins.open', side_effect=Exception("PDF metadata error"))
    def test_extract_pdf_metadata_error_handling(self, mock_file_open):
        """Test PDF metadata extraction error handling."""
        test_metadata = DocumentMetadata(
            name="test.pdf",
            description="Test PDF document for error handling",
            file_path="test.pdf",
            file_type="PDF",
            content=""
        )
        
        # Should not raise exception, but record error
        self.reader._extract_pdf_metadata("test.pdf", test_metadata)
        
        assert 'pdf_metadata_error' in test_metadata.additional_data
        assert "PDF metadata error" in test_metadata.additional_data['pdf_metadata_error']
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('PyPDF2.PdfReader')
    def test_get_page_count(self, mock_pdf_reader, mock_file_open):
        """Test getting page count from PDF."""
        mock_reader_instance = Mock()
        mock_reader_instance.pages = [Mock(), Mock(), Mock()]  # 3 pages
        mock_pdf_reader.return_value = mock_reader_instance
        
        page_count = self.reader.get_page_count("test.pdf")
        assert page_count == 3
    
    @patch('builtins.open', side_effect=Exception("Error"))
    def test_get_page_count_error(self, mock_file_open):
        """Test get_page_count error handling."""
        page_count = self.reader.get_page_count("test.pdf")
        assert page_count == 0
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('PyPDF2.PdfReader')
    def test_extract_text_from_page(self, mock_pdf_reader, mock_file_open):
        """Test extracting text from specific page."""
        mock_page = Mock()
        mock_page.extract_text.return_value = "Page content"
        
        mock_reader_instance = Mock()
        mock_reader_instance.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader_instance
        
        text = self.reader.extract_text_from_page("test.pdf", 0)
        assert text == "Page content"
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('PyPDF2.PdfReader')
    def test_extract_text_from_invalid_page(self, mock_pdf_reader, mock_file_open):
        """Test extracting text from invalid page number."""
        mock_reader_instance = Mock()
        mock_reader_instance.pages = [Mock()]  # Only 1 page
        mock_pdf_reader.return_value = mock_reader_instance
        
        text = self.reader.extract_text_from_page("test.pdf", 5)  # Invalid page
        assert text == ""
    
    def test_extract_organizations_pdf_specific(self):
        """Test PDF-specific organization extraction patterns."""
        content = """
        © 2024 ACME Corporation. All rights reserved.
        Published by Tech Solutions LLC in partnership with XYZ Inc.
        Created using Adobe Acrobat Pro.
        """
        
        metadata = DocumentMetadata(
            name="test.pdf",
            description="Test PDF document for organization extraction",
            file_path="test.pdf",
            file_type="PDF",
            content=content
        )
        
        self.reader._extract_organizations(content, metadata)
        
        # Should find organizations from copyright and publishing info
        organizations = [org.lower() for org in metadata.organizations]
        assert any("acme" in org for org in organizations)
        assert any("tech solutions" in org for org in organizations)
    
    @patch.object(PDFDocumentReader, 'validate_file', return_value=False)
    def test_extract_metadata_file_not_found(self, mock_validate):
        """Test extract_metadata with non-existent file."""
        with pytest.raises(FileNotFoundError):
            self.reader.extract_metadata("nonexistent.pdf")


class TestPDFDocumentReaderIntegration:
    """Integration tests for PDF document reader."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.reader = PDFDocumentReader()
    
    def test_workflow_with_mock_pdf(self):
        """Test complete workflow with mocked PDF."""
        with patch.object(self.reader, 'validate_file', return_value=True), \
             patch.object(self.reader, 'read_content') as mock_read, \
             patch.object(self.reader, '_extract_pdf_metadata') as mock_pdf_meta:
            
            # Mock content
            mock_content = """
            Technical Report - Q1 2024
            Prepared by: Alice Johnson, Bob Smith
            Companies involved: Microsoft Corp, Google LLC, Amazon Inc
            Document references: previous_report.pdf, data_analysis.xlsx
            Important dates: March 1, 2024, April 15, 2024
            """
            mock_read.return_value = mock_content
            
            # Extract metadata
            metadata = self.reader.extract_metadata("report.pdf")
            
            # Verify results
            assert metadata.name == "report.pdf"
            assert metadata.file_type == "PDF"
            # Since we removed entity extraction from PDF reader, these should be empty
            assert len(metadata.organizations) == 0
            assert len(metadata.people_mentioned) == 0
            assert len(metadata.document_dates) == 0
            assert metadata.description is not None
            
            # Verify methods were called
            mock_read.assert_called_once()
            mock_pdf_meta.assert_called_once()
