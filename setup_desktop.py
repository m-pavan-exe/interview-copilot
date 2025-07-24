#!/usr/bin/env python3
"""
Setup script for Desktop Interview Copilot
Installs all dependencies and checks system requirements
"""

import subprocess
import sys
import os
import platform
from pathlib import Path

def run_command(command, check=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {command}")
        print(f"Error: {e.stderr}")
        return None

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_cuda():
    """Check CUDA availability"""
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            print(f"✅ CUDA available - GPU: {gpu_name}")
            return True
        else:
            print("⚠️  CUDA not available - will use CPU (slower)")
            return False
    except ImportError:
        print("⚠️  PyTorch not installed - will install with CUDA support")
        return False

def install_pytorch():
    """Install PyTorch with CUDA support"""
    print("Installing PyTorch with CUDA support...")
    
    # CUDA 11.8 version (most compatible)
    cuda_version = "cu118"
    pytorch_command = f"pip install torch torchaudio --index-url https://download.pytorch.org/whl/{cuda_version}"
    
    result = run_command(pytorch_command, check=False)
    if result is not None:
        print("✅ PyTorch installed successfully")
        return True
    else:
        print("⚠️  Failed to install CUDA version, trying CPU version...")
        cpu_command = "pip install torch torchaudio"
        result = run_command(cpu_command, check=False)
        return result is not None

def install_whisper():
    """Install OpenAI Whisper"""
    print("Installing OpenAI Whisper...")
    result = run_command("pip install openai-whisper")
    if result is not None:
        print("✅ Whisper installed successfully")
        return True
    return False

def install_audio_dependencies():
    """Install audio processing dependencies"""
    print("Installing audio dependencies...")
    
    # Platform-specific audio libraries
    if platform.system() == "Windows":
        commands = [
            "pip install pyaudio",
            "pip install sounddevice"
        ]
    elif platform.system() == "Darwin":  # macOS
        commands = [
            "pip install pyaudio",
            "pip install sounddevice"
        ]
    else:  # Linux
        print("On Linux, you may need to install: sudo apt-get install python3-pyaudio portaudio19-dev")
        commands = [
            "pip install pyaudio",
            "pip install sounddevice"
        ]
    
    for cmd in commands:
        result = run_command(cmd, check=False)
        if result is None:
            print(f"⚠️  Failed to install: {cmd}")
            return False
    
    print("✅ Audio dependencies installed")
    return True

def install_remaining_requirements():
    """Install remaining requirements"""
    print("Installing remaining requirements...")
    result = run_command("pip install google-generativeai keyboard psutil Pillow python-dotenv requests")
    if result is not None:
        print("✅ All requirements installed")
        return True
    return False

def create_config_file():
    """Create configuration file"""
    config_content = '''# Interview Copilot Configuration
# You can modify these settings as needed

[AUDIO]
# Audio recording settings
CHUNK_SIZE = 1024
SAMPLE_RATE = 16000
CHANNELS = 1
RECORD_SECONDS = 3

[WHISPER]
# Whisper model settings
MODEL_SIZE = base  # tiny, base, small, medium, large
LANGUAGE = en

[GEMINI]
# Gemini API settings (set your API key here)
API_KEY = AIzaSyDo7zEUHg-YfjnUz2nSJQYpdFcpFbPSAUU
MODEL = gemini-2.5-pro-preview-05-06

[GUI]
# GUI settings
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 700
TRANSPARENCY = 0.95
ALWAYS_ON_TOP = true

[HOTKEYS]
# Global hotkeys
TOGGLE_LISTENING = ctrl+l
TOGGLE_VISIBILITY = ctrl+h
QUIT = ctrl+q
'''
    
    with open('config.ini', 'w') as f:
        f.write(config_content)
    
    print("✅ Configuration file created: config.ini")

def main():
    """Main setup function"""
    print("🎯 Interview Copilot Desktop Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies step by step
    print("\n📦 Installing dependencies...")
    
    # 1. PyTorch with CUDA
    if not install_pytorch():
        print("❌ Failed to install PyTorch")
        sys.exit(1)
    
    # 2. Check CUDA after PyTorch installation
    check_cuda()
    
    # 3. Whisper
    if not install_whisper():
        print("❌ Failed to install Whisper")
        sys.exit(1)
    
    # 4. Audio dependencies
    if not install_audio_dependencies():
        print("❌ Failed to install audio dependencies")
        print("You may need to install system audio libraries manually")
    
    # 5. Remaining requirements
    if not install_remaining_requirements():
        print("❌ Failed to install some requirements")
        sys.exit(1)
    
    # 6. Create config file
    create_config_file()
    
    print("\n✅ Setup completed successfully!")
    print("\n🚀 To run the Interview Copilot:")
    print("   python interview_copilot.py")
    print("\n📋 Hotkeys:")
    print("   Ctrl+L: Toggle listening")
    print("   Ctrl+H: Hide/Show window")
    print("   Ctrl+Q: Quit application")
    print("\n💡 Tips:")
    print("   - Grant microphone permissions when prompted")
    print("   - Position window where you can see it during interviews")
    print("   - Use Ctrl+H to hide when screen sharing")

if __name__ == "__main__":
    main()