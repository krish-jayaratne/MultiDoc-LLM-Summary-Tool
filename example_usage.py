#!/usr/bin/env python3
"""
Example usage of the Document Analyzer.

This script demonstrates how to use the document analyzer to extract metadata
from documents and perform basic analysis.
"""

import sys
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from document_summarizer.base.document_reader import TextDocumentReader
from document_summarizer.interfaces.llm_interface import DocumentAnalyzer
from document_summarizer.models.metadata import DocumentMetadata


def create_sample_document():
    """Create a sample document for demonstration."""
    sample_content = """
    Meeting Minutes - Project Alpha Planning
    Date: January 15, 2024
    
    Attendees:
    - John Smith (Project Manager, Acme Corporation)
    - Jane Doe (Technical Lead, Tech Solutions LLC)
    - Bob Wilson (Business Analyst, Acme Corporation)
    
    Agenda:
    1. Project timeline review
    2. Resource allocation discussion
    3. Risk assessment update
    
    Discussion:
    John Smith opened the meeting by reviewing the current project status.
    The team discussed the project_timeline.xlsx document and identified 
    several key milestones for Q1 2024.
    
    Jane Doe presented the technical architecture, referencing the 
    system_design.pdf document that was shared last week.
    
    Action Items:
    - Update resource_plan.docx by January 25, 2024
    - Schedule follow-up meeting for February 10, 2024
    - Contact Sarah Johnson at Partner Corp for vendor quotes
    
    Next Meeting: February 10, 2024 at 2:00 PM
    Location: Conference Room B
    
    Organizations mentioned:
    - Acme Corporation (primary client)
    - Tech Solutions LLC (technical partner)
    - Partner Corp (vendor)
    
    Properties discussed:
    - 123 Main Street Office Building (new location)
    - Data Center Facility at 456 Tech Park Drive
    """
    
    # Create sample document
    sample_path = Path("sample_meeting_minutes.txt")
    with open(sample_path, "w") as f:
        f.write(sample_content)
    
    return sample_path


def analyze_document_example():
    """Demonstrate document analysis capabilities."""
    print("Document Analyzer Example")
    print("=" * 50)
    
    # Create sample document
    print("Creating sample document...")
    sample_path = create_sample_document()
    
    try:
        # Initialize document reader and analyzer
        text_reader = TextDocumentReader()
        analyzer = DocumentAnalyzer()  # Without LLM for this example
        
        print(f"Analyzing document: {sample_path}")
        print("-" * 30)
        
        # Analyze the document
        result = analyzer.analyze_single_document(
            str(sample_path), 
            text_reader, 
            use_llm=False  # Set to True when LLM is implemented
        )
        
        # Extract metadata
        metadata = result["basic_metadata"]
        
        # Display results
        print("DOCUMENT METADATA")
        print("=" * 30)
        print(metadata.to_summary())
        print()
        
        print("DETAILED INFORMATION")
        print("=" * 30)
        print(f"File Path: {metadata.file_path}")
        print(f"File Size: {metadata.file_size} bytes")
        print(f"Content Type: {metadata.content_type}")
        print(f"Creation Date: {metadata.creation_date}")
        print(f"Modified Date: {metadata.modified_date}")
        print()
        
        if metadata.people_mentioned:
            print("PEOPLE MENTIONED:")
            for person in metadata.people_mentioned:
                print(f"  - {person}")
            print()
        
        if metadata.organizations:
            print("ORGANIZATIONS:")
            for org in metadata.organizations:
                print(f"  - {org}")
            print()
        
        if metadata.referenced_documents:
            print("REFERENCED DOCUMENTS:")
            for doc in metadata.referenced_documents:
                print(f"  - {doc}")
            print()
        
        if metadata.document_dates:
            print("DATES MENTIONED:")
            for date in metadata.document_dates:
                print(f"  - {date.strftime('%Y-%m-%d')}")
            print()
        
        if metadata.properties:
            print("PROPERTIES:")
            for prop in metadata.properties:
                print(f"  - {prop}")
            print()
        
        print("CONTENT PREVIEW")
        print("=" * 30)
        preview = result["content_preview"]
        print(preview)
        print()
        
        # Demonstrate creating custom metadata
        print("CUSTOM METADATA EXAMPLE")
        print("=" * 30)
        custom_metadata = DocumentMetadata(
            name="custom_document.pdf",
            description="Example of manually created metadata"
        )
        
        # Add entities manually
        custom_metadata.add_person("Alice Johnson")
        custom_metadata.add_person("Charlie Brown")
        custom_metadata.add_organization("Example Corp")
        custom_metadata.add_referenced_document("reference.pdf")
        custom_metadata.additional_data["priority"] = "high"
        custom_metadata.additional_data["department"] = "engineering"
        
        print(custom_metadata.to_summary())
        print(f"Additional Data: {custom_metadata.additional_data}")
        
    finally:
        # Clean up sample file
        if sample_path.exists():
            sample_path.unlink()
            print(f"\nCleaned up sample file: {sample_path}")


