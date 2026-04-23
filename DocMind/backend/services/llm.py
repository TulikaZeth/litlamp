from google import genai
from google.genai import types
import os
from typing import List, AsyncGenerator

from typer import prompt
from services.classifier import CATEGORY_PERSONAS

_client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
_model_name = 'gemini-2.5-flash'


def build_prompt(
  question: str,
  chunks: List[dict],
  category :str='general',
  conversation_history: List[dict] = None,
) -> str:
   """
   Builds the full prompt to send to Gemini.
 
   Args:
   question:             the user's question
   chunks:               list of retrieved chunks from Qdrant
                              each has: text, filename, page, score, doc_id
   category:             doc category from classifier ("legal", "health" etc)
   conversation_history: list of past messages
                              [{"role": "user", "content": "..."},
                               {"role": "assistant", "content": "..."}]
 
   Returns:
    A single string — the complete prompt ready to send to Gemini
   """
  # PERSONA
   persona = CATEGORY_PERSONAS.get(category, CATEGORY_PERSONAS['general']) 
   
   # CONTEXT
   
   # Format each retrieved chunk as a labelled source block.
    # We number them (Source 1, Source 2...) so the LLM can reference
    # them by number in its answer: "According to Source 2..."
   context_blocks= []
   for i, chunk in enumerate(chunks, start=1):
      page_info = f" Page {chunk['page']}" if chunk.get('page') else ""
      relevance = f"{chunk['score']:.0%}" 
      header = f"[Source {i} — {chunk['filename']}{page_info} — {relevance} match]"
      block  = f"{header}\n{chunk['text']}"
      context_blocks.append(block)
   context = "\n\n---\n\n".join(context_blocks)
   
   
   # COnversation memory : will include last 6 msgs
   
   history_text = ""
   if conversation_history:
     recent = conversation_history[-6:]
     lines=[]
     for msg in recent:
       role = 'User' if msg['role'] == 'user' else 'Assistant'
       lines.append(f"{role}: {msg['content']}")
     history_text = "\n".join(lines) + '\n\n'
  
   # FINAL PROMPT
   prompt = f"""{persona}
 
════════════════════════════════════════
DOCUMENT CONTEXT
The following passages were retrieved from the document(s) and are
the ONLY source of truth for your answer. Do not use outside knowledge.
════════════════════════════════════════
 
{context}
 
════════════════════════════════════════
{history_text}USER QUESTION: {question}
════════════════════════════════════════
 
INSTRUCTIONS:
- Answer ONLY using the document context above.
- If the answer is not in the context, say: "I could not find information about this in the document."
- Reference sources by number when quoting (e.g. "According to Source 2...").
- For multi-document answers, always name which document each point came from.
- Be concise and direct. Do not repeat the question.
- Use markdown formatting for clarity (bullet points, bold for key terms).
"""
   return prompt
   
# Regular Answers (Non Streaming)

def answer_question(
  question: str,
  chunks: List[dict],
  category: str = 'general',
  conversation_history: List[dict] = [],
) -> str:
  prompt = build_prompt(question, chunks, category, conversation_history)
  
  response = _client.models.generate_content(
    model=_model_name,
    contents=prompt,
    config=types.GenerateContentConfig(
      temperature=0.1,
      response_mime_type="application/json",
      max_output_tokens=1024
    )
  )
  return response.text.strip()

# Streaming Answers

#this will be used by flutter, instead of waiting for full answers, GEmini sends token one by one as they are generated, We send each token to flutter via Server Sent Events (SSE)

# AsyncGenerator means this is an async function that yields values one at a time instead of returning all at once. Flutter reads these these yields as they arrive


async def stream_answer(
  question: str,
  chunks: List[dict],
  category: str = 'general',
  conversation_history: List[dict] = None,
) -> AsyncGenerator[str, None]:
  
  if conversation_history is None:
      conversation_history = []
      
  prompt = build_prompt(
    question, chunks, category, conversation_history
  )
  
  # Make the streaming API call using the async client
  response_stream = await _client.aio.models.generate_content_stream(
    model=_model_name,
    contents=prompt,
    config=types.GenerateContentConfig(
      temperature=0.1,
      response_mime_type="application/json",
      max_output_tokens=1024,
    )
  )
  
  async for pieces in response_stream:
    if pieces.text:
      yield pieces.text
  
  
# Image doc answer
def answer_image_doc(
  question: str,
  image_bytes: bytes,
  category: str = 'general',
) -> str:
  """
    For image documents — send the image directly to Gemini Vision.
 
    Gemini receives both the image and the question simultaneously.
    No chunking, no vector search — Gemini reads the image itself.
    
  """
  import PIL.Image
  import io
  
  persona = CATEGORY_PERSONAS.get(category, CATEGORY_PERSONAS['general'])
  
  # open image as PIL image, gemini accepts the PIL images
  img = PIL.Image.open(io.BytesIO(image_bytes))
  
  prompt = (
    f"{persona}\n\n"
        f"The user has uploaded an image document. "
        f"Read all text and visual content in the image carefully.\n\n"
        f"Answer this question based ONLY on what you can see in the image:\n\n"
        f"{question}\n\n"
        f"If the answer is not visible in the image, say so clearly."
  )
  
  response = _client.models.generate_content([prompt, img], model=_model_name)
  
  return response.text.strip()
  
   
     
    