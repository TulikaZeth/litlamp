"""
Test script for Document Classification System
"""

import sys
from pathlib import Path


def test_generate_dataset():
    """Test dataset generation."""
    print("=" * 70)
    print("Test 1: Dataset Generation")
    print("=" * 70 + "\n")
    
    try:
        from generate_dataset import generate_dataset
        
        test_file = "test_dataset_100.csv"
        if generate_dataset(test_file, num_samples=100):
            print(f"✓ Dataset generation successful")
            print(f"  File: {test_file}")
            print(f"  Size: {Path(test_file).stat().st_size / 1024:.2f} KB\n")
            return True
        else:
            print("✗ Dataset generation failed\n")
            return False
    except Exception as e:
        print(f"✗ Error: {e}\n")
        return False


def test_classifier_initialization():
    """Test classifier initialization."""
    print("=" * 70)
    print("Test 2: Classifier Initialization")
    print("=" * 70 + "\n")
    
    try:
        from document_classifier import DocumentClassifier
        
        classifier = DocumentClassifier()
        info = classifier.get_model_info()
        
        print(f"✓ Classifier initialized")
        print(f"  Status: {info.get('status', 'N/A')}")
        print(f"  Categories: {info.get('categories', 'N/A')}\n")
        return True
    except Exception as e:
        print(f"✗ Error: {e}\n")
        return False


def test_classifier_training():
    """Test classifier training."""
    print("=" * 70)
    print("Test 3: Classifier Training")
    print("=" * 70 + "\n")
    
    try:
        from document_classifier import DocumentClassifier
        from generate_dataset import generate_dataset
        
        # Generate test dataset
        print("Generating test dataset...")
        test_file = "test_dataset_500.csv"
        generate_dataset(test_file, num_samples=500)
        
        # Initialize and train classifier
        classifier = DocumentClassifier()
        texts, labels = classifier.load_dataset(test_file)
        
        if not texts:
            print("✗ Failed to load dataset\n")
            return False
        
        print("Training on test data...")
        result = classifier.train(
            texts=texts,
            labels=labels,
            test_size=0.2,
            algorithms=["logistic_regression", "svm"]
        )
        
        print(f"\n✓ Training successful")
        print(f"  Best Algorithm: {result['best_algorithm']}")
        print(f"  Accuracy: {result['accuracy']:.4f}\n")
        return True
    
    except Exception as e:
        print(f"✗ Error: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_classification():
    """Test document classification."""
    print("=" * 70)
    print("Test 4: Document Classification")
    print("=" * 70 + "\n")
    
    try:
        from document_classifier import get_document_classifier
        
        classifier = get_document_classifier()
        
        if not classifier.model:
            print("⚠ No pre-trained model available. Training first...\n")
            
            from generate_dataset import generate_dataset
            test_file = "test_dataset_1000.csv"
            generate_dataset(test_file, num_samples=1000)
            
            texts, labels = classifier.load_dataset(test_file)
            classifier.train(texts, labels, algorithms=["logistic_regression"])
        
        # Test classifications
        test_docs = [
            ("Patient shows fever and fatigue after blood test", "Medical"),
            ("The court ruled that the defendant is liable for breach", "Legal"),
            ("Markets surged following tech partnership announcement", "News")
        ]
        
        print("Testing classifications:\n")
        for text, expected in test_docs:
            result = classifier.classify(text)
            predicted = result['predicted_category']
            confidence = result['confidence']
            
            match = "✓" if predicted.lower() == expected.lower() else "⚠"
            print(f"{match} Text: {text[:50]}...")
            print(f"  Predicted: {predicted} (confidence: {confidence})")
            print(f"  Expected: {expected}")
            print(f"  Probabilities: {result['probabilities']}\n")
        
        return True
    
    except Exception as e:
        print(f"✗ Error: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_batch_classification():
    """Test batch classification."""
    print("=" * 70)
    print("Test 5: Batch Classification")
    print("=" * 70 + "\n")
    
    try:
        from document_classifier import get_document_classifier
        from generate_dataset import generate_dataset
        
        classifier = get_document_classifier()
        
        if not classifier.model:
            print("⚠ No pre-trained model available. Training first...\n")
            test_file = "test_dataset_batch.csv"
            generate_dataset(test_file, num_samples=500)
            
            texts, labels = classifier.load_dataset(test_file)
            classifier.train(texts, labels, algorithms=["logistic_regression"])
        
        # Batch test
        batch_texts = [
            "MRI scan indicates normal ranges",
            "Appellate court decision on contract terms",
            "Stock prices surge on economic news"
        ]
        
        results = classifier.batch_classify(batch_texts)
        
        print(f"✓ Batch classification successful")
        print(f"  Texts processed: {len(results)}\n")
        
        for i, result in enumerate(results, 1):
            print(f"  Result {i}: {result.get('predicted_category', 'error')}")
        
        print()
        return True
    
    except Exception as e:
        print(f"✗ Error: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("Document Classification System - Test Suite")
    print("=" * 70 + "\n")
    
    tests = [
        ("Dataset Generation", test_generate_dataset),
        ("Classifier Initialization", test_classifier_initialization),
        ("Classifier Training", test_classifier_training),
        ("Document Classification", test_classification),
        ("Batch Classification", test_batch_classification),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"✗ Test failed with exception: {e}\n")
            results.append((test_name, False))
    
    # Summary
    print("=" * 70)
    print("Test Summary")
    print("=" * 70)
    
    all_passed = True
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed.")
    print("=" * 70 + "\n")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
