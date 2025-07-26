# Interview Copilot - Web Application

A sophisticated web-based interview assistant that provides real-time AI-powered responses during job interviews. Built with React frontend, FastAPI backend, and Google Gemini AI integration.

## 🚀 Features

- **Real-time Speech Recognition**: Uses Web Speech API for continuous transcription
- **AI-Powered Responses**: Gemini 2.5 Pro generates contextual interview answers
- **Stealth Interface**: Minimal, hideable UI with hotkey controls
- **Session Management**: Persistent interview sessions with transcript history
- **Cross-Platform**: Works on any modern web browser
- **Responsive Design**: Optimized for desktop and mobile devices

## 🏗️ Architecture

### Frontend (React)
- **Speech Recognition**: Web Speech API with continuous listening
- **State Management**: React hooks for real-time updates
- **UI Components**: Modular, reusable components
- **API Integration**: Axios-based service layer

### Backend (FastAPI)
- **Database**: MongoDB for session and transcript storage
- **AI Integration**: Gemini API via emergentintegrations library
- **RESTful API**: Comprehensive endpoints for all functionality
- **CORS Support**: Configured for cross-origin requests

## 📋 Prerequisites

- **Node.js** 16.0.0 or higher
- **Python** 3.8 or higher
- **MongoDB** (local or cloud instance)
- **Google Gemini API Key**

## 🛠️ Installation

### 1. Clone and Setup
```bash
git clone <repository-url>
cd interview-copilot-web
npm run install-all
```

### 2. Environment Configuration

**Backend (.env)**:
```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=interview_copilot
GEMINI_API_KEY=your_gemini_api_key_here
CORS_ORIGINS=["http://localhost:3000"]
LOG_LEVEL=INFO
```

**Frontend (.env)**:
```env
REACT_APP_BACKEND_URL=http://localhost:8000
REACT_APP_GEMINI_API_KEY=your_gemini_api_key_here
REACT_APP_APP_NAME=Interview Copilot
```

### 3. Start Development Servers
```bash
npm run dev
```

This starts both backend (port 8000) and frontend (port 3000) concurrently.

## 🎯 Usage

### Basic Operation
1. **Grant Microphone Permission**: Click "Grant Mic Access" when prompted
2. **Start Listening**: Click "🎤 Start Listening" or press `Ctrl+L`
3. **Speak Naturally**: The app transcribes speech in real-time
4. **Get AI Responses**: AI automatically generates responses to detected questions
5. **Hide Interface**: Press `Ctrl+H` to hide during screen sharing

### Hotkeys
- `Ctrl+L`: Toggle listening on/off
- `Ctrl+H`: Hide/show interface
- Click green dot when hidden to show interface

### Interview Tips
- Position the interface where you can glance at it naturally
- Test microphone and permissions before interviews
- Use the hide function when screen sharing
- Speak clearly for better transcription accuracy

## 🔧 API Endpoints

### Session Management
- `POST /api/interview/session` - Create new session
- `GET /api/interview/session/{id}` - Get session details
- `GET /api/interview/sessions` - List all sessions

### Transcript Management
- `POST /api/interview/transcript` - Add transcript entry
- `GET /api/interview/transcript/{session_id}` - Get session transcripts

### AI Integration
- `POST /api/interview/ai-response` - Generate AI response
- `GET /api/interview/ai-responses/{session_id}` - Get AI response history

## 🧪 Testing

### Backend Testing
```bash
npm run test-backend
```

### Manual Testing
1. Open browser to `http://localhost:3000`
2. Grant microphone permissions
3. Start a session and test speech recognition
4. Verify AI responses are generated
5. Test hotkey functionality

## 🚀 Deployment

### Frontend (Netlify/Vercel)
```bash
cd frontend
npm run build
# Deploy dist/ folder to your hosting platform
```

### Backend (Railway/Heroku)
```bash
cd backend
# Configure environment variables on your platform
# Deploy using platform-specific instructions
```

### Environment Variables for Production
- Update `REACT_APP_BACKEND_URL` to your deployed backend URL
- Configure MongoDB connection string
- Set up CORS origins for your domain

## 🔒 Security Considerations

- **API Keys**: Never expose Gemini API keys in frontend code
- **CORS**: Configure appropriate origins for production
- **HTTPS**: Use HTTPS in production for microphone access
- **Rate Limiting**: Implement API rate limiting for production use

## 🐛 Troubleshooting

### Common Issues

**Microphone Not Working**:
- Ensure HTTPS in production (required for microphone access)
- Check browser permissions
- Verify microphone hardware

**Backend Connection Failed**:
- Check if backend server is running on correct port
- Verify CORS configuration
- Check network connectivity

**AI Responses Not Generated**:
- Verify Gemini API key is valid
- Check API quotas and limits
- Review backend logs for errors

**Speech Recognition Issues**:
- Use Chrome/Edge for best compatibility
- Ensure stable internet connection
- Check for background noise interference

## 📊 Performance Optimization

- **Speech Recognition**: Optimized for continuous listening with minimal CPU usage
- **API Calls**: Debounced to prevent excessive requests
- **Memory Management**: Automatic cleanup of old transcripts
- **Network**: Efficient API payload sizes

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Google Gemini AI for intelligent response generation
- Web Speech API for real-time transcription
- FastAPI for robust backend framework
- React for responsive frontend development

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs in browser console and backend
3. Create an issue in the repository

---

**⚠️ Disclaimer**: This tool is for educational and personal use. Ensure compliance with your organization's interview policies before use in professional settings.