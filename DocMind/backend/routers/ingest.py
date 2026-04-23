from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from datetime import datetime, timezone
import uuid
import os

from models.schemas import IngestResponse
from services.parser import parse_document
from services.chunker import chunk_text
from services.embedder import embed_texts
from services.classifier import classify_document
from services.vector_store import upsert_chunks
from services.firebase_store import upload_file, save_doc_record


# Router
router = APIRouter(
  prefix="/ingest",
  tags=['ingest']
)

# Constants
MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20MB limit
ALLOWED_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.txt', '.md'}

# POST
@router.post("/", response_model=IngestResponse)
async def ingest_document(file: UploadFile = File(...)):
  """
    Full document ingestion pipeline.
    Accepts a file upload and returns metadata about what was processed.
 
    Supported formats: PDF, JPG, PNG, WEBP, TXT, MD
    Max file size: 20MB
  """
  # ── STEP 1: Validate the file
  
  ext = os.path.splitext(file.filename)[1].lower()
  
  if ext not in ALLOWED_EXTENSIONS:
    # HTTPException automatically return the right HTTP status code
    # 400 = Bad Request -> Client sent something wrong
    raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")
  
    # await is needed because reading the file is an async operation
  file_bytes = await file.read()
  
  if len(file_bytes) > MAX_FILE_SIZE_BYTES:
    # 413 = Payload Too Large -> Client sent a file that's too big
    raise HTTPException(status_code=413, detail="File size exceeds 20MB limit.")
  
  if len(file_bytes) == 0:
    raise HTTPException(status_code=400, detail="Uploaded file is empty.")
  
  # generating the unique ID for this document, every other step refernnce this ID
  
  doc_id = str(uuid.uuid4())
  
  print(f"\n{'='*50}")
  print(f"Ingesting: {file.filename} ({len(file_bytes)/1024:.1f}KB)")
  print(f"Doc ID: {doc_id}")
  
  
  # Parsing : extracting the text from file, pdf, handles OCR and plain text decoding.
  
  try:
    text, page_count, is_image_doc = parse_document(file_bytes, file.filename)
  except ValueError as e:
    raise HTTPException(status_code=400, detail=str(e))
  except Exception as e:
    print(f"Error during parsing: {e}")
    raise HTTPException(status_code=500, detail=f"failed to parse document: {str(e)}")
  
  if not text.strip():
    raise HTTPException(status_code=400, detail="No text could be extracted from the document...If its a scanned image, ensure its clear and readable.")
  
  print(f"Parsed: {page_count} page(s) | Image doc: {is_image_doc} | Text length: {len(text)} chars")
  
  # now we Classify the type of doc
  classification = classify_document(text)
  category = classification['category']
  confidence = classification['confidence']
  
  print(f"Classified: {category} (confidence: {confidence})")
  
  # now chunk and embed
  chunk_count = 0
  if not is_image_doc:
    chunks = chunk_text(
      text=text,
      doc_id=doc_id,
      filename=file.filename,
    )
    print(f"Chunked: {len(chunks)} chunks")
    
    chunk_texts = [c['text'] for c in chunks]
    embeddings = embed_texts(chunk_texts)
    print(f"Embedded: {len(embeddings)} vectors (each {len(embeddings[0])} dims)")
    
    
    # saving to db
    chunk_count = upsert_chunks(chunks, embeddings)
    print(f"Saved to vector store: {chunk_count} chunks")
  else:
    print("Skipping chunking and embedding for image-based document.")
    
  # Upload the original file to Cloudinary and get the URL
  try:
    storage_url = upload_file(file_bytes=file_bytes,filename=file.filename, doc_id = doc_id)
    print(f"Uploaded file to Cloudinary: {storage_url[:60]}...")
    
    # Save a record in Firestore with all the metadata
    
    record = {
      'doc_id': doc_id,
      'filename' : file.filename,
      'category': category,
      'category_confidence': confidence,
      'chunk_count': chunk_count,
      'page_count': page_count,
      'is_image_doc': is_image_doc,
      'storage_url': storage_url,
      'uploaded_at': datetime.now(timezone.utc).isoformat(),
    }
    
    save_doc_record(record)
    print("Saved document record to Firestore ✓")
    print(f"{'='*50}\n")
    
    # Return response to frontend
    return IngestResponse(
      **record,
      message=(
        f"Document ingested successfully: {file.filename} | "
        f"Category: {category} (confidence: {confidence}) | "
        f"Chunks created: {chunk_count}"
      )
    )
  except Exception as e:
    print(f"Error during file upload: {e}")
    raise HTTPException(status_code=500, detail=f"failed to upload file: {str(e)}")
  
  
  