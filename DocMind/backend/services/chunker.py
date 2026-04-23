from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List
import os
import re


# CHUNK_SIZE: max characters per chunk
#   → ~512 tokens ≈ ~2000 characters (1 token ≈ 4 chars in English)
#   → Too large: less precise retrieval
#   → Too small: chunks lose context, answers feel incomplete
#   → 2000 chars is a proven sweet spot for most documents
#
# CHUNK_OVERLAP: how many characters the next chunk re-uses from the previous
#   → 200 chars = ~50 tokens of overlap
#   → Prevents meaning from being cut at boundaries
#   → Think of it as a "sliding window"



CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', 2000))
CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', 200))

def chunk_text(text: str, doc_id: str, filename: str) -> List[dict]:
  """
  MAINT ENTRY POINT : will be called from the ingest router.
  
  takes the full extracted text from the parser...
  """
  
  # Fetch from OS matching your .env file
  current_chunk_size = int(os.getenv('CHUNK_SIZE', 2000))
  current_chunk_overlap = int(os.getenv('CHUNK_OVERLAP', 200))

  splitter = RecursiveCharacterTextSplitter(
    chunk_size = current_chunk_size,
    chunk_overlap = current_chunk_overlap,
    separators=["\n\n", "\n", ". ", " ", ""]
  )
  
  # split_text returns a plain list of strings
  raw_chunks : List[str] = splitter.split_text(text)
  chunks = []
  
  for index, chunk_text_content in enumerate(raw_chunks):
    # Each chunk might contain a [Page N] marker we injected in the parser.
    # We extract it so we can tell the user exactly where the answer came from.
    
    page = _extract_page_number(chunk_text_content)
    
    chunks.append({
      'text' : chunk_text_content.strip(),
      'doc_id' : doc_id,
      'filename' : filename,
      'chunk_index' : index,
      'page' : page,
    })
    
  return chunks
  
  
def _extract_page_number(text: str) -> int | None:
  """
    Looks for the [Page N] or [Page N - OCR] markers we added in parser.py.
 
    re.search scans through the string looking for the pattern.
    r"\[Page (\d+)" means:
        \[      → literal [
        Page    → literal "Page "
        (\d+)   → capture one or more digits (the page number)
 
    If found, returns the page number as an int.
    If not found, returns None.
    """
    
  match = re.search(r"\[Page (\d+)", text)
  if match:
    return int(match.group(1))
  return None


# Multiple Doc
# When the user uploads multiple documents and asks a question
# across ALL of them, we search the entire Qdrant collection.
# The doc_id and filename stored in each chunk tells us which
# document each result came from, so we can show the user:
# "This part came from contract.pdf, this part from policy.pdf"

def chunk_multiple_docs(docs: List[dict]) -> List[dict]:
  """
    Convenience wrapper for chunking multiple documents at once.
 
    Each item in `docs` should be:
    {
        "text": str,
        "doc_id": str,
        "filename": str
    }
 
    Returns a flat list of ALL chunks across all documents.
    The doc_id in each chunk tells them apart.
    """
  
  all_chunks = []
  for doc in docs:
    doc_chunks = chunk_text(
      text=doc['text'],
      doc_id=doc['doc_id'],
      filename=doc['filename'],
     )
    all_chunks.extend(doc_chunks)
    
  return all_chunks
     
     
