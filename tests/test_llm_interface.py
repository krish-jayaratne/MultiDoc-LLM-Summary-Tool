"""
Tests for the LLM interface and DocumentAnalyzer.
"""

import tempfile
import pytest
from pathlib import Path
from datetime import datetime
# from unittest.mock import Mock

from src.document_summarizer.interfaces.llm_interface import (
    LLMInterface, 
    DocumentAnalyzer
)
from src.document_summarizer.interfaces.openai_llm import OpenAILLM
from src.document_summarizer.base.document_reader import TextDocumentReader
from src.document_summarizer.models.metadata import DocumentMetadata


class MockLLMInterface(LLMInterface):
    """Mock LLM interface for testing."""
    
    def analyze_document(self, content, metadata):
        """Mock document analysis."""
        return {
            "document_type": "business_memo",
            "summary": "Summary of document: " + content[:50] + "...",
            "organizations": ["Acme Corp", "Tech Solutions"],
            "people": ["John Smith", "Jane Doe"],
            "dates": ["2024-01-15", "2024-02-20"],
            "locations": ["New York", "San Francisco"],
            "referenced_documents": ["contract.pdf", "proposal.docx"],
            "key_information": ["quarterly results", "project timeline"],
            "properties": ["123 Main St", "456 Oak Ave"],
            "financial_amounts": ["$10,000", "$25,500"],
            "sentiment": "neutral",
            "topics": ["business", "communication"],
            "complexity_score": 0.7
        }
    
    def _call_llm_for_summary_aggregation(self, prompt: str) -> str:
        """Mock implementation for summary aggregation."""
        return "This is a mock aggregated summary combining multiple document summaries."
    
    def cross_reference_documents(self, documents):
        """Mock cross-referencing."""
        return {
            "relationships": [
                {"type": "direct_reference", "documents": ["doc1.txt", "doc2.txt"], "description": "Doc1 references Doc2"}
            ],
            "common_entities": {
                "people": ["John Smith"],
                "organizations": ["Acme Corp"],
                "locations": ["New York"]
            },
            "timeline": ["2024-01-15: Event A", "2024-02-20: Event B"],
            "summary": "Documents are related through common project references"
        }


class TestLLMInterface:
    """Test cases for the LLM interface abstract class."""
    
    def test_llm_interface_is_abstract(self):
        """Test that LLMInterface cannot be instantiated directly."""
        with pytest.raises(TypeError):
            LLMInterface()
    
    def test_mock_llm_interface(self):
        """Test the mock implementation."""
        mock_llm = MockLLMInterface()
        
        # Test document analysis
        test_content = "This is a test document."
        test_metadata = DocumentMetadata(name="test.txt", description="Test doc")
        
        analysis = mock_llm.analyze_document(test_content, test_metadata)
        assert "document_type" in analysis
        assert "summary" in analysis
        assert "organizations" in analysis
        assert "people" in analysis
        assert "sentiment" in analysis
        assert "topics" in analysis
        assert "complexity_score" in analysis
        
        # Test cross-referencing
        documents = [test_metadata]
        cross_ref = mock_llm.cross_reference_documents(documents)
        assert "relationships" in cross_ref
        assert "common_entities" in cross_ref


