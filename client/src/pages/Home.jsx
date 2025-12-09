import { useNavigate } from 'react-router-dom';
import { v4 as uuidv4 } from 'uuid';
import './Home.css';

function Home() {
  const navigate = useNavigate();

  const createNewSession = () => {
    const sessionId = uuidv4();
    navigate(`/interview/${sessionId}`);
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

        <button className="create-session-btn" onClick={createNewSession}>
          Create New Interview Session
        </button>
      </div>
    </div>
  );
}

export default Home;
