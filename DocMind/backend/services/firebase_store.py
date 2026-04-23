import firebase_admin
from firebase_admin import credentials, firestore
import cloudinary
import cloudinary.uploader
import os
import json
from typing import Optional, List



_firebase_initialised = False


def _init_firebase():
    """
    Initialises Firebase Admin SDK (Firestore only — no Storage).
    Safe to call multiple times — only runs setup once.
    """
    global _firebase_initialised

    if _firebase_initialised:
        return

    # Try loading from JSON string (convenient for platforms like Render/Heroku)
    cred_json_str = os.getenv("FIREBASE_CREDENTIALS_JSON")
    if cred_json_str:
        cred_dict = json.loads(cred_json_str)
        cred = credentials.Certificate(cred_dict)
    else:
        # Fallback to local file path
        cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "./firebase_credentials.json")
        cred = credentials.Certificate(cred_path)

    # Notice: no storageBucket here — we're not using Firebase Storage
    firebase_admin.initialize_app(cred)

    _firebase_initialised = True
    print("Firebase (Firestore) initialised ✓")


def _init_cloudinary():
    """
    Configures Cloudinary SDK with credentials from .env.
    Cloudinary doesn't have a separate initialise step —
    just setting the config is enough.
    """
    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET"),
        secure=True,  # always use HTTPS URLs
    )
    print("Cloudinary initialised ✓")


# FILE STORAGE — Cloudinary
#
# Cloudinary is built for media files (images, PDFs, videos).
# Free tier: 25GB storage + 25GB bandwidth/month
# Files are stored with a public URL — Flutter uses this to
# show document previews.

def upload_file(file_bytes: bytes, filename: str, doc_id: str) -> str:
    """
    Uploads the original document to Cloudinary.

    Files are stored under the folder: docmind/{doc_id}/
    e.g. docmind/abc-123/contract

    Returns the secure HTTPS URL to access the file.
    Flutter uses this URL to preview or download the document.

    Args:
        file_bytes: raw bytes of the uploaded file
        filename:   original filename e.g. "contract.pdf"
        doc_id:     unique ID for this document (used as folder)
    """
    _init_cloudinary()

    import io

    ext = os.path.splitext(filename)[1].lower()

    # Cloudinary needs to know the resource type:
    #   "image" → jpg, png, webp, gif
    #   "raw"   → pdf, txt, md (anything that's not an image or video)
    resource_type = "image" if ext in (".jpg", ".jpeg", ".png", ".webp") else "raw"

    # public_id is the file's name inside Cloudinary (without extension)
    # We use doc_id as the folder so files are organised per document
    public_id = f"docmind/{doc_id}/{os.path.splitext(filename)[0]}"

    # Upload from bytes — wrap in BytesIO so Cloudinary can read it
    result = cloudinary.uploader.upload(
        io.BytesIO(file_bytes),
        public_id=public_id,
        resource_type=resource_type,
        # overwrite=True means re-uploading the same doc_id replaces the file
        overwrite=True,
        # Tell Cloudinary the original filename for display purposes
        original_filename=filename,
    )

    # result["secure_url"] is the HTTPS URL to the uploaded file
    return result["secure_url"]


def delete_file(doc_id: str, filename: str):
    """
    Deletes a file from Cloudinary when a document is deleted.
    """
    _init_cloudinary()

    ext = os.path.splitext(filename)[1].lower()
    resource_type = "image" if ext in (".jpg", ".jpeg", ".png", ".webp") else "raw"
    public_id = f"docmind/{doc_id}/{os.path.splitext(filename)[0]}"

    cloudinary.uploader.destroy(public_id, resource_type=resource_type)


#
# Firestore is a NoSQL document database (free tier is generous).
# Structure:
#
#   documents/              ← Firestore collection
#     {doc_id}              ← one record per uploaded file
#       doc_id, filename, category, chunk_count, ...
#
# Think of a Firestore "collection" like a SQL table.
# A Firestore "document" is one row in that table.
# Fields inside are like columns — but flexible, no fixed schema.

def save_doc_record(record: dict):
    """
    Saves document metadata to Firestore after successful ingestion.

    Called once per document. The record dict should match
    the DocRecord schema from schemas.py.

    Firestore path: documents/{doc_id}
    """
    _init_firebase()
    db = firestore.client()

    # .collection("documents") → select the collection
    # .document(record["doc_id"]) → select (or create) a specific document
    # .set(record) → write the entire dict as fields
    db.collection("documents").document(record["doc_id"]).set(record)


def get_doc_record(doc_id: str) -> Optional[dict]:
    """
    Fetches one document record by its ID.
    Returns None if not found.

    Used by the query router to get the doc's category
    so we can inject the right persona into the LLM prompt.
    """
    _init_firebase()
    db = firestore.client()

    doc = db.collection("documents").document(doc_id).get()

    # .exists tells you whether the document was found
    # .to_dict() converts the Firestore document to a plain Python dict
    return doc.to_dict() if doc.exists else None


def list_doc_records() -> List[dict]:
    """
    Returns all document records, newest first.
    Used by the /history/docs endpoint to show the document list in Flutter.
    """
    _init_firebase()
    db = firestore.client()

    # .order_by + DESCENDING = newest uploads appear first
    docs = (
        db.collection("documents")
        .order_by("uploaded_at", direction=firestore.Query.DESCENDING)
        .stream()  # .stream() returns a lazy iterator — efficient for large lists
    )

    # Convert each Firestore document to a plain dict
    return [d.to_dict() for d in docs]


def delete_doc_record(doc_id: str):
    """
    Deletes a document record from Firestore.
    Called together with delete_doc_chunks() and delete_file()
    when the user removes a document.
    """
    _init_firebase()
    db = firestore.client()
    db.collection("documents").document(doc_id).delete()


# FIRESTORE — sessions collection

#
#   sessions/               ← Firestore collection
#     {session_id}          ← one record per chat session
#       session_id
#       doc_id              ← single doc (None for multi-doc)
#       doc_ids             ← list of doc IDs (multi-doc sessions)
#       messages            ← full conversation history
#       created_at

def save_session(session: dict):
    """
    Saves or updates a chat session.

    Flutter calls this after every message to keep the session
    in sync — so if the user closes the app and reopens it,
    the conversation is still there.
    """
    _init_firebase()
    db = firestore.client()
    db.collection("sessions").document(session["session_id"]).set(session)


def get_session(session_id: str) -> Optional[dict]:
    """Fetches one session by ID. Returns None if not found."""
    _init_firebase()
    db = firestore.client()
    doc = db.collection("sessions").document(session_id).get()
    return doc.to_dict() if doc.exists else None


def list_sessions(doc_id: Optional[str] = None) -> List[dict]:
    """
    Returns all sessions, newest first.
    If doc_id is provided, returns only sessions for that document.

    Used by Flutter to show chat history per document.
    """
    _init_firebase()
    db = firestore.client()

    ref = db.collection("sessions")

    if doc_id:
        # .where() = filter by a field value
        # Only return sessions that belong to this specific document
        ref = ref.where("doc_id", "==", doc_id)

    docs = (
        ref.order_by("created_at", direction=firestore.Query.DESCENDING)
        .stream()
    )

    return [d.to_dict() for d in docs]


def delete_sessions_for_doc(doc_id: str):
    """
    Deletes all sessions associated with a document.
    Called when the user deletes a document — clean up everything.
    """
    _init_firebase()
    db = firestore.client()

    sessions = (
        db.collection("sessions")
        .where("doc_id", "==", doc_id)
        .stream()
    )

    # Firestore doesn't have bulk delete — we delete one by one
    for session in sessions:
        session.reference.delete()