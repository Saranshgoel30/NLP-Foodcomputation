'use client'

import { useState, useEffect, useCallback } from 'react'
import axios from 'axios'
import { Search, Loader2, ChefHat, Clock, Utensils, Globe } from 'lucide-react'
import SearchBar from '@/components/SearchBar'
import RecipeCard from '@/components/RecipeCard'
import FilterSidebar from '@/components/FilterSidebar'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface Recipe {
  document: {
    name: string
    description?: string
    ingredients: string[]
    cuisine?: string
    course?: string
    diet?: string
    total_time?: number
    prep_time?: number
    cook_time?: number
    servings?: number
    url?: string
    instructions?: any
  }
}

interface SearchResult {
  hits: Recipe[]
  found: number
  query: string
  duration_ms: number
  translated_query?: string
  detected_language?: string
  llm_enabled?: boolean
}

export default function Home() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [filters, setFilters] = useState({
    cuisine: '',
    diet: '',
    course: ''
  })

  const handleSearch = useCallback(async (searchQuery: string) => {
    if (!searchQuery.trim()) {
      setResults(null)
      return
    }

    setLoading(true)
    try {
      const params = new URLSearchParams({
        q: searchQuery,
        limit: '50',
        ...(filters.cuisine && { cuisine: filters.cuisine }),
        ...(filters.diet && { diet: filters.diet }),
        ...(filters.course && { course: filters.course })
      })

      const response = await axios.get(`${API_URL}/api/search?${params}`)
      setResults(response.data)
    } catch (error) {
      console.error('Search failed:', error)
    } finally {
      setLoading(false)
    }
  }, [filters])

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50">
      {/* Header */}
      <header className="bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-2xl">
        <div className="container mx-auto px-4 py-12 md:py-16">
          <div className="text-center">
            <div className="flex justify-center mb-4">
              <ChefHat className="w-16 h-16" />
            </div>
            <h1 className="text-5xl md:text-6xl font-bold mb-4 tracking-tight">
              Food Intelligence Platform
            </h1>
            <p className="text-xl md:text-2xl text-purple-100">
              Discover delicious recipes with AI-powered semantic search
            </p>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Sidebar */}
          <aside className="lg:w-64 flex-shrink-0">
            <FilterSidebar filters={filters} onChange={setFilters} />
          </aside>

          {/* Search Area */}
          <main className="flex-1">
            <div className="mb-8">
              <SearchBar 
                value={query} 
                onChange={setQuery}
                onSearch={handleSearch}
              />
            </div>

            {/* Loading State */}
            {loading && (
              <div className="flex items-center justify-center py-20">
                <Loader2 className="w-12 h-12 animate-spin text-purple-600" />
              </div>
            )}

            {/* Results */}
            {!loading && results && (
              <div>
                {/* Query Understanding Card */}
                <div className="mb-6 space-y-4">
                  {/* Translation Info */}
                  {results.translated_query && results.translated_query !== results.query && (
                    <div className="p-4 bg-gradient-to-r from-green-50 to-blue-50 rounded-lg shadow-sm border-2 border-green-200">
                      <div className="flex items-start gap-3">
                        <Globe className="w-6 h-6 text-green-600 mt-0.5 flex-shrink-0" />
                        <div className="flex-1">
                          <p className="font-semibold text-gray-800 mb-2">
                            🌍 Multilingual Query Detected
                          </p>
                          <div className="space-y-1 text-sm">
                            <p className="text-gray-700">
                              <span className="font-medium">Original:</span> "{results.query}"
                            </p>
                            <p className="text-gray-700">
                              <span className="font-medium">Translated to English:</span> "{results.translated_query}"
                            </p>
                            {results.detected_language && (
                              <p className="text-xs text-gray-600 mt-2">
                                Language detected: <span className="font-semibold">{results.detected_language}</span>
                              </p>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                  
                  {/* Results Summary */}
                  <div className="p-4 bg-white rounded-lg shadow-sm border border-gray-200">
                    <div className="flex items-center justify-between flex-wrap gap-2">
                      <p className="text-lg font-semibold text-gray-800">
                        📊 Found <span className="text-purple-600">{results.found}</span> recipes 
                        in <span className="text-purple-600">{results.duration_ms}ms</span>
                      </p>
                      {results.llm_enabled && (
                        <div className="flex items-center gap-2 px-3 py-1.5 bg-gradient-to-r from-purple-100 to-blue-100 rounded-full">
                          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                          <span className="text-xs font-semibold text-purple-700">AI-Powered Search</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  {results.hits.map((hit, index) => (
                    <RecipeCard key={index} recipe={hit.document} index={index + 1} />
                  ))}
                </div>

                {results.hits.length === 0 && (
                  <div className="text-center py-20">
                    <Search className="w-16 h-16 mx-auto text-gray-400 mb-4" />
                    <p className="text-xl text-gray-600">No recipes found. Try a different search!</p>
                  </div>
                )}
              </div>
            )}

            {/* Empty State */}
            {!loading && !results && (
              <div className="text-center py-12">
                <h3 className="text-2xl font-semibold text-gray-800 mb-8">
                  🔍 Try searching for...
                </h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-3xl mx-auto mb-12">
                  {[
                    '🚫 Butter chicken without onions and tomatoes',
                    '⚡ Quick pasta under 20 minutes',
                    '🥗 Jain recipes (no onion no garlic)',
                    '🌶️ Spicy curry with garlic and ginger',
                    '🥞 Chocolate dessert without eggs',
                    '🇮🇳 कांदा नसलेली पनीर भाजी',
                    '🍛 pyaz ke bina dal recipe',
                    '🔥 bina tamatar ka chicken'
                  ].map((example, i) => (
                    <button
                      key={i}
                      onClick={() => {
                        const cleanQuery = example.replace(/[🥞🍰🐟⚡🌶️🥗]/g, '').trim()
                        setQuery(cleanQuery)
                        handleSearch(cleanQuery)
                      }}
                      className="p-4 bg-white rounded-xl border-2 border-gray-200 hover:border-purple-500 hover:shadow-lg transition-all duration-200 text-left font-medium text-gray-700 hover:text-purple-600"
                    >
                      {example}
                    </button>
                  ))}
                </div>

                {/* Stats */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-3xl mx-auto">
                  <div className="p-6 bg-gradient-to-br from-purple-100 to-purple-50 rounded-xl">
                    <Utensils className="w-10 h-10 text-purple-600 mx-auto mb-3" />
                    <p className="text-3xl font-bold text-purple-900">9,600+</p>
                    <p className="text-sm text-purple-700 font-medium">Total Recipes</p>
                  </div>
                  <div className="p-6 bg-gradient-to-br from-blue-100 to-blue-50 rounded-xl">
                    <Globe className="w-10 h-10 text-blue-600 mx-auto mb-3" />
                    <p className="text-3xl font-bold text-blue-900">15+</p>
                    <p className="text-sm text-blue-700 font-medium">Cuisines</p>
                  </div>
                  <div className="p-6 bg-gradient-to-br from-green-100 to-green-50 rounded-xl">
                    <Clock className="w-10 h-10 text-green-600 mx-auto mb-3" />
                    <p className="text-3xl font-bold text-green-900">7+</p>
                    <p className="text-sm text-green-700 font-medium">Diet Types</p>
                  </div>
                </div>
              </div>
            )}
          </main>
        </div>
      </div>
    </div>
  )
}
