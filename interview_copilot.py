#!/usr/bin/env python3
"""
Desktop Interview Copilot - Invisible Assistant for Job Interviews
Features: GPU-accelerated speech recognition, AI responses, stealth UI

Requirements: 
- NVIDIA GPU (4050 or better)
- Python 3.8+
- CUDA-enabled PyTorch

Author: AI Assistant
Version: 1.0
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import queue
import time
import json
import os
from datetime import datetime
import logging
import traceback

# Audio processing imports
import pyaudio
import wave
import numpy as np
import whisper
import torch

# API integration
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# System integration
import keyboard
import psutil
from PIL import Image, ImageTk

class InterviewCopilot:
    def __init__(self):
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.audio_queue = queue.Queue()
        self.transcript_queue = queue.Queue()
        self.response_queue = queue.Queue()
        
        # Audio settings
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 2
        self.RATE = 16000
        self.RECORD_SECONDS = 8  # Process audio in 3-second chunks
        
        # State variables
        self.is_listening = False
        self.is_processing = False
        self.is_hidden = False
        self.current_session_id = None
        self.transcript_history = []
        
        # Initialize AI components
        self.setup_whisper()
        self.setup_gemini()
        
        # Initialize GUI
        self.setup_gui()
        self.setup_hotkeys()
        
        # Start background threads
        self.start_background_threads()
        
        self.logger.info("Interview Copilot initialized successfully")
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('interview_copilot.log'),
                logging.StreamHandler()
            ]
        )
    
    def setup_whisper(self):
        """Initialize Whisper model with GPU acceleration"""
        try:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self.logger.info(f"Loading Whisper model on {device}")
            
            # Use small model for real-time performance, base for better accuracy
            model_size = "medium.en" if torch.cuda.is_available() else "medium.en"
            self.whisper_model = whisper.load_model(model_size, device=device)
            
            self.logger.info(f"Whisper model '{model_size}' loaded successfully on {device}")
            
            # GPU info
            if torch.cuda.is_available():
                gpu_name = torch.cuda.get_device_name(0)
                self.logger.info(f"Using GPU: {gpu_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to load Whisper model: {e}")
            messagebox.showerror("Error", f"Failed to load speech recognition model: {e}")
    
    def setup_gemini(self):
        """Initialize Gemini API"""
        try:
            # API key - you can set this in environment or here
            api_key = "AIzaSyDo7zEUHg-YfjnUz2nSJQYpdFcpFbPSAUU"  # Your provided key
            genai.configure(api_key=api_key)
            
            # Initialize model
            self.gemini_model = genai.GenerativeModel(
                model_name="gemini-2.5-flash",
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.8,
                    "top_k": 40,
                    "max_output_tokens": 1024,
                },
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                }
            )
            
            # Start conversation with system message
            self.chat = self.gemini_model.start_chat(history=[])
            
            system_message = """You are an expert interview copilot assistant specialized in Software engineering, AI, ML, DL. Your role is to help the interviewee answer questions professionally and effectively.

When given an interview question, provide:
1. A clear, concise, and professional answer
2. Key points to emphasize  
3. Examples or experiences to mention if relevant

Keep responses natural, authentic, and appropriate for a professional interview setting.
Format your response to be easy to read quickly during an interview.

