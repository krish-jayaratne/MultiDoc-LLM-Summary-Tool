import pytest
from unittest.mock import Mock
from hypothesis import given, strategies as st

from src.document_summarizer.interfaces import LLMInterface
from src.document_summarizer.models import DocumentMetadata


class TestLLMInterface():
    """Test the abstract base class - focus on concrete methods and interface contract."""
    
    def test_llm_interface_is_abstract(self):
        """Test that LLMInterface cannot be instantiated directly."""
        with pytest.raises(TypeError):
            LLMInterface()
            
    def test_create_document_analysis_prompt(self):
        """Test the concrete prompt creation method."""
        # Use Mock - simple and focused on the method logic
        mock_llm = Mock(spec=LLMInterface)
        
        # Minimal but realistic test data
        content = "Sample document content for analysis."
        metadata = DocumentMetadata(
            name="test_document.pdf",
            description="Test document",
            file_type="PDF"
        )
        
        # Test the concrete method
        prompt = LLMInterface.create_document_analysis_prompt(mock_llm, content, metadata)
        
        # Verify exact output - this is deterministic
        expected_prompt = """Analyze this document:

Filename: test_document.pdf
File Type: PDF

Content:
Sample document content for analysis.

Please extract the structured information as specified."""
        
        assert prompt == expected_prompt

    @given(
        content=st.text(
            min_size=100, 
            max_size=1000,
            alphabet=st.characters(
                min_codepoint=32,  # Space character
                max_codepoint=126,  # Tilde character (~)
                blacklist_characters='\n\r\t'  # Keep some control for readability
            )
        ),
        filename=st.text(
            min_size=1, 
            max_size=100, 
            alphabet=st.characters(
                categories=['Lu', 'Ll', 'Nd', 'Pc'],  # Letters, numbers, connectors
                blacklist_characters='\n\r'
            )
        ),
        file_type=st.sampled_from(['PDF', 'text', 'docx', 'html', 'md']),
        description=st.text(
            min_size=1, 
            max_size=200,
            alphabet=st.characters(
                min_codepoint=32,
                max_codepoint=126
            )
        )
    )
    def test_create_document_analysis_prompt_properties(self, content, filename, file_type, description):
        """Property-based test: verify prompt structure with various inputs."""
        mock_llm = Mock(spec=LLMInterface)
        
        metadata = DocumentMetadata(
            name=filename,
            description=description,
            file_type=file_type
        )
        
        prompt = LLMInterface.create_document_analysis_prompt(mock_llm, content, metadata)
        
        expected_length = (
            len("Analyze this document:\n\nFilename: ") +
            len(filename) +
            len("\nFile Type: ") +
            len(file_type) +
            len("\n\nContent:\n") +
            len(content) +
            len("\n\nPlease extract the structured information as specified.")
        )
       
        print(f"{'='*50}\n{prompt}{'='*50}")
        
        # Verify all input characters are preserved
        assert len(prompt) == expected_length, "Prompt length mismatch suggests character encoding issues"
        assert filename in prompt, "Filename characters may have been altered"
        assert content in prompt, "Content characters may have been altered"
        assert file_type in prompt, "File type characters may have been altered"        
        # Properties that should always be true regardless of input
        assert "Analyze this document:" in prompt
        assert f"Filename: {filename}" in prompt
        assert f"File Type: {file_type}" in prompt
        assert "Content:" in prompt
        assert content in prompt
        assert "Please extract the structured information as specified." in prompt
        
        # Structure properties
        lines = prompt.split('\n')
        assert len(lines) >= 6  # Minimum expected lines
        assert lines[0] == "Analyze this document:"
        assert lines[-1] == "Please extract the structured information as specified."
    
    @given(st.lists(
        st.builds(
            DocumentMetadata,
            name=st.text(min_size=1, max_size=50, alphabet=st.characters(min_codepoint=32, max_codepoint=126, blacklist_characters='\n\r"')),
            description=st.text(min_size=1, max_size=100, alphabet=st.characters(min_codepoint=32, max_codepoint=126)),
            file_type=st.sampled_from(['PDF', 'text', 'docx'])
        ),
        min_size=1,
        max_size=5
    ))
    def test_create_cross_reference_prompt_properties(self, documents):
        """Property-based test: verify cross-reference prompt with various document lists."""
        mock_llm = Mock(spec=LLMInterface)
        
        prompt = LLMInterface.create_cross_reference_prompt(mock_llm, documents)
        
        # Properties that should always be true
        assert f"Analyze relationships between these {len(documents)} documents:" in prompt
        assert "Find all relationships and connections between these documents." in prompt
        
        # Should contain valid JSON structure
        import json
        # Extract the JSON part (between the first [ and last ])
        start_idx = prompt.find('[')
        end_idx = prompt.rfind(']') + 1
        if start_idx != -1 and end_idx != 0:
            json_part = prompt[start_idx:end_idx]
            # Should be valid JSON
            parsed = json.loads(json_part)
            assert len(parsed) == len(documents)
            
            # Verify JSON structure (data might be escaped in JSON)
            for i, doc in enumerate(documents):
                assert parsed[i]['filename'] == doc.name
                assert parsed[i]['type'] == doc.file_type
                assert parsed[i]['description'] == doc.description
                # Don't test raw string presence due to JSON escaping
    
    def test_create_cross_reference_prompt(self):
        """Test the concrete cross-reference prompt method."""
        mock_llm = Mock(spec=LLMInterface)
        
        # Create minimal test documents
        docs = [
            DocumentMetadata(name="doc1.pdf", description="First document", file_type="PDF"),
            DocumentMetadata(name="doc2.txt", description="Second document", file_type="text")
        ]
        
        prompt = LLMInterface.create_cross_reference_prompt(mock_llm, docs)
        
        # Test the exact expected output since the method is deterministic
        expected_prompt = """Analyze relationships between these 2 documents:

[
  {
    "filename": "doc1.pdf",
    "type": "PDF",
    "description": "First document",
    "content_preview": ""
  },
  {
    "filename": "doc2.txt",
    "type": "text",
    "description": "Second document",
    "content_preview": ""
  }
]

Find all relationships and connections between these documents."""
        
        assert prompt == expected_prompt

  