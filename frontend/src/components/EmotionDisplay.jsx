// frontend/src/components/EmotionDisplay.jsx
import './EmotionDisplay.css';

const emotionEmojis = {
  happy: '😊',
  sad: '😢',
  angry: '😠',
  anxious: '😰',
  calm: '😌',
  neutral: '😐',
  surprised: '😲'
};

const emotionColors = {
  happy: '#FFD700',
  sad: '#4A90E2',
  angry: '#F5576C',
  anxious: '#FF9F43',
  calm: '#78E89F',
  neutral: '#95A5A6',
  surprised: '#A78BFA'
};

export default function EmotionDisplay({ emotion, confidence }) {
  const displayEmoji = emotionEmojis[emotion] || '😐';
  const displayColor = emotionColors[emotion] || '#95A5A6';
  const percentage = Math.round(confidence * 100);

  return (
    <div className="emotion-display">
      <div className="emotion-card" style={{ borderColor: displayColor }}>
        <div className="emotion-emoji" style={{ fontSize: '3rem' }}>
          {displayEmoji}
        </div>
        <div className="emotion-name" style={{ color: displayColor }}>
          {emotion.charAt(0).toUpperCase() + emotion.slice(1)}
        </div>
        <div className="emotion-confidence">
          <div className="confidence-bar">
            <div
              className="confidence-fill"
              style={{
                width: `${percentage}%`,
                background: displayColor
              }}
            ></div>
          </div>
          <span className="confidence-text">{percentage}% confident</span>
        </div>
      </div>
    </div>
  );
}
