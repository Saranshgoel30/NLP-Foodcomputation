'use client'

import { Clock, ExternalLink, X } from 'lucide-react'
import { useState, useEffect } from 'react'

interface Recipe {
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
  instructions?: string[] | any[]
}

interface NutritionData {
  serving_size: string
  nutrition_per_serving: Record<string, number>
}

// Human readable labels for nutrients
const NUTRIENT_LABELS: Record<string, string> = {
  energy: 'Energy',
  protein: 'Protein',
  carbohydrate: 'Carbohydrates',
  total_fat: 'Total Fat',
  dietary_fiber: 'Dietary Fiber',
  free_sugars: 'Sugars',
  saturated_fatty_acids: 'Saturated Fat',
  monounsaturated_fatty_acids: 'Monounsaturated Fat',
  polyunsaturated_fatty_acids: 'Polyunsaturated Fat',
  trans_fatty_acids: 'Trans Fat',
  essential_fatty_acids: 'Essential Fatty Acids',
  cholesterol: 'Cholesterol',
  sodium_na: 'Sodium',
  potassium_k: 'Potassium',
  calcium_ca: 'Calcium',
  iron_fe: 'Iron',
  magnesium_mg: 'Magnesium',
  phosphorus_p: 'Phosphorus',
  zinc_zn: 'Zinc',
  copper_cu: 'Copper',
  manganese_mn: 'Manganese',
  selenium_se: 'Selenium',
  vitamin_a: 'Vitamin A',
  ascorbic_acids_c: 'Vitamin C',
  vitamin_d: 'Vitamin D',
  vitamin_k: 'Vitamin K',
  tocopherol_equivalent_e: 'Vitamin E',
  thiamine_b1: 'Vitamin B1 (Thiamine)',
  riboflavin_b2: 'Vitamin B2 (Riboflavin)',
  niacin_b3: 'Vitamin B3 (Niacin)',
  pantothenic_acid_b5: 'Vitamin B5',
  total_b6: 'Vitamin B6',
  biotin_b7: 'Vitamin B7 (Biotin)',
  folates_b9: 'Vitamin B9 (Folate)',
  vitamin_b: 'Vitamin B',
  carotenoids: 'Carotenoids',
  moisture: 'Moisture',
}

// Nutrients to skip (not useful to display)
const SKIP_NUTRIENTS = ['moisture', 'cis_fatty_acids', 'unsaturated_fatty_acids', 'molybdenum_mo']

// Nutrients that should always be shown in mg (even if value is > 1g)
const SHOW_IN_MG = ['sodium_na', 'potassium_k', 'calcium_ca', 'iron_fe', 'magnesium_mg', 'phosphorus_p', 'zinc_zn', 'copper_cu', 'manganese_mn', 'cholesterol']

// Nutrients that should always be shown in mcg
const SHOW_IN_MCG = ['vitamin_a', 'vitamin_d', 'vitamin_k', 'selenium_se', 'folates_b9', 'biotin_b7']

// Format a nutrient value with proper units
function formatNutrientValue(key: string, value: number): { label: string; display: string } | null {
  // Skip invalid values (-1 means not available, 0 means none)
  if (value < 0) return null
  if (value === 0) return null
  if (SKIP_NUTRIENTS.includes(key)) return null
  
  const label = NUTRIENT_LABELS[key] || key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
  
  let display: string
  
  // Energy is in kcal
  if (key === 'energy') {
    display = `${Math.round(value)} kcal`
  }
  // Nutrients that should be shown in mcg
  else if (SHOW_IN_MCG.includes(key)) {
    const mcg = value * 1000000
    display = mcg >= 1 ? `${mcg.toFixed(1)} mcg` : `${mcg.toFixed(2)} mcg`
  }
  // Nutrients that should be shown in mg (sodium, calcium, iron, etc.)
  else if (SHOW_IN_MG.includes(key)) {
    const mg = value * 1000
    display = mg >= 1 ? `${mg.toFixed(1)} mg` : `${mg.toFixed(2)} mg`
  }
  // B vitamins typically shown in mg
  else if (key.includes('b1') || key.includes('b2') || key.includes('b3') || key.includes('b5') || key.includes('b6') || key === 'ascorbic_acids_c') {
    const mg = value * 1000
    display = mg >= 1 ? `${mg.toFixed(1)} mg` : `${mg.toFixed(2)} mg`
  }
  // Regular macros (protein, carbs, fat, fiber, sugars) in grams
  else if (value >= 1) {
    display = `${value.toFixed(1)} g`
  }
  else if (value >= 0.1) {
    display = `${value.toFixed(2)} g`
  }
  else {
    // Small values convert to mg
    display = `${(value * 1000).toFixed(1)} mg`
  }
  
  return { label, display }
}

