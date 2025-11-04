// frontend/src/hooks/useAPI.js
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
});

export function useAPI() {
  const processAudio = async (audioFile) => {
    try {
      const formData = new FormData();
      formData.append('audio', audioFile);

      const response = await api.post('/audio/process', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      return response.data;
    } catch (error) {
      console.error('API Error:', error);
      throw new Error(error.response?.data?.detail || 'Failed to process audio');
    }
  };

  const getMoodHistory = async (limit = 30) => {
    try {
      const response = await api.get(`/audio/history?limit=${limit}`);
      return response.data;
    } catch (error) {
      console.error('API Error:', error);
      throw new Error('Failed to fetch mood history');
    }
  };

  return {
    processAudio,
    getMoodHistory,
  };
}
