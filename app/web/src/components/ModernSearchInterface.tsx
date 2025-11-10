'use client'

import React, { useState } from 'react'
import { Search, Mic, Sparkles, Globe, Clock, ChefHat, Heart, TrendingUp, Zap, ArrowLeft } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import VoiceSearchModal from '@/components/VoiceSearchModal'
import LanguageSelector from './LanguageSelector'
import ModernRecipeCard from './ModernRecipeCard'
import RecipeDetailModal from './RecipeDetailModal'

// Mock recipe data
const mockRecipes = [
  {
    id: '1',
    title: 'Paneer Butter Masala',
    image: 'https://images.unsplash.com/photo-1631452180519-c014fe946bc7?w=400',
    description: 'A creamy and delicious North Indian curry made with paneer cubes in a rich tomato-based gravy.',
    cookTime: 45,
    prepTime: 15,
    servings: 4,
    difficulty: 'medium' as const,
    rating: 4.8,
    cuisine: 'Indian',
    diet: ['Vegetarian'],
    calories: 320,
    isPopular: true,
    isTrending: false,
    ingredients: [
      '400g paneer, cubed',
      '3 large tomatoes, pureed',
      '1 large onion, finely chopped',
      '2 tbsp butter',
      '1 tbsp oil',
      '1 tsp ginger-garlic paste',
      '1 tsp red chili powder',
      '1 tsp garam masala',
      '1/2 tsp turmeric powder',
      '1/2 cup cream',
      'Salt to taste',
      'Fresh coriander for garnish'
    ],
    instructions: [
      'Heat butter and oil in a pan. Add chopped onions and sauté until golden brown.',
      'Add ginger-garlic paste and cook for 1 minute until fragrant.',
      'Add tomato puree, red chili powder, turmeric, and salt. Cook for 10 minutes.',
      'Add cream and garam masala. Mix well and simmer for 5 minutes.',
      'Add paneer cubes and cook for another 5 minutes.',
      'Garnish with fresh coriander and serve hot with naan or rice.'
    ],
    nutrition: {
      protein: 18,
      carbs: 25,
      fat: 22,
      fiber: 4
    },
    tags: ['Dinner', 'Vegetarian', 'Indian', 'Curry']
  },
  {
    id: '2',
    title: 'Chicken Biryani',
    image: 'https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=400',
    description: 'Aromatic basmati rice layered with spiced chicken, cooked in the traditional dum style.',
    cookTime: 90,
    prepTime: 30,
    servings: 6,
    difficulty: 'hard' as const,
    rating: 4.9,
    cuisine: 'Indian',
    diet: [],
    calories: 450,
    isPopular: true,
    isTrending: true,
    ingredients: [
      '500g chicken, cut into pieces',
      '2 cups basmati rice',
      '2 large onions, sliced',
      '1 cup yogurt',
      '2 tbsp biryani masala',
      '1 tsp garam masala',
      'Saffron strands',
      '4 tbsp ghee',
      'Mint and coriander leaves',
      'Salt to taste'
    ],
    instructions: [
      'Marinate chicken with yogurt, biryani masala, and salt for 2 hours.',
      'Soak rice for 30 minutes, then parboil until 70% cooked.',
      'Fry onions until golden brown. Reserve half for garnish.',
      'Layer marinated chicken in a heavy-bottomed pot.',
      'Add rice layer on top, then fried onions, mint, and saffron milk.',
      'Cover tightly and cook on low heat for 45 minutes (dum cooking).',
      'Gently mix and serve hot with raita.'
    ],
    nutrition: {
      protein: 32,
      carbs: 55,
      fat: 18,
      fiber: 3
    },
    tags: ['Dinner', 'Rice', 'Chicken', 'Biryani']
  },
  {
    id: '3',
    title: 'Dal Tadka',
    image: 'https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=400',
    description: 'Comforting yellow lentils tempered with aromatic spices and ghee.',
    cookTime: 30,
    prepTime: 10,
    servings: 4,
    difficulty: 'easy' as const,
    rating: 4.6,
    cuisine: 'Indian',
    diet: ['Vegetarian', 'Vegan'],
    calories: 180,
    isPopular: false,
    isTrending: false,
    ingredients: [
      '1 cup yellow lentils (toor dal)',
      '2 tomatoes, chopped',
      '1 onion, finely chopped',
      '2 green chilies',
      '1 tsp cumin seeds',
      '1/2 tsp turmeric',
      '2 tbsp ghee or oil',
      'Curry leaves',
      'Coriander leaves',
      'Salt to taste'
    ],
    instructions: [
      'Pressure cook lentils with turmeric and salt until soft.',
      'Mash lentils slightly and keep aside.',
      'Heat ghee in a pan, add cumin seeds and let them crackle.',
      'Add curry leaves, green chilies, and onions. Sauté until golden.',
      'Add tomatoes and cook until soft.',
      'Pour this tadka over cooked dal and mix well.',
      'Garnish with coriander and serve with rice or roti.'
    ],
    nutrition: {
      protein: 12,
      carbs: 28,
      fat: 6,
      fiber: 8
    },
    tags: ['Lunch', 'Vegetarian', 'Lentils', 'Healthy']
  },
  {
    id: '4',
    title: 'Palak Paneer',
    image: 'https://images.unsplash.com/photo-1601050690597-df0568f70950?w=400',
    description: 'Soft paneer cubes in a creamy spinach gravy, packed with nutrients.',
    cookTime: 40,
    prepTime: 15,
    servings: 4,
    difficulty: 'medium' as const,
    rating: 4.7,
    cuisine: 'Indian',
    diet: ['Vegetarian'],
    calories: 280,
    isPopular: false,
    isTrending: true,
    ingredients: [
      '300g paneer, cubed',
      '500g spinach leaves',
      '2 tomatoes, chopped',
      '1 onion, chopped',
      '2 green chilies',
      '1 tsp garam masala',
      '1/2 cup cream',
      '2 tbsp butter',
      'Salt to taste'
    ],
    instructions: [
      'Blanch spinach in boiling water for 2 minutes, then puree.',
      'Heat butter, add onions and cook until translucent.',
      'Add tomatoes, green chilies, and cook until soft.',
      'Add spinach puree and bring to a boil.',
      'Add garam masala and cream. Mix well.',
      'Gently add paneer cubes and simmer for 5 minutes.',
      'Serve hot with naan or paratha.'
    ],
    nutrition: {
      protein: 16,
      carbs: 18,
      fat: 20,
      fiber: 6
    },
    tags: ['Dinner', 'Vegetarian', 'Healthy', 'Spinach']
  },
  {
    id: '5',
    title: 'Aloo Gobi',
    image: 'https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=400',
    description: 'Classic dry curry made with potatoes and cauliflower, spiced perfectly.',
    cookTime: 35,
    prepTime: 10,
    servings: 4,
    difficulty: 'easy' as const,
    rating: 4.5,
    cuisine: 'Indian',
    diet: ['Vegetarian', 'Vegan'],
    calories: 150,
    isPopular: false,
    isTrending: false,
    ingredients: [
      '2 large potatoes, cubed',
      '1 cauliflower, cut into florets',
      '2 tomatoes, chopped',
      '1 onion, chopped',
      '1 tsp cumin seeds',
      '1 tsp turmeric',
      '1 tsp coriander powder',
      '2 tbsp oil',
      'Fresh coriander',
      'Salt to taste'
    ],
    instructions: [
      'Heat oil, add cumin seeds until they crackle.',
      'Add onions and sauté until golden.',
      'Add tomatoes and spices, cook for 5 minutes.',
      'Add potatoes and cauliflower, mix well.',
      'Cover and cook on low heat for 20 minutes.',
      'Stir occasionally until vegetables are tender.',
      'Garnish with coriander and serve.'
    ],
    nutrition: {
      protein: 5,
      carbs: 28,
      fat: 7,
      fiber: 6
    },
    tags: ['Lunch', 'Vegetarian', 'Vegan', 'Healthy']
  },
  {
    id: '6',
    title: 'Masala Dosa',
    image: 'https://images.unsplash.com/photo-1630383249896-424e482df921?w=400',
    description: 'Crispy South Indian crepe filled with spiced potato filling.',
    cookTime: 60,
    prepTime: 480,
    servings: 4,
    difficulty: 'medium' as const,
    rating: 4.8,
    cuisine: 'South Indian',
    diet: ['Vegetarian', 'Vegan'],
    calories: 220,
    isPopular: true,
    isTrending: false,
    ingredients: [
      '2 cups rice',
      '1/2 cup urad dal',
      '4 potatoes, boiled',
      '1 onion, chopped',
      '2 green chilies',
      '1 tsp mustard seeds',
      'Curry leaves',
      '1/2 tsp turmeric',
      'Oil for cooking',
      'Salt to taste'
    ],
    instructions: [
      'Soak rice and dal separately for 6-8 hours.',
      'Grind to a smooth batter and ferment overnight.',
      'For filling: heat oil, add mustard seeds and curry leaves.',
      'Add onions, green chilies, and turmeric. Sauté.',
      'Add mashed potatoes, mix well and cook for 5 minutes.',
      'Heat a non-stick pan, spread dosa batter thinly.',
      'Place potato filling in center, fold and serve with chutney.'
    ],
    nutrition: {
      protein: 8,
      carbs: 42,
      fat: 8,
      fiber: 5
    },
    tags: ['Breakfast', 'South Indian', 'Vegetarian', 'Fermented']
  },
]