def demonstrate_inheritance():
    """Demonstrate how to extend the DocumentReader class."""
    print("\n" + "=" * 50)
    print("INHERITANCE EXAMPLE")
    print("=" * 50)
    
    class CustomDocumentReader(TextDocumentReader):
        """Example of extending the TextDocumentReader."""
        
        def __init__(self):
            super().__init__()
            # Add support for additional file types
            self.supported_extensions.add('.log')
            self.supported_extensions.add('.config')
        
        def _extract_custom_entities(self, content, metadata):
            """Example of custom entity extraction."""
            import re
            
            # Extract IP addresses
            ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
            ip_addresses = re.findall(ip_pattern, content)
            
            # Store in additional_data
            if ip_addresses:
                metadata.additional_data['ip_addresses'] = list(set(ip_addresses))
            
            # Extract error codes
            error_pattern = r'ERROR\s+(\d+)'
            error_codes = re.findall(error_pattern, content, re.IGNORECASE)
            
            if error_codes:
                metadata.additional_data['error_codes'] = list(set(error_codes))
        
        def extract_metadata(self, file_path, content=None):
            """Override to add custom extraction."""
            # Call parent method
            metadata = super().extract_metadata(file_path, content)
            
            # Add custom extraction
            if content is None:
                content = self.read_content(file_path)
            
            self._extract_custom_entities(content, metadata)
            
            return metadata
    
    # Test the custom reader
    custom_reader = CustomDocumentReader()
    
    print("Custom Reader Supported Extensions:")
    print(f"  {', '.join(sorted(custom_reader.supported_extensions))}")
    
    # Test with sample content containing IP addresses and error codes
    test_content = """
    Server log file from 2024-01-15
    Connection from 192.168.1.100 established
    ERROR 404: File not found
    Connection from 10.0.0.5 failed
    ERROR 500: Internal server error
    Normal operation resumed
    """
    
    # Create a temporary file
    temp_path = Path("test_log.log")
    with open(temp_path, "w") as f:
        f.write(test_content)
    
    try:
        metadata = custom_reader.extract_metadata(str(temp_path))
        
        print("\nCustom Extraction Results:")
        print(f"IP Addresses: {metadata.additional_data.get('ip_addresses', [])}")
        print(f"Error Codes: {metadata.additional_data.get('error_codes', [])}")
        
    finally:
        if temp_path.exists():
            temp_path.unlink()


if __name__ == "__main__":
    try:
        analyze_document_example()
        demonstrate_inheritance()
        
        print("\n" + "=" * 50)
        print("NEXT STEPS")
        print("=" * 50)
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run tests: pytest")
        print("3. Implement LLM integration in interfaces/llm_interface.py")
        print("4. Create additional document readers for PDF, DOCX, etc.")
        print("5. Add more sophisticated entity extraction patterns")
        
    except Exception as e:
        print(f"Error running example: {e}")
        sys.exit(1)
