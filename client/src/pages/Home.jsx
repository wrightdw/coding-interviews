import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createSession } from '../services/api';
import './Home.css';

function Home() {
  const navigate = useNavigate();
  const [isCreating, setIsCreating] = useState(false);
  const [error, setError] = useState(null);

  const createNewSession = async () => {
    setIsCreating(true);
    setError(null);

    try {
      // Call backend API to create session
      const session = await createSession({
        language: 'javascript',
        title: 'New Interview Session'
      });
      
      console.log('Session created:', session);
      navigate(`/interview/${session.sessionId}`);
    } catch (err) {
      console.error('Failed to create session:', err);
      setError('Failed to create session. Please try again.');
      setIsCreating(false);
    }
  };

  return (
    <div className="home-container">
      <div className="home-content">
        <h1>Code Interview Platform</h1>
        <p className="subtitle">Collaborative coding interviews in real-time</p>
        
        <div className="features">
          <div className="feature">
            <span className="icon">🔗</span>
            <h3>Share Links</h3>
            <p>Create and share interview session links instantly</p>
          </div>
          <div className="feature">
            <span className="icon">👥</span>
            <h3>Real-Time Collaboration</h3>
            <p>Multiple users can edit code simultaneously</p>
          </div>
          <div className="feature">
            <span className="icon">🎨</span>
            <h3>Syntax Highlighting</h3>
            <p>Support for JavaScript, Python, Java, and C++</p>
          </div>
          <div className="feature">
            <span className="icon">▶️</span>
            <h3>Code Execution</h3>
            <p>Run JavaScript code safely in the browser</p>
          </div>
        </div>

        {error && (
          <div className="error-message" style={{ 
            color: '#ff4444', 
            marginBottom: '1rem', 
            padding: '1rem', 
            backgroundColor: 'rgba(255, 68, 68, 0.1)',
            borderRadius: '4px'
          }}>
            {error}
          </div>
        )}

        <button 
          className="create-session-btn" 
          onClick={createNewSession}
          disabled={isCreating}
        >
          {isCreating ? 'Creating Session...' : 'Create New Interview Session'}
        </button>
      </div>
    </div>
  );
}

export default Home;
