'use client'

import { Globe } from 'lucide-react'

interface Language {
  code: string
  name: string
  nativeName: string
}

interface LanguageSelectorProps {
  value: string
  onChange: (language: string) => void
  disabled?: boolean
}

const SUPPORTED_LANGUAGES: Language[] = [
  { code: 'en', name: 'English', nativeName: 'English' },
  { code: 'hi', name: 'Hindi', nativeName: 'हिंदी' },
  { code: 'mr', name: 'Marathi', nativeName: 'मराठी' },
  { code: 'ta', name: 'Tamil', nativeName: 'தமிழ்' },
  { code: 'te', name: 'Telugu', nativeName: 'తెలుగు' },
  { code: 'bn', name: 'Bengali', nativeName: 'বাংলা' },
  { code: 'gu', name: 'Gujarati', nativeName: 'ગુજરાતી' },
  { code: 'kn', name: 'Kannada', nativeName: 'ಕನ್ನಡ' },
  { code: 'ml', name: 'Malayalam', nativeName: 'മലയാളം' },
  { code: 'pa', name: 'Punjabi', nativeName: 'ਪੰਜਾਬੀ' }
]

export default function LanguageSelector({ value, onChange, disabled = false }: LanguageSelectorProps) {
  const selectedLanguage = SUPPORTED_LANGUAGES.find(lang => lang.code === value)

  return (
    <div className="relative">
      <label className="block text-xs font-semibold text-gray-400 mb-1.5 uppercase tracking-wide">
        Voice Language
      </label>
      <div className="relative">
        <div className="absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none">
          <Globe className="w-4 h-4 text-gray-400" />
        </div>
        <select
          value={value}
          onChange={(e) => onChange(e.target.value)}
          disabled={disabled}
          className={`
            w-full pl-10 pr-4 py-2.5 
            bg-slate-800 border-2 border-slate-600 
            rounded-lg text-sm font-medium text-white
            focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20
            transition-all duration-200
            ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer hover:border-slate-500'}
          `}
        >
          <option value="" disabled>Select language...</option>
          {SUPPORTED_LANGUAGES.map((lang) => (
            <option key={lang.code} value={lang.code}>
              {lang.nativeName} ({lang.name})
            </option>
          ))}
        </select>
      </div>
      
      {/* Helper text */}
      {!value && (
        <p className="mt-1.5 text-xs text-yellow-400 flex items-center gap-1">
          <span>⚠️</span>
          <span>Required for accurate transcription</span>
        </p>
      )}
      
      {value && selectedLanguage && (
        <p className="mt-1.5 text-xs text-green-400 flex items-center gap-1">
          <span>✓</span>
          <span>Recording in {selectedLanguage.nativeName}</span>
        </p>
      )}
    </div>
  )
}
