"""
ML-Based Document Classifier
Classifies documents by domain (medical, legal, news) using ML algorithms
"""

import os
import csv
import joblib
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)


class DocumentClassifier:
    """ML-based document classifier for medical, legal, and news documents."""
    
    CATEGORIES = ["medical", "legal", "news"]
    ALGORITHMS = ["logistic_regression", "random_forest", "svm", "naive_bayes", "gradient_boosting"]
    
    def __init__(self, model_dir: str = "./models"):
        """
        Initialize document classifier.
        
        Args:
            model_dir: Directory to store trained models
        """
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True)
        
        self.model = None
        self.current_model_name = None
        self.available_models = {}
        self.label_to_idx = {label: idx for idx, label in enumerate(self.CATEGORIES)}
        self.idx_to_label = {idx: label for label, idx in self.label_to_idx.items()}
        self.model_info = {}
        
        self._try_load_models()
    
    def _try_load_models(self):
        """Try to load all pre-trained models if available."""
        # Try to load best model (logistic regression by default)
        best_model_path = self.model_dir / "logistic_regression_model.pkl"
        
        # Check all saved models
        for algo in self.ALGORITHMS:
            model_path = self.model_dir / f"{algo}_model.pkl"
            if model_path.exists():
                try:
                    model = joblib.load(model_path)
                    self.available_models[algo] = model_path
                    print(f"✓ Found trained model: {algo}")
                except Exception as e:
                    print(f"⚠ Could not load {algo} model: {e}")
        
        # Load best model as default
        if best_model_path.exists():
            try:
                self.model = joblib.load(best_model_path)
                self.current_model_name = "logistic_regression"
                print("✓ Loaded logistic regression as primary model")
            except Exception as e:
                print(f"⚠ Could not load logistic regression model: {e}")
                # Fallback to first available model
                if self.available_models:
                    first_algo = list(self.available_models.keys())[0]
                    self.model = joblib.load(self.available_models[first_algo])
                    self.current_model_name = first_algo
                    print(f"✓ Using {first_algo} as fallback model")
        elif self.available_models:
            # Load first available if best not found
            first_algo = list(self.available_models.keys())[0]
            self.model = joblib.load(self.available_models[first_algo])
            self.current_model_name = first_algo
            print(f"✓ Loaded {first_algo} model")
        else:
            print("⚠ No pre-trained models found")
    
    def load_dataset(self, csv_file: str) -> Tuple[List[str], List[str]]:
        """
        Load dataset from CSV file.
        
        Args:
            csv_file: Path to CSV file with 'text' and 'label' columns
            
        Returns:
            Tuple of (texts, labels)
        """
        texts = []
        labels = []
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    texts.append(row['text'])
                    labels.append(row['label'])
            
            print(f"✓ Loaded {len(texts)} documents from {csv_file}")
            return texts, labels
        except Exception as e:
            print(f"✗ Error loading dataset: {e}")
            return [], []
    
    def train(
        self,
        texts: List[str],
        labels: List[str],
        test_size: float = 0.2,
        algorithms: Optional[List[str]] = None
    ) -> Dict:
        """
        Train document classifier using multiple algorithms.
        
        Args:
            texts: List of document texts
            labels: List of document labels
            test_size: Fraction of data to use for testing
            algorithms: List of algorithms to try. Options: logistic_regression, random_forest, 
                       gradient_boosting, svm, naive_bayes
        
        Returns:
            Training results dictionary
        """
        if not texts or not labels:
            raise ValueError("Texts and labels cannot be empty")
        
        if len(texts) != len(labels):
            raise ValueError("Number of texts and labels must match")
        
        if algorithms is None:
            algorithms = ["logistic_regression", "random_forest", "svm"]
        
        print(f"\nPreparing training data...")
        print(f"Total samples: {len(texts)}")
        print(f"Classes: {self.CATEGORIES}")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            texts, labels, test_size=test_size, random_state=42, stratify=labels
        )
        
        print(f"Training set: {len(X_train)} samples")
        print(f"Test set: {len(X_test)} samples\n")
        
        results = {}
        best_score = 0
        best_algorithm = None
        best_pipeline = None
        
        for algo_name in algorithms:
            print(f"Training {algo_name}...")
            
            # Create pipeline based on algorithm
            if algo_name == "logistic_regression":
                pipeline = Pipeline([
                    ("tfidf", TfidfVectorizer(
                        max_features=5000,
                        ngram_range=(1, 2),
                        min_df=2,
                        max_df=0.9,
                        lowercase=True
                    )),
                    ("classifier", LogisticRegression(
                        max_iter=1000,
                        random_state=42
                    ))
                ])
            
            elif algo_name == "random_forest":
                pipeline = Pipeline([
                    ("tfidf", TfidfVectorizer(
                        max_features=5000,
                        ngram_range=(1, 2),
                        min_df=2,
                        max_df=0.9,
                        lowercase=True
                    )),
                    ("classifier", RandomForestClassifier(
                        n_estimators=100,
                        max_depth=20,
                        random_state=42,
                        n_jobs=-1
                    ))
                ])
            
            elif algo_name == "gradient_boosting":
                pipeline = Pipeline([
                    ("tfidf", TfidfVectorizer(
                        max_features=5000,
                        ngram_range=(1, 2),
                        min_df=2,
                        max_df=0.9,
                        lowercase=True
                    )),
                    ("classifier", GradientBoostingClassifier(
                        n_estimators=100,
                        max_depth=5,
                        learning_rate=0.1,
                        random_state=42
                    ))
                ])
            
            elif algo_name == "svm":
                pipeline = Pipeline([
                    ("tfidf", TfidfVectorizer(
                        max_features=5000,
                        ngram_range=(1, 2),
                        min_df=2,
                        max_df=0.9,
                        lowercase=True
                    )),
                    ("classifier", LinearSVC(
                        max_iter=2000,
                        random_state=42
                    ))
                ])
            
            elif algo_name == "naive_bayes":
                pipeline = Pipeline([
                    ("tfidf", TfidfVectorizer(
                        max_features=5000,
                        ngram_range=(1, 2),
                        min_df=2,
                        max_df=0.9,
                        lowercase=True
                    )),
                    ("classifier", MultinomialNB())
                ])
            
            else:
                print(f"  Unknown algorithm: {algo_name}")
                continue
            
            try:
                # Train
                pipeline.fit(X_train, y_train)
                
                # Evaluate
                y_pred = pipeline.predict(X_test)
                accuracy = accuracy_score(y_test, y_pred)
                f1 = f1_score(y_test, y_pred, average='weighted')
                
                results[algo_name] = {
                    "accuracy": accuracy,
                    "f1_score": f1,
                    "pipeline": pipeline
                }
                
                print(f"  ✓ Accuracy: {accuracy:.4f}, F1-Score: {f1:.4f}")
                
                if accuracy > best_score:
                    best_score = accuracy
                    best_algorithm = algo_name
                    best_pipeline = pipeline
            
            except Exception as e:
                print(f"  ✗ Error training {algo_name}: {e}")
        
        # Save all trained models
        if results:
            print(f"\n✅ Best algorithm: {best_algorithm} (Accuracy: {best_score:.4f})")
            
            # Save all models
            print("\n[Saving all trained models...]")
            for algo_name, result in results.items():
                self._save_model(algo_name, result["pipeline"])
            
            # Load best model as default
            self.model = best_pipeline
            self.current_model_name = best_algorithm
            self.available_models[best_algorithm] = self.model_dir / f"{best_algorithm}_model.pkl"
            
            # Get detailed metrics
            y_pred = self.model.predict(X_test)
            print(f"\nDetailed Classification Report:")
            print(classification_report(y_test, y_pred, target_names=self.CATEGORIES))
            
            return {
                "status": "success",
                "best_algorithm": best_algorithm,
                "accuracy": best_score,
                "all_results": results,
                "all_models_saved": list(results.keys()),
                "test_size": len(X_test)
            }
        else:
            raise RuntimeError("No models trained successfully")
    
    def _save_model(self, algorithm: str, pipeline):
        """Save trained model by algorithm name."""
        model_path = self.model_dir / f"{algorithm}_model.pkl"
        
        joblib.dump(pipeline, model_path)
        print(f"✓ Model saved: {model_path}")
    
    def switch_model(self, algorithm: str):
        """
        Switch to a different trained model.
        
        Args:
            algorithm: Algorithm name (logistic_regression, random_forest, svm, naive_bayes, gradient_boosting)
            
        Returns:
            True if switch successful, False otherwise
        """
        if algorithm not in self.available_models:
            print(f"❌ Model '{algorithm}' not available. Available: {list(self.available_models.keys())}")
            return False
        
        try:
            model_path = self.available_models[algorithm]
            self.model = joblib.load(model_path)
            self.current_model_name = algorithm
            print(f"✓ Switched to {algorithm} model")
            return True
        except Exception as e:
            print(f"❌ Error switching to {algorithm}: {e}")
            return False
    
    def get_available_models(self) -> Dict:
        """Get list of available trained models."""
        return {
            "current_model": self.current_model_name,
            "available_models": list(self.available_models.keys()),
            "total_models": len(self.available_models)
        }
    
    def classify(self, text: str) -> Dict:
        """
        Classify a single document (case-insensitive).
        
        Args:
            text: Document text to classify (automatically normalized)
            
        Returns:
            Dictionary with classification results
        """
        if not self.model:
            raise RuntimeError("No model trained or loaded. Train first using train()")
        
        # Normalize text to lowercase for consistent classification
        normalized_text = text.lower().strip()
        
        # Get prediction and probabilities
        prediction = self.model.predict([normalized_text])[0]
        
        try:
            probabilities = self.model.predict_proba([normalized_text])[0]
            proba_dict = {
                self.CATEGORIES[i]: round(prob, 4)
                for i, prob in enumerate(probabilities)
            }
        except AttributeError:
            # Some models don't have predict_proba
            proba_dict = {self.CATEGORIES[0]: 1.0}
        
        return {
            "text": text[:100] + "..." if len(text) > 100 else text,
            "predicted_category": prediction,
            "confidence": round(max(proba_dict.values()), 4),
            "probabilities": proba_dict
        }
    
    def batch_classify(self, texts: List[str]) -> List[Dict]:
        """
        Classify multiple documents.
        
        Args:
            texts: List of document texts
            
        Returns:
            List of classification results
        """
        results = []
        for text in texts:
            try:
                result = self.classify(text)
                results.append(result)
            except Exception as e:
                results.append({"error": str(e), "text": text[:50]})
        return results
    
    def get_model_info(self) -> Dict:
        """Get information about the trained models."""
        if not self.model:
            return {"status": "no_model"}
        
        return {
            "status": "ready",
            "current_model": self.current_model_name,
            "categories": self.CATEGORIES,
            "model_type": type(self.model.named_steps['classifier']).__name__,
            "vectorizer_type": type(self.model.named_steps['tfidf']).__name__,
            "max_features": self.model.named_steps['tfidf'].max_features,
            "available_models": list(self.available_models.keys()),
            "total_available": len(self.available_models)
        }


# Global instance
_classifier = None


def get_document_classifier() -> DocumentClassifier:
    """Get or create document classifier instance."""
    global _classifier
    if _classifier is None:
        _classifier = DocumentClassifier()
    return _classifier
