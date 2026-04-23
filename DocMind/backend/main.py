import os
from dotenv import load_dotenv
load_dotenv()

from models.schemas import HealthResponse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import ingest

app = FastAPI(
  title = 'DocMind API',
  description = 'RAG-powered document intelligence backend',
  version = os.getenv('API_VERSION', '1.0.0')
  
)



# CORS = Cross-Origin Resource Sharing
# Wwithout this, you flutter app cannot talk to this backkend because browsers block requests to different domains

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # In production, replace * with your app's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest.router)

# Routes
@app.get('/')
def root():
    # fastAPI automatically convets the dict to JSON
    return {
      'app': 'DocMind API',
      'status' : 'running',
      'version': os.getenv('API_VERSION', 'unknown')
    }

@app.get('/health', response_model = HealthResponse)
def health():
    # render pings this URL to know the app is alive
    return HealthResponse(
        status = 'ok',
        version = os.getenv('API_VERSION', '1.0.0'),
        services = {
            
        }
    )
    
@app.on_event("startup")
async def startup():
    # preload the model so first requrest is not slow
    from services.embedder import get_model
    get_model()
    print("DocMind API is ready ✓")