export default function ModernSearchInterface() {
  const [query, setQuery] = useState('')
  const [isVoiceModalOpen, setIsVoiceModalOpen] = useState(false)
  const [selectedLanguage, setSelectedLanguage] = useState('en')
  const [isSearching, setIsSearching] = useState(false)
  const [showResults, setShowResults] = useState(false)
  const [selectedRecipe, setSelectedRecipe] = useState<any>(null)

  const handleSearch = async () => {
    if (!query.trim()) return
    setIsSearching(true)
    // Show results after a short delay
    setTimeout(() => {
      setIsSearching(false)
      setShowResults(true)
    }, 800)
  }

  const handleBackToSearch = () => {
    setShowResults(false)
    setQuery('')
  }

  const quickSearches = [
    { icon: <ChefHat className="w-4 h-4" />, text: 'Paneer recipes' },
    { icon: <Heart className="w-4 h-4" />, text: 'Vegetarian' },
    { icon: <Clock className="w-4 h-4" />, text: 'Quick meals' },
    { icon: <Globe className="w-4 h-4" />, text: 'Indian cuisine' },
  ]

  // If showing results, render the results view
  if (showResults) {
    return (
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
          <div className="container mx-auto px-4 py-4">
            <div className="flex items-center gap-4">
              <Button
                onClick={handleBackToSearch}
                variant="ghost"
                size="icon"
                className="rounded-lg"
              >
                <ArrowLeft className="w-5 h-5" />
              </Button>
              
              <div className="flex items-center gap-3">
                <div className="bg-orange-600 p-2 rounded-lg">
                  <ChefHat className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-lg font-bold text-gray-900">MMFOOD</h1>
                </div>
              </div>

              <div className="flex-1 max-w-2xl mx-auto">
                <div className="bg-white rounded-lg border border-gray-300 shadow-sm p-2 flex items-center gap-3">
                  <Search className="w-5 h-5 text-gray-400 ml-2" />
                  <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                    placeholder="Search recipes..."
                    className="flex-1 bg-transparent border-none outline-none text-sm text-gray-700"
                  />
                  <Button
                    onClick={handleSearch}
                    size="sm"
                    className="bg-orange-600 hover:bg-orange-700 text-white rounded-lg"
                  >
                    <Search className="w-4 h-4" />
                  </Button>
                </div>
              </div>

              <LanguageSelector 
                value={selectedLanguage}
                onChange={setSelectedLanguage}
              />
            </div>
          </div>
        </header>

        {/* Results */}
        <div className="container mx-auto px-4 py-8">
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Search Results for "{query}"
            </h2>
            <p className="text-gray-600">
              Found {mockRecipes.length} recipes
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {mockRecipes.map((recipe) => (
              <ModernRecipeCard
                key={recipe.id}
                recipe={recipe}
                onClick={() => setSelectedRecipe(recipe)}
              />
            ))}
          </div>
        </div>

        {/* Recipe Detail Modal */}
        {selectedRecipe && (
          <RecipeDetailModal
            recipe={selectedRecipe}
            isOpen={!!selectedRecipe}
            onClose={() => setSelectedRecipe(null)}
          />
        )}
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <div className="relative">
        {/* Header */}
        <header className="bg-white border-b border-gray-200">
          <div className="container mx-auto px-4 py-4">
            <nav className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="bg-orange-600 p-2 rounded-lg">
                  <ChefHat className="w-7 h-7 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-gray-900">
                    MMFOOD
                  </h1>
                  <p className="text-xs text-gray-500">Multilingual Food Knowledge</p>
                </div>
              </div>

              <LanguageSelector 
                value={selectedLanguage}
                onChange={setSelectedLanguage}
              />
            </nav>
          </div>
        </header>

        {/* Main Search Section */}
        <div className="container mx-auto px-4 py-16 max-w-5xl">
          <div className="text-center mb-12">
            <div className="inline-flex items-center gap-2 bg-white border border-gray-200 rounded-full px-4 py-2 mb-6">
              <Sparkles className="w-4 h-4 text-orange-600" />
              <span className="text-sm font-medium text-gray-700">
                AI-Powered Recipe Discovery
              </span>
            </div>
            
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4 leading-tight">
              Find Your Perfect Recipe
              <span className="block text-orange-600 mt-2">
                in Any Language
              </span>
            </h2>
            
            <p className="text-lg text-gray-600 mb-10 max-w-2xl mx-auto">
              Search with voice or text in 10+ Indian languages. Get instant results with nutrition info.
            </p>

            {/* Search Bar */}
            <div className="max-w-3xl mx-auto mb-8">
              <div className="bg-white rounded-lg border border-gray-300 shadow-sm hover:shadow-md transition-shadow p-2 flex items-center gap-3">
                <Search className="w-5 h-5 text-gray-400 ml-3" />
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                  placeholder="Try 'paneer recipes without onions' or 'मुझे बिरयानी रेसिपी चाहिए'"
                  className="flex-1 bg-transparent border-none outline-none text-base py-3 text-gray-700 placeholder-gray-400"
                />
                <Button
                  onClick={() => setIsVoiceModalOpen(true)}
                  variant="ghost"
                  size="icon"
                  className="rounded-lg hover:bg-gray-100"
                >
                  <Mic className="w-5 h-5 text-gray-600" />
                </Button>
                <Button
                  onClick={handleSearch}
                  disabled={!query.trim() || isSearching}
                  size="lg"
                  className="bg-orange-600 hover:bg-orange-700 text-white rounded-lg"
                >
                  {isSearching ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                      Searching...
                    </>
                  ) : (
                    <>
                      <Search className="w-5 h-5 mr-2" />
                      Search
                    </>
                  )}
                </Button>
              </div>
            </div>

            {/* Quick Searches */}
            <div className="flex flex-wrap items-center justify-center gap-2">
              <span className="text-sm text-gray-500">Popular:</span>
              {quickSearches.map((item, index) => (
                <button
                  key={index}
                  onClick={() => {
                    setQuery(item.text)
                    setTimeout(() => handleSearch(), 100)
                  }}
                  className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-white border border-gray-300 text-gray-700 text-sm font-medium hover:bg-gray-50 hover:border-orange-600 hover:text-orange-600 transition-colors"
                >
                  {item.icon}
                  {item.text}
                </button>
              ))}
            </div>
          </div>

          {/* Feature Cards */}
          <div className="grid md:grid-cols-3 gap-6 mt-16">
            <FeatureCard
              icon={<Globe className="w-7 h-7 text-blue-600" />}
              title="10+ Languages"
              description="Search in Hindi, Tamil, Telugu, Bengali, and more"
            />
            <FeatureCard
              icon={<Zap className="w-7 h-7 text-purple-600" />}
              title="AI-Powered"
              description="LLM-enhanced understanding for complex queries"
            />
            <FeatureCard
              icon={<Heart className="w-7 h-7 text-red-600" />}
              title="Smart Filtering"
              description="Dietary restrictions, allergens, and preferences"
            />
          </div>
        </div>
      </div>

      {/* Stats Section */}
      <div className="bg-white border-t border-gray-200 py-12">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-4 gap-8 text-center">
            <StatItem number="8,945" label="Recipes" icon={<ChefHat className="w-6 h-6" />} />
            <StatItem number="341K" label="Triples" icon={<Sparkles className="w-6 h-6" />} />
            <StatItem number="10+" label="Languages" icon={<Globe className="w-6 h-6" />} />
            <StatItem number="95%" label="Accuracy" icon={<TrendingUp className="w-6 h-6" />} />
          </div>
        </div>
      </div>

      {/* Voice Search Modal */}
      <VoiceSearchModal
        isOpen={isVoiceModalOpen}
        onClose={() => setIsVoiceModalOpen(false)}
        language={selectedLanguage}
      />
    </div>
  )
}

function FeatureCard({ icon, title, description }: {
  icon: React.ReactNode
  title: string
  description: string
}) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 hover:border-orange-600 hover:shadow-md transition-all">
      <div className="inline-flex p-3 rounded-lg bg-gray-50 mb-4">
        {icon}
      </div>
      <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-600 text-sm leading-relaxed">{description}</p>
    </div>
  )
}

function StatItem({ number, label, icon }: {
  number: string
  label: string
  icon: React.ReactNode
}) {
  return (
    <div>
      <div className="inline-flex items-center justify-center w-12 h-12 rounded-lg bg-orange-600 text-white mb-3">
        {icon}
      </div>
      <div className="text-3xl font-bold text-gray-900 mb-1">{number}</div>
      <div className="text-sm text-gray-500">{label}</div>
    </div>
  )
}
