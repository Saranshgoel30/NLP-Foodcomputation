'use client'

import React, { useState, useEffect, useRef } from 'react'
import { X, Mic, Square, Loader2, Check, AlertCircle } from 'lucide-react'
import { Button } from '@/components/ui/Button'

interface VoiceSearchModalProps {
  isOpen: boolean
  onClose: () => void
  language: string
  onTranscript?: (text: string) => void
}

export default function VoiceSearchModal({ isOpen, onClose, language, onTranscript }: VoiceSearchModalProps) {
  const [isRecording, setIsRecording] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [error, setError] = useState('')
  const [audioLevel, setAudioLevel] = useState(0)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const animationRef = useRef<number>()

  useEffect(() => {
    if (!isOpen) {
      stopRecording()
      setTranscript('')
      setError('')
    }
  }, [isOpen])

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder

      const audioChunks: Blob[] = []
      mediaRecorder.ondataavailable = (event) => {
        audioChunks.push(event.data)
      }

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' })
        await processAudio(audioBlob)
        stream.getTracks().forEach(track => track.stop())
      }

      mediaRecorder.start()
      setIsRecording(true)
      setError('')
      animateAudioLevel()
    } catch (err) {
      setError('Microphone access denied')
      console.error(err)
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
    }
  }

  const animateAudioLevel = () => {
    // Simulate audio level animation
    const animate = () => {
      setAudioLevel(Math.random() * 100)
      animationRef.current = requestAnimationFrame(animate)
    }
    animate()
  }

  const processAudio = async (audioBlob: Blob) => {
    setIsProcessing(true)
    try {
      // Convert blob to base64
      const base64Audio = await blobToBase64(audioBlob)
      
      // TODO: Call your NLP pipeline API
      const response = await fetch('/api/voice-query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          audio: base64Audio,
          language: language
        })
      })

      const data = await response.json()
      setTranscript(data.transcript || 'Could not transcribe audio')
      
      if (onTranscript && data.transcript) {
        onTranscript(data.transcript)
      }
    } catch (err) {
      setError('Failed to process audio. Using demo mode.')
      // Demo mode: simulate transcription
      const demoTranscripts = {
        'hi': 'मुझे पनीर की रेसिपी चाहिए',
        'ta': 'எனக்கு சைவ பிரியாணி வேண்டும்',
        'en': 'Show me vegetarian recipes without onions'
      }
      setTranscript(demoTranscripts[language as keyof typeof demoTranscripts] || demoTranscripts.en)
    } finally {
      setIsProcessing(false)
    }
  }

  const blobToBase64 = (blob: Blob): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onloadend = () => {
        const base64 = (reader.result as string).split(',')[1]
        resolve(base64)
      }
      reader.onerror = reject
      reader.readAsDataURL(blob)
    })
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60">
      <div className="relative w-full max-w-lg bg-white rounded-xl shadow-xl p-8">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 rounded-lg hover:bg-gray-100 transition-colors"
        >
          <X className="w-5 h-5 text-gray-500" />
        </button>

        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-orange-600 mb-4">
            <Mic className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Voice Search</h2>
          <p className="text-gray-600">
            Speak in {language === 'hi' ? 'Hindi' : language === 'ta' ? 'Tamil' : language === 'te' ? 'Telugu' : 'English'}
          </p>
        </div>

        {/* Recording Status */}
        <div className="mb-8">
          {isRecording && (
            <div className="space-y-4">
              <div className="flex justify-center">
                <div className="relative">
                  <div className="absolute inset-0 bg-red-500 rounded-full animate-ping opacity-75"></div>
                  <div className="relative bg-red-500 rounded-full w-20 h-20"></div>
                </div>
              </div>
              
              {/* Audio Visualizer */}
              <div className="flex items-end justify-center gap-1 h-12">
                {[...Array(20)].map((_, i) => (
                  <div
                    key={i}
                    className="w-1 bg-orange-600 rounded-full transition-all duration-150"
                    style={{
                      height: `${Math.max(10, audioLevel * Math.random())}%`
                    }}
                  />
                ))}
              </div>
              
              <p className="text-center text-gray-600 font-medium">Listening...</p>
            </div>
          )}

          {isProcessing && (
            <div className="flex flex-col items-center gap-4">
              <Loader2 className="w-12 h-12 text-orange-500 animate-spin" />
              <p className="text-gray-600 font-medium">Processing your voice...</p>
            </div>
          )}

          {transcript && !isRecording && !isProcessing && (
            <div className="space-y-4">
              <div className="flex justify-center">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-green-100">
                  <Check className="w-8 h-8 text-green-600" />
                </div>
              </div>
              <div className="bg-gray-50 rounded-2xl p-4">
                <p className="text-sm text-gray-500 mb-1">Transcript:</p>
                <p className="text-lg text-gray-900 font-medium">{transcript}</p>
              </div>
            </div>
          )}

          {error && (
            <div className="flex items-start gap-3 bg-red-50 rounded-2xl p-4">
              <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="flex gap-3">
          {!isRecording && !isProcessing && !transcript && (
            <Button
              onClick={startRecording}
              size="lg"
              className="flex-1"
            >
              <Mic className="w-5 h-5 mr-2" />
              Start Recording
            </Button>
          )}

          {isRecording && (
            <Button
              onClick={stopRecording}
              variant="destructive"
              size="lg"
              className="flex-1"
            >
              <Square className="w-5 h-5 mr-2" />
              Stop Recording
            </Button>
          )}

          {transcript && !isRecording && !isProcessing && (
            <>
              <Button
                onClick={() => {
                  setTranscript('')
                  setError('')
                }}
                variant="outline"
                size="lg"
                className="flex-1"
              >
                Try Again
              </Button>
              <Button
                onClick={() => {
                  if (onTranscript) {
                    onTranscript(transcript)
                  }
                  onClose()
                }}
                size="lg"
                className="flex-1"
              >
                Search
              </Button>
            </>
          )}
        </div>

        {/* Tips */}
        <div className="mt-6 pt-6 border-t border-gray-200">
          <p className="text-xs text-gray-500 text-center">
            💡 Tip: Speak clearly and mention specific ingredients or cuisine types
          </p>
        </div>
      </div>
    </div>
  )
}
