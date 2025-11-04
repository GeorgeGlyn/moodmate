# backend/database/models.py
from sqlalchemy import Column, String, Float, DateTime, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class MoodEntry(Base):
    """Stores mood detection history"""
    __tablename__ = "mood_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Emotion data
    primary_emotion = Column(String, index=True)
    emotion_scores = Column(String)  # JSON: {"happy": 0.8, "sad": 0.2, ...}
    confidence = Column(Float)
    
    # Audio data
    transcription = Column(Text)
    audio_duration = Column(Float)  # seconds
    
    # Response data
    ai_response = Column(Text)
    response_audio_path = Column(String, nullable=True)
    
    # User feedback
    user_rating = Column(Integer, nullable=True)  # 1-5 stars
    user_notes = Column(Text, nullable=True)
    
    class Config:
        from_attributes = True
