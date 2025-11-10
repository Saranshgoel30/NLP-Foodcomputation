'use client'

import React, { useState } from 'react'
import { X, Clock, Users, ChefHat, Heart, Share2, Printer, Star, Flame, Leaf, AlertCircle, Check } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { cn } from '@/lib/utils'

interface RecipeDetailModalProps {
  isOpen: boolean
  onClose: () => void
  recipe: {
    id: string
    title: string
    image?: string
    description?: string
    cookTime?: number
    prepTime?: number
    servings?: number
    difficulty?: string
    rating?: number
    cuisine?: string
    diet?: string[]
    calories?: number
    ingredients?: string[]
    instructions?: string[]
    nutrition?: {
      protein?: number
      carbs?: number
      fat?: number
      fiber?: number
    }
    tags?: string[]
  }
}

export default function RecipeDetailModal({ isOpen, onClose, recipe }: RecipeDetailModalProps) {
  const [isLiked, setIsLiked] = useState(false)
  const [activeTab, setActiveTab] = useState<'ingredients' | 'instructions' | 'nutrition'>('ingredients')
  const [checkedIngredients, setCheckedIngredients] = useState<Set<number>>(new Set())
  const [completedSteps, setCompletedSteps] = useState<Set<number>>(new Set())

  if (!isOpen) return null

  const toggleIngredient = (index: number) => {
    const newChecked = new Set(checkedIngredients)
    if (newChecked.has(index)) {
      newChecked.delete(index)
    } else {
      newChecked.add(index)
    }
    setCheckedIngredients(newChecked)
  }

  const toggleStep = (index: number) => {
    const newCompleted = new Set(completedSteps)
    if (newCompleted.has(index)) {
      newCompleted.delete(index)
    } else {
      newCompleted.add(index)
    }
    setCompletedSteps(newCompleted)
  }

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative min-h-screen flex items-center justify-center p-4">
        <div className="relative w-full max-w-6xl bg-white rounded-3xl shadow-2xl overflow-hidden animate-in fade-in slide-in-from-bottom-4">
          {/* Header Image */}
          <div className="relative h-80 bg-gradient-to-br from-orange-100 to-red-100">
            {recipe.image ? (
              <img
                src={recipe.image}
                alt={recipe.title}
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center">
                <ChefHat className="w-32 h-32 text-orange-300" />
              </div>
            )}
            <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent"></div>

            {/* Close Button */}
            <button
              onClick={onClose}
              className="absolute top-4 right-4 p-3 rounded-full bg-white/90 backdrop-blur-sm hover:bg-white transition-colors shadow-lg"
            >
              <X className="w-6 h-6 text-gray-700" />
            </button>

            {/* Action Buttons */}
            <div className="absolute top-4 left-4 flex gap-2">
              <button
                onClick={() => setIsLiked(!isLiked)}
                className={cn(
                  "p-3 rounded-full backdrop-blur-sm transition-all shadow-lg",
                  isLiked
                    ? "bg-red-500 text-white scale-110"
                    : "bg-white/90 text-gray-700 hover:bg-white"
                )}
              >
                <Heart className={cn("w-5 h-5", isLiked && "fill-current")} />
              </button>
              <button className="p-3 rounded-full bg-white/90 backdrop-blur-sm hover:bg-white transition-colors shadow-lg text-gray-700">
                <Share2 className="w-5 h-5" />
              </button>
              <button className="p-3 rounded-full bg-white/90 backdrop-blur-sm hover:bg-white transition-colors shadow-lg text-gray-700">
                <Printer className="w-5 h-5" />
              </button>
            </div>

            {/* Title Overlay */}
            <div className="absolute bottom-0 left-0 right-0 p-8">
              <h1 className="text-4xl font-bold text-white mb-4">{recipe.title}</h1>
              <div className="flex flex-wrap gap-3">
                {recipe.rating && (
                  <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/95 backdrop-blur-sm text-gray-900 font-semibold">
                    <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                    {recipe.rating.toFixed(1)}
                  </span>
                )}
                {recipe.cuisine && (
                  <span className="px-4 py-2 rounded-full bg-white/95 backdrop-blur-sm text-gray-900 font-medium">
                    {recipe.cuisine}
                  </span>
                )}
                {recipe.diet?.map((diet, i) => (
                  <span key={i} className="inline-flex items-center gap-1 px-4 py-2 rounded-full bg-green-500 text-white font-medium">
                    <Leaf className="w-4 h-4" />
                    {diet}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Content */}
          <div className="p-8">
            {/* Meta Info Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
              {recipe.prepTime && (
                <div className="p-4 rounded-xl bg-gradient-to-br from-blue-50 to-cyan-50 border border-blue-200">
                  <Clock className="w-6 h-6 text-blue-600 mb-2" />
                  <p className="text-sm text-gray-600">Prep Time</p>
                  <p className="text-xl font-bold text-gray-900">{recipe.prepTime}m</p>
                </div>
              )}
              {recipe.cookTime && (
                <div className="p-4 rounded-xl bg-gradient-to-br from-orange-50 to-red-50 border border-orange-200">
                  <Flame className="w-6 h-6 text-orange-600 mb-2" />
                  <p className="text-sm text-gray-600">Cook Time</p>
                  <p className="text-xl font-bold text-gray-900">{recipe.cookTime}m</p>
                </div>
              )}
              {recipe.servings && (
                <div className="p-4 rounded-xl bg-gradient-to-br from-purple-50 to-pink-50 border border-purple-200">
                  <Users className="w-6 h-6 text-purple-600 mb-2" />
                  <p className="text-sm text-gray-600">Servings</p>
                  <p className="text-xl font-bold text-gray-900">{recipe.servings}</p>
                </div>
              )}
              {recipe.calories && (
                <div className="p-4 rounded-xl bg-gradient-to-br from-red-50 to-pink-50 border border-red-200">
                  <Flame className="w-6 h-6 text-red-600 mb-2" />
                  <p className="text-sm text-gray-600">Calories</p>
                  <p className="text-xl font-bold text-gray-900">{recipe.calories}</p>
                </div>
              )}
            </div>

            {/* Description */}
            {recipe.description && (
              <div className="mb-8 p-6 rounded-2xl bg-gradient-to-r from-orange-50 to-red-50 border border-orange-200">
                <p className="text-gray-700 leading-relaxed">{recipe.description}</p>
              </div>
            )}

            {/* Tabs */}
            <div className="border-b border-gray-200 mb-6">
              <div className="flex gap-2">
                {['ingredients', 'instructions', 'nutrition'].map((tab) => (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab as any)}
                    className={cn(
                      "px-6 py-3 font-semibold rounded-t-xl transition-all",
                      activeTab === tab
                        ? "bg-gradient-to-r from-orange-500 to-red-500 text-white"
                        : "text-gray-600 hover:bg-gray-100"
                    )}
                  >
                    {tab.charAt(0).toUpperCase() + tab.slice(1)}
                  </button>
                ))}
              </div>
            </div>

            {/* Tab Content */}
            <div className="min-h-[400px]">
              {/* Ingredients Tab */}
              {activeTab === 'ingredients' && (
                <div className="space-y-3">
                  {recipe.ingredients?.map((ingredient, index) => (
                    <label
                      key={index}
                      className="flex items-start gap-4 p-4 rounded-xl bg-white border-2 border-gray-200 hover:border-orange-300 cursor-pointer transition-all group"
                    >
                      <input
                        type="checkbox"
                        checked={checkedIngredients.has(index)}
                        onChange={() => toggleIngredient(index)}
                        className="mt-1 w-5 h-5 rounded border-gray-300 text-orange-500 focus:ring-orange-500"
                      />
                      <span className={cn(
                        "flex-1 text-gray-700 transition-all",
                        checkedIngredients.has(index) && "line-through text-gray-400"
                      )}>
                        {ingredient}
                      </span>
                    </label>
                  )) || (
                    <div className="text-center py-12 text-gray-500">
                      <AlertCircle className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                      <p>No ingredients available</p>
                    </div>
                  )}
                </div>
              )}

              {/* Instructions Tab */}
              {activeTab === 'instructions' && (
                <div className="space-y-6">
                  {recipe.instructions?.map((instruction, index) => (
                    <div
                      key={index}
                      className={cn(
                        "flex gap-4 p-6 rounded-2xl border-2 transition-all",
                        completedSteps.has(index)
                          ? "bg-green-50 border-green-300"
                          : "bg-white border-gray-200 hover:border-orange-300"
                      )}
                    >
                      <button
                        onClick={() => toggleStep(index)}
                        className={cn(
                          "flex-shrink-0 w-10 h-10 rounded-full font-bold text-lg transition-all",
                          completedSteps.has(index)
                            ? "bg-green-500 text-white"
                            : "bg-gradient-to-r from-orange-500 to-red-500 text-white hover:scale-110"
                        )}
                      >
                        {completedSteps.has(index) ? (
                          <Check className="w-6 h-6 mx-auto" />
                        ) : (
                          index + 1
                        )}
                      </button>
                      <p className={cn(
                        "flex-1 text-gray-700 leading-relaxed",
                        completedSteps.has(index) && "text-gray-500"
                      )}>
                        {instruction}
                      </p>
                    </div>
                  )) || (
                    <div className="text-center py-12 text-gray-500">
                      <AlertCircle className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                      <p>No instructions available</p>
                    </div>
                  )}
                </div>
              )}

              {/* Nutrition Tab */}
              {activeTab === 'nutrition' && (
                <div className="space-y-6">
                  {recipe.nutrition ? (
                    <div className="grid md:grid-cols-2 gap-6">
                      {Object.entries(recipe.nutrition).map(([key, value]) => (
                        <div key={key} className="p-6 rounded-2xl bg-gradient-to-br from-blue-50 to-cyan-50 border border-blue-200">
                          <h4 className="text-sm font-medium text-gray-600 mb-2 capitalize">{key}</h4>
                          <p className="text-3xl font-bold text-gray-900">{value}g</p>
                          <div className="mt-4 h-2 bg-white rounded-full overflow-hidden">
                            <div
                              className="h-full bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full"
                              style={{ width: `${Math.min(value as number, 100)}%` }}
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-12 text-gray-500">
                      <AlertCircle className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                      <p>No nutrition information available</p>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Action Buttons */}
            <div className="flex gap-4 mt-8 pt-8 border-t border-gray-200">
              <Button variant="outline" size="lg" className="flex-1">
                <Share2 className="w-5 h-5 mr-2" />
                Share Recipe
              </Button>
              <Button size="lg" className="flex-1">
                <ChefHat className="w-5 h-5 mr-2" />
                Start Cooking
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
