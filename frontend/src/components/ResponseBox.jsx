// frontend/src/components/ResponseBox.jsx
import { useRef, useState } from 'react';
import './ResponseBox.css';

export default function ResponseBox({ response, audioUrl }) {
  const audioRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);

  const togglePlayback = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handleAudioEnd = () => {
    setIsPlaying(false);
  };

  return (
    <div className="response-box">
      <h3>MoodMate's Response 💬</h3>
      
      <div className="response-text">
        <p>{response}</p>
      </div>

      {audioUrl && (
        <div className="audio-player">
          <audio
            ref={audioRef}
            src={audioUrl}
            onEnded={handleAudioEnd}
            onPlay={() => setIsPlaying(true)}
            onPause={() => setIsPlaying(false)}
          />
          
          <button
            className={`play-btn ${isPlaying ? 'playing' : ''}`}
            onClick={togglePlayback}
          >
            {isPlaying ? '⏸️ Pause' : '▶️ Listen'}
          </button>
        </div>
      )}
    </div>
  );
}
