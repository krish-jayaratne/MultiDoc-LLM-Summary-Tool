#!/usr/bin/env python3
"""
Test the new LLM-based summary aggregation vs the old algorithmic approach.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from src.document_summarizer.interfaces.openai_llm import OpenAILLM

def test_llm_summary_aggregation():
    """Test the new LLM-based summary aggregation."""
    llm = OpenAILLM(api_key="test-key-for-demo")
    
    # Sample chunk summaries with redundancy and different focuses
    summaries = [
        "This is a real estate purchase agreement between John Smith (buyer) and Jane Doe (seller) for a property at 123 Main Street, Springfield. The purchase price is $250,000 with a closing date of December 15, 2023.",
        
        "The buyer John Smith will obtain financing through First National Bank for $200,000 (80% LTV). The purchase price is $250,000 with standard contingencies including home inspection and appraisal.",
        
        "Professional home inspection by Quality Home Inspections revealed minor issues totaling $275 in estimated repairs. The property appraisal completed by Certified Property Appraisals came in at $255,000, exceeding the purchase price.",
        
        "The property is a three-bedroom, two-bathroom home built in 1995 with recent updates including new HVAC (2022) and roof replacement (2021). All appliances and fixtures are included in the sale."
    ]
    
    print("Testing LLM-based summary aggregation...")
    print("="*60)
    
    print("\nOriginal chunk summaries:")
    for i, summary in enumerate(summaries, 1):
        print(f"\n{i}. {summary}")
    
    print(f"\n{'='*60}")
    print("LLM AGGREGATION PROCESS:")
    print("="*60)
    
    # Simulate the step-by-step aggregation process
    aggregated = ""
    
    for i, summary in enumerate(summaries):
        print(f"\nStep {i+1}: Adding summary {i+1}")
        print(f"Current length: {len(aggregated)} chars")
        print(f"Adding: {summary[:100]}...")
        
        # This would normally call the LLM
        print(f"🤖 Would call LLM to combine summaries...")
        
        # For demo, show what the process would be
        if not aggregated:
            aggregated = summary
        else:
            # Show what we'd send to LLM
            print(f"\nLLM Input:")
            print(f"  System: {llm.SUMMARY_AGGREGATION_SYSTEM_PROMPT[:100]}...")
            print(f"  User prompt: Combine {len([aggregated, summary])} summaries for better result")
        
        print(f"Result length after step {i+1}: {len(aggregated)} chars")
    
    print(f"\n{'='*60}")
    print("BENEFITS OF LLM AGGREGATION:")
    print("="*60)
    
    benefits = [
        "🎯 Intelligent deduplication - LLM understands that '$250,000' and 'purchase price $250,000' refer to the same thing",
        "📝 Natural language flow - Creates coherent, readable summaries instead of concatenated fragments", 
        "🧠 Context awareness - Understands relationships between different pieces of information",
        "⚖️  Smart prioritization - Focuses on most important information without manual keyword scoring",
        "🔧 Handles edge cases - Better at dealing with complex sentence structures and variations",
        "📊 Consistent quality - Produces professional-quality summaries regardless of input complexity"
    ]
    
    for benefit in benefits:
        print(f"\n{benefit}")
    
    print(f"\n{'='*60}")
    print("COMPARISON:")
    print("="*60)
    
    print(f"""
📈 OLD ALGORITHMIC APPROACH:
   • Sentence-level deduplication with exact/similarity matching
   • Keyword-based importance scoring with manual weights
   • Character-based truncation (often cuts mid-sentence)
   • Rule-based logic that misses context

🤖 NEW LLM APPROACH:
   • Semantic understanding of content relationships
   • Natural language generation for flowing summaries
   • Intelligent content selection based on overall meaning
   • Fallback to simple concatenation if LLM fails

💰 COST CONSIDERATION:
   • Each aggregation call uses ~100-300 tokens
   • For large documents with 5 chunks: ~5 aggregation calls
   • Small additional cost for significantly better quality
    """)

def demonstrate_aggregation_scenarios():
    """Show different scenarios where LLM aggregation excels."""
    
    print(f"\n{'='*60}")
    print("AGGREGATION SCENARIOS:")
    print("="*60)
    
    scenarios = [
        {
            "name": "Redundant Information",
            "summaries": [
                "The contract price is $500,000 for the downtown office building.",
                "Purchase agreement specifies $500,000 as the total cost for the commercial property.",
                "Final terms include the $500,000 purchase amount for the office space."
            ],
            "challenge": "Three ways of saying the same thing - LLM can consolidate into one clear statement."
        },
        {
            "name": "Complementary Details", 
            "summaries": [
                "The sale involves John Smith as buyer and ABC Corp as seller.",
                "The property is located at 456 Business Ave, includes parking for 50 cars.",
                "Closing is scheduled for March 15, 2024, with First Bank providing financing."
            ],
            "challenge": "Different aspects that should flow together - LLM creates narrative structure."
        },
        {
            "name": "Technical vs. Business Language",
            "summaries": [
                "Structural engineer's report indicates foundation meets code requirements per section 12.3.4.",
                "The building inspection showed the foundation is solid and complies with all safety standards.",
                "Engineering analysis confirms structural integrity of the foundation system."
            ],
            "challenge": "Same concept expressed differently - LLM normalizes to consistent language."
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. {scenario['name']}:")
        print(f"   Challenge: {scenario['challenge']}")
        print(f"   Input summaries:")
        for j, summary in enumerate(scenario['summaries'], 1):
            print(f"     {j}. {summary}")
        print(f"   🤖 LLM would create one coherent summary combining all information")

if __name__ == "__main__":
    test_llm_summary_aggregation()
    demonstrate_aggregation_scenarios()
