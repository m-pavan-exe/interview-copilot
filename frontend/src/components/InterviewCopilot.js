import React, { useState, useEffect, useCallback } from 'react';
import { useSpeechRecognition } from '../hooks/useSpeechRecognition';
import { apiService } from '../services/api';
import './InterviewCopilot.css';

const InterviewCopilot = () => {
  const [currentSession, setCurrentSession] = useState(null);
  const [aiResponse, setAiResponse] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [isVisible, setIsVisible] = useState(true);
  const [transcriptHistory, setTranscriptHistory] = useState([]);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [debugInfo, setDebugInfo] = useState('');

  const {
    isListening,
    transcript,
    interimTranscript,
    error: speechError,
    isSupported,
    permission,
    startListening,
    stopListening,
    resetTranscript,
  } = useSpeechRecognition();

  // Check backend connection on mount
  useEffect(() => {
    const checkConnection = async () => {
      try {
        await apiService.healthCheck();
        setConnectionStatus('connected');
        setDebugInfo('✅ Backend connected');
      } catch (error) {
        setConnectionStatus('error');
        setDebugInfo(`❌ Backend connection failed: ${error.message}`);
      }
    };

    checkConnection();
  }, []);

  // Create session when component mounts
  useEffect(() => {
    const initializeSession = async () => {
      if (connectionStatus === 'connected' && !currentSession) {
        try {
          const session = await apiService.createSession();
          setCurrentSession(session);
          setDebugInfo(`✅ Session created: ${session.id.slice(0, 8)}...`);
        } catch (error) {
          setDebugInfo(`❌ Failed to create session: ${error.message}`);
        }
      }
    };

    initializeSession();
  }, [connectionStatus, currentSession]);

  // Handle final speech results
  useEffect(() => {
    const handleSpeechFinal = async (event) => {
      const finalTranscript = event.detail.transcript;
      
      if (!currentSession || !finalTranscript) return;

      try {
        // Save transcript to backend
        await apiService.addTranscript(currentSession.id, finalTranscript, 'interviewer');
        
        // Add to local history
        const historyItem = {
          text: finalTranscript,
          timestamp: new Date(),
          speaker: 'interviewer'
        };
        setTranscriptHistory(prev => [...prev.slice(-4), historyItem]);

        // Generate AI response if it looks like a question
        if (isQuestion(finalTranscript)) {
          await generateAIResponse(finalTranscript);
        }

        // Reset transcript for next input
        resetTranscript();
        
      } catch (error) {
        setDebugInfo(`❌ Error processing transcript: ${error.message}`);
      }
    };

    window.addEventListener('speechFinal', handleSpeechFinal);
    return () => window.removeEventListener('speechFinal', handleSpeechFinal);
  }, [currentSession, resetTranscript]);

  // Check if text is a question
  const isQuestion = (text) => {
    const questionIndicators = [
      '?', 'what', 'how', 'why', 'when', 'where', 'who', 
      'can you', 'tell me', 'describe', 'explain', 'would you'
    ];
    const textLower = text.toLowerCase();
    return questionIndicators.some(indicator => textLower.includes(indicator)) || text.length > 20;
  };

  // Generate AI response
  const generateAIResponse = async (question) => {
    if (!currentSession || isProcessing) return;

    setIsProcessing(true);
    setAiResponse('');
    setDebugInfo('🤖 Generating AI response...');

    try {
      const response = await apiService.generateAIResponse(currentSession.id, question);
      setAiResponse(response.response);
      setDebugInfo('✅ AI response generated');
    } catch (error) {
      setAiResponse(`Error: ${error.message}`);
      setDebugInfo(`❌ AI response failed: ${error.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  // Toggle listening
  const handleToggleListening = async () => {
    if (!isSupported) {
      setDebugInfo('❌ Speech recognition not supported');
      return;
    }

    if (!currentSession) {
      setDebugInfo('❌ No active session');
      return;
    }

    if (isListening) {
      stopListening();
      setDebugInfo('🔴 Stopped listening');
    } else {
      const started = await startListening();
      if (started) {
        setDebugInfo('🎤 Started listening...');
      }
    }
  };

  // Hotkey controls
  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.ctrlKey && event.key === 'h') {
        event.preventDefault();
        setIsVisible(!isVisible);
      }
      if (event.ctrlKey && event.key === 'l') {
        event.preventDefault();
        handleToggleListening();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isVisible, handleToggleListening]);

  // Hidden state
  if (!isVisible) {
    return (
      <div className="hidden-indicator">
        <div className="hidden-dot" onClick={() => setIsVisible(true)}></div>
      </div>
    );
  }

  return (
    <div className="interview-copilot">
      {/* Header */}
      <div className="copilot-header">
        <div className="header-left">
          <h1>🎯 Interview Copilot</h1>
          <div className="session-info">
            {currentSession && (
              <span className="session-id">
                Session: {currentSession.id.slice(0, 8)}...
              </span>
            )}
            <span className={`connection-status ${connectionStatus}`}>
              {connectionStatus === 'connected' ? '🟢' : '🔴'} {connectionStatus}
            </span>
          </div>
        </div>
        <div className="header-controls">
          <button
            className={`listen-btn ${isListening ? 'listening' : ''} ${
              permission !== 'granted' ? 'permission-needed' : ''
            }`}
            onClick={handleToggleListening}
            disabled={!isSupported || connectionStatus !== 'connected'}
          >
            {permission !== 'granted'
              ? '🔒 Grant Mic Access'
              : isListening
              ? '🎤 Listening...'
              : '🎤 Start Listening'}
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

      {/* Content */}
      <div className="copilot-content">
        {/* Live Transcript */}
        <div className="transcript-section">
          <h3>📝 Live Transcript</h3>
          <div className="transcript-box">
            {transcript || interimTranscript || 'Waiting for speech...'}
          </div>
          {(speechError || debugInfo) && (
            <div className="debug-info">
              <small>{speechError || debugInfo}</small>
            </div>
          )}
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

        {/* Recent Questions */}
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

      {/* Footer */}
      <div className="copilot-footer">
        <div className="shortcuts">
          <span>Shortcuts: Ctrl+H (Hide) | Ctrl+L (Listen)</span>
        </div>
        <div className="status">
          <span className={`status-dot ${isListening ? 'active' : ''}`}></span>
          <span className="status-text">
            {isListening ? 'Listening' : 'Ready'}
          </span>
        </div>
      </div>
    </div>
  );
};

export default InterviewCopilot;