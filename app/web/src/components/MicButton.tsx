'use client';

import React, { useState } from 'react';
import { Mic, MicOff, Loader2 } from 'lucide-react';
import { AudioRecorder } from '@/lib/audio-recorder';
import { apiClient } from '@/lib/api-client';

interface MicButtonProps {
  onTranscript: (transcript: string, lang: string) => void;
  onError?: (error: string) => void;
}

export function MicButton({ onTranscript, onError }: MicButtonProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [recorder] = useState(() => new AudioRecorder());

  const handleStartRecording = async () => {
    try {
      await recorder.startRecording();
      setIsRecording(true);
    } catch (error) {
      console.error('Recording failed:', error);
      onError?.(error instanceof Error ? error.message : 'Failed to start recording');
    }
  };

  const handleStopRecording = async () => {
    try {
      setIsRecording(false);
      setIsProcessing(true);

      const audioBase64 = await recorder.stopRecording();
      
      // Send to STT API
      const result = await apiClient.stt(audioBase64, 'webm');
      
      if (result.confidence < 0.5) {
        onError?.('Low confidence transcription. Please try again.');
      }
      
      onTranscript(result.transcript, result.lang);
    } catch (error) {
      console.error('STT failed:', error);
      onError?.(error instanceof Error ? error.message : 'Speech recognition failed');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleClick = () => {
    if (isRecording) {
      handleStopRecording();
    } else {
      handleStartRecording();
    }
  };

  return (
    <button
      onClick={handleClick}
      disabled={isProcessing}
      className={`
        p-3 rounded-full transition-all duration-200
        ${isRecording 
          ? 'bg-red-500 hover:bg-red-600 animate-pulse' 
          : 'bg-primary-500 hover:bg-primary-600'
        }
        ${isProcessing ? 'opacity-50 cursor-not-allowed' : ''}
        text-white shadow-lg
      `}
      title={isRecording ? 'Stop recording' : 'Start voice input'}
    >
      {isProcessing ? (
        <Loader2 className="w-5 h-5 animate-spin" />
      ) : isRecording ? (
        <MicOff className="w-5 h-5" />
      ) : (
        <Mic className="w-5 h-5" />
      )}
    </button>
  );
}
