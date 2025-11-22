'use client'

import { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import { Search, Loader2 } from 'lucide-react'

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
    // Handle Enter key for direct search (works even without suggestions)
    if (e.key === 'Enter') {
      e.preventDefault()
      if (showSuggestions && suggestions.length > 0 && selectedIndex >= 0) {
        // User selected a suggestion with arrow keys
        const selected = suggestions[selectedIndex]
        onChange(selected)
        onSearch(selected)
      } else {
        // Direct search with current input value
        onSearch(value)
      }
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

  return (
    <div className="relative w-full max-w-4xl mx-auto">
      <div className="relative flex gap-2">
        <div className="relative flex-1">
          <input
            ref={inputRef}
            type="text"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onKeyDown={handleKeyDown}
            onFocus={() => suggestions.length > 0 && setShowSuggestions(true)}
          placeholder="Try 'butter chicken without onions' or 'कांदा नसलेली पनीर भाजी' or 'pyaz ke bina dal'..."
          className="w-full px-6 py-4 pl-14 text-lg font-medium border-2 border-gray-300 rounded-2xl focus:outline-none focus:border-purple-500 focus:ring-4 focus:ring-purple-100 transition-all duration-200 shadow-lg bg-white text-gray-900 placeholder-gray-400"
          />
          <Search className="absolute left-5 top-1/2 -translate-y-1/2 w-6 h-6 text-gray-400" />
          {loading && (
            <Loader2 className="absolute right-5 top-1/2 -translate-y-1/2 w-6 h-6 text-purple-600 animate-spin" />
          )}
        </div>
        
        {/* Search Button */}
        <button
          onClick={handleSearchClick}
          disabled={!value.trim()}
          className="px-8 py-4 bg-gradient-to-r from-purple-600 to-blue-600 text-white font-semibold rounded-2xl hover:from-purple-700 hover:to-blue-700 disabled:from-gray-300 disabled:to-gray-400 disabled:cursor-not-allowed transition-all duration-200 shadow-lg hover:shadow-xl flex items-center gap-2"
        >
          <Search className="w-5 h-5" />
          <span>Search</span>
        </button>
      </div>

      {/* Hint */}
      {value.trim() && !showSuggestions && (
        <div className="mt-2 text-sm text-gray-600 text-center">
          💡 Press <kbd className="px-2 py-1 bg-gray-100 border border-gray-300 rounded">Enter</kbd> or click <strong>Search</strong> to find recipes
        </div>
      )}

      {/* Autocomplete Dropdown */}
      {showSuggestions && suggestions.length > 0 && (
        <div
          ref={suggestionsRef}
          className="absolute z-50 w-full mt-2 bg-white border-2 border-gray-200 rounded-xl shadow-2xl overflow-hidden"
        >
          <div className="px-4 py-2 bg-gray-50 border-b border-gray-200">
            <p className="text-xs font-semibold text-gray-600 uppercase tracking-wide">
              💡 Suggested Searches
            </p>
          </div>
          {suggestions.map((suggestion, index) => (
            <button
              key={index}
              onClick={() => handleSuggestionClick(suggestion)}
              onMouseEnter={() => setSelectedIndex(index)}
              className={`w-full px-6 py-3 text-left transition-colors duration-150 flex items-center gap-3 ${
                index === selectedIndex
                  ? 'bg-purple-50 text-purple-900'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              <Search className={`w-4 h-4 flex-shrink-0 ${
                index === selectedIndex ? 'text-purple-600' : 'text-gray-400'
              }`} />
              <span className={`font-medium ${
                index === selectedIndex ? 'text-purple-900' : 'text-gray-800'
              }`}>
                {suggestion}
              </span>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
