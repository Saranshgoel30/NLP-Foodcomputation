'use client'

import React from 'react'
import { Clock, Users, ChefHat, Heart, Star, TrendingUp, Flame, Leaf } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { cn } from '@/lib/utils'

interface Recipe {
  id: string
  title: string
  image?: string
  cookTime?: number
  servings?: number
  difficulty?: 'easy' | 'medium' | 'hard'
  rating?: number
  cuisine?: string
  diet?: string[]
  calories?: number
  isPopular?: boolean
  isTrending?: boolean
}

interface ModernRecipeCardProps {
  recipe: Recipe
  onClick?: () => void
}

export default function ModernRecipeCard({ recipe, onClick }: ModernRecipeCardProps) {
  const [isLiked, setIsLiked] = React.useState(false)
  const [imageError, setImageError] = React.useState(false)

  const difficultyColors = {
    easy: 'bg-green-500',
    medium: 'bg-yellow-500',
    hard: 'bg-red-500',
  }

  const difficultyColor = recipe.difficulty ? difficultyColors[recipe.difficulty] : difficultyColors.easy

  return (
    <div
      onClick={onClick}
      className="group relative bg-white rounded-lg border-2 border-gray-200 hover:border-orange-500 hover:shadow-xl transition-all duration-200 overflow-hidden cursor-pointer"
    >
      {/* Header with Icon and Like Button - No Image */}
      <div className="relative bg-gradient-to-br from-orange-50 to-red-50 p-6">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-xl bg-white shadow-md">
              <ChefHat className="w-8 h-8 text-orange-500" />
            </div>
            <div>
              {recipe.cuisine && (
                <span className="px-3 py-1 rounded-full bg-white text-orange-600 text-xs font-semibold shadow-sm">
                  {recipe.cuisine}
                </span>
              )}
            </div>
          </div>
          
          {/* Like Button */}
          <button
            onClick={(e) => {
              e.stopPropagation()
              setIsLiked(!isLiked)
            }}
            className={cn(
              "p-2 rounded-full transition-all shadow-md",
              isLiked 
                ? "bg-red-500 text-white scale-110" 
                : "bg-white text-gray-600 hover:scale-110"
            )}
          >
            <Heart
              className={cn("w-5 h-5", isLiked && "fill-current")}
            />
          </button>
        </div>

        {/* Badges */}
        <div className="flex flex-wrap gap-2 mt-4">
          {recipe.isPopular && (
            <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-orange-500 text-white text-xs font-semibold shadow-sm">
              <Flame className="w-3 h-3" />
              Popular
            </span>
          )}
          {recipe.isTrending && (
            <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-purple-500 text-white text-xs font-semibold shadow-sm">
              <TrendingUp className="w-3 h-3" />
              Trending
            </span>
          )}
          {recipe.diet && recipe.diet.map((diet, index) => (
            <span
              key={index}
              className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-green-500 text-white text-xs font-semibold shadow-sm"
            >
              <Leaf className="w-3 h-3" />
              {diet}
            </span>
          ))}
        </div>
      </div>

      {/* Content Section */}
      <div className="p-5">
        {/* Title */}
        <h3 className="text-lg font-bold text-gray-900 mb-3 line-clamp-2 group-hover:text-orange-600 transition-colors">
          {recipe.title}
        </h3>

        {/* Tags */}
        <div className="flex flex-wrap gap-2 mb-4">
          {recipe.cuisine && (
            <span className="px-2 py-1 rounded bg-gray-100 text-gray-700 text-xs font-medium">
              {recipe.cuisine}
            </span>
          )}
          {recipe.diet && recipe.diet.map((diet, index) => (
            <span
              key={index}
              className="inline-flex items-center gap-1 px-2 py-1 rounded bg-green-50 text-green-700 text-xs font-medium"
            >
              <Leaf className="w-3 h-3" />
              {diet}
            </span>
          ))}
        </div>

        {/* Meta Information */}
        <div className="grid grid-cols-3 gap-3 mb-4">
          {recipe.cookTime && (
            <div className="flex items-center gap-2 text-gray-600">
              <div className="p-1.5 rounded bg-gray-100">
                <Clock className="w-4 h-4 text-gray-600" />
              </div>
              <div>
                <p className="text-xs text-gray-500">Time</p>
                <p className="text-sm font-semibold">{recipe.cookTime}m</p>
              </div>
            </div>
          )}
          
          {recipe.servings && (
            <div className="flex items-center gap-2 text-gray-600">
              <div className="p-1.5 rounded bg-gray-100">
                <Users className="w-4 h-4 text-gray-600" />
              </div>
              <div>
                <p className="text-xs text-gray-500">Serves</p>
                <p className="text-sm font-semibold">{recipe.servings}</p>
              </div>
            </div>
          )}

          {recipe.calories && (
            <div className="flex items-center gap-2 text-gray-600">
              <div className="p-1.5 rounded bg-gray-100">
                <Flame className="w-4 h-4 text-gray-600" />
              </div>
              <div>
                <p className="text-xs text-gray-500">Calories</p>
                <p className="text-sm font-semibold">{recipe.calories}</p>
              </div>
            </div>
          )}
        </div>

        {/* Difficulty Bar */}
        {recipe.difficulty && (
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="text-gray-500">Difficulty</span>
              <span className="font-semibold capitalize text-gray-700">
                {recipe.difficulty}
              </span>
            </div>
            <div className="h-1.5 bg-gray-200 rounded-full overflow-hidden">
              <div
                className={cn("h-full rounded-full transition-all", difficultyColor)}
                style={{
                  width: recipe.difficulty === 'easy' ? '33%' : recipe.difficulty === 'medium' ? '66%' : '100%'
                }}
              />
            </div>
          </div>
        )}

        {/* Action Button */}
        <Button
          onClick={(e: React.MouseEvent) => {
            e.stopPropagation()
            onClick?.()
          }}
          variant="default"
          className="w-full mt-4"
        >
          View Recipe
        </Button>
      </div>

      {/* Hover Effect Overlay */}
      <div className="absolute inset-0 border-2 border-transparent group-hover:border-orange-500 rounded-2xl transition-colors pointer-events-none"></div>
    </div>
  )
}

// Grid Component for Multiple Cards
interface RecipeGridProps {
  recipes: Recipe[]
  onRecipeClick?: (recipe: Recipe) => void
}

export function RecipeGrid({ recipes, onRecipeClick }: RecipeGridProps) {
  if (recipes.length === 0) {
    return (
      <div className="text-center py-20">
        <ChefHat className="w-20 h-20 text-gray-300 mx-auto mb-4" />
        <h3 className="text-xl font-semibold text-gray-600 mb-2">No recipes found</h3>
        <p className="text-gray-500">Try adjusting your search criteria</p>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      {recipes.map((recipe) => (
        <ModernRecipeCard
          key={recipe.id}
          recipe={recipe}
          onClick={() => onRecipeClick?.(recipe)}
        />
      ))}
    </div>
  )
}
