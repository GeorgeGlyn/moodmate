# test_tts.py
from TTS.api import TTS

# Test Coqui TTS
tts = TTS(model_name="tts_models/en/vctk/vits")
tts.tts_to_file(
    text="Hello, this is MoodMate speaking!",
    speaker="p225",
    file_path="test_output.wav"
)
print("✅ Coqui TTS working!")

# Test pyttsx3
import pyttsx3
engine = pyttsx3.init()
engine.say("Fast mode working!")
engine.runAndWait()
print("✅ pyttsx3 working!")
