"""
Enhanced RAG Bot Streamlit Interface
Multi-modal document Q&A with OCR, reranking, and detailed citations.
"""

import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from pdf_processor import DocumentProcessor
from vector_store import VectorStoreManager
from rag_engine import RAGEngine
from sentiment_analyzer import get_sentiment_analyzer
from document_classifier import get_document_classifier

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="RAG Bot - Document Q&A",
    page_icon="📚",
    layout="wide"
)

# Initialize session state
if 'vector_store' not in st.session_state:
    st.session_state.vector_store = None
if 'rag_engine' not in st.session_state:
    st.session_state.rag_engine = None
if 'sentiment_analyzer' not in st.session_state:
    st.session_state.sentiment_analyzer = None
if 'document_classifier' not in st.session_state:
    st.session_state.document_classifier = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'documents_loaded' not in st.session_state:
    st.session_state.documents_loaded = False


def initialize_system():
    """Initialize vector store and RAG engine."""
    if st.session_state.vector_store is None:
        st.session_state.vector_store = VectorStoreManager(
            persist_directory=os.getenv("PERSIST_DIR", "./chroma_db"),
            embedding_model=os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
            
        )

    if st.session_state.rag_engine is None:
        st.session_state.rag_engine = RAGEngine(
            vector_store=st.session_state.vector_store,
            model_name=os.getenv("CHAT_MODEL", "gemini-1.5-pro"),
            retrieval_k=int(os.getenv("RETRIEVAL_K", "8")),
            use_reranker=os.getenv("USE_RERANKER", "true").lower() == "true",
            reranker_top_k=int(os.getenv("RERANKER_TOP_K", "4"))
        )
    
    if st.session_state.sentiment_analyzer is None:
        st.session_state.sentiment_analyzer = get_sentiment_analyzer(model_type="pretrained")
    
    if st.session_state.document_classifier is None:
        st.session_state.document_classifier = get_document_classifier()


