'use client'

import { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import { Search, Loader2 } from 'lucide-react'
import VoiceInput from './VoiceInput'
import LanguageSelector from './LanguageSelector'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface SearchBarProps {
  value: string
  onChange: (value: string) => void
  onSearch: (query: string) => void
}

export default function SearchBar({ value, onChange, onSearch }: SearchBarProps) {
  const [suggestions, setSuggestions] = useState<string[]>([])
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [loading, setLoading] = useState(false)
  const [selectedIndex, setSelectedIndex] = useState(-1)
  
  // Language state for voice input - Default to auto-detect
  const [selectedLanguage, setSelectedLanguage] = useState<string>('auto')
  
  const inputRef = useRef<HTMLInputElement>(null)
  const suggestionsRef = useRef<HTMLDivElement>(null)

  // Debounced autocomplete
  useEffect(() => {
    const timer = setTimeout(async () => {
      if (value.length >= 2) {
        setLoading(true)
        try {
          const response = await axios.get(`${API_URL}/api/autocomplete?q=${encodeURIComponent(value)}&limit=6`)
          setSuggestions(response.data.suggestions)
          setShowSuggestions(true)
        } catch (error) {
          console.error('Autocomplete failed:', error)
          setSuggestions([])
        } finally {
          setLoading(false)
        }
      } else {
        setSuggestions([])
        setShowSuggestions(false)
      }
    }, 300) // 300ms debounce

    return () => clearTimeout(timer)
  }, [value])

  // Click outside to close suggestions
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        suggestionsRef.current &&
        !suggestionsRef.current.contains(event.target as Node) &&
        inputRef.current &&
        !inputRef.current.contains(event.target as Node)
      ) {
        setShowSuggestions(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleKeyDown = (e: React.KeyboardEvent) => {
    // Handle Enter key - ALWAYS search what's in the input box
    if (e.key === 'Enter') {
      e.preventDefault()
      onSearch(value)
      setShowSuggestions(false)
      setSelectedIndex(-1)
      return
    }

    // Handle other keys only when suggestions are visible
    if (!showSuggestions || suggestions.length === 0) {
      return
    }

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault()
        setSelectedIndex(prev => 
          prev < suggestions.length - 1 ? prev + 1 : prev
        )
        break
      case 'ArrowUp':
        e.preventDefault()
        setSelectedIndex(prev => prev > 0 ? prev - 1 : -1)
        break
      case 'Escape':
        setShowSuggestions(false)
        setSelectedIndex(-1)
        break
    }
  }

  const handleSuggestionClick = (suggestion: string) => {
    onChange(suggestion)
    onSearch(suggestion)
    setShowSuggestions(false)
    setSelectedIndex(-1)
  }

  const handleSearchClick = () => {
    if (value.trim()) {
      onSearch(value)
      setShowSuggestions(false)
    }
  }

  const handleVoiceTranscription = (text: string) => {
    onChange(text)
    onSearch(text)
  }

  return (
    <div className="w-full max-w-5xl mx-auto space-y-4">
      {/* Main Search Row */}
      <div className="relative flex gap-3">
        {/* Search Input */}
        <div className="relative flex-1">
          <input
            ref={inputRef}
            type="text"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onKeyDown={handleKeyDown}
            onFocus={() => suggestions.length > 0 && setShowSuggestions(true)}
            placeholder="Search for recipes... (e.g., 'butter chicken', 'jain recipes', or in any language)"
            className="w-full px-6 py-4 pl-14 text-base font-medium bg-slate-800 border-2 border-slate-600 rounded-lg focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all duration-200 text-white placeholder-gray-400"
          />
          <div className="absolute left-4 top-1/2 -translate-y-1/2 p-2 bg-blue-600 rounded-md">
            <Search className="w-4 h-4 text-white" />
          </div>
          {loading && (
            <div className="absolute right-4 top-1/2 -translate-y-1/2">
              <Loader2 className="w-5 h-5 text-blue-400 animate-spin" />
            </div>
          )}
        </div>
        
        {/* Search Button */}
        <button
          onClick={handleSearchClick}
          disabled={!value.trim()}
          className="px-8 py-4 bg-blue-600 text-white font-bold rounded-lg hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed transition-colors duration-200 flex items-center gap-2"
        >
          <Search className="w-5 h-5" />
          <span>Search</span>
        </button>
      </div>

      {/* Voice Input Row */}
      <div className="flex items-end gap-4 bg-slate-800 rounded-lg p-4 border border-slate-700">
        {/* Language Selector */}
        <div className="flex-1 max-w-xs">
          <LanguageSelector
            value={selectedLanguage}
            onChange={setSelectedLanguage}
            disabled={false}
          />
        </div>

        {/* Divider */}
        <div className="h-12 w-px bg-slate-700"></div>

        {/* Voice Button */}
        <div className="flex flex-col items-center">
          <label className="block text-xs font-semibold text-gray-400 mb-1.5 uppercase tracking-wide text-center">
            Voice Search
          </label>
          <VoiceInput 
            onTranscription={handleVoiceTranscription}
            language={selectedLanguage}
            disabled={loading}
          />
        </div>
      </div>

      {/* Hint */}
      {value.trim() && !showSuggestions && (
        <div className="text-sm text-gray-400 text-center flex items-center justify-center gap-2">
          <span>Press</span>
          <kbd className="px-2 py-1 bg-slate-800 border border-slate-600 rounded text-blue-400 font-mono text-xs">Enter</kbd>
          <span>to search</span>
        </div>
      )}

      {/* Autocomplete Dropdown */}
      {showSuggestions && suggestions.length > 0 && (
        <div
          ref={suggestionsRef}
          className="absolute z-50 w-full mt-2 bg-slate-800 border-2 border-slate-600 rounded-lg shadow-2xl overflow-hidden"
          style={{ maxWidth: 'calc(100% - 120px)' }}
        >
          <div className="px-4 py-2 bg-slate-700 border-b border-slate-600">
            <p className="text-xs font-bold text-gray-400 uppercase tracking-wide">
              Suggestions
            </p>
          </div>
          {suggestions.map((suggestion, index) => (
            <button
              key={index}
              onClick={() => handleSuggestionClick(suggestion)}
              onMouseEnter={() => setSelectedIndex(index)}
              className={`w-full px-5 py-3 text-left transition-all duration-200 flex items-center gap-3 border-b border-slate-700 last:border-b-0 ${
                index === selectedIndex
                  ? 'bg-blue-600 text-white'
                  : 'hover:bg-slate-700 text-gray-300'
              }`}
            >
              <Search className="w-4 h-4" />
              <span className="font-medium text-sm">
                {suggestion}
              </span>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
