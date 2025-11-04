# backend/models/response_generator.py
import google.generativeai as genai
from config import GEMINI_API_KEY

class ResponseGenerator:
    """Generate empathetic AI responses using Google Gemini"""
    
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel("models/gemini-2.5-flash-lite")
        
        # Emotion-specific context
        self.emotion_context = {
            "happy": {
                "tone": "celebratory and encouraging",
                "focus": "celebrate their joy and encourage positive momentum",
            },
            "sad": {
                "tone": "warm, validating, and supportive",
                "focus": "acknowledge their feelings and offer gentle encouragement",
            },
            "angry": {
                "tone": "calm, understanding, and de-escalating",
                "focus": "validate frustration and suggest constructive outlets",
            },
            "anxious": {
                "tone": "reassuring and grounding",
                "focus": "provide calming techniques and perspective",
            },
            "calm": {
                "tone": "supportive and thoughtful",
                "focus": "maintain positivity and deepen self-reflection",
            },
            "neutral": {
                "tone": "friendly and conversational",
                "focus": "engage naturally and explore deeper",
            },
            "surprised": {
                "tone": "curious and engaging",
                "focus": "explore their thoughts and feelings",
            }
        }
    
    def generate(self, emotion: str, user_input: str = None) -> str:
        """
        Generate emotion-aware response
        
        Args:
            emotion: Detected emotion
            user_input: Optional user question/statement
        
        Returns:
            AI response text
        """
        
        context = self.emotion_context.get(emotion, self.emotion_context["neutral"])
        
        system_prompt = f"""
You are MoodMate, an empathetic AI wellness companion designed for mental health support.

CURRENT EMOTIONAL STATE: {emotion.upper()}
Tone: {context['tone']}
Focus: {context['focus']}

GUIDELINES:
1. Keep responses warm, authentic, and non-judgmental
2. Acknowledge their emotional state explicitly
3. Offer practical, actionable suggestions when appropriate
4. Use positive but realistic language
5. Keep responses under 150 words
6. Avoid being preachy or dismissive
7. If they mention specific concerns, address them directly
8. End with a supportive closing or gentle question

Remember: You're a companion, not a therapist. Never pretend to diagnose or treat mental health conditions. If they mention crisis/harm, suggest professional resources.
"""
        
        user_message = user_input or f"I'm feeling {emotion} right now."
        
        try:
            response = self.model.generate_content(
                f"{system_prompt}\n\nUser: {user_message}"
            )
            return response.text
        except Exception as e:
            print(f"❌ Gemini API error: {e}")
            # Fallback response
            return self._fallback_response(emotion)
    
    def _fallback_response(self, emotion: str) -> str:
        """Fallback if API fails"""
        fallbacks = {
            "happy": "That's wonderful! I'm so glad you're feeling good. Keep cherishing these positive moments! 💫",
            "sad": "I hear that you're going through a tough time. It's okay to feel sad sometimes. You're not alone. 💙",
            "angry": "I sense your frustration. That's a valid feeling. Let's find a constructive way to channel this energy. ⚡",
            "anxious": "I understand anxiety can be overwhelming. Let's take a moment to ground ourselves. Breathe with me. 🌬️",
            "calm": "You seem peaceful. That's a beautiful state to be in. Let's reflect on what's working well. ✨",
            "neutral": "I'm here to listen and support you. What's on your mind? 🤝",
            "surprised": "Something unexpected happened! Tell me more, I'm here to listen. 👂",
        }
        return fallbacks.get(emotion, "I'm here to support you on your wellness journey.")
