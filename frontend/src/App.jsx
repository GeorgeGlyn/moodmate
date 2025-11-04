// frontend/src/App.jsx
import { useState } from 'react';
import './App.css';
import Recorder from './components/Recorder';
import Dashboard from './components/Dashboard';
import Header from './components/Header';

function App() {
  const [currentPage, setCurrentPage] = useState('recorder'); // 'recorder' or 'dashboard'
  const [sessionData, setSessionData] = useState(null);
  const [refreshDashboard, setRefreshDashboard] = useState(0);

  const handleSessionComplete = (data) => {
    setSessionData(data);
    // Auto-switch to dashboard after recording
    setTimeout(() => setCurrentPage('dashboard'), 1000);
    setRefreshDashboard(prev => prev + 1);
  };

  return (
    <div className="app">
      <Header currentPage={currentPage} setCurrentPage={setCurrentPage} />
      
      <main className="main-content">
        {currentPage === 'recorder' ? (
          <Recorder onSessionComplete={handleSessionComplete} />
        ) : (
          <Dashboard refreshKey={refreshDashboard} />
        )}
      </main>
    </div>
  );
}

export default App;
