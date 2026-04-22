"""
FastAPI RAG Bot - Single Multimodal Endpoint
Handles document upload + Q&A in one endpoint
"""

import os
import tempfile
import shutil
from pathlib import Path
from typing import List, Optional, Union
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from pdf_processor import DocumentProcessor
from vector_store import VectorStoreManager
from rag_engine import RAGEngine
from sentiment_analyzer import get_sentiment_analyzer
from document_classifier import get_document_classifier

# Load environment
load_dotenv()

# Initialize FastAPI
app = FastAPI(
    title="RAG Bot API",
    description="Multimodal RAG system with document processing and Q&A",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
vector_store = None
rag_engine = None
document_processor = None
sentiment_analyzer = None
document_classifier = None


@app.on_event("startup")
async def startup_event():
    """Initialize components on startup."""
    global vector_store, rag_engine, document_processor, sentiment_analyzer, document_classifier
    
    # Check API key
    if not os.getenv("GOOGLE_API_KEY"):
        raise RuntimeError("GOOGLE_API_KEY not set in environment")
    
    try:
        # Initialize vector store
        vector_store = VectorStoreManager(
            persist_directory=os.getenv("PERSIST_DIR", "./chroma_db"),
            embedding_model=os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        )
    except Exception as e:
        print(f"⚠️  Error initializing vector store: {str(e)}")
        print("This may be due to network issues. Continuing with cached model if available...")
        try:
            vector_store = VectorStoreManager(
                persist_directory=os.getenv("PERSIST_DIR", "./chroma_db"),
                embedding_model=os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
            )
        except Exception as e2:
            print(f"❌ Failed to initialize vector store: {str(e2)}")
            raise
    
    try:
        # Initialize RAG engine
        rag_engine = RAGEngine(
            vector_store=vector_store,
            model_name=os.getenv("CHAT_MODEL", "gemini-2.5-flash"),
            retrieval_k=int(os.getenv("RETRIEVAL_K", "8")),
            use_reranker=os.getenv("USE_RERANKER", "true").lower() == "true",
            reranker_top_k=int(os.getenv("RERANKER_TOP_K", "4"))
        )
    except Exception as e:
        print(f"⚠️  Warning: Error initializing RAG engine: {str(e)}")
        print("RAG functionality may be limited")
        rag_engine = None
    
    # Initialize document processor
    document_processor = DocumentProcessor(
        chunk_size=int(os.getenv("CHUNK_SIZE", "1000")),
        chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "200")),
        use_ocr=os.getenv("USE_OCR", "true").lower() == "true"
    )
    
    # Initialize sentiment analyzer
    try:
        sentiment_analyzer = get_sentiment_analyzer(model_type="pretrained")
        print("✓ Sentiment analyzer initialized")
    except Exception as e:
        print(f"⚠️  Warning: Error initializing sentiment analyzer: {str(e)}")
        sentiment_analyzer = get_sentiment_analyzer(model_type="pretrained")
    
    # Initialize document classifier
    try:
        document_classifier = get_document_classifier()
        print("✓ Document classifier initialized")
    except Exception as e:
        print(f"⚠️  Warning: Error initializing document classifier: {str(e)}")
    
    print("✅ RAG Bot initialized successfully")


class QueryResponse(BaseModel):
    """Response model for queries."""
    answer: str
    sources: list
    metadata: dict
    documents_in_kb: int


