// frontend/src/components/Recorder.jsx
import { useRef, useState } from 'react';
import { useAPI } from '../hooks/useAPI';
import EmotionDisplay from './EmotionDisplay';
import ResponseBox from './ResponseBox';
import './Recorder.css';

export default function Recorder({ onSessionComplete }) {
  const mediaRecorder = useRef(null);
  const chunks = useRef([]);
  
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [recordingTime, setRecordingTime] = useState(0);
  
  const { processAudio } = useAPI();

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        }
      });
      
      mediaRecorder.current = new MediaRecorder(stream, {
        mimeType: 'audio/webm'
      });
      
      chunks.current = [];
      
      mediaRecorder.current.ondataavailable = (e) => {
        chunks.current.push(e.data);
      };
      
      mediaRecorder.current.onstop = async () => {
        await handleRecordingComplete();
      };
      
      mediaRecorder.current.start();
      setIsRecording(true);
      setRecordingTime(0);
      setError(null);
      setResult(null);
      
      // Timer for recording duration
      const interval = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
      
      // Store interval ID for cleanup
      mediaRecorder.current.timerId = interval;
    } catch (err) {
      setError('Failed to access microphone: ' + err.message);
    }
  };

  const stopRecording = () => {
    if (mediaRecorder.current && isRecording) {
      clearInterval(mediaRecorder.current.timerId);
      mediaRecorder.current.stop();
      mediaRecorder.current.stream.getTracks().forEach(track => track.stop());
      setIsRecording(false);
    }
  };

  const handleRecordingComplete = async () => {
    if (chunks.current.length === 0) return;
    
    setIsProcessing(true);
    setError(null);
    
    try {
      // Convert chunks to blob
      const blob = new Blob(chunks.current, { type: 'audio/webm' });
      const file = new File([blob], 'recording.webm', { type: 'audio/webm' });
      
      console.log('Sending audio file:', file.size, 'bytes');
      
      // Send to API
      const data = await processAudio(file);
      
      console.log('Response:', data);
      setResult(data);
      onSessionComplete(data);
    } catch (err) {
      setError(err.message || 'Failed to process audio');
      console.error('Processing error:', err);
    } finally {
      setIsProcessing(false);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="recorder">
      <div className="recorder-container">
        <h2>How are you feeling today?</h2>
        <p className="subtitle">Speak naturally about your emotions, and I'll listen</p>
        
        <div className="recorder-controls">
          <button
            className={`record-btn ${isRecording ? 'recording' : ''} ${isProcessing ? 'disabled' : ''}`}
            onClick={isRecording ? stopRecording : startRecording}
            disabled={isProcessing}
          >
            <span>
              {isRecording ? '⏹️ Stop' : '🎙️ Start Recording'}
            </span>
          </button>
          
          {isRecording && <div className="recording-indicator">● Recording... {formatTime(recordingTime)}</div>}
          {isProcessing && <div className="processing-indicator">⏳ Processing your audio...</div>}
        </div>

        {error && (
          <div className="error-box">
            <p>❌ {error}</p>
          </div>
        )}

        {result && (
          <div className="result-container">
            <EmotionDisplay emotion={result.emotion} confidence={result.confidence} />
            <ResponseBox response={result.ai_response} audioUrl={result.response_audio_url} />
          </div>
        )}
      </div>
    </div>
  );
}
