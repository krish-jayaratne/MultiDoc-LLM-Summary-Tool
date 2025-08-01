#!/usr/bin/env python3
"""
Test script to verify chunking implementation works correctly.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.document_summarizer.interfaces.openai_llm import OpenAILLM
from src.document_summarizer.models.metadata import DocumentMetadata

def test_token_estimation():
    """Test token estimation functionality."""
    llm = OpenAILLM()
    
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
    llm = OpenAILLM()
    
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
    ] * 50  # Repeat to make it long
    
    content = " ".join(sentences)
    print(f"Total content length: {len(content)} characters")
    print(f"Estimated tokens: {llm._estimate_tokens(content)}")
    
    # Test chunking
    chunks = llm._split_content_into_chunks(content, max_tokens=500)
    print(f"Number of chunks: {len(chunks)}")
    
    for i, chunk in enumerate(chunks):
        tokens = llm._estimate_tokens(chunk)
        print(f"Chunk {i+1}: {tokens} tokens, {len(chunk)} chars")
        print(f"Preview: {chunk[:100]}...")
        print()

def test_large_document_processing():
    """Test the large document processing pipeline."""
    llm = OpenAILLM()
    
    # Create a document that would exceed token limits
    content = """
    This is a comprehensive real estate purchase agreement between John Smith (buyer) and Jane Doe (seller) 
    for the property located at 123 Main Street, Springfield, Illinois. The agreed purchase price is $250,000 
    with a closing date of December 15, 2023. The transaction is being facilitated by ABC Realty Company 
    and the mortgage will be processed through First National Bank.
    
    Key terms of the agreement include:
    - Purchase price: $250,000
    - Earnest money deposit: $5,000
    - Home inspection contingency period: 10 days
    - Financing contingency: 30 days
    - Title insurance provided by Secure Title Company
    - Property taxes prorated at closing
    
    The buyer has completed a satisfactory home inspection and the property appraisal came in at $255,000, 
    confirming the fair market value. All necessary disclosures have been provided including lead paint 
    disclosure and property condition reports.
    
    Additional parties involved:
    - Buyer's attorney: Legal Partners LLC
    - Seller's attorney: Thompson & Associates
    - Home inspector: Quality Home Inspections
    - Appraiser: Certified Property Appraisals Inc.
    
    The property includes all fixtures, appliances, and improvements currently on the premises unless 
    specifically excluded in this agreement. The seller warrants clear title and agrees to provide 
    a general warranty deed at closing.
    """ * 20  # Make it large enough to require chunking
    
    doc = DocumentMetadata()
    doc.content = content
    doc.name = "test_large_document.txt"
    
    print(f"Document size: {len(content)} characters")
    print(f"Estimated tokens: {llm._estimate_tokens(content)}")
    
    # This would normally call the actual LLM, but we'll just test the chunking logic
    chunks = llm._split_content_into_chunks(content, max_tokens=1000)
    print(f"Would be split into {len(chunks)} chunks")
    
    for i, chunk in enumerate(chunks):
        print(f"Chunk {i+1}: {llm._estimate_tokens(chunk)} tokens")

if __name__ == "__main__":
    print("Testing token estimation...")
    test_token_estimation()
    
    print("Testing chunking...")
    test_chunking()
    
    print("Testing large document processing...")
    test_large_document_processing()
