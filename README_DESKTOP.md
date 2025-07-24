# Desktop Interview Copilot

A powerful, GPU-accelerated desktop application for interview assistance using OpenAI Whisper and Google Gemini.

## Features

🎤 **Real-time Speech Recognition** - GPU-accelerated Whisper model
🤖 **AI-Powered Responses** - Google Gemini 2.5 Pro integration  
🎯 **Stealth Interface** - Always-on-top, transparent, hideable window
⌨️ **Global Hotkeys** - Control from anywhere with keyboard shortcuts
🔊 **High-Quality Audio** - Professional-grade audio processing
💾 **Local Processing** - Privacy-focused with local speech recognition

## System Requirements

- **Python 3.8+**
- **NVIDIA GPU** (RTX 4050 or better recommended)
- **CUDA 11.8+** for GPU acceleration
- **8GB+ RAM** recommended
- **Windows 10/11**, macOS, or Linux

## Quick Start

### 1. Setup
```bash
# Run the automated setup
python setup_desktop.py
```

### 2. Run the Application
```bash
python interview_copilot.py
```

### 3. Usage
1. **Grant microphone permission** when prompted
2. **Click "Start Listening"** or press `Ctrl+L`
3. **Speak naturally** - transcripts appear in real-time
4. **AI responses** generate automatically for questions
5. **Use `Ctrl+H`** to hide during screen sharing

## Manual Installation

If automated setup fails:

```bash
# Install PyTorch with CUDA
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install Whisper
pip install openai-whisper

# Install other dependencies
pip install google-generativeai pyaudio keyboard psutil Pillow python-dotenv

# For Linux users
sudo apt-get install python3-pyaudio portaudio19-dev
```

## Configuration

Edit `config.ini` to customize:

```ini
[WHISPER]
MODEL_SIZE = base  # tiny, base, small, medium, large

[GEMINI] 
API_KEY = your_gemini_api_key_here

[HOTKEYS]
TOGGLE_LISTENING = ctrl+l
TOGGLE_VISIBILITY = ctrl+h
```

## Hotkeys

| Shortcut | Action |
|----------|--------|
| `Ctrl+L` | Toggle listening on/off |
| `Ctrl+H` | Hide/show window |
| `Ctrl+Q` | Quit application |

## Performance Tips

### GPU Optimization
- **RTX 4050+**: Use `base` or `small` Whisper model
- **RTX 3060+**: Use `small` model  
- **CPU only**: Use `tiny` model

### Audio Quality
- Use a **good quality microphone**
- **Minimize background noise**
- Position mic **6-12 inches** from mouth
- Test audio levels before interviews

### Interview Usage
1. **Position window** in a corner where you can glance at it
2. **Test all features** before the actual interview
3. **Use Ctrl+H** immediately when starting screen share
4. **Keep responses natural** - don't read verbatim

## Troubleshooting

### Common Issues

**"CUDA not available"**
- Install CUDA 11.8+ from NVIDIA
- Reinstall PyTorch with CUDA support

**"Microphone not accessible"**  
- Check system microphone permissions
- Try running as administrator (Windows)
- Check audio input device in system settings

**"Whisper model loading failed"**
- Check internet connection (first-time download)
- Ensure sufficient disk space (1-2GB per model)
- Try smaller model size

**"AI responses not generating"**
- Verify Gemini API key in config.ini
- Check internet connection
- Check API quotas/limits

### Audio Issues

**No transcription appearing:**
```bash
# Test microphone
python -c "import pyaudio; print('PyAudio working')"

# Test Whisper
python -c "import whisper; print('Whisper working')"
```

**Poor transcription quality:**
- Increase Whisper model size in config
- Improve microphone setup
- Reduce background noise

## Security & Privacy

- **Speech processing**: Done locally with Whisper
- **AI responses**: Sent to Gemini API (encrypted)
- **No data storage**: Conversations not saved permanently
- **Stealth mode**: Window can be completely hidden

## Development

### File Structure
```
interview_copilot.py     # Main application
setup_desktop.py         # Automated setup script
config.ini              # Configuration file
requirements_desktop.txt # Python dependencies
README_DESKTOP.md       # This file
```

### Extending
- Modify `generate_ai_response()` for custom prompts
- Adjust `is_question()` for better question detection
- Customize GUI in `setup_gui()` method

## License

This project is for educational and personal use only. Ensure compliance with your organization's policies before use in professional settings.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review logs in `interview_copilot.log`
3. Test individual components separately

---

**⚠️ Important**: Always test thoroughly before actual interviews and ensure compliance with your company's interview policies.