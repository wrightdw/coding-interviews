import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import InterviewSession from './pages/InterviewSession';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/interview/:sessionId" element={<InterviewSession />} />
      </Routes>
    </Router>
  );
}

export default App;
