'use client'

import { useState, useRef, KeyboardEvent } from 'react'
import { X } from 'lucide-react'

interface ChipInputProps {
  values: string[]
  onChange: (values: string[]) => void
  placeholder?: string
  maxChips?: number
  disabled?: boolean
  variant?: 'default' | 'success' | 'danger'
}

export default function ChipInput({
  values,
  onChange,
  placeholder = 'Add item...',
  maxChips,
  disabled = false,
  variant = 'default'
}: ChipInputProps) {
  const [inputValue, setInputValue] = useState('')
  const inputRef = useRef<HTMLInputElement>(null)

  const variantStyles = {
    default: 'bg-blue-600 hover:bg-blue-700',
    success: 'bg-green-600 hover:bg-green-700',
    danger: 'bg-red-600 hover:bg-red-700'
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && inputValue.trim()) {
      e.preventDefault()
      
      // Check if max chips reached
      if (maxChips && values.length >= maxChips) {
        return
      }

      // Check for duplicates
      if (!values.includes(inputValue.trim())) {
        onChange([...values, inputValue.trim()])
        setInputValue('')
      } else {
        // Flash input or show error (optional)
        setInputValue('')
      }
    } else if (e.key === 'Backspace' && !inputValue && values.length > 0) {
      // Remove last chip when backspace is pressed on empty input
      e.preventDefault()
      onChange(values.slice(0, -1))
    }
  }

  const removeChip = (index: number) => {
    onChange(values.filter((_, i) => i !== index))
    // Focus input after removing chip
    inputRef.current?.focus()
  }

  const handleContainerClick = () => {
    // Focus input when clicking anywhere in the container
    inputRef.current?.focus()
  }

  const isMaxReached = typeof maxChips === 'number' ? values.length >= maxChips : false

  return (
    <div
      onClick={handleContainerClick}
      className={`
        flex flex-wrap gap-2 p-3 bg-slate-900 border rounded-lg cursor-text
        transition-all duration-200
        ${disabled ? 'border-slate-700 opacity-50 cursor-not-allowed' : 'border-slate-700 hover:border-slate-600 focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-500/20'}
      `}
    >
      {/* Chips */}
      {values.map((value, index) => (
        <div
          key={index}
          className={`
            flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium text-white
            transition-all duration-200
            ${variantStyles[variant]}
            ${disabled ? 'cursor-not-allowed' : 'cursor-default'}
          `}
        >
          <span>{value}</span>
          {!disabled && (
            <button
              onClick={(e) => {
                e.stopPropagation()
                removeChip(index)
              }}
              className="hover:bg-white/20 rounded-full p-0.5 transition-colors duration-150"
              aria-label={`Remove ${value}`}
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      ))}

      {/* Input */}
      <input
        ref={inputRef}
        type="text"
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={values.length === 0 ? placeholder : ''}
        disabled={disabled || isMaxReached}
        className={`
          flex-1 min-w-[120px] bg-transparent border-none outline-none text-white
          placeholder-gray-500
          ${disabled || isMaxReached ? 'cursor-not-allowed' : ''}
        `}
      />

      {/* Max chips indicator */}
      {isMaxReached && (
        <span className="text-xs text-gray-400 self-center whitespace-nowrap">
          Max {maxChips} items
        </span>
      )}
    </div>
  )
}
