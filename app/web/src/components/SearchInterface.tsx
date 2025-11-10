'use client';

import React, { useState } from 'react';
import { Search, X, SlidersHorizontal } from 'lucide-react';
import { MicButton } from './MicButton';
import { LanguagePicker } from './LanguagePicker';
import { FiltersDrawer } from './FiltersDrawer';
import { ResultsList } from './ResultsList';
import { RecipeModal } from './RecipeModal';
import { apiClient, type Language, type QueryConstraints, type Recipe } from '@/lib/api-client';

export function SearchInterface() {
  const [query, setQuery] = useState('');
  const [selectedLang, setSelectedLang] = useState<Language>('en');
  const [filters, setFilters] = useState<QueryConstraints>({});
  const [isFiltersOpen, setIsFiltersOpen] = useState(false);
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedRecipe, setSelectedRecipe] = useState<Recipe | null>(null);
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearch = async (searchQuery?: string) => {
    const queryText = searchQuery || query;
    
    if (!queryText.trim()) {
      setError('Please enter a search query');
      return;
    }

    setIsLoading(true);
    setError(null);
    setHasSearched(true);

    try {
      const response = await apiClient.search({
        text: queryText,
        lang: selectedLang,
        constraints: filters,
      });

      setRecipes(response.results);
      
      if (response.results.length === 0) {
        setError('No recipes found. Try adjusting your search.');
      }
    } catch (err) {
      console.error('Search failed:', err);
      setError(err instanceof Error ? err.message : 'Search failed. Please try again.');
      setRecipes([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleTranscript = (transcript: string, lang: string) => {
    setQuery(transcript);
    setSelectedLang(lang as Language);
    handleSearch(transcript);
  };

  const handleMicError = (errorMsg: string) => {
    setError(errorMsg);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const clearSearch = () => {
    setQuery('');
    setRecipes([]);
    setError(null);
    setHasSearched(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-white to-red-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                🍲 MMFOOD
              </h1>
              <p className="text-sm text-gray-600 mt-1">
                Multilingual Food Knowledge Search
              </p>
            </div>
            <LanguagePicker
              selectedLang={selectedLang}
              onLanguageChange={setSelectedLang}
            />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search Bar */}
        <div className="mb-8">
          <div className="flex gap-3 items-center">
            <div className="flex-1 relative">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Search for recipes... (e.g., 'Chinese chicken under 30 minutes')"
                className="
                  w-full pl-12 pr-12 py-4 rounded-xl border-2 border-gray-300
                  focus:border-primary-500 focus:ring-2 focus:ring-primary-200
                  text-lg transition-all
                "
              />
              {query && (
                <button
                  onClick={clearSearch}
                  className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  <X className="w-5 h-5" />
                </button>
              )}
            </div>
            
            <MicButton
              onTranscript={handleTranscript}
              onError={handleMicError}
            />
            
            <button
              onClick={() => setIsFiltersOpen(true)}
              className="
                p-4 rounded-xl bg-white border-2 border-gray-300
                hover:border-primary-500 transition-colors
                flex items-center gap-2
              "
            >
              <SlidersHorizontal className="w-5 h-5" />
              <span className="hidden sm:inline">Filters</span>
              {Object.keys(filters).length > 0 && (
                <span className="w-2 h-2 bg-primary-500 rounded-full"></span>
              )}
            </button>
            
            <button
              onClick={() => handleSearch()}
              disabled={isLoading}
              className="
                px-8 py-4 rounded-xl bg-primary-500 text-white font-medium
                hover:bg-primary-600 transition-colors
                disabled:opacity-50 disabled:cursor-not-allowed
              "
            >
              Search
            </button>
          </div>

          {/* Active Filters Display */}
          {Object.keys(filters).length > 0 && (
            <div className="mt-4 flex flex-wrap gap-2">
              {filters.cuisine?.map(c => (
                <span key={c} className="px-3 py-1 bg-blue-100 text-blue-700 text-sm rounded-full">
                  Cuisine: {c}
                </span>
              ))}
              {filters.diet?.map(d => (
                <span key={d} className="px-3 py-1 bg-green-100 text-green-700 text-sm rounded-full">
                  Diet: {d}
                </span>
              ))}
              {filters.maxCookMinutes && (
                <span className="px-3 py-1 bg-purple-100 text-purple-700 text-sm rounded-full">
                  Max: {filters.maxCookMinutes} min
                </span>
              )}
              {filters.exclude?.map(e => (
                <span key={e} className="px-3 py-1 bg-red-100 text-red-700 text-sm rounded-full">
                  No {e}
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Results */}
        {hasSearched && (
          <ResultsList
            recipes={recipes}
            isLoading={isLoading}
            error={error}
            onRecipeClick={setSelectedRecipe}
          />
        )}

        {/* Welcome State */}
        {!hasSearched && (
          <div className="text-center py-16">
            <div className="text-8xl mb-6">👨‍🍳</div>
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Discover Delicious Recipes
            </h2>
            <p className="text-lg text-gray-600 mb-8 max-w-2xl mx-auto">
              Search for recipes in your language using text or voice.
              Filter by cuisine, diet, ingredients, and cooking time.
            </p>
            <div className="flex flex-wrap justify-center gap-3">
              {['brown rice', 'Jain dal', 'Chinese chicken', 'no onion garlic'].map(example => (
                <button
                  key={example}
                  onClick={() => {
                    setQuery(example);
                    handleSearch(example);
                  }}
                  className="px-4 py-2 bg-white border-2 border-gray-300 rounded-lg hover:border-primary-500 transition-colors"
                >
                  {example}
                </button>
              ))}
            </div>
          </div>
        )}
      </main>

      {/* Modals */}
      <FiltersDrawer
        isOpen={isFiltersOpen}
        onClose={() => setIsFiltersOpen(false)}
        filters={filters}
        onFiltersChange={setFilters}
      />

      {selectedRecipe && (
        <RecipeModal
          recipe={selectedRecipe}
          onClose={() => setSelectedRecipe(null)}
        />
      )}
    </div>
  );
}
