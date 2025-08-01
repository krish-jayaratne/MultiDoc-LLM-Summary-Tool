"""
Document Analyzer Package

A Python package for analyzing documents with extensible architecture 
for metadata extraction and LLM integration.
"""

__version__ = "0.1.0"
__author__ = "Document Analyzer Team"

from .base.document_reader import DocumentReader, TextDocumentReader
from .base.pdf_reader import PDFDocumentReader
from .models.metadata import DocumentMetadata
from .interfaces.llm_interface import LLMInterface
from .interfaces.openai_llm import OpenAILLM

__all__ = [
    "DocumentReader", 
    "TextDocumentReader", 
    "PDFDocumentReader", 
    "DocumentMetadata", 
    "LLMInterface", 
    "OpenAILLM"
]
