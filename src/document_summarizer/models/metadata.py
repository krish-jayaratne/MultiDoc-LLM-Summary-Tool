"""
Data models for document metadata.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any

try:
    from dataclasses_json import dataclass_json
    HAS_DATACLASSES_JSON = True
except ImportError:
    # Fallback if dataclasses_json is not available
    def dataclass_json(cls):
        return cls
    HAS_DATACLASSES_JSON = False


@dataclass_json
@dataclass
class DocumentMetadata:
    """
    Comprehensive metadata for a document.
    
    This class stores all relevant information extracted from a document,
    including basic properties, referenced entities, and analysis results.
    """
    
    # Basic document information
    name: str
    description: str
    content: Optional[str] = None
    
    # Temporal information
    creation_date: Optional[datetime] = None
    modified_date: Optional[datetime] = None
    document_dates: List[datetime] = field(default_factory=list)
    
    # Referenced entities
    referenced_documents: List[str] = field(default_factory=list)
    organizations: List[str] = field(default_factory=list)
    properties: List[str] = field(default_factory=list)
    people_mentioned: List[str] = field(default_factory=list)
    
    # Analysis metadata
    file_path: Optional[str] = None
    file_type: Optional[str] = None  
    file_size: Optional[int] = None
    content_type: Optional[str] = None
    analysis_timestamp: Optional[datetime] = field(default_factory=datetime.now)
    
    # Extensible additional data for future LLM integration
    additional_data: Dict[str, Any] = field(default_factory=dict)
    
    def add_referenced_document(self, doc_name: str) -> None:
        """Add a referenced document if not already present."""
        if doc_name not in self.referenced_documents:
            self.referenced_documents.append(doc_name)
    
    def add_organization(self, org_name: str) -> None:
        """Add an organization if not already present."""
        if org_name not in self.organizations:
            self.organizations.append(org_name)
    
    def add_property(self, property_name: str) -> None:
        """Add a property if not already present."""
        if property_name not in self.properties:
            self.properties.append(property_name)
    
    def add_person(self, person_name: str) -> None:
        """Add a person if not already present."""
        if person_name not in self.people_mentioned:
            self.people_mentioned.append(person_name)
    
    def add_date(self, date: datetime) -> None:
        """Add a document date if not already present."""
        if date not in self.document_dates:
            self.document_dates.append(date)
    
    def to_summary(self) -> str:
        """Generate a summary string of the metadata."""
        summary_parts = [
            f"Document: {self.name}",
            f"Description: {self.description}",
        ]
        
        if self.people_mentioned:
            summary_parts.append(f"People: {', '.join(self.people_mentioned)}")
        
        if self.organizations:
            summary_parts.append(f"Organizations: {', '.join(self.organizations)}")
        
        if self.referenced_documents:
            summary_parts.append(f"Referenced Docs: {', '.join(self.referenced_documents)}")
        
        if self.document_dates:
            dates_str = ', '.join(date.strftime("%Y-%m-%d") for date in self.document_dates)
            summary_parts.append(f"Dates: {dates_str}")
        
        return "\n".join(summary_parts)
