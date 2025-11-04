// frontend/src/components/Dashboard.jsx
import { useEffect, useState } from 'react';
import { useAPI } from '../hooks/useAPI';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import './Dashboard.css';

export default function Dashboard({ refreshKey }) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const { getMoodHistory } = useAPI();

  useEffect(() => {
    loadHistory();
  }, [refreshKey]);

  const loadHistory = async () => {
    setLoading(true);
    try {
      const data = await getMoodHistory();
      setHistory(data.entries || []);
    } catch (err) {
      console.error('Failed to load history:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="dashboard"><p>Loading your mood history...</p></div>;
  }

  if (history.length === 0) {
    return (
      <div className="dashboard">
        <div className="empty-state">
          <p>📊 No mood data yet</p>
          <p>Start recording to see your emotional journey!</p>
        </div>
      </div>
    );
  }

  // Prepare chart data
  const timelineData = history.map(entry => ({
    time: new Date(entry.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    emotion: entry.emotion
  }));

  const emotionCounts = history.reduce((acc, entry) => {
    acc[entry.emotion] = (acc[entry.emotion] || 0) + 1;
    return acc;
  }, {});

  const pieData = Object.entries(emotionCounts).map(([emotion, count]) => ({
    name: emotion.charAt(0).toUpperCase() + emotion.slice(1),
    value: count
  }));

  const COLORS = {
    happy: '#FFD700',
    sad: '#4A90E2',
    angry: '#F5576C',
    anxious: '#FF9F43',
    calm: '#78E89F',
    neutral: '#95A5A6',
    surprised: '#A78BFA'
  };

  return (
    <div className="dashboard">
      <h2>Your Emotional Journey 📊</h2>
      
      <div className="dashboard-grid">
        <div className="chart-container">
          <h3>Emotion Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: ${value}`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[entry.name.toLowerCase()] || '#95A5A6'} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="recent-moods">
          <h3>Recent Sessions</h3>
          <div className="mood-list">
            {history.slice(0, 10).map((entry, idx) => (
              <div key={idx} className="mood-item">
                <span className="mood-time">
                  {new Date(entry.timestamp).toLocaleString()}
                </span>
                <span className="mood-emotion" style={{ color: COLORS[entry.emotion] }}>
                  {entry.emotion.toUpperCase()}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="stats">
        <div className="stat-card">
          <span className="stat-label">Total Sessions</span>
          <span className="stat-value">{history.length}</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Most Frequent</span>
          <span className="stat-value">
            {Object.entries(emotionCounts).sort((a, b) => b[1] - a[1])[0]?.[0]?.toUpperCase() || 'N/A'}
          </span>
        </div>
      </div>
    </div>
  );
}