async function getNutrition(name: string): Promise<NutritionData | null> {
  try {
    const response = await fetch('http://16.170.211.162:8001/api/nutrition', {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ dish_name: name })
    })
    
    if (!response.ok) return null
    
    const nutrition = await response.json()
    return nutrition
  } catch (error) {
    console.error('Error fetching nutrition:', error)
    return null
  }
}

// Helper function to parse instructions properly
function parseInstructions(instructions: any): string[] {
  if (!instructions) return []
  
  let rawText = ''
  let parsed = instructions
  
  // If it's a string that looks like JSON, try to parse it
  if (typeof instructions === 'string') {
    // Check if it looks like a stringified array/object
    if (instructions.trim().startsWith('[') || instructions.trim().startsWith('{')) {
      try {
        // Replace single quotes with double quotes for valid JSON
        const jsonString = instructions.replace(/'/g, '"')
        parsed = JSON.parse(jsonString)
      } catch {
        // If parsing fails, treat as plain text
        rawText = instructions
      }
    } else {
      rawText = instructions
    }
  }
  
  // If it's an array of objects with 'instructions' field
  if (Array.isArray(parsed) && parsed.length > 0 && typeof parsed[0] === 'object') {
    rawText = parsed.map(item => item.instructions || '').join(' ')
  }
  // If it's already an array of strings
  else if (Array.isArray(parsed) && parsed.length > 0 && typeof parsed[0] === 'string') {
    rawText = parsed.join(' ')
  }
  
  if (!rawText) return []
  
  // Split by common instruction patterns
  const steps = rawText
    // Split on sentence endings followed by capital letters
    .split(/\.\s+(?=[A-Z])/)
    // Clean up each step
    .map(s => s.trim())
    // Filter out very short fragments and serving suggestions
    .filter(s => {
      if (s.length < 20) return false
      // Skip serving suggestions at the end
      if (s.toLowerCase().startsWith('to serve')) return false
      if (s.toLowerCase().startsWith('serve ')) return false
      return true
    })
    // Ensure each step ends with a period
    .map(s => s.endsWith('.') ? s : `${s}.`)
  
  return steps
}

export default function RecipeCard({ recipe }: { recipe: Recipe }) {
  const [isOpen, setIsOpen] = useState(false)
  const [nutrition, setNutrition] = useState<NutritionData | null>(null)
  const [loadingNutrition, setLoadingNutrition] = useState(false)
  
  const parsedInstructions = parseInstructions(recipe.instructions)

  useEffect(() => {
    if (isOpen && !nutrition) {
      setLoadingNutrition(true)
      getNutrition(recipe.name).then((data) => {
        setNutrition(data)
        setLoadingNutrition(false)
      })
    }
  }, [isOpen, recipe.name, nutrition])

  return (
    <>
      {/* Grid Card - Click to Open */}
      <button
        onClick={() => setIsOpen(true)}
        className="group bg-slate-800 rounded-xl border border-slate-700 p-6 hover:border-blue-500 hover:shadow-2xl hover:shadow-blue-500/10 transition-all duration-300 text-left w-full flex flex-col min-h-[180px]"
      >
        <div className="flex-1 flex flex-col">
          <h3 className="text-lg font-bold text-white leading-tight mb-4 group-hover:text-blue-400 transition-colors line-clamp-3">
            {recipe.name}
          </h3>
          
          <div className="mt-auto space-y-3">
            <div className="flex flex-wrap gap-2">
              {recipe.cuisine && (
                <span className="px-2.5 py-1 bg-blue-600 text-white text-xs font-semibold rounded-md">
                  {recipe.cuisine}
                </span>
              )}
              {recipe.diet && (
                <span className="px-2.5 py-1 bg-green-600 text-white text-xs font-semibold rounded-md">
                  {recipe.diet}
                </span>
              )}
              {recipe.course && (
                <span className="px-2.5 py-1 bg-purple-600 text-white text-xs font-semibold rounded-md">
                  {recipe.course}
                </span>
              )}
            </div>
            
            {recipe.total_time && (
              <div className="flex items-center gap-2 text-gray-400 text-sm">
                <Clock className="w-4 h-4" />
                <span>{recipe.total_time} mins</span>
              </div>
            )}
          </div>
        </div>
      </button>

      {/* Modal */}
      {isOpen && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-slate-900 rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto border border-slate-700 shadow-2xl">
            {/* Modal Header */}
            <div className="sticky top-0 bg-slate-900 border-b border-slate-700 p-6 flex items-start justify-between gap-4 z-10">
              <div className="flex-1">
                <h2 className="text-2xl font-bold text-white mb-3 leading-tight">
                  {recipe.name}
                </h2>
                <div className="flex flex-wrap gap-2">
                  {recipe.cuisine && (
                    <span className="px-3 py-1 bg-blue-600 text-white text-sm font-semibold rounded-md">
                      {recipe.cuisine}
                    </span>
                  )}
                  {recipe.diet && (
                    <span className="px-3 py-1 bg-green-600 text-white text-sm font-semibold rounded-md">
                      {recipe.diet}
                    </span>
                  )}
                  {recipe.course && (
                    <span className="px-3 py-1 bg-purple-600 text-white text-sm font-semibold rounded-md">
                      {recipe.course}
                    </span>
                  )}
                  {recipe.total_time && (
                    <span className="px-3 py-1 bg-slate-700 text-white text-sm font-semibold rounded-md flex items-center gap-1.5">
                      <Clock className="w-4 h-4" />
                      {recipe.total_time} mins
                    </span>
                  )}
                </div>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="flex-shrink-0 p-2 hover:bg-slate-800 rounded-lg transition-colors"
              >
                <X className="w-6 h-6 text-gray-400 hover:text-white" />
              </button>
            </div>

            {/* Modal Content */}
            <div className="p-6 space-y-8">
              {/* Nutrition Information */}
              <div>
                <h3 className="text-xl font-bold text-white mb-4 uppercase tracking-wide">
                  Nutrition Information (per serving)
                </h3>
                <div className="bg-slate-800 rounded-xl p-5 border border-slate-700">
                  {loadingNutrition ? (
                    <p className="text-gray-400">Loading nutrition data...</p>
                  ) : nutrition ? (
                    <div className="space-y-4">
                      <p className="text-gray-300 font-semibold text-lg border-b border-slate-600 pb-3">
                        Serving Size: {Math.round(parseFloat(nutrition.serving_size))} g
                      </p>
                      
                      {/* Nutrition table */}
                      <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                          <tbody className="divide-y divide-slate-700">
                            {Object.entries(nutrition.nutrition_per_serving)
                              .map(([key, value]) => formatNutrientValue(key, value))
                              .filter((item): item is { label: string; display: string } => item !== null)
                              .map(({ label, display }, idx) => (
                                <tr key={idx} className={idx % 2 === 0 ? 'bg-slate-700/30' : ''}>
                                  <td className="py-2 px-3 text-gray-300">{label}</td>
                                  <td className="py-2 px-3 text-white font-medium text-right">{display}</td>
                                </tr>
                              ))
                            }
                          </tbody>
                        </table>
                      </div>
                    </div>
                  ) : (
                    <p className="text-gray-400">Nutrition data not available</p>
                  )}
                </div>
              </div>

              {/* Ingredients */}
              <div>
                <h3 className="text-xl font-bold text-white mb-4 uppercase tracking-wide">
                  Ingredients
                </h3>
                <div className="bg-slate-800 rounded-xl p-5 border border-slate-700">
                  <ul className="space-y-3">
                    {recipe.ingredients.map((ing, i) => (
                      <li key={i} className="text-gray-300 flex items-start gap-3 leading-relaxed">
                        <span className="text-blue-400 font-bold mt-1 flex-shrink-0">•</span>
                        <span>{ing}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Instructions */}
              {parsedInstructions.length > 0 && (
                <div>
                  <h3 className="text-xl font-bold text-white mb-4 uppercase tracking-wide">
                    Instructions
                  </h3>
                  <div className="space-y-4">
                    {parsedInstructions.map((step, i) => (
                      <div key={i} className="flex items-start gap-4 bg-slate-800 rounded-xl p-5 border border-slate-700">
                        <div className="flex-shrink-0 w-8 h-8 flex items-center justify-center bg-blue-600 text-white font-bold rounded-lg">
                          {i + 1}
                        </div>
                        <p className="flex-1 text-gray-300 leading-relaxed pt-1">
                          {step.endsWith('.') ? step : `${step}.`}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* View Original */}
              {recipe.url && (
                <div className="pt-4 border-t border-slate-700">
                  <a
                    href={recipe.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    <ExternalLink className="w-4 h-4" />
                    View Original Recipe
                  </a>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  )
}
