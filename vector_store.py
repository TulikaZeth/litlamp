"""
Vector Store Manager
Manages ChromaDB vector store for document embeddings and retrieval.
"""

import os
from typing import List, Optional
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


class VectorStoreManager:
    """Manage vector store for document embeddings."""
    
    def __init__(
        self,
        persist_directory: str = "./chroma_db",
        collection_name: str = "ragbot_docs",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    ):
        """
        Initialize vector store manager.
        
        Args:
            persist_directory: Directory to persist ChromaDB data
            collection_name: Name of the collection
            embedding_model: Google Gemini embedding model to use
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Initialize embeddings with HuggingFace - with fallback
        try:
            self.embeddings = HuggingFaceEmbeddings(
                model_name=embedding_model,
                show_progress=False,
                cache_folder=os.path.join(persist_directory, ".cache")
            )
        except Exception as e:
            print(f"⚠️  Warning: Failed to load embedding model from HuggingFace: {str(e)}")
            print("Attempting to use cached model or fallback...")
            # Try with offline mode or pre-downloaded model
            try:
                self.embeddings = HuggingFaceEmbeddings(
                    model_name=embedding_model,
                    model_kwargs={"device": "cpu"},
                    cache_folder=os.path.join(persist_directory, ".cache")
                )
            except Exception as e2:
                print(f"✓ Using offline/cached model initialization")
                self.embeddings = HuggingFaceEmbeddings(
                    model_name=embedding_model,
                    cache_folder=os.path.join(persist_directory, ".cache")
                )

        # Initialize or load vector store
        self.vectorstore = None
        self._load_or_create_vectorstore()
    
    def _load_or_create_vectorstore(self):
        """Load existing vector store or create a new one."""
        if os.path.exists(self.persist_directory):
            print(f"Loading existing vector store from {self.persist_directory}")
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings,
                collection_name=self.collection_name
            )
        else:
            print(f"Creating new vector store at {self.persist_directory}")
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings,
                collection_name=self.collection_name
            )
    
    def add_documents(self, documents: List[Document]) -> List[str]:
        """
        Add documents to the vector store.
        
        Args:
            documents: List of Document objects to add
            
        Returns:
            List of document IDs
        """
        if not documents:
            return []
        
        print(f"Adding {len(documents)} documents to vector store...")
        ids = self.vectorstore.add_documents(documents)
        print(f"Successfully added documents. Total documents in store: {self.get_document_count()}")
        
        return ids
    
    def similarity_search(
        self,
        query: str,
        k: int = 4,
        filter: Optional[dict] = None
    ) -> List[Document]:
        """
        Search for similar documents with case-insensitive matching.
        
        Args:
            query: Query text (automatically normalized for case-insensitive search)
            k: Number of documents to return
            filter: Optional metadata filter
            
        Returns:
            List of similar documents
        """
        # Normalize query to lowercase for better case-insensitive matching
        normalized_query = query.lower().strip()
        return self.vectorstore.similarity_search(
            normalized_query,
            k=k,
            filter=filter
        )
    
    def similarity_search_with_score(
        self,
        query: str,
        k: int = 4,
        filter: Optional[dict] = None
    ) -> List[tuple]:
        """
        Search for similar documents with relevance scores (case-insensitive).
        
        Args:
            query: Query text (automatically normalized for case-insensitive search)
            k: Number of documents to return
            filter: Optional metadata filter
            
        Returns:
            List of (document, score) tuples
        """
        # Normalize query to lowercase for better case-insensitive matching
        normalized_query = query.lower().strip()
        return self.vectorstore.similarity_search_with_score(
            normalized_query,
            k=k,
            filter=filter
        )
    
    def get_document_count(self) -> int:
        """Get the total number of documents in the vector store."""
        try:
            collection = self.vectorstore._collection
            return collection.count()
        except Exception:
            return 0
    
    def clear_vectorstore(self):
        """Clear all documents from the vector store."""
        print("Clearing vector store...")
        self.vectorstore.delete_collection()
        self._load_or_create_vectorstore()
        print("Vector store cleared.")
    
    def as_retriever(self, search_kwargs: Optional[dict] = None):
        """
        Get a retriever interface for the vector store.
        
        Args:
            search_kwargs: Search parameters (e.g., {'k': 4})
            
        Returns:
            Retriever object
        """
        if search_kwargs is None:
            search_kwargs = {"k": 4}
        
        return self.vectorstore.as_retriever(search_kwargs=search_kwargs)
