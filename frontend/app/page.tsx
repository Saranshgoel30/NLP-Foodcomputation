'use client';

import { useState, useEffect, useCallback } from 'react';
import { Search, Mic, MicOff, Moon, Sun, Sparkles } from 'lucide-react';
import { SearchResults } from '@/components/SearchResults';
import { SearchFilters } from '@/components/SearchFilters';
import { VoiceInput } from '@/components/VoiceInput';
import { searchIngredients } from '@/lib/api';
import type { Ingredient, SearchResponse } from '@/types';

export default function Home() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<Ingredient[]>([]);
  const [loading, setLoading] = useState(false);
  const [responseTime, setResponseTime] = useState<number | null>(null);
  const [searchStrategy, setSearchStrategy] = useState<'semantic' | 'keyword' | 'hybrid'>('hybrid');
  const [selectedFilters, setSelectedFilters] = useState<{
    foodGroups: string[];
    tags: string[];
  }>({ foodGroups: [], tags: [] });
  const [isVoiceActive, setIsVoiceActive] = useState(false);
  const [darkMode, setDarkMode] = useState(false);

  // Toggle dark mode
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  // Debounced search
  const performSearch = useCallback(async (searchQuery: string) => {
    if (!searchQuery.trim()) {
      setResults([]);
      setResponseTime(null);
      return;
    }

    setLoading(true);
    const startTime = performance.now();

    try {
      const response: SearchResponse = await searchIngredients(
        searchQuery,
        searchStrategy,
        selectedFilters
      );

      const endTime = performance.now();
      setResponseTime(endTime - startTime);
      setResults(response.results);
    } catch (error) {
      console.error('Search error:', error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  }, [searchStrategy, selectedFilters]);

  // Real-time search with debounce
  useEffect(() => {
    const timer = setTimeout(() => {
      performSearch(query);
    }, 300); // 300ms debounce

    return () => clearTimeout(timer);
  }, [query, performSearch]);

  const handleVoiceResult = (transcript: string) => {
    setQuery(transcript);
    setIsVoiceActive(false);
  };

  return (
    <div className={`min-h-screen transition-colors duration-200 ${
      darkMode ? 'dark bg-gray-900' : 'bg-gradient-to-br from-orange-50 via-white to-green-50'
    }`}>
      {/* Header */}
      <header className="sticky top-0 z-50 backdrop-blur-lg bg-white/80 dark:bg-gray-900/80 border-b border-gray-200 dark:border-gray-700 shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Sparkles className="w-8 h-8 text-orange-500" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                  FoodKG Search
                </h1>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Multilingual Semantic Search • 100x Faster
                </p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              {/* Search Strategy Selector */}
              <select
                value={searchStrategy}
                onChange={(e) => setSearchStrategy(e.target.value as any)}
                className="px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-orange-500 outline-none"
              >
                <option value="hybrid">🚀 Hybrid Search</option>
                <option value="semantic">🧠 Semantic Search</option>
                <option value="keyword">🔍 Keyword Search</option>
              </select>

              {/* Dark Mode Toggle */}
              <button
                onClick={() => setDarkMode(!darkMode)}
                className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                aria-label="Toggle dark mode"
              >
                {darkMode ? (
                  <Sun className="w-5 h-5 text-yellow-500" />
                ) : (
                  <Moon className="w-5 h-5 text-gray-600" />
                )}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* Search Bar */}
        <div className="max-w-4xl mx-auto mb-8">
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <Search className="w-5 h-5 text-gray-400" />
            </div>
            
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search ingredients in any language... (English, Hindi, Tamil, Kannada, etc.)"
              className="w-full pl-12 pr-32 py-4 text-lg rounded-2xl border-2 border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:border-orange-500 focus:ring-4 focus:ring-orange-500/20 outline-none transition-all shadow-lg"
            />

            {/* Voice Input Button */}
            <div className="absolute inset-y-0 right-0 pr-4 flex items-center gap-2">
              {loading && (
                <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                  <div className="w-4 h-4 border-2 border-orange-500 border-t-transparent rounded-full animate-spin" />
                  Searching...
                </div>
              )}
              
              <button
                onClick={() => setIsVoiceActive(!isVoiceActive)}
                className={`p-3 rounded-xl transition-all ${
                  isVoiceActive
                    ? 'bg-red-500 text-white shadow-lg shadow-red-500/50'
                    : 'bg-orange-500 hover:bg-orange-600 text-white shadow-lg hover:shadow-xl'
                }`}
                aria-label="Voice search"
              >
                {isVoiceActive ? (
                  <MicOff className="w-5 h-5" />
                ) : (
                  <Mic className="w-5 h-5" />
                )}
              </button>
            </div>
          </div>

          {/* Voice Input Component */}
          {isVoiceActive && (
            <VoiceInput
              onResult={handleVoiceResult}
              onClose={() => setIsVoiceActive(false)}
            />
          )}

          {/* Response Time Badge */}
          {responseTime !== null && (
            <div className="mt-4 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="px-3 py-1 rounded-full bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 text-sm font-semibold">
                  ⚡ {responseTime.toFixed(0)}ms
                </span>
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  Found {results.length} results
                </span>
              </div>
              
              <div className="text-sm text-gray-500 dark:text-gray-400">
                {searchStrategy === 'hybrid' && '🚀 Hybrid: Semantic + Keyword'}
                {searchStrategy === 'semantic' && '🧠 Understanding meaning'}
                {searchStrategy === 'keyword' && '🔍 Exact matching'}
              </div>
            </div>
          )}
        </div>

        {/* Filters and Results */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Filters Sidebar */}
          <div className="lg:col-span-1">
            <SearchFilters
              selectedFilters={selectedFilters}
              onFilterChange={setSelectedFilters}
            />
          </div>

          {/* Search Results */}
          <div className="lg:col-span-3">
            {query.trim() === '' ? (
              <div className="text-center py-20">
                <Sparkles className="w-16 h-16 text-orange-300 mx-auto mb-4" />
                <h2 className="text-2xl font-semibold text-gray-800 dark:text-gray-200 mb-2">
                  Revolutionary Multilingual Search
                </h2>
                <p className="text-gray-600 dark:text-gray-400 mb-6">
                  Search in 10+ languages with semantic understanding
                </p>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 max-w-2xl mx-auto">
                  {['Rice', 'दूध (Milk)', 'தக்காளி (Tomato)', 'ಬೆಳ್ಳುಳ್ಳಿ (Garlic)', 'মরিচ (Chili)', 'پیاز (Onion)', 'हल्दी (Turmeric)', 'नमक (Salt)'].map((example) => (
                    <button
                      key={example}
                      onClick={() => setQuery(example.split(' ')[0])}
                      className="px-4 py-2 rounded-lg bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-400 hover:bg-orange-200 dark:hover:bg-orange-900/50 transition-colors text-sm font-medium"
                    >
                      {example}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <SearchResults results={results} loading={loading} />
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-20 py-8 border-t border-gray-200 dark:border-gray-700">
        <div className="container mx-auto px-4 text-center text-gray-600 dark:text-gray-400">
          <p className="text-sm">
            Powered by <span className="font-semibold text-orange-500">Typesense</span> • 
            768-dim embeddings • RRF fusion • 100x faster than traditional search
          </p>
        </div>
      </footer>
    </div>
  );
}
