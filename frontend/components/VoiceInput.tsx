'use client'

import { useState, useRef } from 'react'
import { Mic, MicOff, Loader2, AlertCircle } from 'lucide-react'

interface VoiceInputProps {
  onTranscription: (text: string) => void
  language: string  // CRITICAL: Language is now required from parent
  disabled?: boolean
}

export default function VoiceInput({ onTranscription, language, disabled = false }: VoiceInputProps) {
  const [isRecording, setIsRecording] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<Blob[]>([])

  const startRecording = async () => {
    // CRITICAL: Check if language is selected
    if (!language) {
      setError('Please select a language before recording')
      return
    }

    try {
      setError(null)
      
      // Request microphone permission
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          channelCount: 1,
          sampleRate: 16000,
          echoCancellation: true,
          noiseSuppression: true,
        } 
      })
      
      // Create MediaRecorder with webm format (best compatibility)
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      })
      
      chunksRef.current = []
      
      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data)
        }
      }
      
      mediaRecorder.onstop = async () => {
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop())
        
        // Create audio blob
        const audioBlob = new Blob(chunksRef.current, { type: 'audio/webm' })
        
        // Transcribe
        await transcribeAudio(audioBlob)
      }
      
      mediaRecorder.start()
      mediaRecorderRef.current = mediaRecorder
      setIsRecording(true)
      
    } catch (err: any) {
      console.error('Error accessing microphone:', err)
      setError('Could not access microphone. Please check permissions.')
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
      setIsProcessing(true)
    }
  }

  const transcribeAudio = async (audioBlob: Blob) => {
    try {
      const formData = new FormData()
      formData.append('audio', audioBlob, 'recording.webm')
      
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      
      // CRITICAL: Send language parameter
      const response = await fetch(`${API_URL}/api/transcribe?language=${language}`, {
        method: 'POST',
        body: formData,
      })
      
      if (!response.ok) {
        const errorData = await response.json()
        
        // Handle language_required error specifically
        if (errorData.error === 'language_required') {
          throw new Error('Please select a language before recording')
        }
        
        throw new Error(errorData.detail || 'Transcription failed')
      }
      
      const data = await response.json()
      
      if (data.status === 'success' && data.transcription) {
        onTranscription(data.transcription)
        
        // Show success feedback
        console.log('✅ Transcription successful')
        console.log('Detected language:', data.detected_language)
        console.log('Cost:', `$${data.cost_usd.toFixed(6)}`)
        
        // Show warnings if any
        if (data.warnings && data.warnings.length > 0) {
          console.warn('⚠️ Warnings:', data.warnings)
        }
      } else {
        throw new Error('No transcription received')
      }
      
    } catch (err: any) {
      console.error('Transcription error:', err)
      setError(err.message || 'Failed to transcribe audio')
    } finally {
      setIsProcessing(false)
    }
  }

  const handleClick = () => {
    if (isRecording) {
      stopRecording()
    } else {
      startRecording()
    }
  }

  // Check if disabled due to no language selection
  const isDisabledNoLang = !language

  return (
    <div className="flex flex-col items-center gap-2">
      <button
        onClick={handleClick}
        disabled={disabled || isProcessing || isDisabledNoLang}
        className={`
          p-3 rounded-full transition-all duration-300 shadow-lg
          ${isRecording 
            ? 'bg-red-500 hover:bg-red-600 animate-pulse' 
            : isDisabledNoLang
            ? 'bg-gray-600 cursor-not-allowed'
            : 'bg-blue-500 hover:bg-blue-600'
          }
          ${(disabled || isProcessing || isDisabledNoLang) ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer hover:scale-110'}
          text-white
        `}
        title={
          isDisabledNoLang 
            ? 'Please select a language first' 
            : isRecording 
            ? 'Stop recording' 
            : 'Start voice search'
        }
      >
        {isProcessing ? (
          <Loader2 className="w-6 h-6 animate-spin" />
        ) : isRecording ? (
          <MicOff className="w-6 h-6" />
        ) : (
          <Mic className="w-6 h-6" />
        )}
      </button>
      
      {/* Status messages */}
      {isDisabledNoLang && (
        <div className="text-sm text-yellow-400 font-medium flex items-center gap-1">
          <AlertCircle className="w-4 h-4" />
          <span>Select language first</span>
        </div>
      )}
      
      {isRecording && (
        <div className="text-sm text-red-500 font-medium animate-pulse">
          Recording...
        </div>
      )}
      
      {isProcessing && (
        <div className="text-sm text-blue-500 font-medium">
          Transcribing...
        </div>
      )}
      
      {error && (
        <div className="text-sm text-red-500 max-w-xs text-center">
          {error}
        </div>
      )}
    </div>
  )
}
