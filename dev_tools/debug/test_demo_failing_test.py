"""
Example test that will fail to demonstrate pytest --pdb usage.
"""

import pytest
from src.document_summarizer.base.document_reader import TextDocumentReader

import pytest
from src.document_summarizer.base.document_reader import TextDocumentReader


def test_that_will_fail_for_demo():
    """This test will fail to demonstrate pytest --pdb."""
    reader = TextDocumentReader()
    
    # This assertion will fail
    result = reader._generate_description("Test content")
    
    # Deliberately wrong assertion to trigger failure
    assert result == "This will not match", f"Expected 'This will not match', got '{result}'"


def test_with_manual_debugging():
    """Test with manual pdb breakpoint."""
    reader = TextDocumentReader()
    
    content = "Test content for debugging"
    
    # Add manual breakpoint
    import pdb; pdb.set_trace()
    
    result = reader._generate_description(content)
    assert len(result) > 0


if __name__ == "__main__":
    # You can run this with:
    # pytest demo_failing_test.py::test_that_will_fail_for_demo --pdb
    test_that_will_fail_for_demo()