@app.post("/api/rag")
async def multimodal_rag(
    files: List[UploadFile] = File(default=[], description="Upload: PDF (.pdf), Images (.jpg, .jpeg, .png), Text (.txt, .md), Documents (.docx, .doc)"),
    question: str = Form(default="", description="Question to ask about documents"),
    use_ocr: bool = Form(default=True, description="Enable OCR for images/scanned PDFs"),
    clear_kb: bool = Form(default=False, description="Clear knowledge base before uploading new documents")
):
    """
    **Multimodal RAG Endpoint - All-in-One**
    
    This single endpoint handles:
    1. Document upload (PDF, images, txt, docx) - Optional
    2. Document processing with OCR - Optional
    3. Vector storage
    4. Question answering with citations
    
    **Use Cases:**
    - Upload documents and ask question: `files + question`
    - Ask about existing documents: `question only`
    - Upload documents without question: `files only` (returns confirmation)
    - Clear and reload: `clear_kb=true + files + question`
    
    **Example 1: Upload and Ask**
    ```
    POST /api/rag
    files: book.pdf, image.jpg
    question: "What is the main topic?"
    use_ocr: true
    ```
    
    **Example 2: Ask Only**
    ```
    POST /api/rag
    question: "Summarize chapter 1"
    ```
    
    **Example 3: Just Upload**
    ```
    POST /api/rag
    files: document.pdf
    ```
    """
    
    try:
        # Validate: at least files or question must be provided
        if not files and not question.strip():
            raise HTTPException(
                status_code=400,
                detail="Please provide either 'files' to upload or 'question' to ask, or both."
            )
        
        # Step 1: Clear knowledge base if requested
        if clear_kb:
            vector_store.clear_vectorstore()
            print("🗑️ Knowledge base cleared")
        
        # Step 2: Process uploaded files if provided
        if files and len(files) > 0:
            # Validate file types
            ALLOWED_EXTENSIONS = {'.pdf', '.txt', '.md', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'}
            
            temp_dir = tempfile.mkdtemp()
            
            try:
                # Save uploaded files
                file_paths = []
                for uploaded_file in files:
                    if uploaded_file.filename:  # Skip empty files
                        file_ext = Path(uploaded_file.filename).suffix.lower()
                        
                        # Validate file extension
                        if file_ext not in ALLOWED_EXTENSIONS:
                            raise HTTPException(
                                status_code=400,
                                detail=f"Unsupported file type: {file_ext}. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
                            )
                        
                        file_path = Path(temp_dir) / uploaded_file.filename
                        with open(file_path, "wb") as f:
                            content = await uploaded_file.read()
                            f.write(content)
                        file_paths.append(str(file_path))
                
                # Process documents
                if file_paths:
                    document_processor.use_ocr = use_ocr
                    chunks = document_processor.process_multiple_documents(file_paths)
                    
                    if chunks:
                        vector_store.add_documents(chunks)
                        print(f"✅ Processed {len(file_paths)} files into {len(chunks)} chunks")
                    else:
                        raise HTTPException(status_code=400, detail="No content extracted from files")
            
            finally:
                # Cleanup temp files
                shutil.rmtree(temp_dir, ignore_errors=True)
        
        # Step 3: Answer question if provided
        if question and question.strip():
            # Check if we have documents
            doc_count = vector_store.get_document_count()
            if doc_count == 0:
                raise HTTPException(
                    status_code=400,
                    detail="No documents in knowledge base. Please upload documents first."
                )
            
            # Query RAG engine
            result = rag_engine.query(question)
            
            # Format sources
            sources = []
            for doc in result["source_documents"]:
                sources.append({
                    "source": doc.metadata.get('source', 'Unknown'),
                    "chunk_id": doc.metadata.get('chunk_id', 'N/A'),
                    "doc_type": doc.metadata.get('doc_type', 'unknown'),
                    "rerank_score": doc.metadata.get('rerank_score'),
                    "excerpt": doc.page_content[:300].strip()
                })
            
            return QueryResponse(
                answer=result["answer"],
                sources=sources,
                metadata=result["metadata"],
                documents_in_kb=doc_count
            )
        
        else:
            # No question provided - just return upload confirmation
            doc_count = vector_store.get_document_count()
            return QueryResponse(
                answer="Documents uploaded successfully. No question provided.",
                sources=[],
                metadata={"upload_only": True},
                documents_in_kb=doc_count
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    doc_count = vector_store.get_document_count() if vector_store else 0
    return {
        "status": "healthy",
        "documents": doc_count,
        "model": os.getenv("CHAT_MODEL", "gemini-2.5-flash"),
        "reranker_enabled": os.getenv("USE_RERANKER", "true").lower() == "true"
    }


@app.get("/api/stats")
async def get_stats():
    """Get knowledge base statistics."""
    return {
        "total_chunks": vector_store.get_document_count() if vector_store else 0,
        "embedding_model": os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"),
        "chat_model": os.getenv("CHAT_MODEL", "gemini-2.5-flash"),
        "retrieval_k": int(os.getenv("RETRIEVAL_K", "8")),
        "reranker_top_k": int(os.getenv("RERANKER_TOP_K", "4")),
        "ocr_enabled": os.getenv("USE_OCR", "true").lower() == "true"
    }


@app.delete("/api/clear")
async def clear_knowledge_base():
    """Clear all documents from knowledge base."""
    try:
        vector_store.clear_vectorstore()
        return {"status": "success", "message": "Knowledge base cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== DOCUMENT CLASSIFICATION ENDPOINTS ====================


@app.post("/api/classify")
async def classify_document(text: str = Form(..., description="Document text to classify")):
    """
    **Classify Document by Domain**
    
    Uses trained ML model to classify document as medical, legal, or news.
    
    Returns classification category, confidence, and probabilities for each category.
    
    **Example:**
    ```
    POST /api/classify
    text: "Patient diagnosed with hypertension after blood pressure test."
    ```
    """
    try:
        if not text or not text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        result = document_classifier.classify(text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error classifying document: {str(e)}")


@app.post("/api/classify/batch")
async def batch_classify_documents(texts: List[str] = Form(..., description="List of texts to classify")):
    """
    **Batch Classify Documents**
    
    Classify multiple documents at once.
    
    **Example:**
    ```
    POST /api/classify/batch
    texts: ["Medical text...", "Legal text...", "News text..."]
    ```
    """
    try:
        if not texts or len(texts) == 0:
            raise HTTPException(status_code=400, detail="Texts list cannot be empty")
        
        results = document_classifier.batch_classify(texts)
        return {
            "total": len(texts),
            "results": results,
            "model_type": type(document_classifier.model.named_steps['classifier']).__name__ if document_classifier.model else "unknown"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in batch classification: {str(e)}")


@app.get("/api/classify/info")
async def get_classifier_info():
    """
    **Get Document Classifier Information**
    
    Returns information about the trained classification model.
    """
    return document_classifier.get_model_info()


@app.get("/api/classify/models")
async def get_available_models():
    """
    **Get List of Available Classification Models**
    
    Returns all trained models available for use.
    """
    return document_classifier.get_available_models()


@app.post("/api/classify/switch/{algorithm}")
async def switch_classification_model(algorithm: str):
    """
    **Switch Classification Model**
    
    Switch to a different trained model algorithm.
    
    Available algorithms: logistic_regression, random_forest, svm, naive_bayes, gradient_boosting
    
    **Example:**
    ```
    POST /api/classify/switch/random_forest
    ```
    """
    if algorithm not in document_classifier.ALGORITHMS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid algorithm. Available: {document_classifier.ALGORITHMS}"
        )
    
    success = document_classifier.switch_model(algorithm)
    if success:
        return {
            "status": "success",
            "current_model": algorithm,
            "model_info": document_classifier.get_model_info()
        }
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Model '{algorithm}' not available. Train first using train_document_classifier.py"
        )


# ==================== SENTIMENT ANALYSIS ENDPOINTS ====================


@app.post("/api/sentiment/analyze")
async def analyze_sentiment(text: str = Form(..., description="Text to analyze sentiment")):
    """
    **Analyze Sentiment of Text**
    
    Uses pre-trained DistilBERT model fine-tuned on sentiment analysis.
    
    Returns sentiment (positive/negative), confidence score, and probabilities.
    
    **Example:**
    ```
    POST /api/sentiment/analyze
    text: "I really love this product, it's amazing!"
    ```
    """
    try:
        if not text or not text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        result = sentiment_analyzer.analyze(text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing sentiment: {str(e)}")


@app.post("/api/sentiment/batch")
async def batch_analyze_sentiment(texts: List[str] = Form(..., description="List of texts to analyze")):
    """
    **Batch Analyze Sentiment**
    
    Analyze sentiment for multiple texts at once.
    
    **Example:**
    ```
    POST /api/sentiment/batch
    texts: ["Great product!", "Terrible experience", "It's okay"]
    ```
    """
    try:
        if not texts or len(texts) == 0:
            raise HTTPException(status_code=400, detail="Texts list cannot be empty")
        
        results = sentiment_analyzer.batch_analyze(texts)
        return {
            "total": len(texts),
            "results": results,
            "model": sentiment_analyzer.model_type
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in batch analysis: {str(e)}")


@app.get("/api/sentiment/documents")
async def analyze_documents_sentiment():
    """
    **Analyze Sentiment Across All Documents**
    
    Analyzes sentiment distribution across all documents in the knowledge base.
    
    Returns:
    - Total documents and analyzed documents
    - Sentiment distribution (positive/negative/neutral counts)
    - Average confidence score
    - Dominant sentiment
    """
    try:
        doc_count = vector_store.get_document_count()
        if doc_count == 0:
            raise HTTPException(
                status_code=400,
                detail="No documents in knowledge base"
            )
        
        # Get all documents from vector store
        all_docs = vector_store.get_all_documents()
        
        if not all_docs:
            raise HTTPException(status_code=400, detail="Could not retrieve documents")
        
        # Analyze sentiment
        summary = sentiment_analyzer.get_document_sentiment_summary(all_docs)
        summary["model"] = sentiment_analyzer.model_type
        
        return summary
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing documents: {str(e)}")


class TrainSentimentRequest(BaseModel):
    """Request model for training sentiment model."""
    texts: List[str]
    labels: List[int]  # 0=negative, 1=neutral, 2=positive
    model_type: str = "logistic_regression"  # or "naive_bayes"


@app.post("/api/sentiment/train")
async def train_sentiment_model(request: TrainSentimentRequest):
    """
    **Train Custom Sentiment Model**
    
    Train a Logistic Regression or Naive Bayes model on custom data.
    
    Labels: 
    - 0 = Negative
    - 1 = Neutral
    - 2 = Positive
    
    **Example:**
    ```
    POST /api/sentiment/train
    {
        "texts": ["Great!", "Bad experience", "Average"],
        "labels": [2, 0, 1],
        "model_type": "logistic_regression"
    }
    ```
    """
    try:
        if len(request.texts) != len(request.labels):
            raise HTTPException(
                status_code=400,
                detail="Number of texts and labels must match"
            )
        
        if len(request.texts) < 5:
            raise HTTPException(
                status_code=400,
                detail="Need at least 5 training samples"
            )
        
        if request.model_type not in ["logistic_regression", "naive_bayes"]:
            raise HTTPException(
                status_code=400,
                detail="Model type must be 'logistic_regression' or 'naive_bayes'"
            )
        
        # Train model
        result = sentiment_analyzer.train_custom_model(
            texts=request.texts,
            labels=request.labels,
            model_type=request.model_type
        )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error training model: {str(e)}")


@app.get("/api/sentiment/info")
async def get_sentiment_info():
    """
    **Get Sentiment Analyzer Information**
    
    Returns info about the current sentiment analysis model and capabilities.
    """
    return {
        "current_model": sentiment_analyzer.model_type,
        "supported_models": ["pretrained", "logistic_regression", "naive_bayes"],
        "sentiment_labels": {
            "0": "negative",
            "1": "neutral",
            "2": "positive"
        },
        "pretrained_model_name": "distilbert-base-uncased-finetuned-sst-2-english",
        "features": {
            "single_text_analysis": "/api/sentiment/analyze",
            "batch_analysis": "/api/sentiment/batch",
            "document_analysis": "/api/sentiment/documents",
            "model_training": "/api/sentiment/train"
        }
    }


@app.get("/api/sentiment/models")
async def get_sentiment_models():
    """
    **Get List of Available Sentiment Models**
    
    Returns all available pre-trained and custom sentiment models.
    """
    return sentiment_analyzer.get_available_models()


@app.post("/api/sentiment/switch/{model_name}")
async def switch_sentiment_model(model_name: str):
    """
    **Switch Sentiment Model**
    
    Switch to a different sentiment analysis model.
    
    Available models: pretrained, logistic_regression, naive_bayes
    
    **Example:**
    ```
    POST /api/sentiment/switch/logistic_regression
    ```
    """
    if model_name == "pretrained":
        sentiment_analyzer.model_type = "pretrained"
        sentiment_analyzer.current_model_name = "pretrained"
        return {
            "status": "success",
            "current_model": "pretrained",
            "message": "Switched to pre-trained DistilBERT model"
        }
    
    if model_name not in sentiment_analyzer.CUSTOM_MODELS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid model. Available: {['pretrained'] + sentiment_analyzer.CUSTOM_MODELS}"
        )
    
    success = sentiment_analyzer.switch_model(model_name)
    if success:
        return {
            "status": "success",
            "current_model": model_name,
            "model_info": sentiment_analyzer.get_available_models()
        }
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Model '{model_name}' not available. Train first using train_sentiment_analyzer.py"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=True
    )
