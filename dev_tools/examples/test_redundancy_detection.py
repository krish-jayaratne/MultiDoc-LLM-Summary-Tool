#!/usr/bin/env python3
"""
Advanced test to show how summary aggregation handles various types of redundancy.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from src.document_summarizer.interfaces.openai_llm import OpenAILLM

def test_redundancy_detection():
    """Test different types of redundancy in summary aggregation."""
    llm = OpenAILLM(api_key="test-key")
    
    print("Testing redundancy detection...")
    
    # Test cases with different types of redundancy
    test_cases = [
        {
            "name": "Exact duplicates",
            "summaries": [
                "The purchase price is $250,000.",
                "The purchase price is $250,000.",
                "Additional terms are included."
            ]
        },
        {
            "name": "Similar sentences",
            "summaries": [
                "The purchase price is $250,000 with closing on December 15.",
                "The purchase price is $250,000 with standard contingencies.",
                "Home inspection was completed successfully."
            ]
        },
        {
            "name": "Different content",
            "summaries": [
                "John Smith is the buyer.",
                "Jane Doe is the seller.",
                "The property is on Main Street."
            ]
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['name']}")
        print("Input summaries:")
        for j, summary in enumerate(test_case['summaries']):
            print(f"  {j+1}. {summary}")
        
        # Aggregate step by step
        result = ""
        for summary in test_case['summaries']:
            result = llm._aggregate_summaries(result, summary)
        
        print(f"Aggregated result: {result}")
        
        # Count sentences in result
        result_sentences = [s.strip() for s in result.split('.') if s.strip()]
        input_sentences = sum(len([s.strip() for s in summary.split('.') if s.strip()]) 
                            for summary in test_case['summaries'])
        
        print(f"Sentences: {input_sentences} input → {len(result_sentences)} output")
        
        if len(result_sentences) < input_sentences:
            print("✓ Successfully removed redundant content")
        else:
            print("→ No redundancy detected")

def demonstrate_current_behavior():
    """Show exactly what happens with the real estate example."""
    llm = OpenAILLM(api_key="test-key")
    
    print("\n" + "="*60)
    print("Current behavior with real estate example:")
    
    summaries = [
        "This is a real estate purchase agreement between John Smith and Jane Doe for a property at 123 Main Street. The purchase price is $250,000 with a closing date of December 15, 2023.",
        "The buyer John Smith will obtain financing through First National Bank for $200,000. The purchase price is $250,000 with standard contingencies including home inspection.",
        "Professional home inspection revealed minor issues totaling $275 in estimated repairs. The property appraisal came in at $255,000, exceeding the purchase price by $5,000."
    ]
    
    # Test similarity detection
    sent1 = "the purchase price is $250000 with a closing date of december 15 2023"
    sent2 = "the purchase price is $250000 with standard contingencies including home inspection"
    
    similarity = llm._sentences_similar(sent1, sent2)
    print(f"\nSimilarity between price sentences: {similarity:.2f}")
    
    words1 = set(sent1.split())
    words2 = set(sent2.split())
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    print(f"Common words: {intersection}")
    print(f"Total unique words: {len(union)}")
    print(f"Jaccard similarity: {len(intersection)/len(union):.2f}")
    
    # Show final aggregation
    result = ""
    for i, summary in enumerate(summaries):
        result = llm._aggregate_summaries(result, summary)
        print(f"\nAfter adding summary {i+1}:")
        print(f"Length: {len(result)} chars")
        sentences = [s.strip() for s in result.split('.') if s.strip()]
        print(f"Sentences: {len(sentences)}")

if __name__ == "__main__":
    test_redundancy_detection()
    demonstrate_current_behavior()
