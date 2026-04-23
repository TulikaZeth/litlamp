from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class DocCategory(str, Enum):
    legal      = "legal"
    health     = "health"
    finance    = "finance"
    education  = "education"
    research   = "research"
    hobbies    = "hobbies"
    technology = "technology"
    general    = "general"
    
# Ingest Schemas 

class IngestResponse(BaseModel):
    """
    What the backend send back AFTER successfully ingesting a document. Flutter read this to show the user what happend.
    """
    
    doc_id : str
    filename : str
    category : DocCategory
    category_confidence : str
    chunk_count : int
    page_count : int
    is_image_doc : bool
    storage_url : str
    message : str
    
    
    
# Query Schemas
class QueryRequest(BaseModel):
    """
    
    What flutter sends to the backend when the user asks a question.
    
    """
    question : str = Field(..., min_length=1, max_length=2000)
    
    # doc_id is Optional - if None, we search across ALL docs, and if provided, we only search within that specific document
    doc_id : Optional[str] = None
    
    # the last few messages so the LLM remebers context
    # eg. : [{'role' : 'user', 'content' : '...'}]
    
    conversation_history: Optional[List[dict]] = []
    
class SourceChunk(BaseModel):
  """
  A single passage retrieved from Quadrant that was used to answer the question. Flutter show these as tappable source chips below the anser.
  
  """
  
  text: str
  page : Optional[int] = None
  score : float
  doc_id : str
  filename : str
  
class QueryResponse(BaseModel):
  """
  What backend sends back after answering a question.
  """
  
  answer: str # llms response
  sources : List[SourceChunk]
  doc_category : Optional[DocCategory]
  model_used : str
  
  
# History Schemas
class DocRecord(BaseModel):
  """
  Stored in firestore for every ingested document. Flutter uses this to display the document list.
  """
  
  doc_id: str
  filename: str
  category: DocCategory
  category_confidence: str
  chunk_count: int
  page_count: int
  is_image_doc: bool
  storage_url: str
  uploaded_at: str   
  
  
class ChatMessage(BaseModel):
    """
    A single message in a conversation (either user or assistant).
    """
    role: str                               # "user" or "assistant"
    content: str
    sources: Optional[List[SourceChunk]] = []
    timestamp: str
  
class SessionRecord(BaseModel):
  """
  A full conversation session, a list of messages ties to one or more documents.
  """
  
  session_id : str
  doc_id : Optional[str] = None # None = multi doc session
  doc_ids : Optional[List[str]] = None # for multi doc sessions
  messages : List[ChatMessage]
  createdAt : str
  

# System Schemas
class HealthResponse(BaseModel):
    
    status : str  # ok or degraded
    version : str
    services : dict # e.g. {'gemini' : 'ok', 'quadrant' : 'MISSING'}
  
  
    
