import React, { useState, useEffect, useRef, useCallback } from 'react';
import './App.css';

function App() {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [currentSession, setCurrentSession] = useState(null);
  const [aiResponse, setAiResponse] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [isVisible, setIsVisible] = useState(true);
  const [transcriptHistory, setTranscriptHistory] = useState([]);
  const [isScreenSharing, setIsScreenSharing] = useState(false);
  
  const recognitionRef = useRef(null);
  const silenceTimeoutRef = useRef(null);
  const backendUrl = process.env.REACT_APP_BACKEND_URL;

  // Initialize speech recognition
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = 'en-US';
      
      recognitionRef.current.onresult = (event) => {
        let finalTranscript = '';
        let interimTranscript = '';
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript;
          } else {
            interimTranscript += transcript;
          }
        }
        
        if (finalTranscript) {
          setTranscript(finalTranscript);
          handleFinalTranscript(finalTranscript);
        } else {
          setTranscript(interimTranscript);
        }
        
        // Reset silence timeout
        if (silenceTimeoutRef.current) {
          clearTimeout(silenceTimeoutRef.current);
        }
        
        // Set new silence timeout (3 seconds of silence)
        silenceTimeoutRef.current = setTimeout(() => {
          if (finalTranscript && currentSession) {
            processQuestion(finalTranscript);
          }
        }, 3000);
      };
      
      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
      };
      
      recognitionRef.current.onend = () => {
        if (isListening) {
          // Restart recognition if it stops unexpectedly
          setTimeout(() => {
            if (recognitionRef.current && isListening) {
              recognitionRef.current.start();
            }
          }, 100);
        }
      };
    }
  }, [isListening, currentSession]);

  // Screen sharing detection - removed automatic detection to prevent permission prompts
  // Users can manually hide the interface using Ctrl+H hotkey

  // Hotkey controls (Ctrl+H to hide/show)
  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.ctrlKey && event.key === 'h') {
        event.preventDefault();
        setIsVisible(!isVisible);
      }
      if (event.ctrlKey && event.key === 'l') {
        event.preventDefault();
        toggleListening();
      }
    };
    
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isVisible, isListening]);

  // Create new interview session
  const createSession = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/interview/session`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
      });
      const session = await response.json();
      setCurrentSession(session);
      return session;
    } catch (error) {
      console.error('Failed to create session:', error);
      return null;
    }
  };

  // Handle final transcript
  const handleFinalTranscript = async (text) => {
    if (!currentSession || !text.trim()) return;
    
    try {
      await fetch(`${backendUrl}/api/interview/transcript`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: currentSession.id,
          text: text.trim(),
          speaker: 'interviewer'
        })
      });
      
      setTranscriptHistory(prev => [...prev, { text: text.trim(), timestamp: new Date() }]);
    } catch (error) {
      console.error('Failed to save transcript:', error);
    }
  };

  // Process question and get AI response
  const processQuestion = async (question) => {
    if (!currentSession || isProcessing) return;
    
    setIsProcessing(true);
    try {
      const response = await fetch(`${backendUrl}/api/interview/ai-response`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: currentSession.id,
          question: question.trim()
        })
      });
      
      const aiResponseData = await response.json();
      setAiResponse(aiResponseData.response);
    } catch (error) {
      console.error('Failed to get AI response:', error);
      setAiResponse('Error: Could not generate response. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  // Toggle listening
  const toggleListening = async () => {
    if (!currentSession) {
      const session = await createSession();
      if (!session) return;
    }
    
    if (isListening) {
      recognitionRef.current?.stop();
      setIsListening(false);
    } else {
      recognitionRef.current?.start();
      setIsListening(true);
    }
  };

  // Auto-hide when screen sharing is detected
  const shouldHide = isScreenSharing || !isVisible;

  if (shouldHide) {
    return (
      <div className="hidden-indicator">
        <div className="hidden-dot"></div>
      </div>
    );
  }

  return (
    <div className="interview-copilot">
      <div className="copilot-header">
        <div className="header-left">
          <h1>🎯 Interview Copilot</h1>
          <div className="session-info">
            {currentSession && (
              <span className="session-id">Session: {currentSession.id.slice(0, 8)}...</span>
            )}
          </div>
        </div>
        <div className="header-controls">
          <button 
            className={`listen-btn ${isListening ? 'listening' : ''}`}
            onClick={toggleListening}
            disabled={isProcessing}
          >
            {isListening ? '🎤 Listening...' : '🎤 Start Listening'}
          </button>
          <button 
            className="hide-btn"
            onClick={() => setIsVisible(false)}
            title="Hide (Ctrl+H)"
          >
            👁️
          </button>
        </div>
      </div>

      <div className="copilot-content">
        {/* Real-time transcript */}
        <div className="transcript-section">
          <h3>📝 Live Transcript</h3>
          <div className="transcript-box">
            {transcript || 'Waiting for speech...'}
          </div>
        </div>

        {/* AI Response */}
        <div className="response-section">
          <h3>🤖 AI Response</h3>
          <div className="response-box">
            {isProcessing ? (
              <div className="processing">
                <div className="spinner"></div>
                Generating response...
              </div>
            ) : (
              <div className="response-content">
                {aiResponse || 'AI response will appear here...'}
              </div>
            )}
          </div>
        </div>

        {/* Recent questions */}
        <div className="history-section">
          <h3>📋 Recent Questions</h3>
          <div className="history-list">
            {transcriptHistory.length === 0 ? (
              <div className="no-history">No questions yet</div>
            ) : (
              transcriptHistory.slice(-3).map((item, index) => (
                <div key={index} className="history-item">
                  <div className="history-text">{item.text}</div>
                  <div className="history-time">
                    {item.timestamp.toLocaleTimeString()}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      <div className="copilot-footer">
        <div className="shortcuts">
          <span>Shortcuts: Ctrl+H (Hide) | Ctrl+L (Listen)</span>
        </div>
        <div className="status">
          {isScreenSharing && <span className="screen-sharing">📺 Screen sharing detected</span>}
          <span className={`status-dot ${isListening ? 'active' : ''}`}></span>
        </div>
      </div>
    </div>
  );
}

export default App;