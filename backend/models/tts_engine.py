# backend/models/tts_engine.py
import pyttsx3
from TTS.api import TTS
from config import TTS_MODE
from typing import Literal
import os

class TTSEngine:
    """
    Text-to-speech with emotion-aware tone control
    Supports both fast (pyttsx3) and quality (Coqui) modes
    """
    
    def __init__(self, mode: str = None):
        self.mode = mode or TTS_MODE
        print(f"🔊 Initializing TTS in {self.mode} mode...")
        
        # Fast mode: pyttsx3
        if self.mode == "fast":
            self.fast_engine = pyttsx3.init()
            self.fast_engine.setProperty('rate', 150)
            self.fast_engine.setProperty('volume', 0.9)
            print("✅ pyttsx3 initialized")
        
        # Quality mode: Coqui TTS
        elif self.mode == "quality":
            try:
                self.quality_engine = TTS(
                    model_name="tts_models/en/ljspeech/vits",
                    gpu=False
                )
                print("✅ Coqui TTS initialized")
            except Exception as e:
                print(f"⚠️ Coqui TTS failed: {e}, falling back to fast mode")
                self.mode = "fast"
                self.fast_engine = pyttsx3.init()
        
        # Emotion-specific voice settings
        self.emotion_config = {
            "happy": {"rate": 180, "volume": 1.0},
            "sad": {"rate": 120, "volume": 0.7},
            "angry": {"rate": 200, "volume": 1.0},
            "anxious": {"rate": 140, "volume": 0.8},
            "calm": {"rate": 120, "volume": 0.9},
            "neutral": {"rate": 150, "volume": 0.9},
            "surprised": {"rate": 170, "volume": 0.95}
        }
    
    def synthesize(
        self, 
        text: str, 
        emotion: str = "neutral",
        output_path: str = None
    ) -> str:
        """
        Generate speech with emotional tone
        
        Args:
            text: Text to synthesize
            emotion: Emotional context
            output_path: Where to save the audio file
        
        Returns:
            Path to generated audio file
        """
        
        if output_path is None:
            output_path = f"outputs/tts_{emotion}_{os.urandom(4).hex()}.wav"
        
        try:
            if self.mode == "fast":
                return self._synthesize_fast(text, emotion, output_path)
            else:
                return self._synthesize_quality(text, emotion, output_path)
        except Exception as e:
            print(f"❌ TTS generation failed: {e}")
            raise
    
    def _synthesize_fast(self, text: str, emotion: str, output_path: str) -> str:
        """pyttsx3 synthesis with emotion control"""
        config = self.emotion_config.get(emotion, self.emotion_config["neutral"])
        self.fast_engine.setProperty('rate', config['rate'])
        self.fast_engine.setProperty('volume', config['volume'])
        
        self.fast_engine.save_to_file(text, output_path)
        self.fast_engine.runAndWait()
        
        return output_path
    
    def _synthesize_quality(self, text: str, emotion: str, output_path: str) -> str:
        """Coqui TTS synthesis"""
        self.quality_engine.tts_to_file(
            text=text,
            file_path=output_path
        )
        return output_path
