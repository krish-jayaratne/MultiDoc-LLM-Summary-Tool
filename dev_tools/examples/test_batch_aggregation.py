#!/usr/bin/env python3
"""
Test the improved batch summary aggregation approach.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from src.document_summarizer.interfaces.openai_llm import OpenAILLM

def demonstrate_batch_vs_progressive():
    """Show the difference between batch and progressive aggregation."""
    llm = OpenAILLM(api_key="test-key-for-demo")
    
    # Sample chunk summaries from a large document
    chunk_summaries = [
        "This is a real estate purchase agreement between John Smith (buyer) and Jane Doe (seller) for a property at 123 Main Street, Springfield. The purchase price is $250,000 with a closing date of December 15, 2023.",
        
        "The buyer John Smith will obtain financing through First National Bank for $200,000 (80% LTV). The purchase price is $250,000 with standard contingencies including home inspection and appraisal.",
        
        "Professional home inspection by Quality Home Inspections revealed minor issues totaling $275 in estimated repairs. The property appraisal completed by Certified Property Appraisals came in at $255,000, exceeding the purchase price.",
        
        "The property is a three-bedroom, two-bathroom home built in 1995 with recent updates including new HVAC (2022) and roof replacement (2021). All appliances and fixtures are included in the sale.",
        
        "Legal representation includes Legal Partners LLC for the buyer and Thompson & Associates for the seller. All necessary disclosures have been provided including lead paint and property condition reports."
    ]
    
    print("COMPARISON: Batch vs Progressive Summary Aggregation")
    print("=" * 65)
    
    print("\n📊 EFFICIENCY ANALYSIS:")
    print("-" * 30)
    
    num_chunks = len(chunk_summaries)
    
    print(f"Document chunks: {num_chunks}")
    print(f"Summary aggregation approaches:")
    
    print(f"\n❌ OLD (Progressive) Approach:")
    print(f"   • LLM calls: {num_chunks - 1} calls")
    print(f"   • Process: Chunk1 → LLM → Chunk2 → LLM → ... → Final")
    print(f"   • Timeline: After each chunk analysis")
    
    for i in range(2, num_chunks + 1):
        print(f"   • Call {i-1}: Combine summaries 1-{i-1} + summary {i}")
    
    print(f"\n✅ NEW (Batch) Approach:")
    print(f"   • LLM calls: 1 call")
    print(f"   • Process: All chunks → Collect summaries → Single LLM call")
    print(f"   • Timeline: After all chunks analyzed")
    print(f"   • Single call: Combine all {num_chunks} summaries at once")
    
    print(f"\n💰 COST COMPARISON:")
    print("-" * 20)
    
    # Estimated token usage
    avg_summary_length = 150  # characters
    tokens_per_summary = avg_summary_length // 4  # rough estimate
    
    old_total_tokens = 0
    for i in range(2, num_chunks + 1):
        # Each progressive call processes i summaries
        input_tokens = i * tokens_per_summary
        output_tokens = tokens_per_summary  # estimated output
        old_total_tokens += input_tokens + output_tokens
    
    # New approach: single call with all summaries
    new_input_tokens = num_chunks * tokens_per_summary
    new_output_tokens = tokens_per_summary  # single output
    new_total_tokens = new_input_tokens + new_output_tokens
    
    print(f"Progressive approach: ~{old_total_tokens} tokens")
    print(f"Batch approach: ~{new_total_tokens} tokens")
    print(f"Token savings: ~{old_total_tokens - new_total_tokens} tokens ({((old_total_tokens - new_total_tokens) / old_total_tokens * 100):.1f}% reduction)")
    
    print(f"\n🚀 PERFORMANCE BENEFITS:")
    print("-" * 25)
    benefits = [
        "🔥 Fewer API calls → Faster processing",
        "💸 Lower token usage → Reduced costs", 
        "🧠 Better context → LLM sees all summaries together",
        "📊 Simpler logic → Easier to debug and maintain",
        "⚡ No progressive state → More reliable processing"
    ]
    
    for benefit in benefits:
        print(f"   {benefit}")
    
    print(f"\n🔍 EXAMPLE LLM INPUT:")
    print("-" * 20)
    print("System prompt: You are a document summarization expert...")
    print("User prompt:")
    print(f"   Please combine these {len(chunk_summaries)} partial summaries for document 'sample.pdf':")
    for i, summary in enumerate(chunk_summaries, 1):
        print(f"   Summary {i}: {summary[:60]}...")
    print("   Final combined summary:")

def test_batch_aggregation_method():
    """Test the new batch aggregation method."""
    llm = OpenAILLM(api_key="test-key-for-demo")
    
    print(f"\n{'=' * 65}")
    print("TESTING BATCH AGGREGATION METHOD")
    print("=" * 65)
    
    test_summaries = [
        "Document is a purchase agreement for $500,000 commercial property.",
        "Buyer is Tech Innovations LLC, seller is Downtown Properties Inc.",
        "Property located at 456 Business Avenue with 10,000 sq ft office space.",
        "Closing scheduled for March 15, 2024, with First Commercial Bank financing."
    ]
    
    print(f"\nInput summaries ({len(test_summaries)} chunks):")
    for i, summary in enumerate(test_summaries, 1):
        print(f"  {i}. {summary}")
    
    print(f"\n🤖 LLM Aggregation Process:")
    print(f"   • Method: _aggregate_all_summaries_with_llm()")
    print(f"   • Input: List of {len(test_summaries)} summaries")
    print(f"   • Processing: Single LLM call")
    print(f"   • Output: One coherent summary")
    
    # Show what the prompt would look like
    prompt = llm.create_summary_aggregation_prompt(test_summaries, "commercial_property.pdf")
    print(f"\n📝 Generated Prompt Preview:")
    print(f"   {prompt[:150]}...")
    
    print(f"\n✅ Expected Benefits:")
    print(f"   • Removes duplicate '$500,000' mentions")
    print(f"   • Combines party information naturally")
    print(f"   • Creates single flowing narrative")
    print(f"   • Maintains all important details")

if __name__ == "__main__":
    demonstrate_batch_vs_progressive()
    test_batch_aggregation_method()
