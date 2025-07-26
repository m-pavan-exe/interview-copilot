import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

// Create axios instance with default config
const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// API service functions
export const apiService = {
  // Session Management
  async createSession() {
    const response = await api.post('/interview/session', {});
    return response.data;
  },

  async getSession(sessionId) {
    const response = await api.get(`/interview/session/${sessionId}`);
    return response.data;
  },

  async getAllSessions() {
    const response = await api.get('/interview/sessions');
    return response.data;
  },

  // Transcript Management
  async addTranscript(sessionId, text, speaker = 'interviewer') {
    const response = await api.post('/interview/transcript', {
      session_id: sessionId,
      text,
      speaker,
    });
    return response.data;
  },

  async getSessionTranscripts(sessionId) {
    const response = await api.get(`/interview/transcript/${sessionId}`);
    return response.data;
  },

  // AI Response Generation
  async generateAIResponse(sessionId, question) {
    const response = await api.post('/interview/ai-response', {
      session_id: sessionId,
      question,
    });
    return response.data;
  },

  async getSessionAIResponses(sessionId) {
    const response = await api.get(`/interview/ai-responses/${sessionId}`);
    return response.data;
  },

  // Health Check
  async healthCheck() {
    const response = await api.get('/');
    return response.data;
  },
};

export default api;