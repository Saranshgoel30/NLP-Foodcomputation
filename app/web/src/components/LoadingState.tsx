'use client'

import React from 'react'
import { ChefHat, Sparkles, Loader2 } from 'lucide-react'

interface LoadingStateProps {
  message?: string
  type?: 'search' | 'cooking' | 'analyzing'
}

export default function LoadingState({ message, type = 'search' }: LoadingStateProps) {
  const messages = {
    search: [
      'Searching 8,945 recipes...',
      'Finding perfect matches...',
      'Analyzing ingredients...',
    ],
    cooking: [
      'Preparing your recipe...',
      'Gathering ingredients...',
      'Setting up instructions...',
    ],
    analyzing: [
      'Understanding your query...',
      'Applying AI magic...',
      'Finding the best recipes...',
    ]
  }

  const [currentMessage, setCurrentMessage] = React.useState(0)

  React.useEffect(() => {
    const interval = setInterval(() => {
      setCurrentMessage((prev) => (prev + 1) % messages[type].length)
    }, 2000)
    return () => clearInterval(interval)
  }, [type])

  return (
    <div className="flex flex-col items-center justify-center py-20">
      {/* Animated Icon */}
      <div className="relative mb-8">
        {/* Outer Circle */}
        <div className="absolute inset-0 animate-spin">
          <div className="w-32 h-32 rounded-full border-4 border-transparent border-t-orange-500 border-r-red-500"></div>
        </div>
        
        {/* Inner Circle */}
        <div className="absolute inset-4 animate-spin animation-delay-1000" style={{ animationDirection: 'reverse' }}>
          <div className="w-24 h-24 rounded-full border-4 border-transparent border-b-orange-400 border-l-red-400"></div>
        </div>

        {/* Center Icon */}
        <div className="relative w-32 h-32 flex items-center justify-center">
          <div className="absolute inset-8 rounded-full bg-gradient-to-r from-orange-500 to-red-500 animate-pulse"></div>
          <ChefHat className="relative w-12 h-12 text-white z-10" />
        </div>
      </div>

      {/* Loading Message */}
      <div className="text-center mb-4">
        <h3 className="text-2xl font-bold text-gray-900 mb-2">
          {message || messages[type][currentMessage]}
        </h3>
        <p className="text-gray-600">This will only take a moment...</p>
      </div>

      {/* Progress Dots */}
      <div className="flex gap-2">
        {[...Array(3)].map((_, i) => (
          <div
            key={i}
            className="w-3 h-3 rounded-full bg-gradient-to-r from-orange-500 to-red-500 animate-bounce"
            style={{ animationDelay: `${i * 0.15}s` }}
          />
        ))}
      </div>
    </div>
  )
}

// Skeleton Loader for Recipe Cards
export function RecipeCardSkeleton() {
  return (
    <div className="bg-white rounded-2xl shadow-lg overflow-hidden animate-pulse">
      <div className="h-56 bg-gradient-to-br from-gray-200 to-gray-300"></div>
      <div className="p-5 space-y-4">
        <div className="h-6 bg-gray-200 rounded w-3/4"></div>
        <div className="flex gap-2">
          <div className="h-6 bg-gray-200 rounded-full w-20"></div>
          <div className="h-6 bg-gray-200 rounded-full w-24"></div>
        </div>
        <div className="space-y-2">
          <div className="h-4 bg-gray-200 rounded w-full"></div>
          <div className="h-4 bg-gray-200 rounded w-2/3"></div>
        </div>
      </div>
    </div>
  )
}

// Grid of Skeleton Cards
export function RecipeGridSkeleton({ count = 8 }: { count?: number }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      {[...Array(count)].map((_, i) => (
        <RecipeCardSkeleton key={i} />
      ))}
    </div>
  )
}

// Inline Loading Spinner
export function Spinner({ size = 'md' }: { size?: 'sm' | 'md' | 'lg' }) {
  const sizeClasses = {
    sm: 'w-4 h-4 border-2',
    md: 'w-6 h-6 border-3',
    lg: 'w-8 h-8 border-4'
  }

  return (
    <div className={`${sizeClasses[size]} border-gray-200 border-t-orange-500 rounded-full animate-spin`}></div>
  )
}
