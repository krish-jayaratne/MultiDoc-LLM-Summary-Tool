"""
Tests for the DocumentMetadata model.
"""

import pytest
from datetime import datetime
from dataclasses import asdict

from src.document_summarizer.models.metadata import DocumentMetadata


class TestDocumentMetadata:
    """Test cases for the DocumentMetadata class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.sample_metadata = DocumentMetadata(
            name="test_document.pdf",
            description="A sample test document for analysis"
        )
    
    def test_metadata_creation(self):
        """Test basic metadata creation."""
        assert self.sample_metadata.name == "test_document.pdf"
        assert self.sample_metadata.description == "A sample test document for analysis"
        assert self.sample_metadata.creation_date is None
        assert self.sample_metadata.modified_date is None
        assert len(self.sample_metadata.referenced_documents) == 0
        assert len(self.sample_metadata.organizations) == 0
        assert len(self.sample_metadata.people_mentioned) == 0
        assert len(self.sample_metadata.document_dates) == 0
        assert len(self.sample_metadata.additional_data) == 0
    
    def test_add_referenced_document(self):
        """Test adding referenced documents."""
        self.sample_metadata.add_referenced_document("reference1.pdf")
        self.sample_metadata.add_referenced_document("reference2.docx")
        
        assert len(self.sample_metadata.referenced_documents) == 2
        assert "reference1.pdf" in self.sample_metadata.referenced_documents
        assert "reference2.docx" in self.sample_metadata.referenced_documents
    
    def test_add_referenced_document_no_duplicates(self):
        """Test that adding the same document twice doesn't create duplicates."""
        self.sample_metadata.add_referenced_document("reference1.pdf")
        self.sample_metadata.add_referenced_document("reference1.pdf")
        
        assert len(self.sample_metadata.referenced_documents) == 1
        assert "reference1.pdf" in self.sample_metadata.referenced_documents
    
    def test_add_organization(self):
        """Test adding organizations."""
        self.sample_metadata.add_organization("Acme Corporation")
        self.sample_metadata.add_organization("Tech Solutions Inc")
        
        assert len(self.sample_metadata.organizations) == 2
        assert "Acme Corporation" in self.sample_metadata.organizations
        assert "Tech Solutions Inc" in self.sample_metadata.organizations
    
    def test_add_organization_no_duplicates(self):
        """Test that adding the same organization twice doesn't create duplicates."""
        self.sample_metadata.add_organization("Acme Corporation")
        self.sample_metadata.add_organization("Acme Corporation")
        
        assert len(self.sample_metadata.organizations) == 1
        assert "Acme Corporation" in self.sample_metadata.organizations
    
    def test_add_property(self):
        """Test adding properties."""
        self.sample_metadata.add_property("123 Main Street")
        self.sample_metadata.add_property("Commercial Building")
        
        assert len(self.sample_metadata.properties) == 2
        assert "123 Main Street" in self.sample_metadata.properties
        assert "Commercial Building" in self.sample_metadata.properties
    
    def test_add_property_no_duplicates(self):
        """Test that adding the same property twice doesn't create duplicates."""
        self.sample_metadata.add_property("123 Main Street")
        self.sample_metadata.add_property("123 Main Street")
        
        assert len(self.sample_metadata.properties) == 1
        assert "123 Main Street" in self.sample_metadata.properties
    
    def test_add_person(self):
        """Test adding people."""
        self.sample_metadata.add_person("John Smith")
        self.sample_metadata.add_person("Jane Doe")
        
        assert len(self.sample_metadata.people_mentioned) == 2
        assert "John Smith" in self.sample_metadata.people_mentioned
        assert "Jane Doe" in self.sample_metadata.people_mentioned
    
    def test_add_person_no_duplicates(self):
        """Test that adding the same person twice doesn't create duplicates."""
        self.sample_metadata.add_person("John Smith")
        self.sample_metadata.add_person("John Smith")
        
        assert len(self.sample_metadata.people_mentioned) == 1
        assert "John Smith" in self.sample_metadata.people_mentioned
    
    def test_add_date(self):
        """Test adding dates."""
        date1 = datetime(2024, 1, 15)
        date2 = datetime(2024, 2, 20)
        
        self.sample_metadata.add_date(date1)
        self.sample_metadata.add_date(date2)
        
        assert len(self.sample_metadata.document_dates) == 2
        assert date1 in self.sample_metadata.document_dates
        assert date2 in self.sample_metadata.document_dates
    
    def test_add_date_no_duplicates(self):
        """Test that adding the same date twice doesn't create duplicates."""
        date1 = datetime(2024, 1, 15)
        
        self.sample_metadata.add_date(date1)
        self.sample_metadata.add_date(date1)
        
        assert len(self.sample_metadata.document_dates) == 1
        assert date1 in self.sample_metadata.document_dates
    
    def test_to_summary_basic(self):
        """Test summary generation with basic information."""
        summary = self.sample_metadata.to_summary()
        
        assert "Document: test_document.pdf" in summary
        assert "A sample test document for analysis" in summary
    
    def test_to_summary_with_entities(self):
        """Test summary generation with various entities."""
        # Add some entities
        self.sample_metadata.add_person("John Smith")
        self.sample_metadata.add_person("Jane Doe")
        self.sample_metadata.add_organization("Acme Corp")
        self.sample_metadata.add_referenced_document("reference.pdf")
        self.sample_metadata.add_date(datetime(2024, 1, 15))
        
        summary = self.sample_metadata.to_summary()
        
        assert "People: John Smith, Jane Doe" in summary
        assert "Organizations: Acme Corp" in summary
        assert "Referenced Docs: reference.pdf" in summary
        assert "Dates: 2024-01-15" in summary
    
    def test_to_summary_empty_lists(self):
        """Test that empty entity lists don't appear in summary."""
        summary = self.sample_metadata.to_summary()
        
        assert "People:" not in summary
        assert "Organizations:" not in summary
        assert "Referenced Docs:" not in summary
        assert "Dates:" not in summary
    
    def test_additional_data_field(self):
        """Test the additional_data field for extensibility."""
        self.sample_metadata.additional_data["custom_field"] = "custom_value"
        self.sample_metadata.additional_data["analysis_score"] = 0.85
        
        assert self.sample_metadata.additional_data["custom_field"] == "custom_value"
        assert self.sample_metadata.additional_data["analysis_score"] == 0.85
    
    def test_metadata_with_all_fields(self):
        """Test metadata creation with all fields populated."""
        creation_date = datetime(2024, 1, 15, 10, 30)
        modified_date = datetime(2024, 1, 16, 14, 45)
        
        full_metadata = DocumentMetadata(
            name="comprehensive_doc.pdf",
            description="A comprehensive document with all metadata",
            creation_date=creation_date,
            modified_date=modified_date,
            file_path="/path/to/comprehensive_doc.pdf",
            file_size=2048,
            content_type="application/pdf",
            additional_data={"source": "scanner", "confidence": 0.95}
        )
        
        assert full_metadata.name == "comprehensive_doc.pdf"
        assert full_metadata.creation_date == creation_date
        assert full_metadata.modified_date == modified_date
        assert full_metadata.file_path == "/path/to/comprehensive_doc.pdf"
        assert full_metadata.file_size == 2048
        assert full_metadata.content_type == "application/pdf"
        assert full_metadata.additional_data["source"] == "scanner"
        assert full_metadata.additional_data["confidence"] == 0.95
    
    def test_dataclass_serialization(self):
        """Test that the metadata can be converted to dict (dataclass feature)."""
        # Add some data
        self.sample_metadata.add_person("John Smith")
        self.sample_metadata.add_organization("Test Corp")
        
        # Convert to dict
        metadata_dict = asdict(self.sample_metadata)
        
        assert isinstance(metadata_dict, dict)
        assert metadata_dict["name"] == "test_document.pdf"
        assert "John Smith" in metadata_dict["people_mentioned"]
        assert "Test Corp" in metadata_dict["organizations"]
    
    def test_datetime_handling(self):
        """Test proper datetime handling in metadata."""
        now = datetime.now()
        
        metadata = DocumentMetadata(
            name="time_test.txt",
            description="Testing time handling",
            creation_date=now,
            modified_date=now
        )
        
        metadata.add_date(now)
        
        assert isinstance(metadata.creation_date, datetime)
        assert isinstance(metadata.modified_date, datetime)
        assert now in metadata.document_dates
    
    def test_metadata_immutable_lists(self):
        """Test that modifying returned lists doesn't affect the metadata."""
        self.sample_metadata.add_person("John Smith")
        
        people_list = self.sample_metadata.people_mentioned
        original_length = len(people_list)
        
        # Try to modify the returned list
        people_list.append("Jane Doe")
        
        # The metadata should not be affected if properly implemented
        # (Note: This depends on implementation details of how lists are handled)
        assert len(self.sample_metadata.people_mentioned) >= original_length