Structure your response as:
**Main Answer:** [Direct response to the question]
**Key Points:** [2-3 bullet points of important aspects to mention]
**Example/Experience:** [If relevant, suggest a brief example to share]"""

            # Send system message
            self.chat.send_message(system_message)
            
            self.logger.info("Gemini API initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Gemini API: {e}")
            messagebox.showerror("Error", f"Failed to initialize AI model: {e}")
    
    def setup_gui(self):
        """Initialize the GUI"""
        self.root = tk.Tk()
        self.root.title("Interview Copilot")
        self.root.geometry("500x700")
        self.root.configure(bg='#1e293b')
        
        # Make window always on top and semi-transparent
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.95)
        
        # Configure colors
        self.colors = {
            'bg': '#1e293b',
            'panel': '#334155',
            'accent': '#10b981',
            'text': '#f1f5f9',
            'muted': '#94a3b8'
        }
        
        # Configure styles
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Dark.TFrame', background=self.colors['bg'])
        style.configure('Panel.TFrame', background=self.colors['panel'])
        
        # Main container
        main_frame = ttk.Frame(self.root, style='Dark.TFrame')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Header
        header_frame = ttk.Frame(main_frame, style='Panel.TFrame')
        header_frame.pack(fill='x', pady=(0, 10))
        
        title_label = tk.Label(
            header_frame, 
            text="🎯 Interview Copilot", 
            font=('Arial', 16, 'bold'),
            bg=self.colors['panel'], 
            fg=self.colors['text']
        )
        title_label.pack(pady=10)
        
        # Status frame
        status_frame = ttk.Frame(header_frame, style='Panel.TFrame')
        status_frame.pack(fill='x', padx=10, pady=5)
        
        self.status_label = tk.Label(
            status_frame,
            text="🔴 Ready to start",
            font=('Arial', 10),
            bg=self.colors['panel'],
            fg=self.colors['muted']
        )
        self.status_label.pack(side='left')
        
        self.gpu_label = tk.Label(
            status_frame,
            text=f"GPU: {'✅' if torch.cuda.is_available() else '❌'}",
            font=('Arial', 9),
            bg=self.colors['panel'],
            fg=self.colors['muted']
        )
        self.gpu_label.pack(side='right')
        
        # Controls frame
        controls_frame = ttk.Frame(main_frame, style='Panel.TFrame')
        controls_frame.pack(fill='x', pady=(0, 10))
        
        # Control buttons
        button_frame = tk.Frame(controls_frame, bg=self.colors['panel'])
        button_frame.pack(pady=10)
        
        self.listen_button = tk.Button(
            button_frame,
            text="🎤 Start Listening",
            command=self.toggle_listening,
            bg=self.colors['accent'],
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=20,
            pady=5
        )
        self.listen_button.pack(side='left', padx=5)
        
        self.hide_button = tk.Button(
            button_frame,
            text="👁️ Hide",
            command=self.toggle_visibility,
            bg=self.colors['panel'],
            fg=self.colors['text'],
            font=('Arial', 10),
            padx=15,
            pady=5
        )
        self.hide_button.pack(side='left', padx=5)
        
        # Live transcript section
        transcript_frame = ttk.Frame(main_frame, style='Panel.TFrame')
        transcript_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        transcript_label = tk.Label(
            transcript_frame,
            text="📝 Live Transcript",
            font=('Arial', 12, 'bold'),
            bg=self.colors['panel'],
            fg=self.colors['text']
        )
        transcript_label.pack(anchor='w', padx=10, pady=(10, 5))
        
        self.transcript_text = scrolledtext.ScrolledText(
            transcript_frame,
            height=4,
            bg='#0f172a',
            fg=self.colors['text'],
            font=('Arial', 10),
            wrap='word'
        )
        self.transcript_text.pack(fill='x', padx=10, pady=(0, 10))
        
        # AI response section
        response_label = tk.Label(
            transcript_frame,
            text="🤖 AI Response",
            font=('Arial', 12, 'bold'),
            bg=self.colors['panel'],
            fg=self.colors['text']
        )
        response_label.pack(anchor='w', padx=10, pady=(10, 5))
        
        self.response_text = scrolledtext.ScrolledText(
            transcript_frame,
            height=8,
            bg='#064e3b',
            fg='#d1fae5',
            font=('Arial', 10),
            wrap='word'
        )
        self.response_text.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Shortcuts info
        shortcuts_label = tk.Label(
            main_frame,
            text="Shortcuts: Ctrl+L (Listen) | Ctrl+H (Hide) | Ctrl+Q (Quit)",
            font=('Arial', 8),
            bg=self.colors['bg'],
            fg=self.colors['muted']
        )
        shortcuts_label.pack(pady=(5, 0))
        
        # Protocol for window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_hotkeys(self):
        """Setup global hotkeys"""
        try:
            keyboard.add_hotkey('ctrl+l', self.toggle_listening)
            keyboard.add_hotkey('ctrl+h', self.toggle_visibility)  
            keyboard.add_hotkey('ctrl+q', self.on_closing)
            self.logger.info("Global hotkeys registered successfully")
        except Exception as e:
            self.logger.error(f"Failed to register hotkeys: {e}")
    
    def start_background_threads(self):
        """Start background processing threads"""
        # Audio processing thread
        self.audio_thread = threading.Thread(target=self.audio_processor, daemon=True)
        self.audio_thread.start()
        
        # Transcript processing thread
        self.transcript_thread = threading.Thread(target=self.transcript_processor, daemon=True)
        self.transcript_thread.start()
        
        # Response processing thread
        self.response_thread = threading.Thread(target=self.response_processor, daemon=True)
        self.response_thread.start()
        
        # GUI update thread
        self.gui_thread = threading.Thread(target=self.gui_updater, daemon=True)
        self.gui_thread.start()
    
    def toggle_listening(self):
        """Toggle speech recognition on/off"""
        if self.is_listening:
            self.stop_listening()
        else:
            self.start_listening()
    
    def start_listening(self):
        """Start speech recognition"""
        try:
            self.is_listening = True
            self.listen_button.config(text="🔴 Stop Listening", bg='#dc2626')
            self.status_label.config(text="🎤 Listening...", fg=self.colors['accent'])
            
            # Start audio capture
            self.audio_capture_thread = threading.Thread(target=self.capture_audio, daemon=True)
            self.audio_capture_thread.start()
            
            self.logger.info("Started listening")
            
        except Exception as e:
            self.logger.error(f"Failed to start listening: {e}")
            messagebox.showerror("Error", f"Failed to start listening: {e}")
            self.is_listening = False
    
    def stop_listening(self):
        """Stop speech recognition"""
        self.is_listening = False
        self.listen_button.config(text="🎤 Start Listening", bg=self.colors['accent'])
        self.status_label.config(text="🔴 Ready to start", fg=self.colors['muted'])
        self.logger.info("Stopped listening")
    
    def capture_audio(self):
        """Capture audio from microphone"""
        try:
            audio = pyaudio.PyAudio()
            
            stream = audio.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK
            )
            
            self.logger.info("Audio capture started")
            
            while self.is_listening:
                frames = []
                for _ in range(0, int(self.RATE / self.CHUNK * self.RECORD_SECONDS)):
                    if not self.is_listening:
                        break
                    data = stream.read(self.CHUNK)
                    frames.append(data)
                
                if frames and self.is_listening:
                    # Convert to numpy array
                    audio_data = b''.join(frames)
                    audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
                    
                    # Add to processing queue
                    self.audio_queue.put(audio_np)
            
            stream.stop_stream()
            stream.close()
            audio.terminate()
            
        except Exception as e:
            self.logger.error(f"Audio capture error: {e}")
            self.is_listening = False
    
    def audio_processor(self):
        """Process audio data with Whisper"""
        while True:
            try:
                if not self.audio_queue.empty():
                    audio_data = self.audio_queue.get()
                    
                    # Process with Whisper
                    result = self.whisper_model.transcribe(
                        audio_data,
                        language='en',
                        fp16=torch.cuda.is_available()
                    )
                    
                    text = result['text'].strip()
                    if text and len(text) > 2:  # Filter out very short utterances
                        self.transcript_queue.put({
                            'text': text,
                            'timestamp': datetime.now(),
                            'confidence': 1.0  # Whisper doesn't provide confidence
                        })
                
                time.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Audio processing error: {e}")
                time.sleep(1)
    
    def transcript_processor(self):
        """Process transcripts and generate AI responses"""
        while True:
            try:
                if not self.transcript_queue.empty():
                    transcript_data = self.transcript_queue.get()
                    text = transcript_data['text']
                    
                    # Add to conversation history
                    self.transcript_history.append(transcript_data)
                    
                    # Keep only last 10 entries
                    if len(self.transcript_history) > 10:
                        self.transcript_history.pop(0)
                    
                    # Update transcript display
                    self.update_transcript_display(text)
                    
                    # Generate AI response if this looks like a question
                    if self.is_question(text):
                        self.generate_ai_response(text)
                
                time.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Transcript processing error: {e}")
                time.sleep(1)
    
    def is_question(self, text):
        """Simple heuristic to determine if text is a question"""
        question_indicators = ['?', 'what', 'how', 'why', 'when', 'where', 'who', 'can you', 'tell me', 'describe', 'explain']
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in question_indicators) or len(text) > 20
    
    def generate_ai_response(self, question):
        """Generate AI response using Gemini"""
        try:
            self.is_processing = True
            self.status_label.config(text="🤖 Generating response...", fg='#f59e0b')
            
            # Build context from recent conversation
            context = "Recent conversation:\n"
            for entry in self.transcript_history[-5:]:  # Last 5 entries
                context += f"- {entry['text']}\n"
            
            full_prompt = f"{context}\n\nCurrent question: {question}\n\nPlease provide a professional interview response:"
            
            response = self.chat.send_message(full_prompt)
            
            self.response_queue.put({
                'question': question,
                'response': response.text,
                'timestamp': datetime.now()
            })
            
        except Exception as e:
            self.logger.error(f"AI response generation error: {e}")
            self.response_queue.put({
                'question': question,
                'response': f"Error generating response: {str(e)}",
                'timestamp': datetime.now()
            })
        finally:
            self.is_processing = False
            self.status_label.config(text="🎤 Listening...", fg=self.colors['accent'])
    
    def response_processor(self):
        """Process AI responses"""
        while True:
            try:
                if not self.response_queue.empty():
                    response_data = self.response_queue.get()
                    self.update_response_display(response_data['response'])
                
                time.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Response processing error: {e}")
                time.sleep(1)
    
    def update_transcript_display(self, text):
        """Update transcript display in GUI"""
        def update():
            self.transcript_text.delete(1.0, tk.END)
            self.transcript_text.insert(tk.END, text)
            self.transcript_text.see(tk.END)
        
        self.root.after(0, update)
    
    def update_response_display(self, response):
        """Update AI response display in GUI"""
        def update():
            self.response_text.delete(1.0, tk.END)
            self.response_text.insert(tk.END, response)
            self.response_text.see(tk.END)
        
        self.root.after(0, update)
    
    def gui_updater(self):
        """Update GUI elements periodically"""
        while True:
            try:
                # Update queue sizes in status
                if hasattr(self, 'status_label'):
                    def update_status():
                        if self.is_processing:
                            status = "🤖 Processing..."
                        elif self.is_listening:
                            status = f"🎤 Listening... (Q:{self.audio_queue.qsize()})"
                        else:
                            status = "🔴 Ready to start"
                        
                        if hasattr(self, 'status_label'):
                            self.status_label.config(text=status)
                    
                    self.root.after(0, update_status)
                
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"GUI update error: {e}")
                time.sleep(5)
    
    def toggle_visibility(self):
        """Toggle window visibility"""
        if self.is_hidden:
            self.root.deiconify()
            self.root.attributes('-topmost', True)
            self.is_hidden = False
            self.logger.info("Window shown")
        else:
            self.root.withdraw()
            self.is_hidden = True
            self.logger.info("Window hidden")
    
    def on_closing(self):
        """Handle application closing"""
        self.logger.info("Shutting down Interview Copilot")
        self.is_listening = False
        time.sleep(0.5)  # Allow threads to finish
        self.root.destroy()
    
    def run(self):
        """Start the application"""
        try:
            self.logger.info("Starting Interview Copilot GUI")
            self.root.mainloop()
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")
            self.on_closing()
        except Exception as e:
            self.logger.error(f"Application error: {e}")
            traceback.print_exc()

def main():
    """Main application entry point"""
    print("🎯 Interview Copilot - Desktop Version")
    print("=" * 50)
    
    # Check requirements
    if not torch.cuda.is_available():
        print("⚠️  Warning: CUDA not available. Speech recognition will be slower.")
    else:
        print(f"✅ GPU detected: {torch.cuda.get_device_name(0)}")
    
    try:
        app = InterviewCopilot()
        app.run()
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()