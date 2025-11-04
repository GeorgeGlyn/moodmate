# backend/app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import ALLOWED_ORIGINS
from database.database import init_db
from routes import audio

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title="MoodMate API",
    description="Emotion-aware wellness companion API",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount outputs directory
import os
if not os.path.exists("outputs"):
    os.makedirs("outputs")
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

# Include routes
app.include_router(audio.router)

@app.get("/")
def root():
    return {
        "message": "🧠 MoodMate API is running!",
        "docs": "/docs",
        "endpoints": {
            "process_audio": "POST /api/audio/process",
            "mood_history": "GET /api/audio/history"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
