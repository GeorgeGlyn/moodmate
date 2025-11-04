// frontend/src/components/Header.jsx
import './Header.css';

export default function Header({ currentPage, setCurrentPage }) {
  return (
    <header className="header">
      <div className="header-container">
        <div className="logo">
          <span className="logo-icon">🧠</span>
          <h1>MoodMate</h1>
          <span className="tagline">Your AI Wellness Companion</span>
        </div>
        
        <nav className="nav">
          <button
            className={`nav-btn ${currentPage === 'recorder' ? 'active' : ''}`}
            onClick={() => setCurrentPage('recorder')}
          >
            🎙️ Record
          </button>
          <button
            className={`nav-btn ${currentPage === 'dashboard' ? 'active' : ''}`}
            onClick={() => setCurrentPage('dashboard')}
          >
            📊 Dashboard
          </button>
        </nav>
      </div>
    </header>
  );
}
