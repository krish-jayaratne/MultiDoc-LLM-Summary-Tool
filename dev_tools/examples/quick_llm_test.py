#!/usr/bin/env python3
"""
Quick OpenAI Test - Minimal example for testing

Run this for a quick test of the OpenAI integration.
"""

import os
from src.document_summarizer.interfaces.openai_llm import OpenAILLM
from src.document_summarizer.base.pdf_reader import PDFDocumentReader

# Quick test
if __name__ == "__main__":
    api_key = os.getenv('OPENAI_KEY')
    if not api_key:
        print("❌ Set OPENAI_KEY environment variable first")
        exit(1)
    
    # Initialize
    llm = OpenAILLM(api_key=api_key)
    pdf_reader = PDFDocumentReader()
    
    # Analyze PDF
    pdf_file = "data/sample_pdfs/Correspondence 1.pdf"
    content = pdf_reader.read_content(pdf_file)
    metadata = pdf_reader.extract_metadata(pdf_file)
    
    print("🤖 Analyzing with OpenAI...")
    result = llm.analyze_document(content, metadata)
    
    print(f"✅ Document type: {result.get('document_type', 'Unknown')}")
    print(f"📝 Summary: {result.get('summary', 'No summary')}")
    print(f"👥 People: {', '.join(result.get('people', []))}")
    print(f"🏢 Organizations: {', '.join(result.get('organizations', []))}")
    print(f"💰 Financial amounts: {', '.join(result.get('financial_amounts', []))}")
