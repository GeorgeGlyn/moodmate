# backend/config.py
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# Project paths
BASE_DIR = Path(__file__).parent.parent
BACKEND_DIR = Path(__file__).parent

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./moodmate.db")

# Audio settings
SAMPLE_RATE = 16000
CHUNK_SIZE = 1024
UPLOAD_DIR = BACKEND_DIR / "uploads"
OUTPUT_DIR = BACKEND_DIR / "outputs"

# Create directories
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# TTS settings
TTS_MODE = os.getenv("TTS_MODE", "quality")  # "quality" or "fast"

# Emotion categories
EMOTIONS = ["happy", "sad", "angry", "anxious", "calm", "neutral", "surprised"]

# CORS
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
]
