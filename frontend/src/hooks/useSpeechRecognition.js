import { useState, useEffect, useRef, useCallback } from 'react';

export const useSpeechRecognition = () => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [error, setError] = useState(null);
  const [isSupported, setIsSupported] = useState(false);
  const [permission, setPermission] = useState('prompt');

  const recognitionRef = useRef(null);
  const silenceTimeoutRef = useRef(null);
  const restartTimeoutRef = useRef(null);

  // Check browser support and permissions
  useEffect(() => {
    const checkSupport = async () => {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      
      if (!SpeechRecognition) {
        setError('Speech recognition not supported in this browser');
        setIsSupported(false);
        return;
      }

      setIsSupported(true);

      // Check microphone permission
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        stream.getTracks().forEach(track => track.stop());
        setPermission('granted');
      } catch (err) {
        if (err.name === 'NotAllowedError') {
          setPermission('denied');
          setError('Microphone permission denied');
        } else {
          setError('Microphone not accessible');
        }
      }
    };

    checkSupport();
  }, []);

  // Initialize speech recognition
  useEffect(() => {
    if (!isSupported || permission !== 'granted') return;

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognitionRef.current = new SpeechRecognition();

    const recognition = recognitionRef.current;
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
      console.log('Speech recognition started');
      setError(null);
    };

    recognition.onresult = (event) => {
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
        setTranscript(prev => prev + finalTranscript);
        setInterimTranscript('');
        
        // Reset silence timeout
        if (silenceTimeoutRef.current) {
          clearTimeout(silenceTimeoutRef.current);
        }
        
        // Set silence timeout for processing
        silenceTimeoutRef.current = setTimeout(() => {
          // Trigger processing after 2 seconds of silence
          if (finalTranscript.trim()) {
            // This will be handled by the parent component
            const event = new CustomEvent('speechFinal', { 
              detail: { transcript: finalTranscript.trim() } 
            });
            window.dispatchEvent(event);
          }
        }, 2000);
      } else {
        setInterimTranscript(interimTranscript);
      }
    };

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      
      switch (event.error) {
        case 'no-speech':
          setError('No speech detected. Please speak clearly.');
          break;
        case 'audio-capture':
          setError('Microphone not accessible');
          setIsListening(false);
          break;
        case 'not-allowed':
          setError('Microphone permission denied');
          setPermission('denied');
          setIsListening(false);
          break;
        case 'network':
          setError('Network error occurred');
          break;
        default:
          setError(`Recognition error: ${event.error}`);
      }
    };

    recognition.onend = () => {
      console.log('Speech recognition ended');
      
      // Auto-restart if we should be listening
      if (isListening) {
        restartTimeoutRef.current = setTimeout(() => {
          if (isListening && recognitionRef.current) {
            try {
              recognitionRef.current.start();
            } catch (err) {
              console.error('Failed to restart recognition:', err);
              setIsListening(false);
            }
          }
        }, 100);
      }
    };

    return () => {
      if (recognition) {
        recognition.stop();
      }
    };
  }, [isSupported, permission, isListening]);

  const startListening = useCallback(async () => {
    if (!isSupported) {
      setError('Speech recognition not supported');
      return false;
    }

    if (permission !== 'granted') {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        stream.getTracks().forEach(track => track.stop());
        setPermission('granted');
      } catch (err) {
        setError('Microphone permission required');
        return false;
      }
    }

    if (recognitionRef.current && !isListening) {
      try {
        setTranscript('');
        setInterimTranscript('');
        setError(null);
        recognitionRef.current.start();
        setIsListening(true);
        return true;
      } catch (err) {
        setError('Failed to start speech recognition');
        return false;
      }
    }
    return false;
  }, [isSupported, permission, isListening]);

  const stopListening = useCallback(() => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
      
      // Clear timeouts
      if (silenceTimeoutRef.current) {
        clearTimeout(silenceTimeoutRef.current);
      }
      if (restartTimeoutRef.current) {
        clearTimeout(restartTimeoutRef.current);
      }
    }
  }, [isListening]);

  const resetTranscript = useCallback(() => {
    setTranscript('');
    setInterimTranscript('');
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (silenceTimeoutRef.current) {
        clearTimeout(silenceTimeoutRef.current);
      }
      if (restartTimeoutRef.current) {
        clearTimeout(restartTimeoutRef.current);
      }
    };
  }, []);

  return {
    isListening,
    transcript,
    interimTranscript,
    error,
    isSupported,
    permission,
    startListening,
    stopListening,
    resetTranscript,
  };
};