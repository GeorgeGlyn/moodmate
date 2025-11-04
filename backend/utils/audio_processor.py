# backend/utils/audio_processor.py
import librosa
import numpy as np
from scipy import signal
from typing import Tuple
import warnings

# Suppress librosa warnings
warnings.filterwarnings('ignore')

class AudioProcessor:
    """Extract audio features for emotion detection"""
    
    def __init__(self, sr: int = 16000):
        self.sr = sr
    
    def extract_features(self, audio_path: str) -> dict:
        """
        Extract prosodic and spectral features from audio
        Returns: dict with features for emotion detection
        """
        try:
            # Load audio
            y, sr = librosa.load(audio_path, sr=self.sr)
            
            # Extract features
            features = {}
            
            # 1. Pitch-based features (safe method)
            try:
                features['pitch_mean'], features['pitch_std'] = self._extract_pitch(y, sr)
            except:
                features['pitch_mean'] = 0.0
                features['pitch_std'] = 0.0
            
            # 2. Energy features
            try:
                features['energy_mean'], features['energy_std'] = self._extract_energy(y)
            except:
                features['energy_mean'] = 0.0
                features['energy_std'] = 0.0
            
            # 3. MFCCs (Mel-Frequency Cepstral Coefficients)
            try:
                mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
                features['mfcc_mean'] = np.mean(mfccs, axis=1)
                features['mfcc_std'] = np.std(mfccs, axis=1)
            except:
                features['mfcc_mean'] = np.zeros(13)
                features['mfcc_std'] = np.zeros(13)
            
            # 4. Spectral features
            try:
                spec = np.abs(librosa.stft(y))
                features['spectral_centroid'] = np.mean(librosa.feature.spectral_centroid(S=spec, sr=sr))
            except:
                features['spectral_centroid'] = 0.0
            
            # 5. Zero crossing rate
            try:
                features['zero_crossing_rate'] = np.mean(librosa.feature.zero_crossing_rate(y))
            except:
                features['zero_crossing_rate'] = 0.0
            
            # 6. Tempo (use new librosa API)
            try:
                # New API for librosa 0.10+
                features['tempo'] = librosa.feature.rhythm.tempo(y=y, sr=sr)[0]
            except:
                try:
                    # Fallback to old API
                    features['tempo'] = librosa.beat.tempo(y=y, sr=sr)[0]
                except:
                    features['tempo'] = 100.0  # Default
            
            return features
        
        except Exception as e:
            print(f"⚠️ Error extracting audio features: {e}")
            # Return safe defaults
            return self._get_default_features()
    
    def _extract_pitch(self, y: np.ndarray, sr: int) -> Tuple[float, float]:
        """Extract fundamental frequency (pitch) - safe method"""
        try:
            # Use a simpler, more stable method
            f0 = librosa.yin(y, fmin=50, fmax=500, sr=sr)
            f0 = f0[f0 > 0]  # Remove unvoiced frames
            
            if len(f0) > 0:
                return float(np.mean(f0)), float(np.std(f0))
        except:
            pass
        
        return 100.0, 20.0  # Safe defaults
    
    def _extract_energy(self, y: np.ndarray) -> Tuple[float, float]:
        """Extract energy envelope - safe method"""
        try:
            # Use a simpler method to avoid NumPy issues
            # Compute RMS energy frame by frame
            frame_length = 2048
            hop_length = 512
            
            S = np.abs(librosa.stft(y, n_fft=frame_length, hop_length=hop_length))
            energy = np.sqrt(np.sum(S**2, axis=0))
            
            if len(energy) > 0:
                return float(np.mean(energy)), float(np.std(energy))
        except:
            pass
        
        return 0.05, 0.02  # Safe defaults