class TestDocumentAnalyzer:
    """Test cases for the DocumentAnalyzer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = DocumentAnalyzer()
        self.analyzer_with_llm = DocumentAnalyzer(llm_interface=MockLLMInterface())
        self.text_reader = TextDocumentReader()
        
        self.test_content = """
        Meeting minutes from January 15, 2024.
        Attendees: John Smith (Acme Corp), Jane Doe (Tech Solutions LLC).
        Discussed project timeline and referenced project_plan.pdf.
        Next meeting: February 20, 2024.
        """
    
    def test_analyzer_initialization(self):
        """Test analyzer initialization."""
        # Without LLM
        analyzer = DocumentAnalyzer()
        assert analyzer.llm_interface is None
        assert len(analyzer._document_cache) == 0
        
        # With LLM
        mock_llm = MockLLMInterface()
        analyzer_with_llm = DocumentAnalyzer(llm_interface=mock_llm)
        assert analyzer_with_llm.llm_interface is mock_llm
    
    def test_analyze_single_document_basic(self):
        """Test single document analysis without LLM."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write(self.test_content)
            temp_file.flush()
            
            try:
                result = self.analyzer.analyze_single_document(
                    temp_file.name, 
                    self.text_reader, 
                    use_llm=False
                )
                
                assert "basic_metadata" in result
                assert "content_preview" in result
                assert "file_path" in result
                assert "analysis_timestamp" in result
                assert "llm_analysis" not in result  # Should not be present when use_llm=False
                
                # Check basic metadata
                metadata = result["basic_metadata"]
                assert isinstance(metadata, DocumentMetadata)
                assert metadata.file_path == temp_file.name
                
                # Check content preview
                preview = result["content_preview"]
                assert len(preview) <= 503  # 500 + "..."
                assert "Meeting minutes" in preview
                
            finally:
                temp_file.close()
                Path(temp_file.name).unlink()
    
    def test_analyze_single_document_with_llm(self):
        """Test single document analysis with LLM."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write(self.test_content)
            temp_file.flush()
            
            try:
                result = self.analyzer_with_llm.analyze_single_document(
                    temp_file.name, 
                    self.text_reader, 
                    use_llm=True
                )
                
                assert "basic_metadata" in result
                assert "llm_analysis" in result
                
                # Check LLM results - all data is now in llm_analysis
                llm_data = result["llm_analysis"]
                assert "document_type" in llm_data
                assert "summary" in llm_data
                assert "organizations" in llm_data
                assert "people" in llm_data
                assert "sentiment" in llm_data
                
            finally:
                temp_file.close()
                Path(temp_file.name).unlink()
    
    def test_analyze_single_document_caching(self):
        """Test that document metadata is cached."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write(self.test_content)
            temp_file.flush()
            
            try:
                # Analyze document
                self.analyzer.analyze_single_document(temp_file.name, self.text_reader)
                
                # Check that metadata is cached
                cached_metadata = self.analyzer.get_cached_metadata(temp_file.name)
                assert cached_metadata is not None
                assert isinstance(cached_metadata, DocumentMetadata)
                assert cached_metadata.file_path == temp_file.name
                
            finally:
                temp_file.close()
                Path(temp_file.name).unlink()
    
    def test_cross_reference_documents_basic(self):
        """Test cross-referencing documents without LLM."""
        # Create two temporary files
        test_content_1 = """
        Project proposal by John Smith from Acme Corp.
        References design_document.pdf and timeline.xlsx.
        Deadline: March 15, 2024.
        """
        
        test_content_2 = """
        Meeting notes with John Smith and Jane Doe.
        Discussed design_document.pdf implementation.
        Acme Corp timeline updated.
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file_1:
            temp_file_1.write(test_content_1)
            temp_file_1.flush()
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file_2:
                temp_file_2.write(test_content_2)
                temp_file_2.flush()
                
                try:
                    file_paths = [temp_file_1.name, temp_file_2.name]
                    result = self.analyzer.cross_reference_documents(file_paths, self.text_reader)
                    
                    assert "documents_analyzed" in result
                    assert "basic_relationships" in result
                    assert "document_summaries" in result
                    assert result["documents_analyzed"] == 2
                    
                    # Check basic relationships
                    relationships = result["basic_relationships"]
                    assert "shared_people" in relationships
                    assert "shared_organizations" in relationships
                    assert "shared_references" in relationships
                    
                    # Should have empty relationships since no entity extraction without LLM
                    assert len(relationships["shared_people"]) == 0
                    assert len(relationships["shared_organizations"]) == 0
                    assert len(relationships["shared_references"]) == 0
                    
                finally:
                    temp_file_1.close()
                    temp_file_2.close()
                    Path(temp_file_1.name).unlink()
                    Path(temp_file_2.name).unlink()
    
    def test_cross_reference_documents_with_llm(self):
        """Test cross-referencing documents with LLM."""
        test_content = "Test document with shared content."
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write(test_content)
            temp_file.flush()
            
            try:
                file_paths = [temp_file.name]
                result = self.analyzer_with_llm.cross_reference_documents(
                    file_paths, 
                    self.text_reader
                )
                
                assert "llm_relationships" in result
                assert "relationships" in result["llm_relationships"]
                assert "common_entities" in result["llm_relationships"]
                
            finally:
                temp_file.close()
                Path(temp_file.name).unlink()
    
    def test_find_basic_relationships(self):
        """Test basic relationship finding between documents."""
        # Create test metadata
        metadata_1 = DocumentMetadata(name="doc1.txt", description="First document")
        metadata_1.add_person("John Smith")
        metadata_1.add_organization("Acme Corp")
        metadata_1.add_referenced_document("shared_doc.pdf")
        
        metadata_2 = DocumentMetadata(name="doc2.txt", description="Second document")
        metadata_2.add_person("John Smith")  # Shared person
        metadata_2.add_person("Jane Doe")
        metadata_2.add_organization("Tech Solutions")
        metadata_2.add_referenced_document("other_doc.pdf")
        
        documents = [metadata_1, metadata_2]
        relationships = self.analyzer._find_basic_relationships(documents)
        
        # Should find shared people
        shared_people_key = "doc1.txt <-> doc2.txt"
        assert shared_people_key in relationships["shared_people"]
        assert "John Smith" in relationships["shared_people"][shared_people_key]
    
    def test_cache_operations(self):
        """Test cache get and clear operations."""
        # Add something to cache
        test_metadata = DocumentMetadata(name="test.txt", description="Test")
        self.analyzer._document_cache["test_path"] = test_metadata
        
        # Test get cached metadata
        cached = self.analyzer.get_cached_metadata("test_path")
        assert cached is test_metadata
        
        # Test cache miss
        not_cached = self.analyzer.get_cached_metadata("nonexistent_path")
        assert not_cached is None
        
        # Test clear cache
        self.analyzer.clear_cache()
        assert len(self.analyzer._document_cache) == 0
