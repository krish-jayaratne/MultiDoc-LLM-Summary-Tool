#!/usr/bin/env python3
"""
Practical examples of using pdb debugger in different ways.
"""

import sys
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from document_summarizer.base.document_reader import TextDocumentReader


def example_with_manual_breakpoint():
    """Example 1: Manual breakpoint in code."""
    print("=== EXAMPLE 1: Manual Breakpoint ===")
    
    reader = TextDocumentReader()
    short_content = "Short document content."
    
    print("About to call _generate_description...")
    
    # METHOD 1: Classic pdb breakpoint
    import pdb; pdb.set_trace()
    
    # METHOD 2: Python 3.7+ breakpoint (uncomment to use instead)
    # breakpoint()
    
    description = reader._generate_description(short_content)
    print(f"Result: {description}")


def example_with_exception_handling():
    """Example 2: Using pdb for post-mortem debugging."""
    print("=== EXAMPLE 2: Post-mortem Debugging ===")
    
    try:
        # This will cause an error
        reader = TextDocumentReader()
        result = reader._generate_description(None)  # This will fail
    except Exception as e:
        print(f"Exception occurred: {e}")
        
        # METHOD 3: Post-mortem debugging
        import pdb
        import traceback
        import sys
        
        print("Entering post-mortem debugger...")
        extype, value, tb = sys.exc_info()
        traceback.print_exc()
        pdb.post_mortem(tb)


def example_with_conditional_breakpoint():
    """Example 3: Conditional breakpoint."""
    print("=== EXAMPLE 3: Conditional Breakpoint ===")
    
    reader = TextDocumentReader()
    
    test_cases = [
        "Short text.",
        "Medium length text that might be interesting.",
        "Very long text that should definitely trigger our breakpoint because it's longer than expected and we want to debug this specific case."
    ]
    
    for i, content in enumerate(test_cases):
        print(f"Processing case {i}: {content[:30]}...")
        
        # METHOD 4: Conditional breakpoint
        if len(content) > 50:
            import pdb; pdb.set_trace()
        
        description = reader._generate_description(content)
        print(f"Result {i}: {description}")


def example_debugger_in_test():
    """Example 4: How to add debugging to a test function."""
    print("=== EXAMPLE 4: Debugging in Test Function ===")
    
    # This simulates what you'd do in an actual test
    reader = TextDocumentReader()
    short_content = "Short document content."
    
    # Add debugging right before the assertion that might fail
    print("Before calling the function...")
    
    # METHOD 5: Strategic breakpoint before assertion
    import pdb; pdb.set_trace()
    
    description = reader._generate_description(short_content)
    expected = short_content
    
    # Now you can examine both values in the debugger
    assert description == expected, f"Expected '{expected}', got '{description}'"
    print("Test passed!")


if __name__ == "__main__":
    print("PDB Debugging Examples")
    print("=" * 50)
    print("Choose an example to run:")
    print("1. Manual breakpoint")
    print("2. Post-mortem debugging (will cause an error)")
    print("3. Conditional breakpoint")
    print("4. Debugging in test function")
    
    choice = input("Enter choice (1-4): ").strip()
    
    if choice == "1":
        example_with_manual_breakpoint()
    elif choice == "2":
        example_with_exception_handling()
    elif choice == "3":
        example_with_conditional_breakpoint()
    elif choice == "4":
        example_debugger_in_test()
    else:
        print("Invalid choice. Running example 1...")
        example_with_manual_breakpoint()
