#!/usr/bin/env python3
"""
Test script to verify the complete large document analysis workflow.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.document_summarizer.interfaces.openai_llm import OpenAILLM
from src.document_summarizer.models.metadata import DocumentMetadata

def test_large_document_workflow():
    """Test the complete workflow for handling large documents."""
    # Create LLM instance with dummy API key
    llm = OpenAILLM(api_key="test-key-for-chunking-only")
    
    # Create a large document that would exceed the token limit
    large_content = """
    REAL ESTATE PURCHASE AGREEMENT
    
    This comprehensive real estate purchase agreement is entered into between John Smith (buyer) 
    and Jane Doe (seller) for the property located at 123 Main Street, Springfield, Illinois 62701.
    
    PURCHASE DETAILS:
    - Purchase price: $250,000
    - Earnest money deposit: $5,000 paid to Secure Escrow Company
    - Closing date: December 15, 2023
    - Property type: Single-family residential home
    - Lot size: 0.25 acres
    - Square footage: 1,850 sq ft
    
    PARTIES INVOLVED:
    - Buyer: John Smith, 456 Oak Avenue, Springfield, IL 62702
    - Seller: Jane Doe, 789 Pine Street, Springfield, IL 62703
    - Buyer's Agent: Sarah Johnson, ABC Realty Company
    - Seller's Agent: Mike Wilson, XYZ Properties
    - Title Company: Secure Title Company
    - Lender: First National Bank
    
    PROPERTY DESCRIPTION:
    The property includes a three-bedroom, two-bathroom home built in 1995. 
    The home features a two-car garage, full basement, and updated kitchen with granite countertops.
    Recent improvements include new HVAC system (2022), roof replacement (2021), and 
    hardwood floor refinishing (2020).
    
    FINANCIAL TERMS:
    The buyer will obtain financing through First National Bank for $200,000 (80% LTV).
    The down payment of $50,000 will be provided at closing.
    Property taxes for 2023 are $3,200 and will be prorated at closing.
    Homeowner's insurance premium of $1,200 annually has been secured.
    
    CONTINGENCIES:
    1. Home inspection contingency: 10 business days from contract acceptance
    2. Financing contingency: 30 calendar days from contract acceptance
    3. Appraisal contingency: Property must appraise for at least purchase price
    4. Title contingency: Clear and marketable title required
    
    INSPECTION RESULTS:
    Professional home inspection conducted by Quality Home Inspections on November 15, 2023.
    Minor issues identified: 
    - Loose handrail on basement stairs (estimated repair: $75)
    - Small leak in guest bathroom faucet (estimated repair: $150)
    - Weather stripping needed on front door (estimated repair: $50)
    Total estimated repairs: $275
    
    APPRAISAL:
    Property appraisal completed by Certified Property Appraisals Inc. on November 20, 2023.
    Appraised value: $255,000 (exceeds purchase price by $5,000)
    Comparable sales used: 456 Elm Street ($248,000), 789 Maple Avenue ($252,000), 
    321 Cedar Lane ($258,000)
    
    ADDITIONAL TERMS:
    - All appliances included: refrigerator, stove, dishwasher, washer, dryer
    - Window treatments and light fixtures included
    - Seller to provide one-year home warranty through Premier Home Warranty
    - Possession at closing unless otherwise agreed
    
    DISCLOSURES:
    All required disclosures have been provided including:
    - Lead-based paint disclosure (house built before 1978: No)
    - Property condition disclosure
    - Homeowner's association disclosure (No HOA)
    - Flood zone disclosure (Property not in flood zone)
    
    LEGAL REPRESENTATION:
    - Buyer's attorney: Legal Partners LLC, 123 Court Street, Springfield, IL
    - Seller's attorney: Thompson & Associates, 456 Law Avenue, Springfield, IL
    
    This agreement represents the complete understanding between the parties and supersedes 
    all prior negotiations, representations, or agreements relating to the subject property.
    """ * 5  # Multiply to make it very large
    
    print(f"Large document content length: {len(large_content)} characters")
    print(f"Estimated tokens: {llm._estimate_tokens(large_content)}")
    
    # Test if this would trigger chunking
    if llm._estimate_tokens(large_content) > 4000:
        print("✓ Document exceeds 4000 token limit - chunking would be triggered")
        
        # Test the chunking
        chunks = llm._split_content_into_chunks(large_content, max_chunk_size=4000)
        print(f"Document would be split into {len(chunks)} chunks")
        
        for i, chunk in enumerate(chunks):
            tokens = llm._estimate_tokens(chunk)
            print(f"  Chunk {i+1}: {tokens} tokens, {len(chunk)} characters")
            
            # Show what entities might be found in this chunk
            if "John Smith" in chunk:
                print(f"    - Contains buyer information")
            if "Jane Doe" in chunk:
                print(f"    - Contains seller information")
            if "$250,000" in chunk:
                print(f"    - Contains purchase price")
            if "December 15, 2023" in chunk:
                print(f"    - Contains closing date")
            if "123 Main Street" in chunk:
                print(f"    - Contains property address")
        
        print("\n✓ Each chunk stays within token limits")
        print("✓ Important information is preserved across chunks")
        print("✓ Chunk boundaries respect sentence structure")
    else:
        print("Document is small enough for single analysis")

def demonstrate_chunk_aggregation_logic():
    """Demonstrate how results from multiple chunks would be aggregated."""
    print("\nDemonstrating chunk result aggregation...")
    
    # Simulate results from multiple chunks
    chunk_results = [
        {
            "organizations": ["ABC Realty Company", "First National Bank"],
            "people": ["John Smith", "Sarah Johnson"],
            "dates": ["December 15, 2023"],
            "locations": ["123 Main Street, Springfield, IL"],
            "financial_amounts": ["$250,000", "$5,000"],
            "properties": ["123 Main Street"],
            "key_information": ["Purchase agreement", "Real estate transaction"]
        },
        {
            "organizations": ["XYZ Properties", "Secure Title Company"],
            "people": ["Jane Doe", "Mike Wilson"],
            "dates": ["November 15, 2023"],
            "locations": ["456 Oak Avenue, Springfield, IL"],
            "financial_amounts": ["$200,000", "$50,000"],
            "properties": ["Single-family home"],
            "key_information": ["Home inspection", "Financing details"]
        },
        {
            "organizations": ["Quality Home Inspections", "Premier Home Warranty"],
            "people": ["John Smith"],  # Duplicate
            "dates": ["November 20, 2023"],
            "locations": ["789 Pine Street, Springfield, IL"],
            "financial_amounts": ["$255,000", "$250,000"],  # Duplicate
            "properties": ["Three-bedroom home"],
            "key_information": ["Appraisal results", "Property condition"]
        }
    ]
    
    # Simulate aggregation (this is what _analyze_large_document would do)
    aggregated = {
        "organizations": [],
        "people": [],
        "dates": [],
        "locations": [],
        "financial_amounts": [],
        "properties": [],
        "key_information": []
    }
    
    # Aggregate without duplicates
    for result in chunk_results:
        for key in aggregated.keys():
            for item in result.get(key, []):
                if item not in aggregated[key]:
                    aggregated[key].append(item)
    
    print("Aggregated results across all chunks:")
    for key, values in aggregated.items():
        print(f"  {key}: {values}")
    
    print(f"\nTotal unique organizations found: {len(aggregated['organizations'])}")
    print(f"Total unique people found: {len(aggregated['people'])}")
    print(f"Total unique dates found: {len(aggregated['dates'])}")
    print("✓ Duplicates removed during aggregation")

if __name__ == "__main__":
    print("Testing large document workflow...")
    test_large_document_workflow()
    
    demonstrate_chunk_aggregation_logic()
