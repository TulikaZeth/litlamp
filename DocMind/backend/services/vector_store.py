from qdrant_client import QdrantClient
from qdrant_client.models import (
  Distance,
  VectorParams,
  PointStruct,
  Filter,
  FieldCondition,
  MatchValue
)

import os
import uuid 
from typing import List, Optional


QDRANT_URL = os.getenv('QDRANT_URL')
QDRANT_API_KEY = os.getenv('QDRANT_API_KEY')
COLLECTION = os.getenv('QDRANT_COLLECTION', 'docmind_chunks')

VECTOR_DIM = 384

TOP_K = int(os.getenv('TOP_K', 5))

_client: QdrantClient | None = None

import time

def get_client() -> QdrantClient:
  """
  Returns the Qdrant client, creating it if needed.
  Also ensures our collection exists (created it if not).
  Includes a retry mechanism for sporadic DNS errors.
  """
  global _client
  if _client is None:
    _client = QdrantClient(
      url=QDRANT_URL,
      api_key=QDRANT_API_KEY
    )
    
    # Retry mechanism for sporadic getaddrinfo errors
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Check if collection exists, if not create it
            _ensure_collection(_client)
            break
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Qdrant connection failed, retrying in 2s (Attempt {attempt+1}/{max_retries})...")
                time.sleep(2)
            else:
                raise e
      
  return _client

def _ensure_collection(client:QdrantClient):
  """
  Will create the collection if it doesn't exist.
  
  VectorParams tells Qdrant:
      - size: how many dimensions each vector has (384)
      - distance: how to measure similarity (COSINE)
 
    COSINE similarity is perfect for normalised embeddings.
    It measures the angle between two vectors, not their length.
    Score of 1.0 = identical meaning, 0.0 = completely unrelated.
  """
  
  exitsing_collections = [
    c.name for c in client.get_collections().collections
  ]
  
  if COLLECTION not in exitsing_collections:
    client.recreate_collection(
      collection_name=COLLECTION,
      vectors_config=VectorParams(size=VECTOR_DIM, distance=Distance.COSINE)
    )
    print(f"Created Qdrant collection: '{COLLECTION}'✓")
  else:
    print(f"Qdrant collection '{COLLECTION}' already exists✓")
    

# stroing the chunks in Qdrant

def upsert_chunks(chunks: List[dict], embeddings: List[List[float]]) -> int:
  """
  it stores chunk vectors + metadata in Qdrant.
  Upsert = update + insert.
  if a point with the same ID exists, it updates it. If not, it creates a new one.
  
  Args: 
   chunks : list of chunk dicts from chunker.py
     each has : text, doc_id, filename, chunk_index, page
    embeddings : list of vectors from embedder.py
                embeddings[i] corresponds to chunks[i]
  Returns:
    the number of points stored
  
  """
  
  client = get_client()
  
  points = []
  
  # zip() pairs each chunk with its corresponding vector
  for chunk, vector in zip(chunks, embeddings):
    points.append(
            PointStruct(
                # random uuid
                id=str(uuid.uuid4()),
 
                # The actual vector — 384 floats
                vector=vector,
 
                # Payload = metadata stored alongside the vector
                # When Qdrant returns this point in a search,
                # we get this payload back so we can show the user
                # the actual text and where it came from
                payload={
                    "text":        chunk["text"],
                    "doc_id":      chunk["doc_id"],
                    "filename":    chunk["filename"],
                    "chunk_index": chunk["chunk_index"],
                    "page":        chunk.get("page"),  # .get() = None if missing
                },
            )
        )
  # upsert sends all points in one batch ,faster than one by one
  client.upsert(
    collection_name=COLLECTION,
    points=points
  )
  return len(points)


def search_chunks(
  query_vector: List[float],
  doc_id: Optional[str] = None ,# if None , search all docs. Otherwise, only these doc_ids (comma separated)
  doc_ids : Optional[List[str]] = None, # alternative to doc_id, as a list
  top_k : int = TOP_K,
) -> List[dict]:
  """
  Semantic search - finds the most relevant chunks to the query vector.
  
  returs list of dicts:
   
   [
     {
       "text": "Payment is due in 30 days",
       "doc_id": "abc-123",
       "filename": "contract.pdf",
       "page": 2,
       "score": 0.94
     }
   ]
  """
  
  _client = get_client()
  
  query_filter = None
  
  if doc_id:
    # single document - filter to only chunks this doc
    query_filter = Filter(
      must=[
        FieldCondition(
          key="doc_id",
          match=MatchValue(value=doc_id)
        )
      ]
    )
  elif doc_ids and len(doc_ids) > 0:
    # multiple docs - filter to chunks from any of these docs
    # We use "should" (OR logic) match any of the doc_ids
    query_filter = Filter(
      should=[
        FieldCondition(
          key="doc_id",
          match=MatchValue(value=d_id)
        ) for d_id in doc_ids
      ],
    )
    
    query_filter.min_should_match = 1 # at least one of the doc_ids should match
    
  # run the search
  response = _client.query_points(
    collection_name = COLLECTION,
    query = query_vector,
    query_filter = query_filter,
    limit = top_k,
    with_payload = True # we want the metadata back with the results
  )
  
  return [
    {
      'text' : r.payload['text'],
      'doc_id' : r.payload['doc_id'],
      'filename' : r.payload['filename'],
      'page' : r.payload.get('page'),
      'score' : round(r.score, 4) # round score to 4 decimals
    }
    for r in response.points
  ]
  
def delete_doc_chunks(doc_id: str) -> str:
  
  """
  Removes all chunks belonging to a specific document from Qdrant.
  Called when a user deletes a document
  
  we filter by doc_id in the payload and delete all matching points.
  """
  
  client = get_client()
  
  client.delete(
    collection_name=COLLECTION,
    points_selector=Filter(
      
      must=[
        FieldCondition(
          key="doc_id",
          match=MatchValue(value=doc_id)
        )
      ]
    )
  )
  print(f"Deleted chunks with doc_id '{doc_id}' from Qdrant✓")

def get_collection_info() -> dict:
  """
  Returns stats about the collection,
  Useful for the / health endpoints to confirm Qdrant is connected
  """
  client = get_client()
  info = client.get_collection(collection_name=COLLECTION)
  return {
    'points_count': info.points_count,
    'indexed_vectors_count': info.indexed_vectors_count,
    'status' : str(info.status)
  }