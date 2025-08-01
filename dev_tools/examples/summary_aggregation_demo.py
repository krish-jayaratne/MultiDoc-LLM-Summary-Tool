#!/usr/bin/env python3
"""
Demonstration of different summary aggregation strategies for chunked documents.
"""

def simple_concatenation(chunk_summaries):
    """Current implementation: Simple concatenation with length limit."""
    combined = ' '.join(chunk_summaries)
    if len(combined) > 500:
        combined = combined[:500] + '...'
    return combined

def intelligent_deduplication(chunk_summaries):
    """Remove duplicate sentences and redundant information."""
    sentences = []
    seen_sentences = set()
    
    for summary in chunk_summaries:
        # Split into sentences
        summary_sentences = [s.strip() for s in summary.split('.') if s.strip()]
        
        for sentence in summary_sentences:
            # Normalize for comparison (lowercase, remove extra spaces)
            normalized = ' '.join(sentence.lower().split())
            
            # Check for exact duplicates
            if normalized not in seen_sentences:
                sentences.append(sentence)
                seen_sentences.add(normalized)
    
    # Join back together
    result = '. '.join(sentences)
    if not result.endswith('.'):
        result += '.'
    
    return result

def key_point_extraction(chunk_summaries):
    """Extract key points and combine into structured summary."""
    key_points = []
    financial_info = []
    party_info = []
    timeline_info = []
    
    for summary in chunk_summaries:
        sentences = [s.strip() for s in summary.split('.') if s.strip()]
        
        for sentence in sentences:
            lower_sentence = sentence.lower()
            
            # Categorize sentence content
            if any(term in lower_sentence for term in ['$', 'price', 'amount', 'cost', 'payment']):
                if sentence not in financial_info:
                    financial_info.append(sentence)
            elif any(term in lower_sentence for term in ['buyer', 'seller', 'agent', 'attorney']):
                if sentence not in party_info:
                    party_info.append(sentence)
            elif any(term in lower_sentence for term in ['date', 'closing', 'inspection', 'deadline']):
                if sentence not in timeline_info:
                    timeline_info.append(sentence)
            else:
                if sentence not in key_points:
                    key_points.append(sentence)
    
    # Build structured summary
    structured_parts = []
    
    if key_points:
        structured_parts.append(' '.join(key_points[:2]))  # Top 2 key points
    
    if party_info:
        structured_parts.append(' '.join(party_info[:1]))  # Top party info
    
    if financial_info:
        structured_parts.append(' '.join(financial_info[:1]))  # Top financial info
    
    if timeline_info:
        structured_parts.append(' '.join(timeline_info[:1]))  # Top timeline info
    
    return '. '.join(structured_parts) + '.'

def weighted_importance_summary(chunk_summaries):
    """Weight sentences by importance indicators and combine top ones."""
    sentence_scores = {}
    
    # Importance keywords and their weights
    importance_keywords = {
        'agreement': 3, 'contract': 3, 'purchase': 3, 'sale': 3,
        'buyer': 2, 'seller': 2, 'property': 2, 'closing': 2,
        'price': 2, 'amount': 2, 'financing': 2, 'mortgage': 2,
        'inspection': 1, 'appraisal': 1, 'title': 1, 'contingency': 1
    }
    
    for summary in chunk_summaries:
        sentences = [s.strip() for s in summary.split('.') if s.strip()]
        
        for sentence in sentences:
            if sentence in sentence_scores:
                continue
                
            # Calculate importance score
            score = 0
            words = sentence.lower().split()
            
            for word in words:
                if word in importance_keywords:
                    score += importance_keywords[word]
            
            # Bonus for sentence length (more comprehensive)
            if len(words) > 10:
                score += 1
            
            sentence_scores[sentence] = score
    
    # Sort by score and take top sentences
    sorted_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)
    top_sentences = [sentence for sentence, score in sorted_sentences[:4]]  # Top 4 sentences
    
    return '. '.join(top_sentences) + '.'

def test_aggregation_methods():
    """Test different aggregation methods with sample chunk summaries."""
    
    # Sample chunk summaries from a real estate document
    chunk_summaries = [
        "This is a real estate purchase agreement between John Smith and Jane Doe for a property at 123 Main Street. The purchase price is $250,000 with a closing date of December 15, 2023.",
        "The buyer John Smith will obtain financing through First National Bank for $200,000. The property includes a three-bedroom home with recent renovations including new HVAC and roof.",
        "The purchase price is $250,000 with standard contingencies including home inspection and financing approval. ABC Realty Company is representing the buyer in this transaction.",
        "Professional home inspection revealed minor issues totaling $275 in estimated repairs. The property appraisal came in at $255,000, exceeding the purchase price by $5,000."
    ]
    
    print("Original chunk summaries:")
    for i, summary in enumerate(chunk_summaries, 1):
        print(f"  Chunk {i}: {summary}")
    
    print(f"\n{'='*60}")
    
    # Test each method
    methods = [
        ("Simple Concatenation (Current)", simple_concatenation),
        ("Intelligent Deduplication", intelligent_deduplication),
        ("Key Point Extraction", key_point_extraction),
        ("Weighted Importance", weighted_importance_summary)
    ]
    
    for method_name, method_func in methods:
        result = method_func(chunk_summaries)
        print(f"\n{method_name}:")
        print(f"  Result: {result}")
        print(f"  Length: {len(result)} characters")

if __name__ == "__main__":
    test_aggregation_methods()