def process_uploaded_files(uploaded_files, use_ocr=True):
    """Process uploaded multi-modal files."""
    processor = DocumentProcessor(
        chunk_size=int(os.getenv("CHUNK_SIZE", "1000")),
        chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "200")),
        use_ocr=use_ocr
    )
    
    # Save uploaded files temporarily
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    
    file_paths = []
    for uploaded_file in uploaded_files:
        file_path = os.path.join(temp_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        file_paths.append(file_path)
    
    # Process documents with progress tracking
    with st.spinner("Processing documents (OCR enabled for images)..."):
        chunks = processor.process_multiple_documents(file_paths)
        if chunks:
            st.session_state.vector_store.add_documents(chunks)
    
    # Clean up temp files
    for file_path in file_paths:
        try:
            os.remove(file_path)
        except:
            pass
    
    st.session_state.documents_loaded = True
    return len(chunks)


def main():
    """Main application."""
    st.title("📚 RAG Bot - Multi-Modal Document Intelligence")
    st.markdown("*Upload PDFs, images, or text files - Ask questions with AI-powered retrieval & citations!*")
    st.caption("Powered by Google Gemini 🤖")
    
    # Check for API key
    if not os.getenv("GOOGLE_API_KEY"):
        st.error("⚠️ Please set your GOOGLE_API_KEY in the .env file")
        st.info("Get your API key from: https://makersuite.google.com/app/apikey")
        st.stop()
    
    # Initialize system
    initialize_system()
    
    # Sidebar for document management
    with st.sidebar:
        st.header("📁 Document Management")
        
        # File uploader with multi-format support
        uploaded_files = st.file_uploader(
            "Upload Documents",
            type=['pdf', 'png', 'jpg', 'jpeg', 'txt', 'md', 'docx'],
            accept_multiple_files=True,
            help="Upload PDFs, images (OCR enabled), text files, or DOCX documents"
        )
        
        use_ocr = st.checkbox("Enable OCR for images/scanned PDFs", value=True)
        
        if uploaded_files and st.button("🚀 Process Documents", type="primary"):
            num_chunks = process_uploaded_files(uploaded_files, use_ocr)
            if num_chunks > 0:
                st.success(f"✅ Processed {len(uploaded_files)} files into {num_chunks} chunks")
            else:
                st.error("❌ No documents were successfully processed")
        
        st.divider()
        
        # Document stats
        st.subheader("📊 Knowledge Base Stats")
        doc_count = st.session_state.vector_store.get_document_count() if st.session_state.vector_store else 0
        st.metric("Total Chunks", doc_count)
        
        if st.button("Clear Knowledge Base", type="secondary"):
            if st.session_state.vector_store:
                st.session_state.vector_store.clear_vectorstore()
                st.session_state.chat_history = []
                st.session_state.documents_loaded = False
                st.success("✅ Knowledge base cleared")
                st.rerun()
        
        st.divider()
        
        # Settings
        st.subheader("⚙️ Settings")
        show_sources = st.checkbox("Show source documents", value=True)
        show_relevance = st.checkbox("Show relevance scores", value=True)
        st.caption("📊 Reranking: Enabled" if st.session_state.rag_engine and st.session_state.rag_engine.use_reranker else "📊 Reranking: Disabled")
        
        st.divider()
        
        # ML Features
        st.subheader("🤖 ML Features")
        ml_tab = st.radio("Select Feature", ["Sentiment Analysis", "Document Classification"], horizontal=True)
    
    # Main content area with tabs
    tab1, tab2 = st.tabs(["💬 RAG Q&A", "🔍 ML Tools"])
    
    with tab1:
        # Main chat interface
        if not st.session_state.documents_loaded and doc_count == 0:
            st.info("👈 Please upload PDF documents to get started!")
        else:
            st.success(f"✅ {doc_count} document chunks loaded and ready!")
        
        # Display chat history
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if message["role"] == "assistant" and "sources" in message and show_sources:
                    with st.expander(f"📄 View {len(message['sources'])} Sources"):
                        for i, source in enumerate(message["sources"], 1):
                            relevance_badge = f" `{source['relevance']:.3f}`" if source.get('relevance') else ""
                            st.markdown(f"**[{i}] {source['name']}**{relevance_badge}")
                            st.caption(f"Type: {source['type']} | Chunk: {source['chunk']}")
                            st.text(f"📝 {source['preview']}")
                            st.divider()        # Chat input
        if question := st.chat_input("Ask a question about your documents..."):
            # Add user message to chat
            st.session_state.chat_history.append({
                "role": "user",
                "content": question
            })
            
            with st.chat_message("user"):
                st.markdown(question)
            
            # Get answer from RAG engine
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    result = st.session_state.rag_engine.query(question)
                    
                    st.markdown(result["answer"])
                    
                    # Prepare sources info with enhanced citations
                    sources_info = []
                    if show_sources and result["source_documents"]:
                        with st.expander(f"📄 View {len(result['source_documents'])} Sources"):
                            for i, doc in enumerate(result["source_documents"], 1):
                                source_name = doc.metadata.get('source', 'Unknown')
                                chunk_id = doc.metadata.get('chunk_id', 'N/A')
                                doc_type = doc.metadata.get('doc_type', 'unknown')
                                rerank_score = doc.metadata.get('rerank_score', None)
                                preview = doc.page_content[:250].replace('\n', ' ').strip() + "..."
                                
                                # Display with relevance score if available
                                relevance_badge = f" `Relevance: {rerank_score:.3f}`" if rerank_score and show_relevance else ""
                                st.markdown(f"**[{i}] {source_name}**{relevance_badge}")
                                st.caption(f"Type: {doc_type} | Chunk: {chunk_id}")
                                st.text(f"📝 {preview}")
                                st.divider()
                                
                                sources_info.append({
                                    "name": source_name,
                                    "chunk": chunk_id,
                                    "type": doc_type,
                                    "preview": preview,
                                    "relevance": rerank_score
                                })
                    
                    # Add assistant response to chat history
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": result["answer"],
                        "sources": sources_info
                    })
        
        # Clear chat button
        if st.session_state.chat_history and st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()
    
    with tab2:
        # ML Tools Interface
        st.header("🤖 Machine Learning Tools")
        
        ml_mode = st.radio("Select Tool", ["📊 Sentiment Analysis", "🏷️ Document Classification"], horizontal=True)
        
        st.divider()
        
        if ml_mode == "📊 Sentiment Analysis":
            st.subheader("Sentiment Analysis")
            st.write("Analyze the emotional tone of text using pre-trained or custom models.")
            
            sentiment_input = st.text_area("Enter text to analyze:", placeholder="Type your text here...", height=150)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔍 Analyze Sentiment", type="primary"):
                    if sentiment_input:
                        with st.spinner("Analyzing sentiment..."):
                            try:
                                result = st.session_state.sentiment_analyzer.analyze(sentiment_input)
                                
                                st.success("✅ Analysis Complete")
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Sentiment", result['sentiment'].upper(), delta=f"{result['confidence']:.2%}")
                                with col2:
                                    st.metric("Positive Score", f"{result['scores']['positive']:.3f}")
                                with col3:
                                    st.metric("Confidence", f"{result['confidence']:.2%}")
                                
                                st.write("**Detailed Scores:**")
                                scores_df = pd.DataFrame([result['scores']])
                                st.dataframe(scores_df, use_container_width=True)
                                
                                # Display as chart
                                chart_data = pd.DataFrame({
                                    'Sentiment': ['Positive', 'Negative', 'Neutral'],
                                    'Score': [
                                        result['scores']['positive'],
                                        result['scores']['negative'],
                                        result['scores']['neutral']
                                    ]
                                })
                                st.bar_chart(chart_data.set_index('Sentiment'))
                                
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
                    else:
                        st.warning("Please enter some text to analyze.")
            
            with col2:
                if st.button("🗑️ Clear"):
                    st.rerun()
            
            # Batch analysis
            st.divider()
            st.subheader("Batch Analysis")
            batch_text = st.text_area("Enter multiple texts (one per line):", placeholder="Text 1\nText 2\nText 3", height=150)
            
            if st.button("📈 Analyze Batch"):
                if batch_text:
                    texts = [t.strip() for t in batch_text.split('\n') if t.strip()]
                    with st.spinner(f"Analyzing {len(texts)} texts..."):
                        try:
                            results = st.session_state.sentiment_analyzer.batch_analyze(texts)
                            
                            st.success(f"✅ Analyzed {len(results)} texts")
                            results_df = pd.DataFrame(results)
                            st.dataframe(results_df, use_container_width=True)
                            
                            # Statistics
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                positive_count = len([r for r in results if r['sentiment'] == 'positive'])
                                st.metric("Positive", positive_count)
                            with col2:
                                negative_count = len([r for r in results if r['sentiment'] == 'negative'])
                                st.metric("Negative", negative_count)
                            with col3:
                                neutral_count = len([r for r in results if r['sentiment'] == 'neutral'])
                                st.metric("Neutral", neutral_count)
                            
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
                else:
                    st.warning("Please enter at least one text.")
        
        else:  # Document Classification
            st.subheader("Document Classification")
            st.write("Classify documents into predefined categories using machine learning.")
            
            # Check if model exists
            if not os.path.exists("models/document_classifier_model.pkl"):
                st.warning("⚠️ Document classifier model not trained yet. Please train the model first.")
                st.info("Run: `python train_document_classifier.py` to train the model.")
            else:
                classification_input = st.text_area("Enter text to classify:", placeholder="Type your document text here...", height=150)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🏷️ Classify Document", type="primary"):
                        if classification_input:
                            with st.spinner("Classifying document..."):
                                try:
                                    result = st.session_state.document_classifier.classify(classification_input)
                                    
                                    st.success("✅ Classification Complete")
                                    
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.metric("Predicted Category", result['category'].upper(), delta=f"{result['confidence']:.2%}")
                                    with col2:
                                        st.metric("Confidence", f"{result['confidence']:.2%}")
                                    
                                    st.write("**Category Probabilities:**")
                                    probs_df = pd.DataFrame({
                                        'Category': list(result['probabilities'].keys()),
                                        'Probability': list(result['probabilities'].values())
                                    }).sort_values('Probability', ascending=False)
                                    st.dataframe(probs_df, use_container_width=True)
                                    
                                    # Display as chart
                                    st.bar_chart(probs_df.set_index('Category'))
                                    
                                except Exception as e:
                                    st.error(f"❌ Error: {str(e)}")
                        else:
                            st.warning("Please enter some text to classify.")
                
                with col2:
                    if st.button("🗑️ Clear"):
                        st.rerun()
                
                # Batch classification
                st.divider()
                st.subheader("Batch Classification")
                batch_classify_text = st.text_area("Enter multiple documents (one per line):", placeholder="Document 1\nDocument 2\nDocument 3", height=150)
                
                if st.button("📊 Classify Batch"):
                    if batch_classify_text:
                        texts = [t.strip() for t in batch_classify_text.split('\n') if t.strip()]
                        with st.spinner(f"Classifying {len(texts)} documents..."):
                            try:
                                results = st.session_state.document_classifier.batch_classify(texts)
                                
                                st.success(f"✅ Classified {len(results)} documents")
                                results_df = pd.DataFrame(results)
                                st.dataframe(results_df, use_container_width=True)
                                
                                # Category distribution
                                category_counts = results_df['category'].value_counts()
                                st.bar_chart(category_counts)
                                
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
                    else:
                        st.warning("Please enter at least one document.")


if __name__ == "__main__":
    main()
