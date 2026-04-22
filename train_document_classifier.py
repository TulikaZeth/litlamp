"""
Training script for Document Classifier

"""

import sys
from pathlib import Path
from generate_dataset import generate_dataset
from document_classifier import DocumentClassifier


def main():
    """Main training workflow."""
    print("=" * 70)
    print("Document Classification System - Training Pipeline")
    print("=" * 70)
    
    # Step 1: Generate dataset
    print("\n[Step 1] Generating synthetic dataset...")
    dataset_file = "mock_dataset_5000.csv"
    
    if not Path(dataset_file).exists():
        print(f"Generating {dataset_file}...")
        if not generate_dataset(dataset_file, num_samples=5000):
            print("❌ Failed to generate dataset")
            return False
    else:
        print(f"✓ Dataset already exists: {dataset_file}")
    
    # Step 2: Load dataset
    print("\n[Step 2] Loading dataset...")
    classifier = DocumentClassifier()
    texts, labels = classifier.load_dataset(dataset_file)
    
    if not texts:
        print("❌ Failed to load dataset")
        return False
    
    # Display dataset info
    from collections import Counter
    label_counts = Counter(labels)
    print(f"\nDataset composition:")
    for label, count in sorted(label_counts.items()):
        percentage = (count / len(labels)) * 100
        print(f"  {label}: {count} samples ({percentage:.1f}%)")
    
    # Step 3: Train models
    print("\n[Step 3] Training ML models...")
    print("Testing algorithms: Logistic Regression,\n")
    
    try:
        result = classifier.train(
            texts=texts,
            labels=labels,
            test_size=0.2,
            algorithms=[
                "logistic_regression",
                "random_forest",
                "svm",
                "naive_bayes",
                "gradient_boosting"
            ]
        )
        
        print("\n" + "=" * 70)
        print("Training Results:")
        print("=" * 70)
        print(f"Best Algorithm: {result['best_algorithm']}")
        print(f"Accuracy: {result['accuracy']:.4f}")
        print(f"Test Samples: {result['test_size']}")
        
        # Step 4: Test predictions
        print("\n[Step 4] Testing predictions...\n")
        
        test_docs = [
            "Patient diagnosed with hypertension after blood pressure test showed elevated levels.",
            "The court ruled that the defendant is liable for breach of contract.",
            "Markets surged following announcement of new tech partnership between companies."
        ]
        
        for doc in test_docs:
            prediction = classifier.classify(doc)
            print(f"Text: {doc[:60]}...")
            print(f"Category: {prediction['predicted_category']}")
            print(f"Confidence: {prediction['confidence']}")
            print(f"Probabilities: {prediction['probabilities']}\n")
        
        print("=" * 70)
        print("✅ Training pipeline completed successfully!")
        print("=" * 70)
        print("\nModel saved and ready to use via API endpoints:")
        print("  POST /api/classify - Classify a single document")
        print("  POST /api/classify/batch - Classify multiple documents")
        print("  GET /api/classify/info - Get model information")
        
        return True
    
    except Exception as e:
        print(f"\n❌ Error during training: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
