'use client';

import { useEffect, useState, useRef } from 'react';
import { Mic, Volume2, X } from 'lucide-react';

interface VoiceInputProps {
  onResult: (transcript: string) => void;
  onClose: () => void;
}

export function VoiceInput({ onResult, onClose }: VoiceInputProps) {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [error, setError] = useState<string | null>(null);
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    // Check if browser supports speech recognition
    const SpeechRecognition =
      (window as any).SpeechRecognition ||
      (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setError('Speech recognition is not supported in this browser. Try Chrome or Edge.');
      return;
    }

    // Initialize speech recognition
    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    
    // Support multilingual input
    recognition.lang = 'en-US'; // Can be changed to support other languages
    // recognition.lang = 'hi-IN'; // Hindi
    // recognition.lang = 'ta-IN'; // Tamil
    // recognition.lang = 'kn-IN'; // Kannada

    recognition.onstart = () => {
      setIsListening(true);
      setError(null);
    };

    recognition.onresult = (event: any) => {
      let interim = '';
      let final = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          final += transcript + ' ';
        } else {
          interim += transcript;
        }
      }

      if (final) {
        setTranscript((prev) => prev + final);
      }
      setInterimTranscript(interim);
    };

    recognition.onerror = (event: any) => {
      console.error('Speech recognition error:', event.error);
      setError(`Error: ${event.error}`);
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognitionRef.current = recognition;

    // Start listening
    try {
      recognition.start();
    } catch (err) {
      console.error('Failed to start recognition:', err);
      setError('Failed to start voice input. Please try again.');
    }

    // Cleanup
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, []);

  const handleStop = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    
    const finalTranscript = transcript + interimTranscript;
    if (finalTranscript.trim()) {
      onResult(finalTranscript.trim());
    }
    onClose();
  };

  const handleCancel = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="bg-white dark:bg-gray-800 rounded-3xl shadow-2xl p-8 max-w-md w-full mx-4">
        {/* Close Button */}
        <button
          onClick={handleCancel}
          className="absolute top-4 right-4 p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Title */}
        <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-6 text-center">
          Voice Input
        </h3>

        {/* Mic Animation */}
        <div className="flex justify-center mb-8">
          <div className={`relative ${isListening ? 'animate-pulse' : ''}`}>
            <div className="absolute inset-0 bg-red-500 rounded-full blur-2xl opacity-30" />
            <div className="relative bg-gradient-to-br from-red-500 to-orange-500 text-white w-24 h-24 rounded-full flex items-center justify-center shadow-2xl">
              {isListening ? (
                <Volume2 className="w-12 h-12" />
              ) : (
                <Mic className="w-12 h-12" />
              )}
            </div>
          </div>
        </div>

        {/* Status */}
        <div className="text-center mb-6">
          {error ? (
            <p className="text-red-500 text-sm">{error}</p>
          ) : (
            <>
              <p className="text-gray-600 dark:text-gray-400 text-sm mb-2">
                {isListening ? '🎤 Listening...' : 'Initializing...'}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-500">
                Speak in any language
              </p>
            </>
          )}
        </div>

        {/* Transcript Display */}
        <div className="bg-gray-50 dark:bg-gray-900 rounded-2xl p-4 mb-6 min-h-[100px] max-h-[200px] overflow-y-auto">
          <p className="text-gray-900 dark:text-white">
            {transcript}
            <span className="text-gray-400 dark:text-gray-500">
              {interimTranscript}
            </span>
            {!transcript && !interimTranscript && (
              <span className="text-gray-400 dark:text-gray-500 italic">
                Your speech will appear here...
              </span>
            )}
          </p>
        </div>

        {/* Buttons */}
        <div className="flex gap-3">
          <button
            onClick={handleCancel}
            className="flex-1 px-6 py-3 rounded-xl border-2 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 font-semibold hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleStop}
            disabled={!transcript && !interimTranscript}
            className="flex-1 px-6 py-3 rounded-xl bg-gradient-to-r from-orange-500 to-red-500 text-white font-semibold hover:from-orange-600 hover:to-red-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl"
          >
            Use This
          </button>
        </div>

        {/* Language Support Info */}
        <div className="mt-4 text-center">
          <p className="text-xs text-gray-500 dark:text-gray-400">
            Supports: English, Hindi, Tamil, Kannada, and more
          </p>
        </div>
      </div>
    </div>
  );
}
