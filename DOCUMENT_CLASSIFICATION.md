# Document Classification Feature

This RAG application includes a powerful **ML-based Document Classification** system that automatically categorizes documents into three domains: Medical, Legal, and News.

## Overview

The classification system uses trained machine learning models instead of simple regex patterns:

### Supported Categories
- **Medical** - Healthcare, patient records, medical procedures, drug information
- **Legal** - Court rulings, contracts, lawsuits, legal agreements, statutory information
- **News** - News articles, market reports, government announcements, industry trends

### ML Algorithms Used
- Logistic Regression (fast, interpretable)
- Random Forest (ensemble method, high accuracy)
- SVM (Support Vector Machine, good for text)
- Naive Bayes (probabilistic approach)
- Gradient Boosting (boosting ensemble)

All models use **TF-IDF vectorization** for feature extraction with n-grams (1-2 word phrases).

## Installation

Required packages are already in `requirements.txt`. Ensure you have:
```bash
pip install -r requirements.txt
```

## Quick Start

### 1. Generate Training Dataset

Create a synthetic dataset of 5000 documents:
```bash
python generate_dataset.py 5000 mock_dataset_5000.csv
```

This creates realistic synthetic documents in the three categories with varied content and vocabulary.

### 2. Train the Model

```bash
python train_document_classifier.py
```

This will:
- Generate dataset (if not exists)
- Load dataset
- Train 5 different ML algorithms
- Evaluate performance
- Save best model
- Display test results

**Sample output:**
```
[Step 3] Training ML models...

Training logistic_regression...
  ✓ Accuracy: 0.9234, F1-Score: 0.9241

Training random_forest...
  ✓ Accuracy: 0.9156, F1-Score: 0.9163

Training svm...
  ✓ Accuracy: 0.9345, F1-Score: 0.9351
  
✅ Best algorithm: svm (Accuracy: 0.9345)
```

### 3. Use via API

#### **Classify Single Document**
```bash
curl -X POST "http://localhost:8000/api/classify" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "text=Patient diagnosed with hypertension after blood pressure test showed elevated levels"
```

**Response:**
```json
{
  "text": "Patient diagnosed with hypertension after...",
  "predicted_category": "medical",
  "confidence": 0.9876,
  "probabilities": {
    "medical": 0.9876,
    "legal": 0.0098,
    "news": 0.0026
  }
}
```

#### **Batch Classify Multiple Documents**
```bash
curl -X POST "http://localhost:8000/api/classify/batch" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "texts=Medical text here&texts=Legal text here&texts=News text here"
```

**Response:**
```json
{
  "total": 3,
  "results": [
    {"predicted_category": "medical", "confidence": 0.95, "probabilities": {...}},
    {"predicted_category": "legal", "confidence": 0.92, "probabilities": {...}},
    {"predicted_category": "news", "confidence": 0.88, "probabilities": {...}}
  ],
  "model_type": "LinearSVC"
}
```

#### **Get Classifier Info**
```bash
curl -X GET "http://localhost:8000/api/classify/info"
```

**Response:**
```json
{
  "status": "ready",
  "categories": ["medical", "legal", "news"],
  "model_type": "LinearSVC",
  "vectorizer_type": "TfidfVectorizer",
  "max_features": 5000
}
```

### 4. Test Everything

```bash
python test_document_classifier.py
```

Runs comprehensive tests including:
- Dataset generation
- Classifier initialization
- Model training
- Single classification
- Batch classification

## Python API Usage

```python
from document_classifier import get_document_classifier

# Get classifier instance
classifier = get_document_classifier()

# Classify single document
result = classifier.classify("Patient shows fever and fatigue...")
print(result)
# Output: {'predicted_category': 'medical', 'confidence': 0.95, ...}

# Batch classification
texts = ["Medical...", "Legal...", "News..."]
results = classifier.batch_classify(texts)

# Get model info
info = classifier.get_model_info()
print(info)

# Train custom model
from generate_dataset import generate_dataset
texts, labels = classifier.load_dataset("mock_dataset_5000.csv")
result = classifier.train(texts, labels)
```

## Dataset Generation

The `generate_dataset.py` script creates realistic synthetic documents using:

### Templates (Domain-Specific)
Each category has multiple sentence templates that are filled with vocabulary:

**Medical Templates:**
- "Patient shows signs of {symptom} and {symptom}."
- "Laboratory results for {test} indicate {result}."
- "Diagnosis of {condition} confirmed via {test}."
- etc.

**Legal Templates:**
- "The {party} filed a motion for {action} in the {court}."
- "Clause {number} of the agreement specifies terms for {topic}."
- "The court ruled that the {party} is liable for {claim}."
- etc.

**News Templates:**
- "{entity} announced a new partnership with {entity2} today."
- "Markets reacted {reaction} to the latest report on {topic}."
- "Breaking: {entity} has won the award for {topic}."
- etc.

