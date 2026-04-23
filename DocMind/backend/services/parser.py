import fitz
import pytesseract

# Configure Tesseract path for Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

from PIL import Image
import io
import os
from typing import Tuple



# This file contains functions to parse documents, extract text, and handle OCR for image-based PDFs.
# We return is_image_doc so the pipeline knows : 
# False : chunk the text -> embed -> store in quadrant 
# True : send img directly to Gemini Vision (no chunking needed)


def extract_text_from_pdf(file_bytes: bytes) -> Tuple[str, int, bool]:
  """"
  Opens a PDF and extracts text page by page.
  
  for each page:
  -> If there is a text layer : grab it
  -> If there is no text layer : render the page as an image ->  run OCR
  
  returns (full_text, page_count, is_image_doc)
  
  """
  
  
  # filetype = tells it what format
  doc = fitz.open(stream=file_bytes, filetype='pdf')
  page_count = len(doc)
  
  full_text = ''
  image_page_count = 0 # keeps track of how many pages had no text layer
  
  for page in doc:
    # page.get_text() extracts the text layer
    text = page.get_text().strip()
    
    if text:
      full_text += f"\n[Page {page.number + 1}]\n{text}"
    
    else:
      # No text layer
      image_page_count += 1
    # get_pixmap renders the page as an image at 200 DPI
    # higher DPI, better OCR but slower, so 200 is good.
    
      pix = page.get_pixmap(dpi=200)
      
      # convert to PNG bytes , then open with Pillow
      # pytesseract needs a Pillow image object
      img_bytes = pix.tobytes('png')
      img = Image.open(io.BytesIO(img_bytes))
      
      # Run OCR, takes 1-3 seconds per page
      ocr_text = pytesseract.image_to_string(img).strip()
      
      if ocr_text:
        full_text += f"\n[Page {page.number + 1} - OCR]\n{ocr_text}"  
  
  doc.close()
    
  # is_image_doc is True ONLy when Every page needed OCR
    # If even one page had a text layer, its a mixed / text pdf
    
  is_image_doc = (image_page_count == page_count)
  return full_text.strip(), page_count, is_image_doc

def extract_text_from_image(file_bytes : bytes) -> Tuple[str, int, bool]:
  
  """
  For plain Image files (jpg, png, webp, etx).
  
  Instead of chunking this, we'll send it straight to Gemini Vision. But we still exract the text here so the classifier can categorize it.
  
  
  
  Returns (text, page_count, is_image_doc=True)
  
  """
  
  img = Image.open(io.BytesIO(file_bytes))
  text = pytesseract.image_to_string(img).strip()
  
  
  # page_count = 1 
  # is_image_doc is always true in case of plain imagers
  return text, 1, True

def extract_from_text(file_bytes : bytes) -> Tuple[str, int, bool]:
  """
  For plain text files, just decode the bytes and return.
  
  errors = "replace" means if there are any characters that can't be decoded, replace them with a placeholder instead of throwing an error.
  """
  
  text = file_bytes.decode('utf-8', errors='replace').strip()
  
  page_count = max(1, text.count("\x0c") + 1)
  return text, page_count, False
  
  
def parse_document(file_bytes: bytes, filename: str) -> Tuple[str, int, bool]:
  """"
  MAIN ENRY POINT -> called from the ingest router
  
  Looks at the file extension and routes to the right extracter .
  
  Raises value error if the file type is not supported.
  """
  
  # os.path.splitext("report.pdf") -> ("repost" , ".pdf")
  
  ext = os.path.splitext(filename)[1].lower()
  
  if(ext == '.pdf'):
    return extract_text_from_pdf(file_bytes)
  
  elif ext in (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"):
        return extract_text_from_image(file_bytes)
  
  elif ext in (".txt", ".md"):
        return extract_from_text(file_bytes)
      
      
  else:
        raise ValueError(
            f"Unsupported file type: '{ext}'. "
            f"Allowed: .pdf, .jpg, .jpeg, .png, .webp, .txt, .md"
        )
      
 