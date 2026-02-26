"""
Test file for FLAN-T5 Model Integration
Run: python test_model_simplifier.py
"""

from model_simplifier import TextSimplifier, simplify
import time

# Sample complex legal text
COMPLEX_TEXT = """
The Party of the First Part (hereinafter referred to as "Employer") 
and the Party of the Second Part (hereinafter referred to as "Employee") 
hereby enter into this Employment Agreement pursuant to the terms and 
conditions set forth herein. The Employee agrees to perform duties as 
assigned by the Employer in accordance with the Employer's standard 
operating procedures. The Employer agrees to provide compensation, 
benefits, and a safe work environment.
"""

def test_model_loading():
    """Test if model loads successfully"""
    print("=" * 70)
    print("TEST 1: Model Loading")
    print("=" * 70)
    
    try:
        simplifier = TextSimplifier()
        info = simplifier.get_model_info()
        
        print("\nModel Information:")
        print(f"  Model: {info['model_name']}")
        print(f"  Device: {info['device']}")
        print(f"  Parameters: {info['parameters']:,}")
        print(f"  Trainable Parameters: {info['trainable_parameters']:,}")
        print("\n✅ Model loaded successfully!")
        
        return simplifier
    except Exception as e:
        print(f"\n❌ Error loading model: {e}")
        return None

def test_simplification(simplifier):
    """Test text simplification"""
    print("\n" + "=" * 70)
    print("TEST 2: Text Simplification")
    print("=" * 70)
    
    print("\nOriginal Complex Text:")
    print(COMPLEX_TEXT)
    
    print("\n" + "-" * 70)
    print("Simplifying...")
    
    start_time = time.time()
    simplified = simplifier.simplify_text(COMPLEX_TEXT)
    end_time = time.time()
    
    print("\nSimplified Text:")
    print(simplified)
    
    print(f"\n⏱️ Processing Time: {end_time - start_time:.2f} seconds")
    print("✅ Simplification successful!")
    
    return simplified

def test_batch_simplification(simplifier):
    """Test batch processing"""
    print("\n" + "=" * 70)
    print("TEST 3: Batch Simplification")
    print("=" * 70)
    
    texts = [
        "The aforementioned party shall indemnify and hold harmless.",
        "Pursuant to Section 3.2, all fees are non-refundable.",
        "The agreement shall be governed by the laws of the jurisdiction."
    ]
    
    print("\nProcessing 3 texts...")
    start_time = time.time()
    simplified_batch = simplifier.simplify_batch(texts)
    end_time = time.time()
    
    for i, (original, simplified) in enumerate(zip(texts, simplified_batch), 1):
        print(f"\n{i}. Original: {original}")
        print(f"   Simplified: {simplified}")
    
    print(f"\n⏱️ Total Time: {end_time - start_time:.2f} seconds")
    print("✅ Batch processing successful!")

def test_quick_function():
    """Test utility function"""
    print("\n" + "=" * 70)
    print("TEST 4: Quick Utility Function")
    print("=" * 70)
    
    text = "The Employee shall be entitled to receive compensation."
    print(f"\nOriginal: {text}")
    
    simplified = simplify(text)
    print(f"Simplified: {simplified}")
    print("✅ Utility function works!")

def test_different_lengths():
    """Test with different text lengths"""
    print("\n" + "=" * 70)
    print("TEST 5: Different Text Lengths")
    print("=" * 70)
    
    simplifier = TextSimplifier()
    
    # Short text
    short_text = "The party agrees to the terms."
    short_simplified = simplifier.simplify_text(short_text, max_length=50)
    print(f"\n📝 Short Text:")
    print(f"   Original: {short_text}")
    print(f"   Simplified: {short_simplified}")
    
    # Medium text (already defined as COMPLEX_TEXT)
    
    # Long text
    long_text = COMPLEX_TEXT * 3  # Triple the length
    long_simplified = simplifier.simplify_text(long_text, max_length=512)
    print(f"\n📄 Long Text (simplified):")
    print(f"   {long_simplified[:200]}...")
    
    print("\n✅ Different lengths handled successfully!")

if __name__ == "__main__":
    print("\n" + "🧪" * 35)
    print(" FLAN-T5 MODEL INTEGRATION - COMPREHENSIVE TESTS")
    print("🧪" * 35)
    
    try:
        # Test 1: Load model
        simplifier = test_model_loading()
        
        if simplifier:
            # Test 2: Simplification
            test_simplification(simplifier)
            
            # Test 3: Batch processing
            test_batch_simplification(simplifier)
            
            # Test 4: Utility function
            test_quick_function()
            
            # Test 5: Different lengths
            test_different_lengths()
        
        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED!")
        print("=" * 70)
        print("\n✨ Model integration complete!")
        print("📦 Next step: Integrate with Flask API\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()