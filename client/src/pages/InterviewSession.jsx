import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import CollaborativeEditor from '../components/CollaborativeEditor';
import './InterviewSession.css';

function InterviewSession() {
  const { sessionId } = useParams();
  const [language, setLanguage] = useState('javascript');
  const [code, setCode] = useState('');
  const [output, setOutput] = useState('');
  const [isRunning, setIsRunning] = useState(false);
  const [copied, setCopied] = useState(false);
  const [editorError, setEditorError] = useState(null);

  const sessionUrl = `${window.location.origin}/interview/${sessionId}`;

  console.log('InterviewSession rendering, sessionId:', sessionId);

  if (!sessionId) {
    return <div style={{ padding: '20px', color: 'white' }}>Invalid session ID</div>;
  }

  const copyToClipboard = () => {
    navigator.clipboard.writeText(sessionUrl);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const executeCode = () => {
    setIsRunning(true);
    setOutput('Running...');

    // Only JavaScript can be executed in the browser safely
    if (language === 'javascript') {
      try {
        // Create a sandboxed execution environment
        const logs = [];
        const customConsole = {
          log: (...args) => logs.push(args.join(' ')),
          error: (...args) => logs.push('Error: ' + args.join(' ')),
          warn: (...args) => logs.push('Warning: ' + args.join(' '))
        };

        // Execute in a limited scope
        const func = new Function('console', code);
        func(customConsole);

        setOutput(logs.length > 0 ? logs.join('\n') : 'Code executed successfully (no output)');
      } catch (error) {
        setOutput(`Error: ${error.message}`);
      }
    } else {
      setOutput(`Note: ${language} execution is not supported in the browser. Only JavaScript can be executed directly.`);
    }

    setIsRunning(false);
  };

  return (
    <div className="interview-session">
      <header className="session-header">
        <div className="header-content">
          <h2>Interview Session</h2>
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
            onChange={(e) => setLanguage(e.target.value)}
            className="language-select"
          >
            <option value="javascript">JavaScript</option>
            <option value="python">Python</option>
            <option value="java">Java</option>
            <option value="cpp">C++</option>
          </select>
          <button 
            onClick={executeCode} 
            disabled={isRunning || language !== 'javascript'}
            className="run-btn"
            title={language !== 'javascript' ? 'Only JavaScript can be executed' : 'Run code'}
          >
            ▶️ Run Code
          </button>
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
              onCodeChange={setCode}
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
