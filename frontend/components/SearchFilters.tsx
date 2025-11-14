'use client';

import { useState } from 'react';
import { Filter, X } from 'lucide-react';
import type { SearchFiltersType } from '@/types';

interface SearchFiltersProps {
  selectedFilters: SearchFiltersType;
  onFilterChange: (filters: SearchFiltersType) => void;
}

const FOOD_GROUPS = [
  'Vegetables',
  'Fruits',
  'Grains',
  'Dairy',
  'Proteins',
  'Spices',
  'Herbs',
  'Nuts & Seeds',
  'Legumes',
  'Oils & Fats',
];

const COMMON_TAGS = [
  'Vegan',
  'Vegetarian',
  'Gluten-Free',
  'Organic',
  'High-Protein',
  'Low-Carb',
  'Indian',
  'Asian',
  'Mediterranean',
  'Healthy',
];

export function SearchFilters({ selectedFilters, onFilterChange }: SearchFiltersProps) {
  const [expanded, setExpanded] = useState(true);

  const toggleFoodGroup = (group: string) => {
    const newGroups = selectedFilters.foodGroups.includes(group)
      ? selectedFilters.foodGroups.filter((g) => g !== group)
      : [...selectedFilters.foodGroups, group];
    
    onFilterChange({ ...selectedFilters, foodGroups: newGroups });
  };

  const toggleTag = (tag: string) => {
    const newTags = selectedFilters.tags.includes(tag)
      ? selectedFilters.tags.filter((t) => t !== tag)
      : [...selectedFilters.tags, tag];
    
    onFilterChange({ ...selectedFilters, tags: newTags });
  };

  const clearAllFilters = () => {
    onFilterChange({ foodGroups: [], tags: [] });
  };

  const hasActiveFilters = 
    selectedFilters.foodGroups.length > 0 || selectedFilters.tags.length > 0;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-md border border-gray-100 dark:border-gray-700 overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Filter className="w-5 h-5 text-orange-500" />
            <h3 className="font-semibold text-gray-900 dark:text-white">
              Filters
            </h3>
            {hasActiveFilters && (
              <span className="px-2 py-0.5 bg-orange-500 text-white rounded-full text-xs font-semibold">
                {selectedFilters.foodGroups.length + selectedFilters.tags.length}
              </span>
            )}
          </div>
          
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
          >
            {expanded ? '▼' : '▶'}
          </button>
        </div>

        {hasActiveFilters && (
          <button
            onClick={clearAllFilters}
            className="mt-2 flex items-center gap-1 text-sm text-orange-600 dark:text-orange-400 hover:text-orange-700 dark:hover:text-orange-300"
          >
            <X className="w-4 h-4" />
            Clear all
          </button>
        )}
      </div>

      {/* Filter Options */}
      {expanded && (
        <div className="p-4 space-y-6">
          {/* Food Groups */}
          <div>
            <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
              Food Groups
            </h4>
            <div className="space-y-2">
              {FOOD_GROUPS.map((group) => (
                <label
                  key={group}
                  className="flex items-center gap-2 cursor-pointer group"
                >
                  <input
                    type="checkbox"
                    checked={selectedFilters.foodGroups.includes(group)}
                    onChange={() => toggleFoodGroup(group)}
                    className="w-4 h-4 rounded border-gray-300 text-orange-500 focus:ring-2 focus:ring-orange-500"
                  />
                  <span className="text-sm text-gray-700 dark:text-gray-300 group-hover:text-orange-600 dark:group-hover:text-orange-400 transition-colors">
                    {group}
                  </span>
                </label>
              ))}
            </div>
          </div>

          {/* Tags */}
          <div>
            <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
              Tags
            </h4>
            <div className="flex flex-wrap gap-2">
              {COMMON_TAGS.map((tag) => (
                <button
                  key={tag}
                  onClick={() => toggleTag(tag)}
                  className={`px-3 py-1 rounded-lg text-xs font-medium transition-all ${
                    selectedFilters.tags.includes(tag)
                      ? 'bg-orange-500 text-white shadow-md'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                  }`}
                >
                  {tag}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
