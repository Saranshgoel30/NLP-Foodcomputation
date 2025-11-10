# Changelog

All notable changes to the MMFOOD API project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-11

### Added
- 🎤 **Speech-to-Text System**
  - OpenAI Whisper integration with 11 Indian language support
  - Auto language detection with confidence scoring
  - Multiple audio format support (webm, wav, mp3, ogg, m4a)
  - CUDA acceleration support
  - Production-grade error handling
  
- 🌐 **Translation System**
  - Bidirectional translation between English and 10 Indian languages
  - Culinary terminology preservation (40+ food terms)
  - Auto language detection via Unicode script analysis
  - Graceful fallback for translation failures
  
- 🎙️ **Voice Search Pipeline**
  - End-to-end pipeline: STT → Translation → NLP → Search
  - Multi-stage logging for debugging
  - Support for native language queries
  - Sub-3s total latency
  
- 🧠 **NLP Query Parser**
  - Rule-based pattern matching (302 lines)
  - Constraint extraction (include, exclude, cuisine, diet, time, course)
  - 40+ cuisine types, 10+ diet types
  - Confidence scoring
  
- 🔍 **Recipe Search Engine**
  - Food Graph API integration (9000+ recipes)
  - Intelligent multi-field filtering
  - Automatic NLP constraint extraction
  - 100-500ms search latency
  
- 🔒 **Security & Performance**
  - Token bucket rate limiting (different limits per endpoint)
  - Request ID tracking for distributed tracing
  - Security headers (X-Frame-Options, CSP, etc.)
  - CORS configuration with specific origins
  
- 📊 **Monitoring & Observability**
  - Comprehensive health check with dependency status
  - Metrics endpoint for monitoring dashboards
  - Structured logging with request IDs
  - Performance timing headers
  
- 📚 **Documentation**
  - VOICE_SEARCH_API.md - Complete API documentation
  - PRODUCTION_STATUS.md - System architecture and deployment guide
  - OpenAPI/Swagger integration with tags
  - API examples for all endpoints

### Changed
- Enhanced error responses with specific error codes
- Improved CORS middleware configuration
- Better logging structure with request context
- Optimized search filtering logic

### Fixed
- Rate limiting edge cases
- Memory leaks in temp file cleanup
- Translation adapter initialization warnings
- Frontend-backend field mapping consistency

### Security
- Added rate limiting to prevent abuse
- Implemented security headers
- Added input validation for all endpoints
- Removed hardcoded credentials from test files (moved to environment variables)

---

## [0.9.0] - 2025-11-10

### Added
- Initial NLP query parser implementation
- Basic search endpoint with Food Graph API
- GraphDB client for SPARQL queries
- SPARQL query builder

### Changed
- Migrated from mock data to Food Graph API
- Updated recipe card UI without images
- Fixed frontend-backend data field mismatch

---

## [0.8.0] - 2025-11-09

### Added
- Next.js 14 frontend with TypeScript
- FastAPI backend structure
- Basic search interface
- Recipe card components

### Fixed
- Port conflicts on Windows
- CORS configuration issues

---

## Future Releases

### [1.1.0] - Planned
- Frontend voice input UI
- Real-time transcription display
- Language selector component
- Constraint pills visualization
- Recording waveform animation

### [1.2.0] - Planned
- Redis caching layer
- Response compression
- Database connection pooling
- CDN integration for static assets

### [2.0.0] - Planned
- User authentication and API keys
- Personalized recommendations
- Recipe collections and favorites
- User-submitted recipes
- Advanced nutrition analysis
- Meal planning features

---

**Legend:**
- 🎤 Speech/Audio
- 🌐 Translation/i18n
- 🧠 AI/ML
- 🔍 Search
- 🔒 Security
- 📊 Monitoring
- 📚 Documentation
