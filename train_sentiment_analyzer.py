"""
Training script for Sentiment Analyzer
Trains Logistic Regression and Naive Bayes models for sentiment analysis
"""

from pathlib import Path
from sentiment_analyzer import SentimentAnalyzer


def generate_training_data():
    """Generate synthetic training data for sentiment analysis."""
    
    # Negative sentiment samples (label: 0)
    negative_texts = [
        "This product is terrible and completely useless.",
        "I hate this, worst experience ever.",
        "Absolutely awful, wasted my money.",
        "Horrible quality, very disappointed.",
        "This is garbage, total waste of time.",
        "Disgusting and poor quality.",
        "Bad experience, would not recommend.",
        "Terrible service, very angry.",
        "Not worth it, very unsatisfied.",
        "Worst purchase I've ever made.",
        "Dreadful, absolutely dreadful.",
        "Pathetic and disappointing.",
        "I'm furious about this.",
        "Complete disaster, very upset.",
        "Unacceptable and insulting.",
        "Shameful quality, never again.",
        "Infuriating, makes me angry.",
        "Detestable product.",
        "Loathsome and offensive.",
        "Despicable service, very sad.",
        "Miserable experience overall.",
        "Regret buying this.",
        "Atrocious, beyond bad.",
        "Sickening, truly terrible.",
        "Contemptible, lowest quality.",
    ]
    
    # Neutral sentiment samples (label: 1)
    neutral_texts = [
        "The product is okay, nothing special.",
        "It's average, does what it says.",
        "Neither good nor bad.",
        "Standard quality, as expected.",
        "Mediocre performance.",
        "Could be better, could be worse.",
        "It's fine, nothing remarkable.",
        "Acceptable but unremarkable.",
        "Middle of the road product.",
        "Decent enough for the price.",
        "Nothing to complain about.",
        "Satisfactory performance.",
        "Meets basic requirements.",
        "Fair quality overall.",
        "Adequate for everyday use.",
        "Reasonable product.",
        "Not bad, not great.",
        "Tolerable experience.",
        "Serviceable but mundane.",
        "Standard, ordinary product.",
        "Neutral about this one.",
        "Just okay, nothing special.",
        "Acceptable quality.",
        "Unremarkable but functional.",
        "Fair and balanced experience.",
    ]
    
    # Positive sentiment samples (label: 2)
    positive_texts = [
        "This is fantastic, love it!",
        "Absolutely amazing product!",
        "Best purchase ever!",
        "Excellent quality and service.",
        "I'm so happy with this.",
        "Outstanding experience!",
        "Wonderful and delightful.",
        "Perfect, couldn't ask for better.",
        "Brilliant product, highly recommended.",
        "Incredible quality and performance.",
        "This made me very happy.",
        "Superb, exceeds expectations.",
        "Fantastic beyond words.",
        "Marvelous and beautiful.",
        "Extraordinary product!",
        "Phenomenal, absolutely brilliant.",
        "Fabulous, I'm in love with it.",
        "Stunning quality and design.",
        "Magnificent, truly exceptional.",
        "Amazing, better than expected.",
        "Splendid, highly satisfied.",
        "Glorious, absolutely perfect.",
        "Superb experience throughout.",
        "Excellent in every way.",
        "Wonderful, my new favorite.",
    ]
    
    # Combine all data
    texts = negative_texts + neutral_texts + positive_texts
    labels = [0] * len(negative_texts) + [1] * len(neutral_texts) + [2] * len(positive_texts)
    
    return texts, labels


def main():
    """Main training workflow."""
    print("=" * 70)
    print("Sentiment Analysis - Training Pipeline")
    print("=" * 70)
    
    # Step 1: Generate training data
    print("\n[Step 1] Generating training data...")
    texts, labels = generate_training_data()
    
    print(f"✓ Generated {len(texts)} training samples")
    print(f"  Negative (0): {sum(1 for l in labels if l == 0)}")
    print(f"  Neutral (1): {sum(1 for l in labels if l == 1)}")
    print(f"  Positive (2): {sum(1 for l in labels if l == 2)}")
    
    # Step 2: Initialize analyzer and train models
    print("\n[Step 2] Training sentiment models...")
    
    analyzer = SentimentAnalyzer(model_type="pretrained")
    
    # Train Logistic Regression
    print("\nTraining Logistic Regression...")
    try:
        result1 = analyzer.train_custom_model(
            texts=texts,
            labels=labels,
            model_type="logistic_regression"
        )
        print(f"✓ {result1['status'].upper()}: {result1['model_type']}")
    except Exception as e:
        print(f"✗ Error training logistic_regression: {e}")
    
    # Train Naive Bayes
    print("\nTraining Naive Bayes...")
    try:
        result2 = analyzer.train_custom_model(
            texts=texts,
            labels=labels,
            model_type="naive_bayes"
        )
        print(f"✓ {result2['status'].upper()}: {result2['model_type']}")
    except Exception as e:
        print(f"✗ Error training naive_bayes: {e}")
    
    # Step 3: Test models
    print("\n[Step 3] Testing trained models...\n")
    
    test_texts = [
        "This product is amazing and I love it!",
        "It's okay, nothing special really.",
        "Terrible experience, very disappointed.",
    ]
    
    for model_name in ["logistic_regression", "naive_bayes"]:
        print(f"Testing {model_name}:")
        analyzer.switch_model(model_name)
        
        for text in test_texts:
            try:
                result = analyzer.analyze(text)
                print(f"  '{text[:40]}...'")
                print(f"    Sentiment: {result['sentiment'].upper()}, Confidence: {result['confidence']}")
            except Exception as e:
                print(f"    Error: {e}")
        print()
    
    print("=" * 70)
    print("✅ Training completed successfully!")
    print("=" * 70)
    print("\nTrained models saved:")
    print("  - logistic_regression_model.pkl")
    print("  - naive_bayes_model.pkl")
    print("\nModels ready to use via API endpoints:")
    print("  GET /api/sentiment/models - List available models")
    print("  POST /api/sentiment/switch/{model} - Switch models")
    print("  POST /api/sentiment/analyze - Analyze sentiment")


if __name__ == "__main__":
    main()
