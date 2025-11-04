# backend/routes/audio.py
from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from datetime import datetime
import json
import os

from models.emotion_detector import EmotionDetector
from models.response_generator import ResponseGenerator
from models.tts_engine import TTSEngine
from database.database import get_db
from database.models import MoodEntry
import whisper

router = APIRouter(prefix="/api/audio", tags=["audio"])

# Initialize models (loaded once)
emotion_detector = EmotionDetector()
response_generator = ResponseGenerator()
tts_engine = TTSEngine()
whisper_model = whisper.load_model("base")

@router.post("/process")
async def process_audio(audio: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Main endpoint: Process audio → Detect emotion → Generate response → TTS
    """
    
    try:
        # 1. Save uploaded audio
        audio_path = f"uploads/{audio.filename}"
        with open(audio_path, "wb") as f:
            f.write(await audio.read())
        
        # 2. Transcribe audio
        result = whisper_model.transcribe(audio_path, language="en")
        transcription = result["text"]
        
        # 3. Detect emotion
        emotion_result = emotion_detector.detect(audio_path, transcription)
        
        # 4. Generate response
        ai_response = response_generator.generate(
            emotion=emotion_result["primary_emotion"],
            user_input=transcription
        )
        
        # 5. Generate response audio (TTS)
        response_audio_path = tts_engine.synthesize(
            text=ai_response,
            emotion=emotion_result["primary_emotion"]
        )
        
        # 6. Save to database
        mood_entry = MoodEntry(
            timestamp=datetime.utcnow(),
            primary_emotion=emotion_result["primary_emotion"],
            emotion_scores=json.dumps(emotion_result["scores"]),
            confidence=emotion_result["confidence"],
            transcription=transcription,
            audio_duration=0.0,  # Could calculate from audio
            ai_response=ai_response,
            response_audio_path=response_audio_path
        )
        db.add(mood_entry)
        db.commit()
        db.refresh(mood_entry)
        
        # 7. Return response
        return {
            "session_id": mood_entry.id,
            "emotion": emotion_result["primary_emotion"],
            "confidence": emotion_result["confidence"],
            "emotion_scores": emotion_result["scores"],
            "transcription": transcription,
            "ai_response": ai_response,
            "response_audio_url": f"/api/audio/file/{response_audio_path}",
            "timestamp": mood_entry.timestamp.isoformat()
        }
    
    except Exception as e:
        print(f"❌ Error processing audio: {e}")
        return {"error": str(e)}, 500
    
    finally:
        # Cleanup
        if os.path.exists(audio_path):
            os.remove(audio_path)

@router.get("/file/{file_path:path}")
async def get_audio_file(file_path: str):
    """Serve generated audio files"""
    from fastapi.responses import FileResponse
    
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="audio/wav")
    return {"error": "File not found"}, 404

@router.get("/history")
async def get_mood_history(db: Session = Depends(get_db), limit: int = 30):
    """Retrieve mood history"""
    entries = db.query(MoodEntry).order_by(MoodEntry.timestamp.desc()).limit(limit).all()
    
    return {
        "entries": [
            {
                "id": e.id,
                "timestamp": e.timestamp.isoformat(),
                "emotion": e.primary_emotion,
                "confidence": e.confidence,
                "response": e.ai_response
            }
            for e in entries
        ]
    }
