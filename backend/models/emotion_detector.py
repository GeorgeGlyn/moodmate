# backend/models/emotion_detector.py
import numpy as np
from transformers import pipeline
from utils.audio_processor import AudioProcessor
import json
from typing import Dict

class EmotionDetector:
    """
    Detect emotion from audio using:
    1. Audio emotion classification (wav2vec2-lg-xlsr)
    2. Transcription sentiment
    3. Prosodic features
    """
    
    def __init__(self):
        print("Loading emotion detection models...")
        
        try:
            # Use the verified working model you suggested!
            self.audio_emotion = pipeline(
                "audio-classification",
                model="ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition"
            )
            print("✅ Speech emotion model loaded!")
        except Exception as e:
            print(f"❌ Emotion model failed: {e}")
            self.audio_emotion = None
        
        # Text sentiment (for transcription)
        try:
            self.text_sentiment = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english"
            )
            print("✅ Text sentiment model loaded!")
        except Exception as e:
            print(f"⚠️ Text sentiment model failed: {e}")
            self.text_sentiment = None
        
        # Audio features
        self.audio_processor = AudioProcessor(sr=16000)
        
        print("✅ All emotion detection models loaded!")
    
    def detect(
        self, 
        audio_path: str, 
        transcription: str = None
    ) -> Dict:
        """
        Comprehensive emotion detection combining multiple signals
        
        Returns:
            {
                "primary_emotion": "anxious",
                "confidence": 0.85,
                "scores": {"happy": 0.1, "sad": 0.2, ...},
            }
        """
        
        # 1. Audio-based emotion detection
        audio_emotions = self._detect_from_audio(audio_path)
        
        # 2. Text-based emotion (if transcription available)
        text_emotions = self._detect_from_text(transcription) if transcription else None
        
        # 3. Prosodic features analysis
        features = self.audio_processor.extract_features(audio_path)
        
        # 4. Fuse all signals
        result = self._fuse_emotions(audio_emotions, text_emotions, features)
        
        return result
    
    def _detect_from_audio(self, audio_path: str) -> Dict[str, float]:
        """Speech emotion recognition from audio"""
        if self.audio_emotion is None:
            print("⚠️ Audio emotion model not available")
            return {}
        
        try:
            predictions = self.audio_emotion(audio_path)
            
            # Model outputs 8 emotions: 'angry', 'calm', 'disgust', 'fearful', 'happy', 'neutral', 'sad', 'surprised'
            # Map to our 7 emotion categories
            emotion_map = {
                "angry": "angry",
                "calm": "calm",
                "disgust": "angry",      # Disgust → Angry
                "fearful": "anxious",    # Fearful → Anxious
                "happy": "happy",
                "neutral": "neutral",
                "sad": "sad",
                "surprised": "surprised"
            }
            
            scores = {e: 0.0 for e in ["happy", "sad", "angry", "anxious", "calm", "neutral", "surprised"]}
            
            print(f"Raw model predictions: {predictions}")
            
            for pred in predictions:
                label = pred['label'].lower()
                mapped = emotion_map.get(label, "neutral")
                confidence = pred['score']
                
                # Aggregate multiple scores for same emotion
                scores[mapped] = max(scores[mapped], confidence)
            
            print(f"Mapped emotion scores: {scores}")
            
            return scores
        
        except Exception as e:
            print(f"❌ Audio emotion detection failed: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def _detect_from_text(self, text: str) -> Dict[str, float]:
        """Sentiment from transcribed text"""
        if self.text_sentiment is None:
            return {}
        
        try:
            result = self.text_sentiment(text[:512])  # Limit to 512 chars
            
            sentiment = result[0]['label'].lower()
            score = result[0]['score']
            
            scores = {e: 0.0 for e in ["happy", "sad", "angry", "anxious", "calm", "neutral", "surprised"]}
            
            # Map sentiment to emotions
            if sentiment == "positive":
                scores["happy"] = score
                scores["calm"] = score * 0.3
            else:
                scores["sad"] = score
                scores["anxious"] = score * 0.4
            
            return scores
        except Exception as e:
            print(f"⚠️ Text emotion detection failed: {e}")
            return {}
    
    def _fuse_emotions(
        self, 
        audio_emotions: Dict, 
        text_emotions: Dict = None,
        features: Dict = None
    ) -> Dict:
        """
        Combine audio, text, and prosodic signals
        Weights: 60% audio, 30% text, 10% prosody
        """
        
        emotion_categories = ["happy", "sad", "angry", "anxious", "calm", "neutral", "surprised"]
        fused_scores = {e: 0.0 for e in emotion_categories}
        
        # Initialize defaults if empty
        if not audio_emotions:
            audio_emotions = {e: 0.0 for e in emotion_categories}
        if not text_emotions:
            text_emotions = {e: 0.0 for e in emotion_categories}
        
        # Audio emotions (60% weight - strongest signal)
        for emotion in emotion_categories:
            fused_scores[emotion] += audio_emotions.get(emotion, 0.0) * 0.6
        
        # Text emotions (30% weight)
        if text_emotions:
            for emotion in emotion_categories:
                fused_scores[emotion] += text_emotions.get(emotion, 0.0) * 0.3
        
        # Prosody-based adjustments (10% weight)
        if features:
            prosody_scores = self._prosody_to_emotion(features)
            for emotion in emotion_categories:
                fused_scores[emotion] += prosody_scores.get(emotion, 0.0) * 0.1
        
        # Normalize to sum to 1
        total = sum(fused_scores.values())
        if total > 0:
            fused_scores = {k: v / total for k, v in fused_scores.items()}
        else:
            fused_scores["neutral"] = 1.0
        
        # Get primary emotion
        primary_emotion = max(fused_scores.items(), key=lambda x: x[1])
        
        return {
            "primary_emotion": primary_emotion[0],
            "confidence": round(primary_emotion[1], 4),
            "scores": {k: round(v, 4) for k, v in fused_scores.items()}
        }
    
    def _prosody_to_emotion(self, features: Dict) -> Dict[str, float]:
        """Infer emotion from prosodic features"""
        scores = {e: 0.1 for e in ["happy", "sad", "angry", "anxious", "calm", "neutral", "surprised"]}
        
        try:
            pitch_mean = features.get('pitch_mean', 100)
            pitch_std = features.get('pitch_std', 20)
            energy_mean = features.get('energy_mean', 0.05)
            
            # High pitch + high energy → happy
            if pitch_mean > 150 and energy_mean > 0.1:
                scores['happy'] = 0.8
                scores['surprised'] = 0.4
            
            # Low pitch + low energy → sad
            elif pitch_mean < 100 and energy_mean < 0.05:
                scores['sad'] = 0.7
                scores['calm'] = 0.3
            
            # High pitch variation + high energy → anxious
            elif pitch_std > 50 and energy_mean > 0.08:
                scores['anxious'] = 0.6
                scores['angry'] = 0.3
            
            # Consistent pitch + moderate energy → calm
            elif pitch_std < 30 and 0.05 < energy_mean < 0.1:
                scores['calm'] = 0.7
                scores['neutral'] = 0.4
        except:
            pass
        
        return scores
