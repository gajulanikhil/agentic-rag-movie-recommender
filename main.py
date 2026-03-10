from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import sys
import os

# Add src to path so its internal imports work
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from src.rag_chain import NetflixGPTRobust

app = FastAPI(title="AI Movie Recommender API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the recommender once
try:
    recommender = NetflixGPTRobust()
except Exception as e:
    logger.error(f"Failed to initialize recommender: {e}")
    recommender = None

class ChatRequest(BaseModel):
    prompt: str
    mood: str = ""
    genre: str = "All"
    min_year: int = 1950
    max_year: int = 2024
    min_rating: float = 0.0
    content_type: str = "All"

from typing import List, Dict, Any, Optional

class ChatResponse(BaseModel):
    response: str
    error: str = None
    sources: Optional[List[Dict[str, Any]]] = None

@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    if not recommender:
        raise HTTPException(status_code=500, detail="Recommender model not initialized")
    
    try:
        # Build the augmented prompt with filters
        augmented_prompt = request.prompt
        if request.mood:
            augmented_prompt = f"[{request.mood} mood] " + augmented_prompt
            
        settings_info = f"\n[Filters: Genre={request.genre}, Year {request.min_year}-{request.max_year}, Rating > {request.min_rating}, Type={request.content_type}]"
        
        # Combine them
        full_query = augmented_prompt + settings_info
        
        # Get response from the RAG chain safely
        result = recommender.query_safe(full_query)
        
        answer = result.get('answer', 'Sorry, I failed to generate a response.')
        
        if result.get('sources'):
            answer += "\n\n**Sources:**\n"
            for s in result['sources']:
                answer += f"• {s.get('title', 'Unknown')} ({s.get('year', 'N/A')})\n"
                
        print(f"🔥 DEBUG: Sending sources to Next.js -> {result.get('sources', [])}")
        
        return ChatResponse(
            response=answer.strip(),
            sources=result.get('sources', [])
        )
    
    except Exception as e:
        logger.error(f"Error during recommendation: {e}")
        return ChatResponse(response="", error=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
