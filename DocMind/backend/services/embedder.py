from sentence_transformers import SentenceTransformer
from typing import List
 
 


# We load the model ONCE when the server starts.
# Loading takes ~3 seconds the first time (downloads ~80MB).
# After that it lives in memory and each embedding takes ~80ms.
#
# _model starts as None and gets set the first time get_model() is called.
# This pattern is called "lazy loading" — we don't load until we need it.

 
_model: SentenceTransformer | None = None
 
 
def get_model() -> SentenceTransformer:
    """
    Returns the embedding model, loading it if not already loaded.
    All other functions call this — never access _model directly.
    """
    global _model
 
    if _model is None:
        print("Loading embedding model — this takes ~3s on first load...")
 
        # This downloads the model from HuggingFace on first run.
        # After that it's cached locally in ~/.cache/huggingface/
        _model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
 
        print("Embedding model ready ✓")
 
    return _model
 
 
def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Converts a LIST of strings into a list of vectors.
    Use this when embedding chunks during ingestion.
 
    Example:
        texts = ["Payment is due in 30 days", "The contract is valid for 1 year"]
        vectors = embed_texts(texts)
        # vectors[0] is the vector for the first text
        # vectors[1] is the vector for the second text
        # each vector is a list of 384 floats
 
    Why batch? Sending 50 texts at once is much faster than
    sending them one by one. The model processes them in parallel.
    batch_size=32 means process 32 at a time.
    """
    model = get_model()
 
    embeddings = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=False,
 
        # normalize_embeddings=True is IMPORTANT.
        # It makes every vector exactly length 1 (unit vector).
        # This means we can measure similarity with a simple dot product
        # instead of the more expensive cosine similarity formula.
        # Qdrant uses this when Distance.COSINE is set.
        normalize_embeddings=True,
    )
 
    # model.encode returns a numpy array.
    # We convert to a plain Python list of lists because:
    # 1. JSON serialisation needs plain Python types
    # 2. Qdrant client expects plain lists
    return embeddings.tolist()
 
 
def embed_query(text: str) -> List[float]:
    """
    Converts a SINGLE string into a vector.
    Use this when embedding the user's question at query time.
 
    This is separate from embed_texts for clarity —
    during querying we always have exactly one string (the question).
    """
    # embed_texts handles a list, so we wrap in a list and take [0]
    return embed_texts([text])[0]