import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import CollaborativeEditor from '../components/CollaborativeEditor';
import { getSession, updateSession, saveCode, executeCode as executeCodeAPI } from '../services/api';
import { WebSocketClient } from '../services/websocket';
import './InterviewSession.css';

function InterviewSession() {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [language, setLanguage] = useState('javascript');
  const [code, setCode] = useState('');
  const [output, setOutput] = useState('');
  const [isRunning, setIsRunning] = useState(false);
  const [copied, setCopied] = useState(false);
  const [editorError, setEditorError] = useState(null);
  const [sessionTitle, setSessionTitle] = useState('Interview Session');
  const [participants, setParticipants] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const wsClient = useRef(null);
  const userId = useRef(`user-${Math.random().toString(36).substr(2, 9)}`);

  const sessionUrl = `${window.location.origin}/interview/${sessionId}`;

  console.log('InterviewSession rendering, sessionId:', sessionId);

  // Load session data from backend
  useEffect(() => {
    if (!sessionId) {
      setError('Invalid session ID');
      setIsLoading(false);
      return;
    }

    async function loadSession() {
      try {
        const session = await getSession(sessionId);
        console.log('Session loaded:', session);
        
        setLanguage(session.language);
        setSessionTitle(session.title || 'Interview Session');
        
        // Get initial code
        // Note: Code is loaded via WebSocket welcome message
        
        setIsLoading(false);
      } catch (err) {
        console.error('Failed to load session:', err);
        setError(`Session not found or failed to load: ${err.message}`);
        setIsLoading(false);
      }
    }

    loadSession();
  }, [sessionId]);

  // Setup WebSocket connection
  useEffect(() => {
    if (!sessionId || isLoading || error) return;

    const client = new WebSocketClient(
      sessionId,
      userId.current,
      'Anonymous User'
    );

    // Handle welcome message
    client.on('welcome', (message) => {
      console.log('Welcome message received:', message);
      if (message.data.currentCode) {
        setCode(message.data.currentCode);
      }
      if (message.data.participants) {
        setParticipants(message.data.participants);
      }
    });

    // Handle user joined
    client.on('user-joined', (message) => {
      console.log('User joined:', message);
      setParticipants(prev => [...prev, {
        userId: message.userId,
        name: message.data.name
      }]);
    });

    // Handle user left
    client.on('user-left', (message) => {
      console.log('User left:', message);
      setParticipants(prev => prev.filter(p => p.userId !== message.userId));
    });

    // Handle code updates from others
    client.on('code-update', (message) => {
      console.log('Code update received:', message);
      if (message.userId !== userId.current && message.data.code) {
        setCode(message.data.code);
      }
    });

    // Handle language changes
    client.on('language-changed', (message) => {
      console.log('Language changed:', message);
      if (message.data.language) {
        setLanguage(message.data.language);
      }
    });

    // Connect
    client.connect().then(() => {
      console.log('WebSocket connected successfully');
      client.startHeartbeat();
    }).catch(err => {
      console.error('Failed to connect WebSocket:', err);
      setError('Failed to connect to real-time collaboration');
    });

    wsClient.current = client;

    return () => {
      if (wsClient.current) {
        wsClient.current.disconnect();
      }
    };
  }, [sessionId, isLoading, error]);

  // Handle code changes (for WebSocket sync)
  const handleCodeChange = (newCode) => {
    setCode(newCode);
    
    // Send code update via WebSocket
    if (wsClient.current && wsClient.current.isConnected()) {
      wsClient.current.sendCodeUpdate(newCode);
    }
  };

  // Handle language change
  const handleLanguageChange = async (newLanguage) => {
    setLanguage(newLanguage);
    
    try {
      // Update on backend
      await updateSession(sessionId, { language: newLanguage });
      
      // Notify via WebSocket
      if (wsClient.current && wsClient.current.isConnected()) {
        wsClient.current.sendLanguageChange(newLanguage);
      }
    } catch (err) {
      console.error('Failed to update language:', err);
    }
  };

  if (!sessionId) {
    return <div style={{ padding: '20px', color: 'white' }}>Invalid session ID</div>;
  }

  if (isLoading) {
    return <div style={{ padding: '20px', color: 'white' }}>Loading session...</div>;
  }

  if (error) {
    return (
      <div style={{ padding: '20px', color: 'white' }}>
        <h2>Error</h2>
        <p>{error}</p>
        <button onClick={() => navigate('/')} style={{ marginTop: '1rem' }}>
          Go Home
        </button>
      </div>
    );
  }

  const copyToClipboard = () => {
    navigator.clipboard.writeText(sessionUrl);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const executeCode = async () => {
    setIsRunning(true);
    setOutput('Running...');

    try {
      // Call backend API to execute code
      const result = await executeCodeAPI(code, language, 5);
      
      if (result.success) {
        const output = [
          result.stdout && `Output:\n${result.stdout}`,
          result.stderr && `Errors:\n${result.stderr}`,
          result.executionTime && `Execution time: ${result.executionTime}s`
        ].filter(Boolean).join('\n\n');
        
        setOutput(output || 'Code executed successfully (no output)');
      } else {
        setOutput(`Error: ${result.error || 'Unknown error'}`);
      }
      
      // Save code after execution
      await saveCode(sessionId, code, language);
      
    } catch (error) {
      console.error('Execution error:', error);
      setOutput(`Error: ${error.message || 'Failed to execute code'}`);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="interview-session">
      <header className="session-header">
        <div className="header-content">
          <h2>{sessionTitle}</h2>
          <div className="session-info">
            <input 
              type="text" 
              value={sessionUrl} 
              readOnly 
              className="session-url"
            />
            <button 
              onClick={copyToClipboard} 
              className="copy-btn"
              title="Copy link"
            >
              {copied ? '✓ Copied!' : '📋 Copy Link'}
            </button>
          </div>
        </div>
        <div className="controls">
          <select 
            value={language} 
            onChange={(e) => handleLanguageChange(e.target.value)}
            className="language-select"
          >
            <option value="javascript">JavaScript</option>
            <option value="python">Python</option>
            <option value="java">Java</option>
            <option value="cpp">C++</option>
          </select>
          <button 
            onClick={executeCode} 
            disabled={isRunning}
            className="run-btn"
            title="Run code on server"
          >
            ▶️ Run Code
          </button>
          {participants.length > 0 && (
            <div className="participants-badge" title={`${participants.length} active participant(s)`}>
              👥 {participants.length}
            </div>
          )}
        </div>
      </header>

      <div className="session-content">
        <div className="editor-panel">
          <div className="panel-header">
            <h3>Code Editor</h3>
            <span className="status-indicator">🟢 Connected</span>
          </div>
          {editorError ? (
            <div style={{ padding: '20px', color: '#ff6b6b' }}>
              Error loading editor: {editorError}
            </div>
          ) : (
            <CollaborativeEditor 
              sessionId={sessionId}
              language={language}
              onCodeChange={handleCodeChange}
              initialCode={code}
            />
          )}
        </div>

        <div className="output-panel">
          <div className="panel-header">
            <h3>Output</h3>
          </div>
          <pre className="output-content">{output || 'Run your code to see output here...'}</pre>
        </div>
      </div>
    </div>
  );
}

export default InterviewSession;
