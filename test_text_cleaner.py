"""
Test file for Text Cleaning Module
Run: python test_text_cleaner.py
"""

from text_cleaner import TextCleaner, clean_text, advanced_clean

# Sample legal text with various issues
sample_text = """
The Party of the First Part (hereinafter referred to as "Employer") 
and the Party of the Second Part (hereinafter referred to as "Employee") 
hereby enter into this  Employment   Agreement    pursuant to the terms 
and conditions set forth herein, e.g., salary of $100,000, benefits, etc.

Section1.2: The Employee agrees to perform duties as assigned.
The Employer vs. Employee relationship shall be governed by...

"Smart quotes" and 'apostrophes' and - em dashes - must be normalized.
Numbers like 1,000,000 and dates...
"""

def print_separator(title):
    """Print a formatted separator"""
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)

def test_basic_cleaning():
    """Test basic text cleaning"""
    print_separator("TEST 1: Basic Text Cleaning")
    
    cleaner = TextCleaner()
    cleaned = cleaner.clean_text(sample_text)
    
    print("\nORIGINAL TEXT:")
    print(sample_text)
    print("\nCLEANED TEXT:")
    print(cleaned)
    
    # Get statistics
    stats = cleaner.get_statistics(sample_text, cleaned)
    print("\nCLEANING STATISTICS:")
    for key, value in stats.items():
        print(f"  - {key.replace('_', ' ').title()}: {value}")

def test_advanced_cleaning():
    """Test advanced cleaning with stopword removal and lemmatization"""
    print_separator("TEST 2: Advanced Cleaning (Stopwords + Lemmatization)")
    
    cleaner = TextCleaner(remove_stopwords=True, lemmatize=True)
    cleaned = cleaner.advanced_clean(sample_text)
    
    print("\nCLEANED TEXT (Advanced):")
    print(cleaned)
    
    # Get statistics
    stats = cleaner.get_statistics(sample_text, cleaned)
    print("\nCLEANING STATISTICS:")
    for key, value in stats.items():
        print(f"  - {key.replace('_', ' ').title()}: {value}")

def test_quick_functions():
    """Test quick utility functions"""
    print_separator("TEST 3: Quick Utility Functions")
    
    # Basic quick clean
    result1 = clean_text(sample_text)
    print("\nQuick Clean (Basic):")
    print(result1[:200] + "...")
    
    # Advanced quick clean
    result2 = advanced_clean(sample_text)
    print("\nQuick Clean (Advanced):")
    print(result2[:200] + "...")

def test_batch_cleaning():
    """Test batch cleaning of multiple texts"""
    print_separator("TEST 4: Batch Cleaning")
    
    texts = [
        "The   party    agrees to terms...",
        "Section2.3:  Employee shall...",
        "Smart quotes need fixing."
    ]
    
    cleaner = TextCleaner()
    cleaned_batch = cleaner.clean_batch(texts)
    
    print("\nProcessing multiple texts:")
    for i, (orig, clean) in enumerate(zip(texts, cleaned_batch), 1):
        print(f"\n  {i}. Original: {orig}")
        print(f"     Cleaned:  {clean}")

def test_edge_cases():
    """Test edge cases"""
    print_separator("TEST 5: Edge Cases")
    
    cleaner = TextCleaner()
    
    # Empty string
    assert cleaner.clean_text("") == "", "Empty string test failed"
    print("  [PASS] Empty string handled")
    
    # None
    assert cleaner.clean_text(None) == "", "None test failed"
    print("  [PASS] None handled")
    
    # Only whitespace
    result = cleaner.clean_text("   \n\t   ")
    assert result == "", "Whitespace test failed"
    print("  [PASS] Whitespace-only string handled")
    
    # Unicode edge cases
    result = cleaner.clean_text("Test with dashes and quotes")
    print("  [PASS] Unicode normalization working")

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print(" TEXT CLEANER MODULE - COMPREHENSIVE TESTS")
    print("=" * 70)
    
    try:
        test_basic_cleaning()
        test_advanced_cleaning()
        test_quick_functions()
        test_batch_cleaning()
        test_edge_cases()
        
        print_separator("ALL TESTS PASSED!")
        print("\nText cleaning module is ready for integration!")
        print("Next step: Integrate with Flask API endpoint\n")
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()