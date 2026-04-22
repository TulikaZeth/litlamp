"""
Sentiment Analysis Module
Supports both pre-trained transformer models and custom trained models (Logistic Regression, Naive Bayes)
"""

import os
import joblib
import numpy as np
from typing import Dict, List, Tuple, Optional
from pathlib import Path

# Pre-trained model
from transformers import pipeline

# Custom ML models
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline


class SentimentAnalyzer:
    """Sentiment analysis with pre-trained and custom models."""
    
    CUSTOM_MODELS = ["logistic_regression", "naive_bayes"]
    
    def __init__(self, model_type: str = "pretrained", model_dir: str = "./models"):
        """
        Initialize sentiment analyzer.
        
        Args:
            model_type: "pretrained", "logistic_regression", or "naive_bayes"
            model_dir: Directory to store trained models
        """
        self.model_type = model_type
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True)
        
        self.pretrained_model = None
        self.custom_model = None
        self.current_model_name = model_type
        self.available_custom_models = {}
        
        if model_type == "pretrained":
            self._load_pretrained_model()
        else:
            self._load_all_custom_models()
            self._load_custom_model(model_type)
    
    def _load_pretrained_model(self):
        """Load pre-trained sentiment model from HuggingFace."""
        try:
            print("Loading pre-trained sentiment model...")
            self.pretrained_model = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english"
            )
            print("✓ Pre-trained model loaded successfully")
        except Exception as e:
            print(f"⚠️  Warning: Failed to load pre-trained sentiment model: {str(e)}")
            print("Sentiment analysis will use fallback simple model")
            # Store error state - we'll handle this in analyze()
            self.pretrained_model = None
    
    def _load_all_custom_models(self):
        """Load all available trained custom models."""
        for model_name in self.CUSTOM_MODELS:
            model_path = self.model_dir / f"{model_name}_model.pkl"
            if model_path.exists():
                try:
                    model = joblib.load(model_path)
                    self.available_custom_models[model_name] = model_path
                    print(f"✓ Found trained model: {model_name}")
                except Exception as e:
                    print(f"⚠ Could not load {model_name} model: {e}")
    
    def _load_custom_model(self, model_type: str):
        """Load custom trained model if available."""
        model_path = self.model_dir / f"{model_type}_model.pkl"
        
        if model_path.exists():
            try:
                print(f"Loading {model_type} model from disk...")
                self.custom_model = joblib.load(model_path)
                print(f"✓ {model_type} model loaded successfully")
            except Exception as e:
                print(f"⚠ Could not load {model_type} model: {e}")
        else:
            print(f"⚠ No trained {model_type} model found. Train first using train_sentiment_analyzer.py")
    
    def analyze_pretrained(self, text: str) -> Dict[str, any]:
        """
        Analyze sentiment using pre-trained model.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dict with sentiment label and score
        """
        if not self.pretrained_model:
            self._load_pretrained_model()
        
        # Fallback if model still not loaded
        if not self.pretrained_model:
            return self._fallback_sentiment_analysis(text)
        
        try:
            result = self.pretrained_model(text[:512])[0]  # Limit to 512 chars
            return {
                "sentiment": result["label"].lower(),
                "score": round(result["score"], 4),
                "model": "distilbert-pretrained"
            }
        except Exception as e:
            print(f"⚠️  Error in pretrained analysis: {str(e)}, using fallback")
            return self._fallback_sentiment_analysis(text)
    
    def _fallback_sentiment_analysis(self, text: str) -> Dict[str, any]:
        """Fallback sentiment analysis using simple keyword matching."""
        text_lower = text.lower()
        
        positive_words = {"good", "great", "excellent", "amazing", "wonderful", "love", "perfect", "best", "happy", "awesome"}
        negative_words = {"bad", "terrible", "awful", "hate", "worst", "poor", "horrible", "disgusting", "sad", "angry"}
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = "positive"
            confidence = min(0.99, 0.5 + (positive_count * 0.1))
        elif negative_count > positive_count:
            sentiment = "negative"
            confidence = min(0.99, 0.5 + (negative_count * 0.1))
        else:
            sentiment = "neutral"
            confidence = 0.5
        
        return {
            "sentiment": sentiment,
            "confidence": round(confidence, 4),
            "scores": {
                "positive": round(0.5 + (positive_count * 0.1), 4),
                "negative": round(0.5 + (negative_count * 0.1), 4),
                "neutral": 0.5
            },
            "model": "fallback-keyword"
        }
    
    def analyze_custom(self, text: str) -> Dict[str, any]:
        """
        Analyze sentiment using custom trained model.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dict with sentiment label and probability
        """
        if not self.custom_model:
            raise RuntimeError(f"Custom {self.model_type} model not trained. Call train_sentiment_analyzer.py first.")
        
        # Predict (pipeline includes vectorizer)
        prediction = self.custom_model.predict([text])[0]
        probabilities = self.custom_model.predict_proba([text])[0]
        
        # Map to label
        sentiment_map = {0: "negative", 1: "neutral", 2: "positive"}
        label = sentiment_map.get(prediction, "unknown")
        
        # Get confidence (probability of predicted class)
        confidence = round(max(probabilities), 4)
        
        return {
            "sentiment": label,
            "confidence": confidence,
            "scores": {
                "negative": round(probabilities[0], 4),
                "neutral": round(probabilities[1], 4),
                "positive": round(probabilities[2], 4)
            },
            "model": self.model_type
        }
    
    def switch_model(self, model_name: str) -> bool:
        """
        Switch to a different custom model.
        
        Args:
            model_name: Model name (logistic_regression or naive_bayes)
            
        Returns:
            True if switch successful, False otherwise
        """
        if model_name not in self.available_custom_models:
            print(f"❌ Model '{model_name}' not available. Available: {list(self.available_custom_models.keys())}")
            return False
        
        try:
            model_path = self.available_custom_models[model_name]
            self.custom_model = joblib.load(model_path)
            self.model_type = model_name
            self.current_model_name = model_name
            print(f"✓ Switched to {model_name} model")
            return True
        except Exception as e:
            print(f"❌ Error switching to {model_name}: {e}")
            return False
    
    def get_available_models(self) -> Dict:
        """Get list of available trained models."""
        return {
            "pretrained_available": self.pretrained_model is not None,
            "current_model": self.current_model_name,
            "custom_models": list(self.available_custom_models.keys()),
            "total_custom_models": len(self.available_custom_models)
        }
    
    def analyze(self, text: str) -> Dict[str, any]:
        """Analyze sentiment using configured model (case-insensitive)."""
        # Normalize text to lowercase for consistent sentiment analysis
        normalized_text = text.lower().strip()
        if self.model_type == "pretrained":
            return self.analyze_pretrained(normalized_text)
        else:
            return self.analyze_custom(normalized_text)
    
    def train_custom_model(
        self,
        texts: List[str],
        labels: List[int],
        model_type: str = "logistic_regression"
    ) -> Dict[str, any]:
        """
        Train custom sentiment model.
        
        Args:
            texts: List of training texts
            labels: List of labels (0=negative, 1=neutral, 2=positive)
            model_type: "logistic_regression" or "naive_bayes"
            
        Returns:
            Training results dict
        """
        print(f"Training {model_type} model on {len(texts)} samples...")
        
        # Create pipeline
        if model_type == "logistic_regression":
            model = Pipeline([
                ("tfidf", TfidfVectorizer(max_features=5000, ngram_range=(1, 2))),
                ("classifier", LogisticRegression(max_iter=1000, random_state=42))
            ])
        elif model_type == "naive_bayes":
            model = Pipeline([
                ("tfidf", TfidfVectorizer(max_features=5000, ngram_range=(1, 2))),
                ("classifier", MultinomialNB())
            ])
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        # Train
        model.fit(texts, labels)
        
        # Save complete pipeline
        model_path = self.model_dir / f"{model_type}_model.pkl"
        joblib.dump(model, model_path)
        print(f"✓ Model saved to {model_path}")
        
        # Track available model
        self.available_custom_models[model_type] = model_path
        
        # Update current model if first one or explicitly requested
        if not self.custom_model:
            self.custom_model = model
            self.model_type = model_type
            self.current_model_name = model_type
        
        return {
            "status": "success",
            "model_type": model_type,
            "samples": len(texts),
            "saved_path": str(model_path)
        }
    
    def batch_analyze(self, texts: List[str]) -> List[Dict[str, any]]:
        """
        Analyze sentiment for multiple texts (case-insensitive).
        
        Args:
            texts: List of texts to analyze (automatically normalized)
            
        Returns:
            List of sentiment analysis results
        """
        results = []
        for text in texts:
            try:
                result = self.analyze(text)  # Normalization happens inside analyze()
                results.append(result)
            except Exception as e:
                results.append({"error": str(e), "text": text[:50]})
        return results
    
    def get_document_sentiment_summary(self, documents: List[Dict]) -> Dict[str, any]:
        """
        Analyze sentiment across multiple documents and provide summary.
        
        Args:
            documents: List of document dicts with 'content' key
            
        Returns:
            Summary of sentiment distribution
        """
        sentiments = []
        scores = []
        
        for doc in documents:
            content = doc.get("content", "")
            if content:
                result = self.analyze(content)
                sentiments.append(result["sentiment"])
                if "score" in result:
                    scores.append(result["score"])
                elif "confidence" in result:
                    scores.append(result["confidence"])
        
        # Calculate distribution
        unique, counts = np.unique(sentiments, return_counts=True)
        distribution = dict(zip(unique, counts.tolist()))
        
        # Calculate average confidence
        avg_confidence = round(np.mean(scores), 4) if scores else 0
        
        return {
            "total_documents": len(documents),
            "analyzed": len(sentiments),
            "distribution": distribution,
            "average_confidence": avg_confidence,
            "dominant_sentiment": max(distribution, key=distribution.get) if distribution else "unknown"
        }


# Global instance
_sentiment_analyzer = None


def get_sentiment_analyzer(model_type: str = "pretrained") -> SentimentAnalyzer:
    """Get or create sentiment analyzer instance."""
    global _sentiment_analyzer
    if _sentiment_analyzer is None:
        _sentiment_analyzer = SentimentAnalyzer(model_type=model_type)
    return _sentiment_analyzer