### Vocabulary (Domain-Specific)
Each template variable has a list of realistic values:

- **Medical:** symptoms (fever, fatigue, nausea), tests (MRI, blood panel, biopsy), conditions (diabetes, hypertension, bronchitis), medications (Amoxicillin, Metformin), etc.
- **Legal:** parties (plaintiff, defendant), actions (summary judgment, dismissal), courts (District, Supreme), topics (intellectual property, breach of contract), etc.
- **News:** entities (Global Tech Corp, NASA, Federal Reserve), sectors (energy, technology, healthcare), trends (growth, decline, volatility), etc.

## Usage Examples

### Example 1: Classify Medical Document
```bash
POST /api/classify
text: Patient prescribed Metformin for type 2 diabetes. Follow-up scheduled for condition management.

Response: {"predicted_category": "medical", "confidence": 0.98, ...}
```

### Example 2: Classify Legal Document
```bash
POST /api/classify
text: The plaintiff filed a motion for dismissal in Superior Court. Counsel argued regarding breach of contract under state law.

Response: {"predicted_category": "legal", "confidence": 0.96, ...}
```

### Example 3: Classify News Document
```bash
POST /api/classify
text: Global Tech Corp announced a new partnership with Amazon today. Markets reacted positively to the news. Analysts predict significant growth in the technology sector.

Response: {"predicted_category": "news", "confidence": 0.94, ...}
```

## Model Performance

Typical accuracy across algorithms (on 5000 sample balanced dataset):

| Algorithm | Accuracy | F1-Score | Training Time | Speed |
|-----------|----------|----------|---------------|-------|
| Logistic Regression | 92-94% | 0.92-0.94 | Fast | Very Fast |
| Random Forest | 88-92% | 0.88-0.92 | Slow | Medium |
| SVM (Linear) | 93-95% | 0.93-0.95 | Medium | Fast |
| Naive Bayes | 85-88% | 0.85-0.88 | Very Fast | Very Fast |
| Gradient Boosting | 91-94% | 0.91-0.94 | Slow | Medium |

**Best Overall:** SVM typically provides best balance of accuracy and speed.

## Integration with RAG

### Use Case 1: Automatic Document Classification on Upload
```python
# When uploading documents, automatically classify them
files = uploaded_documents
for doc in files:
    category = classifier.classify(doc.content)
    # Tag document with category for better organization
```

### Use Case 2: Filter Results by Domain
```python
# After RAG retrieval, filter results by category
results = rag_engine.query("What are symptoms?")
# Filter only medical results
medical_results = [r for r in results if classifier.classify(r.content)["predicted_category"] == "medical"]
```

### Use Case 3: Multi-Domain Analysis
```python
# Analyze documents across multiple domains
for doc in knowledge_base:
    category = classifier.classify(doc)
    sentiment = sentiment_analyzer.analyze(doc)
    # Create combined insights
```

## Advanced Configuration

### Custom Vectorizer Parameters
Edit `document_classifier.py` to modify TF-IDF:
```python
"tfidf", TfidfVectorizer(
    max_features=5000,      # Limit vocabulary size
    ngram_range=(1, 2),     # Use 1-word and 2-word phrases
    min_df=2,               # Minimum document frequency
    max_df=0.9,             # Maximum document frequency
    lowercase=True          # Normalize case
)
```

### Custom Algorithm Parameters
Adjust classifier hyperparameters:
```python
# For Logistic Regression
LogisticRegression(
    max_iter=1000,
    random_state=42,
    multi_class='multinomial'
)

# For Random Forest
RandomForestClassifier(
    n_estimators=100,
    max_depth=20,
    random_state=42
)
```

## Troubleshooting

**Q: Model accuracy is low**
- A: Train on more data (use larger num_samples in generate_dataset)
- A: Adjust TF-IDF parameters (max_features, ngram_range)
- A: Try different algorithms (SVM or Gradient Boosting often work better)

**Q: Predictions are not confident**
- A: Check if document is actually from one of the categories
- A: The text might be borderline between categories
- A: Use confidence threshold: `if result['confidence'] < 0.7: manual_review()`

**Q: Model training is slow**
- A: Reduce number of samples in training dataset
- A: Use faster algorithms (Logistic Regression, Naive Bayes)
- A: Reduce max_features in TfidfVectorizer

**Q: Misclassification between similar categories**
- A: Add more diverse training data
- A: Increase TF-IDF max_features (more vocabulary)
- A: Use ensemble methods (Random Forest, Gradient Boosting)

## File Structure

```
.
├── generate_dataset.py              # Dataset generation script
├── document_classifier.py           # ML classifier module
├── train_document_classifier.py     # Training pipeline script
├── test_document_classifier.py      # Test suite
├── main.py                          # FastAPI integration
├── models/
│   ├── document_classifier_model.pkl
│   ├── document_classifier_vectorizer.pkl
│   └── document_classifier_info.pkl
└── README.md                        # This file
```

## License

Same as the main project.
