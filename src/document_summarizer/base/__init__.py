"""
Base package for document analyzer.
"""

from .document_reader import DocumentReader, TextDocumentReader
from .pdf_reader import PDFDocumentReader

__all__ = ["DocumentReader", "TextDocumentReader", "PDFDocumentReader"]
