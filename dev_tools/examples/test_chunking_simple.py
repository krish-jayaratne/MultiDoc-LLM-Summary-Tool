#!/usr/bin/env python3
"""
Test script to verify chunking implementation works correctly without requiring API key.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.document_summarizer.interfaces.openai_llm import OpenAILLM
from src.document_summarizer.models.metadata import DocumentMetadata

def test_token_estimation():
    """Test token estimation functionality."""
    # Create LLM instance with dummy API key
    llm = OpenAILLM(api_key="test-key-for-chunking-only")
    
    # Test with a known text
    text = "This is a test document with some content to estimate tokens."
    tokens = llm._estimate_tokens(text)
    print(f"Text: '{text}'")
    print(f"Estimated tokens: {tokens}")
    print(f"Characters: {len(text)}")
    print(f"Words: {len(text.split())}")
    print()

def test_chunking():
    """Test document chunking functionality."""
    llm = OpenAILLM(api_key="test-key-for-chunking-only")
    
    # Create a long text that would exceed token limit
    sentences = [
        "This is the first sentence of our test document.",
        "It contains important information about a property transaction.",
        "The buyer is John Smith and the seller is Jane Doe.",
        "The property is located at 123 Main Street, Springfield.",
        "The transaction amount is $250,000.",
        "The closing date is scheduled for December 15, 2023.",
        "The real estate agent is ABC Realty Company.",
        "Additional terms include a home inspection contingency.",
        "The mortgage will be handled by First National Bank.",
        "This concludes the main points of the agreement."
    ] * 20  # Repeat to make it long
    
    content = " ".join(sentences)
    print(f"Total content length: {len(content)} characters")
    print(f"Estimated tokens: {llm._estimate_tokens(content)}")
    
    # Test chunking
    chunks = llm._split_content_into_chunks(content, max_chunk_size=500)
    print(f"Number of chunks: {len(chunks)}")
    
    total_chars = 0
    for i, chunk in enumerate(chunks):
        tokens = llm._estimate_tokens(chunk)
        total_chars += len(chunk)
        print(f"Chunk {i+1}: {tokens} tokens, {len(chunk)} chars")
        print(f"Preview: {chunk[:100]}...")
        print()
    
    print(f"Total characters across all chunks: {total_chars}")
    print(f"Original content characters: {len(content)}")
    print(f"Character preservation: {total_chars >= len(content) * 0.95}")  # Allow some overlap/trimming

def test_chunk_boundary_preservation():
    """Test that sentence boundaries are preserved in chunks."""
    llm = OpenAILLM(api_key="test-key-for-chunking-only")
    
    # Create content with clear sentence boundaries
    sentences = [
        "First sentence about real estate.",
        "Second sentence about the buyer John Smith.",
        "Third sentence about the seller Jane Doe.",
        "Fourth sentence about the property location.",
        "Fifth sentence about the purchase amount."
    ]
    
    content = " ".join(sentences)
    print(f"Original content: {content}")
    print(f"Original sentences: {len(sentences)}")
    
    # Use a very small token limit to force chunking
    chunks = llm._split_content_into_chunks(content, max_chunk_size=50)
    print(f"Number of chunks: {len(chunks)}")
    
    for i, chunk in enumerate(chunks):
        print(f"Chunk {i+1}: '{chunk}'")
        # Check that chunk ends with sentence boundary
        if i < len(chunks) - 1:  # Not the last chunk
            ends_with_period = chunk.rstrip().endswith('.')
            print(f"  Ends with sentence boundary: {ends_with_period}")
        print()

if __name__ == "__main__":
    print("Testing token estimation...")
    test_token_estimation()
    
    print("\nTesting chunking...")
    test_chunking()
    
    print("\nTesting chunk boundary preservation...")
    test_chunk_boundary_preservation()
