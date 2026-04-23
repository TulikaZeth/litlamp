from google import genai
from google.genai import types
import os
import json
from typing import Literal

_client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
_model_name = 'gemini-2.5-flash'

VALID_CATEGORIES = [
  "legal",
  "health",
  "finance",
  "education",
  "research",
  "hobbies",
  "technology",
  "general",
]

CLASSIFICATION_PROMPT="""You are a document classification assistant.
 
Classify the document excerpt below into EXACTLY ONE of these categories:
legal, health, finance, education, research, hobbies, technology, general
 
Rules:
- legal: contracts, agreements, terms, court documents, compliance, regulations
- health: medical records, prescriptions, health reports, clinical notes
- finance: invoices, bank statements, tax documents, financial reports
- education: textbooks, syllabi, academic papers, study material, certificates
- research: scientific papers, studies, white papers, research reports
- hobbies: recipes, sports, travel, gaming, DIY, personal interests
- technology: software docs, API references, technical manuals, code documentation
- general: anything that doesn't fit the above categories
 
Respond with ONLY this JSON — no markdown, no explanation, no extra text:
{"category": "<one of the 8 categories>", "confidence": "<high|medium|low>", "reason": "<one short sentence>"}
 
Document excerpt:
"""

def classify_document(text: str) -> dict:
  """
  MAIN ENTRY POINT : will be called from the ingest router.
 
    Reads the first 1500 characters of the document text
    and asks Gemini to classify it into a category.
 
    Why only 1500 chars?
      - The category is almost always clear from the beginning
      - Using the full doc wastes tokens and costs more
      - 1500 chars ≈ ~400 tokens — fast and cheap
 
    Returns:
    {
        "category":   "legal",    categories
        "confidence": "high",     how sure Gemini is
        "reason":     "Contains contract clauses and legal terminology"
    }
 
    Never raises an exception — returns "general" as safe fallback.
  """
  
  
  sample = text[:1500].strip()
  
  if not sample:
    return _fallback('Empty document text')
  
  try:
    response = _client.models.generate_content(
      model=_model_name,
      contents=CLASSIFICATION_PROMPT + sample,
      config=types.GenerateContentConfig(
        temperature=0.1,
        response_mime_type="application/json",
      )
    )

    raw = response.text.strip()
    # sometimes gemini wraps JSON in  markdown code fences like :
    # ```json
    # { "category": "legal", "confidence": "high"}
    # ```
    # we strip those just in case, even though we told it not to

    raw = raw.replace("```json", "").replace("```", "").strip()

    result=json.loads(raw)

    # Validating the response
    if result.get('category') not in VALID_CATEGORIES:
      result['category'] = 'general'
      result['confidence'] = 'low'

    return result
  except json.JSONDecodeError:
    return _fallback('Invalid JSON response from LLM')

  except Exception as e:
    # maybe network error, timeout, or something else went wrong with the API call
    return _fallback(f'LLM error: {str(e)}')
    return _fallback('Unexpected error occurred')
  
  
def _fallback(reason: str) -> dict:
  print(f"Classifier fallback: {reason}")
  return {
        "category":   "general",
        "confidence": "low",
        "reason":     reason,
    }
  
CATEGORY_PERSONAS = {
  "legal": (
        "You are an expert legal document analyst with deep knowledge of "
        "contracts, agreements, and legal terminology. Be precise. Always "
        "clarify that your analysis is informational and not legal advice."
    ),
    "health": (
        "You are a knowledgeable medical document assistant. Interpret "
        "clinical language accurately. Always recommend the user consult "
        "a qualified healthcare professional for medical decisions."
    ),
    "finance": (
        "You are a financial document analyst. Be exact with numbers, "
        "dates, and monetary values. Note that this is informational "
        "analysis, not financial advice."
    ),
    "education": (
        "You are an educational content expert. Explain concepts clearly "
        "and accessibly. Use examples where helpful. Adapt your tone to "
        "be encouraging and clear."
    ),
    "research": (
        "You are a research paper analyst. Maintain academic precision. "
        "Reference specific sections and findings accurately. Distinguish "
        "between the paper's claims and established fact."
    ),
    "hobbies": (
        "You are a helpful and enthusiastic assistant for hobbyist content. "
        "Be practical, friendly, and specific. Focus on actionable information."
    ),
    "technology": (
        "You are a technical documentation expert. Be precise with "
        "terminology. Explain technical concepts clearly. Reference "
        "specific sections, versions, or specifications when relevant."
    ),
    "general": (
        "You are a helpful document assistant. Answer questions accurately "
        "and concisely based on the document content provided."
    ),
}
