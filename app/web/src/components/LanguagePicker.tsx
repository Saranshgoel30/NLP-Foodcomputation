'use client';

import React from 'react';
import { Globe } from 'lucide-react';
import type { Language } from '@/lib/api-client';

const LANGUAGES = [
  { code: 'en', name: 'English', nativeName: 'English' },
  { code: 'hi', name: 'Hindi', nativeName: 'हिन्दी' },
  { code: 'mr', name: 'Marathi', nativeName: 'मराठी' },
  { code: 'ta', name: 'Tamil', nativeName: 'தமிழ்' },
  { code: 'te', name: 'Telugu', nativeName: 'తెలుగు' },
  { code: 'bn', name: 'Bengali', nativeName: 'বাংলা' },
  { code: 'gu', name: 'Gujarati', nativeName: 'ગુજરાતી' },
  { code: 'kn', name: 'Kannada', nativeName: 'ಕನ್ನಡ' },
  { code: 'ml', name: 'Malayalam', nativeName: 'മലയാളം' },
];

interface LanguagePickerProps {
  selectedLang: Language;
  onLanguageChange: (lang: Language) => void;
}

export function LanguagePicker({ selectedLang, onLanguageChange }: LanguagePickerProps) {
  return (
    <div className="relative inline-block">
      <div className="flex items-center gap-2">
        <Globe className="w-5 h-5 text-gray-600" />
        <select
          value={selectedLang}
          onChange={(e) => onLanguageChange(e.target.value as Language)}
          className="
            px-3 py-2 pr-8 rounded-lg border border-gray-300 
            focus:ring-2 focus:ring-primary-500 focus:border-transparent
            bg-white text-sm font-medium text-gray-700
            cursor-pointer appearance-none
          "
        >
          {LANGUAGES.map((lang) => (
            <option key={lang.code} value={lang.code}>
              {lang.nativeName}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}
