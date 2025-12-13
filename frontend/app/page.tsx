'use client'

import { useState, useEffect, useCallback } from 'react'
import axios from 'axios'
import { Search, Loader2, ChefHat, Clock, Utensils, Globe, Sparkles } from 'lucide-react'
import SearchBar from '@/components/SearchBar'
import RecipeCard from '@/components/RecipeCard'
import FilterSidebar from '@/components/FilterSidebar'
import VoiceInput from '@/components/VoiceInput'
import QueryEditor from '@/components/QueryEditor'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface StructuredQuery {
  base_query: string
  include_ingredients: string[]
  exclude_ingredients: string[]
  tags: string[]
  original_query: string
}

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
  page: number
  limit: number
  total_pages: number
  query: string
  duration_ms: number
  translated_query?: string
  detected_language?: string
  llm_enabled?: boolean
  excluded_applied?: boolean
  fallback_message?: string
  is_fallback?: boolean
  excluded_count?: number
  rag_enabled?: boolean
  ai_summary?: string
}

export default function Home() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [currentPage, setCurrentPage] = useState(1)
  const [filters, setFilters] = useState({
    cuisine: '',
    diet: '',
    course: ''
  })
  const [structuredQuery, setStructuredQuery] = useState<StructuredQuery | null>(null)
  const [parsingQuery, setParsingQuery] = useState(false)
  
  // RAG Mode state
  const [ragEnabled, setRagEnabled] = useState(false)
  const [aiSummary, setAiSummary] = useState<string | null>(null)
  const [loadingRag, setLoadingRag] = useState(false)

  const handleSearch = useCallback(async (searchQuery: string, page: number = 1) => {
    if (!searchQuery.trim()) {
      setResults(null)
      setStructuredQuery(null)
      return
    }

    setLoading(true)
    setParsingQuery(true)
    
    // Reset RAG state on new search
    setRagEnabled(false)
    setAiSummary(null)
    
    try {
      // Step 1: Parse the query into structured components
      const parseResponse = await axios.post(`${API_URL}/api/parse-query?query=${encodeURIComponent(searchQuery)}`)
      const parsed = parseResponse.data
      
      // Store structured query with original
      const structured: StructuredQuery = {
        base_query: parsed.base_query || '',
        include_ingredients: parsed.include_ingredients || [],
        exclude_ingredients: parsed.exclude_ingredients || [],
        tags: parsed.tags || [],
        original_query: searchQuery
      }
      setStructuredQuery(structured)
      setParsingQuery(false)
      
      // Step 2: Search with structured parameters
      await searchWithStructured(structured, page)
      
    } catch (error) {
      console.error('Search failed:', error)
      setParsingQuery(false)
      setLoading(false)
    }
  }, [filters])
  
  const searchWithStructured = async (structured: StructuredQuery, page: number = 1, useRag: boolean = ragEnabled) => {
    setLoading(true)
    if (useRag) setLoadingRag(true)
    
    try {
      const params = new URLSearchParams({
        q: structured.original_query,
        limit: '20',
        page: page.toString(),
        ...(filters.cuisine && { cuisine: filters.cuisine }),
        ...(filters.diet && { diet: filters.diet }),
        ...(filters.course && { course: filters.course }),
        // Add structured parameters
        ...(structured.base_query && { base_query: structured.base_query }),
        ...(structured.include_ingredients.length > 0 && { 
          include_ingredients: structured.include_ingredients.join(',') 
        }),
        ...(structured.exclude_ingredients.length > 0 && { 
          exclude_ingredients: structured.exclude_ingredients.join(',') 
        }),
        ...(structured.tags.length > 0 && { 
          tags: structured.tags.join(',') 
        })
      })

      // Use RAG search endpoint when enabled, otherwise regular search
      const endpoint = useRag ? '/api/rag-search' : '/api/search'
      console.log(`🔍 Searching with ${useRag ? 'RAG' : 'regular'} endpoint: ${API_URL}${endpoint}`)
      const response = await axios.get(`${API_URL}${endpoint}?${params}`)
      
      setResults(response.data)
      setCurrentPage(page)
      
      // RAG search returns ai_summary directly
      if (useRag && response.data.ai_summary) {
        // Handle both string and object formats
        const summary = response.data.ai_summary
        if (typeof summary === 'string') {
          setAiSummary(summary)
        } else if (summary && typeof summary === 'object' && summary.summary) {
          setAiSummary(summary.summary)
        } else {
          setAiSummary(null)
        }
      } else {
        setAiSummary(null)
      }
    } catch (error) {
      console.error('Search failed:', error)
      setAiSummary(null)
    } finally {
      setLoading(false)
      setLoadingRag(false)
    }
  }

  const handlePageChange = (page: number) => {
    if (structuredQuery) {
      searchWithStructured(structuredQuery, page)
    } else {
      handleSearch(query, page)
    }
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
  
  // Fetch RAG summary from backend
  const fetchRagSummary = async (searchQuery: string, hits: Recipe[]) => {
    setLoadingRag(true)
    try {
      const recipeNames = hits.slice(0, 5).map(h => h.document.name).join(',')
      const response = await axios.post(
        `${API_URL}/api/rag-summary?query=${encodeURIComponent(searchQuery)}&recipe_names=${encodeURIComponent(recipeNames)}`
      )
      if (response.data.summary) {
        setAiSummary(response.data.summary)
      }
    } catch (error) {
      console.error('RAG summary failed:', error)
      setAiSummary(null)
    } finally {
      setLoadingRag(false)
    }
  }
  
  // Re-search when RAG toggle changes (if we have a query)
  useEffect(() => {
    console.log('🔄 RAG toggle changed:', { ragEnabled, structuredQuery: !!structuredQuery })
    if (structuredQuery) {
      console.log('🚀 Triggering re-search with RAG:', ragEnabled)
      // Re-search with new RAG setting
      searchWithStructured(structuredQuery, 1, ragEnabled)
    }
  }, [ragEnabled])
  
  const handleStructuredUpdate = async (updated: StructuredQuery) => {
    // User edited the structured query - re-search with new parameters
    setStructuredQuery(updated)
    await searchWithStructured(updated, 1)
  }
  
  const handleReset = async () => {
    // Reset back to original query parsing
    if (structuredQuery) {
      setParsingQuery(true)
      await handleSearch(structuredQuery.original_query, 1)
    }
  }

  // Real-time filtering: re-search when filters change
  useEffect(() => {
    if (query.trim() && results) {
      setCurrentPage(1)
      handleSearch(query, 1)
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

            {/* RAG Mode Toggle */}
            <div className="mb-6 flex items-center justify-end">
              <button
                onClick={() => setRagEnabled(!ragEnabled)}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-lg font-semibold text-sm transition-all duration-300 ${
                  ragEnabled 
                    ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-lg shadow-purple-500/25' 
                    : 'bg-slate-800 text-gray-400 hover:bg-slate-700 hover:text-white border border-slate-700'
                }`}
              >
                <Sparkles className={`w-4 h-4 ${ragEnabled ? 'animate-pulse' : ''}`} />
                <span>AI Summary</span>
                <span className={`text-xs px-2 py-0.5 rounded ${ragEnabled ? 'bg-white/20' : 'bg-slate-700'}`}>
                  {ragEnabled ? 'ON' : 'OFF'}
                </span>
              </button>
            </div>

            {/* Query Editor - Shown after parsing */}
            {structuredQuery && (
              <div className="mb-8">
                <QueryEditor
                  structured={structuredQuery}
                  onUpdate={handleStructuredUpdate}
                  onReset={handleReset}
                  loading={parsingQuery || loading}
                />
              </div>
            )}

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
                {/* AI Summary (RAG) */}
                {ragEnabled && (
                  <div className="mb-6">
                    {loadingRag ? (
                      <div className="p-5 bg-gradient-to-r from-purple-900/50 to-pink-900/50 rounded-xl border border-purple-500/50 shadow-xl">
                        <div className="flex items-center gap-3">
                          <Loader2 className="w-5 h-5 animate-spin text-purple-400" />
                          <p className="text-purple-300 font-medium">Generating AI summary...</p>
                        </div>
                      </div>
                    ) : aiSummary ? (
                      <div className="p-5 bg-gradient-to-r from-purple-900/50 to-pink-900/50 rounded-xl border border-purple-500/50 shadow-xl">
                        <div className="flex items-start gap-4">
                          <div className="p-2.5 bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg flex-shrink-0">
                            <Sparkles className="w-5 h-5 text-white" />
                          </div>
                          <div className="flex-1">
                            <p className="font-bold text-base mb-2 text-white flex items-center gap-2">
                              AI-Powered Results
                              <span className="text-xs px-2 py-0.5 bg-purple-500/30 text-purple-300 rounded">RAG</span>
                              <span className="text-xs px-2 py-0.5 bg-pink-500/30 text-pink-300 rounded">Re-ranked</span>
                            </p>
                            <p className="text-gray-200 leading-relaxed">{aiSummary}</p>
                          </div>
                        </div>
                      </div>
                    ) : null}
                  </div>
                )}

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
                  
                  {/* Fallback/Alternative Suggestions Message */}
                  {results.fallback_message && (
                    <div className="p-5 bg-slate-800 rounded-lg border border-orange-600 shadow-xl">
                      <div className="flex items-start gap-4">
                        <div className="p-2.5 bg-orange-600 rounded-md">
                          <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                        </div>
                        <div className="flex-1">
                          <p className="font-bold text-base mb-2 text-white">
                            {results.is_fallback ? 'Showing Alternative Recipes' : 'No Results Found'}
                          </p>
                          <p className="text-sm text-gray-300 leading-relaxed">
                            {results.fallback_message}
                          </p>
                        </div>
                      </div>
                    </div>
                  )}
                  
                  {/* Results Summary - Only show if we have results */}
                  {results.found > 0 && (
                    <div className="p-5 bg-slate-800 rounded-lg border border-slate-700 shadow-xl">
                      <div className="flex items-center justify-between flex-wrap gap-4">
                        <div className="flex items-center gap-6">
                          <div>
                            <p className="text-xs text-gray-400 mb-1 uppercase tracking-wide font-semibold">Results Found</p>
                            <p className="text-2xl font-bold text-white">
                              {results.found}
                              {results.is_fallback && (
                                <span className="text-sm text-orange-400 ml-2">(alternatives)</span>
                              )}
                            </p>
                          </div>
                          <div className="h-10 w-px bg-slate-700"></div>
                          <div>
                            <p className="text-xs text-gray-400 mb-1 uppercase tracking-wide font-semibold">Response Time</p>
                            <p className="text-2xl font-bold text-white">
                              {results.duration_ms}<span className="text-sm text-gray-400 ml-1">ms</span>
                            </p>
                          </div>
                          {results.excluded_count && results.excluded_count > 0 && (
                            <>
                              <div className="h-10 w-px bg-slate-700"></div>
                              <div>
                                <p className="text-xs text-gray-400 mb-1 uppercase tracking-wide font-semibold">Filtered Out</p>
                                <p className="text-2xl font-bold text-red-400">
                                  {results.excluded_count}
                                </p>
                              </div>
                            </>
                          )}
                        </div>
                        {results.llm_enabled && (
                          <div className="flex items-center gap-2 px-3 py-2 bg-blue-600 rounded-md">
                            <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
                            <span className="text-sm font-bold text-white">AI-Powered</span>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>

                {results.hits.length > 0 ? (
                  <>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {results.hits.map((hit, index) => (
                        <RecipeCard key={index} recipe={hit.document} />
                      ))}
                    </div>

                    {/* Pagination Controls */}
                    {results.total_pages > 1 && (
                      <div className="mt-8 flex flex-col items-center gap-4">
                        {/* Page Info */}
                        <div className="text-sm text-gray-400">
                          Page <span className="font-bold text-white">{results.page}</span> of{' '}
                          <span className="font-bold text-white">{results.total_pages}</span>
                          {' '}({results.found} total results)
                        </div>

                        {/* Pagination Buttons */}
                        <div className="flex items-center gap-2">
                          {/* First Page */}
                          <button
                            onClick={() => handlePageChange(1)}
                            disabled={results.page === 1}
                            className="px-3 py-2 bg-slate-800 border border-slate-700 rounded-md text-sm font-medium text-white hover:bg-slate-700 hover:border-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                          >
                            First
                          </button>

                          {/* Previous Page */}
                          <button
                            onClick={() => handlePageChange(results.page - 1)}
                            disabled={results.page === 1}
                            className="px-3 py-2 bg-slate-800 border border-slate-700 rounded-md text-sm font-medium text-white hover:bg-slate-700 hover:border-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                          >
                            Previous
                          </button>

                          {/* Page Numbers */}
                          <div className="flex gap-1">
                            {Array.from({ length: Math.min(5, results.total_pages) }, (_, i) => {
                              // Show pages around current page
                              let pageNum: number
                              if (results.total_pages <= 5) {
                                pageNum = i + 1
                              } else if (results.page <= 3) {
                                pageNum = i + 1
                              } else if (results.page >= results.total_pages - 2) {
                                pageNum = results.total_pages - 4 + i
                              } else {
                                pageNum = results.page - 2 + i
                              }

                              return (
                                <button
                                  key={pageNum}
                                  onClick={() => handlePageChange(pageNum)}
                                  className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
                                    results.page === pageNum
                                      ? 'bg-blue-600 text-white border-2 border-blue-400'
                                      : 'bg-slate-800 text-gray-300 border border-slate-700 hover:bg-slate-700 hover:border-blue-500'
                                  }`}
                                >
                                  {pageNum}
                                </button>
                              )
                            })}
                          </div>

                          {/* Next Page */}
                          <button
                            onClick={() => handlePageChange(results.page + 1)}
                            disabled={results.page === results.total_pages}
                            className="px-3 py-2 bg-slate-800 border border-slate-700 rounded-md text-sm font-medium text-white hover:bg-slate-700 hover:border-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                          >
                            Next
                          </button>

                          {/* Last Page */}
                          <button
                            onClick={() => handlePageChange(results.total_pages)}
                            disabled={results.page === results.total_pages}
                            className="px-3 py-2 bg-slate-800 border border-slate-700 rounded-md text-sm font-medium text-white hover:bg-slate-700 hover:border-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                          >
                            Last
                          </button>
                        </div>

                        {/* Quick Jump */}
                        {results.total_pages > 10 && (
                          <div className="flex items-center gap-2">
                            <span className="text-sm text-gray-400">Jump to page:</span>
                            <input
                              type="number"
                              min="1"
                              max={results.total_pages}
                              placeholder="Page"
                              className="w-20 px-3 py-2 bg-slate-800 border border-slate-700 rounded-md text-sm text-white focus:border-blue-500 focus:outline-none"
                              onKeyPress={(e) => {
                                if (e.key === 'Enter') {
                                  const page = parseInt((e.target as HTMLInputElement).value)
                                  if (page >= 1 && page <= results.total_pages) {
                                    handlePageChange(page)
                                  }
                                }
                              }}
                            />
                          </div>
                        )}
                      </div>
                    )}
                  </>
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
                    { query: 'paneer without onion', tag: 'Dietary' },
                    { query: 'chicken curry', tag: 'Popular' },
                    { query: 'jain recipes', tag: 'Dietary' },
                    { query: 'dal without garlic', tag: 'Dietary' },
                    { query: 'pyaz ke bina sabzi', tag: 'Hindi 🇮🇳' },
                    { query: 'vegan desserts', tag: 'Dietary' },
                    { query: 'लसूण नाही भाजी', tag: 'Marathi 🇮🇳' },
                    { query: 'vegetarian biryani', tag: 'Popular' },
                    { query: 'paneer no cream', tag: 'Healthy' },
                    { query: 'கேரட் ஹல்வா', tag: 'Tamil 🇮🇳' },
                    { query: 'quick breakfast under 15 minutes', tag: 'Time' },
                    { query: 'masala dosa', tag: 'South Indian' }
                  ].map((example, i) => (
                    <button
                      key={i}
                      onClick={() => {
                        setQuery(example.query)
                        handleSearch(example.query)
                      }}
                      className="group relative p-4 bg-slate-800 rounded-lg border border-slate-700 hover:border-blue-500 hover:bg-slate-700 transition-all duration-200 text-left"
                    >
                      <div className="flex items-center justify-between gap-2">
                        <span className="font-medium text-gray-300 group-hover:text-white">
                          {example.query}
                        </span>
                        <span className="text-xs px-2 py-1 rounded-full bg-slate-700 text-gray-400 group-hover:bg-blue-600 group-hover:text-white transition-all">
                          {example.tag}
                        </span>
                      </div>
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
