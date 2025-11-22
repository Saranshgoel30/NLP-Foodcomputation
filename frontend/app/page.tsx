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
  excluded_applied?: boolean
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

  // Real-time filtering: re-search when filters change
  useEffect(() => {
    if (query.trim() && results) {
      handleSearch(query)
    }
  }, [filters])

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Header */}
      <header className="bg-slate-900 border-b border-slate-800 shadow-xl">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center">
            <div className="flex justify-center mb-4">
              <ChefHat className="w-16 h-16 text-blue-500" />
            </div>
            <h1 className="text-5xl md:text-6xl font-bold mb-3 tracking-tight text-white">
              Food Intelligence
            </h1>
            <p className="text-lg md:text-xl text-gray-400">
              AI-Powered Multilingual Recipe Discovery
            </p>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="relative container mx-auto px-4 py-8">
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Sidebar */}
          <aside className="lg:w-64 flex-shrink-0">
            <div className="sticky top-8">
              <FilterSidebar filters={filters} onChange={setFilters} />
            </div>
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
              <div className="flex flex-col items-center justify-center py-20">
                <Loader2 className="w-12 h-12 animate-spin text-blue-500" />
                <p className="mt-4 text-gray-400">Searching recipes...</p>
              </div>
            )}

            {/* Results */}
            {!loading && results && (
              <div>
                {/* Query Understanding Card */}
                <div className="mb-6 space-y-4">
                  {/* Translation Info */}
                  {results.translated_query && results.translated_query !== results.query && (
                    <div className="p-5 bg-slate-800 rounded-lg border border-green-600 shadow-xl">
                      <div className="flex items-start gap-4">
                        <div className="p-2.5 bg-green-600 rounded-md">
                          <Globe className="w-5 h-5 text-white" />
                        </div>
                        <div className="flex-1">
                          <p className="font-bold text-base mb-3 text-white">
                            Translation Applied
                          </p>
                          <div className="space-y-2 text-sm">
                            <div className="p-3 bg-slate-900 rounded-md border border-slate-700">
                              <span className="text-gray-400 font-medium">Original Query:</span>
                              <p className="text-white mt-1">"{results.query}"</p>
                            </div>
                            <div className="p-3 bg-slate-900 rounded-md border border-green-600">
                              <span className="text-green-400 font-medium">Translated To:</span>
                              <p className="text-white mt-1">"{results.translated_query}"</p>
                            </div>
                            {results.detected_language && (
                              <p className="text-xs text-gray-400 flex items-center gap-2 mt-2">
                                <span className="px-2 py-1 bg-green-600 rounded-md font-semibold text-white">
                                  {results.detected_language}
                                </span>
                                <span>detected</span>
                              </p>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                  
                  {/* Exclusion Warning */}
                  {results.excluded_applied === false && (
                    <div className="p-5 bg-slate-800 rounded-lg border border-yellow-600 shadow-xl">
                      <div className="flex items-start gap-4">
                        <div className="p-2.5 bg-yellow-600 rounded-md">
                          <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                          </svg>
                        </div>
                        <div className="flex-1">
                          <p className="font-bold text-base mb-2 text-white">
                            No Perfect Matches
                          </p>
                          <p className="text-sm text-gray-300 leading-relaxed">
                            Your exclusion filters were too strict. Showing all relevant results - 
                            <span className="text-yellow-400 font-semibold"> please check ingredients carefully</span>.
                          </p>
                        </div>
                      </div>
                    </div>
                  )}
                  
                  {/* Results Summary */}
                  <div className="p-5 bg-slate-800 rounded-lg border border-slate-700 shadow-xl">
                    <div className="flex items-center justify-between flex-wrap gap-4">
                      <div className="flex items-center gap-6">
                        <div>
                          <p className="text-xs text-gray-400 mb-1 uppercase tracking-wide font-semibold">Results Found</p>
                          <p className="text-2xl font-bold text-white">
                            {results.found}
                          </p>
                        </div>
                        <div className="h-10 w-px bg-slate-700"></div>
                        <div>
                          <p className="text-xs text-gray-400 mb-1 uppercase tracking-wide font-semibold">Response Time</p>
                          <p className="text-2xl font-bold text-white">
                            {results.duration_ms}<span className="text-sm text-gray-400 ml-1">ms</span>
                          </p>
                        </div>
                      </div>
                      {results.llm_enabled && (
                        <div className="flex items-center gap-2 px-3 py-2 bg-blue-600 rounded-md">
                          <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
                          <span className="text-sm font-bold text-white">AI-Powered</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {results.hits.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {results.hits.map((hit, index) => (
                      <RecipeCard key={index} recipe={hit.document} />
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-20 bg-slate-800 rounded-lg border border-slate-700">
                    <Search className="w-12 h-12 mx-auto text-gray-500 mb-4" />
                    <p className="text-lg text-gray-400">No recipes found matching your criteria.</p>
                    <p className="text-sm text-gray-500 mt-2">Try adjusting your search or filters.</p>
                  </div>
                )}
              </div>
            )}

            {/* Empty State */}
            {!loading && !results && (
              <div className="py-12">
                <h3 className="text-xl font-bold text-white mb-6 text-center">
                  Try searching for...
                </h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-4xl mx-auto mb-12">
                  {[
                    'Butter chicken without onions and tomatoes',
                    'Quick pasta under 20 minutes',
                    'Jain recipes (no onion no garlic)',
                    'Spicy curry with garlic and ginger',
                    'Chocolate dessert without eggs',
                    'कांदा नसलेली पनीर भाजी',
                    'pyaz ke bina dal recipe',
                    'bina tamatar ka chicken'
                  ].map((example, i) => (
                    <button
                      key={i}
                      onClick={() => {
                        setQuery(example)
                        handleSearch(example)
                      }}
                      className="p-4 bg-slate-800 rounded-lg border border-slate-700 hover:border-blue-500 hover:bg-slate-700 transition-all duration-200 text-left font-medium text-gray-300 hover:text-white"
                    >
                      {example}
                    </button>
                  ))}
                </div>

                {/* Stats */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-4xl mx-auto">
                  <div className="p-6 bg-slate-800 rounded-lg border border-slate-700 text-center">
                    <Utensils className="w-8 h-8 text-blue-500 mx-auto mb-3" />
                    <p className="text-3xl font-bold text-white mb-1">9,600+</p>
                    <p className="text-sm text-gray-400 font-medium">Total Recipes</p>
                  </div>
                  <div className="p-6 bg-slate-800 rounded-lg border border-slate-700 text-center">
                    <Globe className="w-8 h-8 text-green-500 mx-auto mb-3" />
                    <p className="text-3xl font-bold text-white mb-1">15+</p>
                    <p className="text-sm text-gray-400 font-medium">Cuisines</p>
                  </div>
                  <div className="p-6 bg-slate-800 rounded-lg border border-slate-700 text-center">
                    <Clock className="w-8 h-8 text-purple-500 mx-auto mb-3" />
                    <p className="text-3xl font-bold text-white mb-1">7+</p>
                    <p className="text-sm text-gray-400 font-medium">Diet Types</p>
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
