'use client';

import React from 'react';
import { X } from 'lucide-react';
import type { QueryConstraints } from '@/lib/api-client';

interface FiltersDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  filters: QueryConstraints;
  onFiltersChange: (filters: QueryConstraints) => void;
}

const DIETS = ['Vegetarian', 'Vegan', 'Jain', 'Non-Vegetarian', 'Gluten-Free'];
const CUISINES = ['Indian', 'Chinese', 'Italian', 'Mexican', 'Thai', 'Japanese'];
const COURSES = ['Breakfast', 'Lunch', 'Dinner', 'Snack', 'Dessert', 'Appetizer'];

export function FiltersDrawer({ isOpen, onClose, filters, onFiltersChange }: FiltersDrawerProps) {
  if (!isOpen) return null;

  const updateFilter = (key: keyof QueryConstraints, value: any) => {
    onFiltersChange({ ...filters, [key]: value });
  };

  const toggleArrayItem = (key: 'diet' | 'cuisine' | 'course', item: string) => {
    const current = filters[key] || [];
    const updated = current.includes(item)
      ? current.filter(i => i !== item)
      : [...current, item];
    updateFilter(key, updated.length > 0 ? updated : undefined);
  };

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black bg-opacity-50 transition-opacity"
        onClick={onClose}
      />
      
      {/* Drawer */}
      <div className="absolute right-0 top-0 h-full w-full max-w-md bg-white shadow-xl">
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b">
            <h2 className="text-xl font-bold text-gray-900">Filters</h2>
            <button
              onClick={onClose}
              className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {/* Diet */}
            <div>
              <h3 className="text-sm font-semibold text-gray-900 mb-3">Diet</h3>
              <div className="flex flex-wrap gap-2">
                {DIETS.map(diet => (
                  <button
                    key={diet}
                    onClick={() => toggleArrayItem('diet', diet)}
                    className={`
                      px-4 py-2 rounded-full text-sm font-medium transition-colors
                      ${(filters.diet || []).includes(diet)
                        ? 'bg-primary-500 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }
                    `}
                  >
                    {diet}
                  </button>
                ))}
              </div>
            </div>

            {/* Cuisine */}
            <div>
              <h3 className="text-sm font-semibold text-gray-900 mb-3">Cuisine</h3>
              <div className="flex flex-wrap gap-2">
                {CUISINES.map(cuisine => (
                  <button
                    key={cuisine}
                    onClick={() => toggleArrayItem('cuisine', cuisine)}
                    className={`
                      px-4 py-2 rounded-full text-sm font-medium transition-colors
                      ${(filters.cuisine || []).includes(cuisine)
                        ? 'bg-primary-500 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }
                    `}
                  >
                    {cuisine}
                  </button>
                ))}
              </div>
            </div>

            {/* Course */}
            <div>
              <h3 className="text-sm font-semibold text-gray-900 mb-3">Course</h3>
              <div className="flex flex-wrap gap-2">
                {COURSES.map(course => (
                  <button
                    key={course}
                    onClick={() => toggleArrayItem('course', course)}
                    className={`
                      px-4 py-2 rounded-full text-sm font-medium transition-colors
                      ${(filters.course || []).includes(course)
                        ? 'bg-primary-500 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }
                    `}
                  >
                    {course}
                  </button>
                ))}
              </div>
            </div>

            {/* Time */}
            <div>
              <h3 className="text-sm font-semibold text-gray-900 mb-3">Max Cooking Time</h3>
              <input
                type="number"
                placeholder="Minutes"
                value={filters.maxCookMinutes || ''}
                onChange={(e) => updateFilter('maxCookMinutes', e.target.value ? parseInt(e.target.value) : undefined)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>

            {/* Excludes */}
            <div>
              <h3 className="text-sm font-semibold text-gray-900 mb-3">Exclude Ingredients</h3>
              <input
                type="text"
                placeholder="e.g., banana, onion"
                value={(filters.exclude || []).join(', ')}
                onChange={(e) => {
                  const items = e.target.value.split(',').map(s => s.trim()).filter(Boolean);
                  updateFilter('exclude', items.length > 0 ? items : undefined);
                }}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
              <p className="mt-2 text-xs text-gray-500">Comma-separated list</p>
            </div>
          </div>

          {/* Footer */}
          <div className="p-6 border-t space-y-3">
            <button
              onClick={() => onFiltersChange({})}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg text-gray-700 font-medium hover:bg-gray-50 transition-colors"
            >
              Clear All Filters
            </button>
            <button
              onClick={onClose}
              className="w-full px-4 py-2 bg-primary-500 text-white rounded-lg font-medium hover:bg-primary-600 transition-colors"
            >
              Apply Filters
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
