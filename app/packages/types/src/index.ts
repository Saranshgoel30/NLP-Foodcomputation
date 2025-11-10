/**
 * Shared types for MMFOOD application
 * Both frontend and backend use these contracts
 */

export type Language = 'en' | 'hi' | 'mr' | 'ta' | 'te' | 'bn' | 'gu' | 'kn' | 'ml' | 'or' | 'pa' | 'auto';

export interface QueryConstraints {
  include?: string[];       // ingredients to include
  exclude?: string[];       // ingredients to exclude
  cuisine?: string[];       // e.g., ['Indian', 'Chinese']
  diet?: string[];          // e.g., ['Jain', 'Vegan', 'Vegetarian']
  maxCookMinutes?: number;  // max cooking time
  maxTotalMinutes?: number; // max total time
  course?: string[];        // e.g., ['Main Course', 'Dessert']
  keywords?: string[];      // technique terms, e.g., ['dum cook', 'tandoor']
}

export interface UserQuery {
  text: string;             // raw query text
  lang: Language;           // source language
  constraints?: QueryConstraints;
}

export interface Recipe {
  iri: string;              // recipe URI from GraphDB
  title?: string;
  url?: string;
  course?: string;
  cuisine?: string;
  diet?: string;
  servings?: string | number;
  ingredients?: string[];   // normalized ingredient tokens
  instructions?: string;
  difficulty?: string;
  cookTime?: string;        // original literal (e.g., "30 minutes")
  totalTime?: string;       // original literal
  score?: number;           // ranking score
}

export interface SearchRequest {
  query: UserQuery;
}

export interface SearchResponse {
  results: Recipe[];
  query: UserQuery;
  translatedQuery?: string; // English translation if non-English input
  count: number;
  durationMs: number;
}

export interface STTRequest {
  audio: string;            // base64 encoded audio data
  format?: string;          // 'webm' | 'pcm' | 'wav'
  lang?: Language;
}

export interface STTResponse {
  transcript: string;
  confidence: number;       // 0.0 to 1.0
  lang: Language;
}

export interface TranslateRequest {
  text: string;
  sourceLang: Language;     // 'auto' for detection
  targetLang: Language;
}

export interface TranslateResponse {
  translatedText: string;
  sourceLang: Language;
  targetLang: Language;
}

export interface NLUParseRequest {
  text: string;
  lang: Language;
}

export interface NLUParseResponse {
  constraints: QueryConstraints;
  confidence: number;
  originalText: string;
}

export interface SPARQLBuildRequest {
  constraints: QueryConstraints;
}

export interface SPARQLBuildResponse {
  sparql: string;
  params?: Record<string, any>;
}

// Error types
export interface APIError {
  error: string;
  message: string;
  code?: string;
  details?: any;
}

// Config types
export interface AppConfig {
  graphdb: {
    url: string;
    repository: string;
    namedGraph: string;
    username?: string;
    password?: string;
    timeout: number;
  };
  translation: {
    provider: 'indicTrans2' | 'marianMT' | 'api';
    endpoint?: string;
  };
  stt: {
    provider: 'whisper' | 'vosk';
    modelPath?: string;
  };
  api: {
    port: number;
    corsOrigins: string[];
    rateLimit: {
      perMinute: number;
    };
  };
}
