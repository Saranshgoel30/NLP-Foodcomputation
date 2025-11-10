# Contributing to MMFOOD

Thank you for your interest in contributing to MMFOOD! This document provides guidelines and instructions for contributing.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)

---

## 📜 Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inspiring community for all. Please be respectful and constructive in all interactions.

### Our Standards

**Positive behaviors:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community

**Unacceptable behaviors:**
- Trolling, insulting/derogatory comments, and personal or political attacks
- Public or private harassment
- Publishing others' private information without permission

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+**
- **Node.js 20+**
- **Git**
- **Docker** (optional, for containerized development)

### Fork and Clone

```bash
# Fork the repository on GitHub first, then:
git clone https://github.com/YOUR_USERNAME/NLP-Foodcomputation.git
cd NLP-Foodcomputation

# Add upstream remote
git remote add upstream https://github.com/Saranshgoel30/NLP-Foodcomputation.git
```

### Development Setup

```bash
# Backend setup
cd app/api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.template .env
# Edit .env with your configuration

# Frontend setup
cd ../web
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8080" > .env.local
```

---

## 🔄 Development Workflow

### Branch Naming

Use descriptive branch names:
- `feature/voice-input-ui` - New features
- `fix/rate-limit-bug` - Bug fixes
- `docs/api-examples` - Documentation updates
- `refactor/search-logic` - Code refactoring
- `test/stt-accuracy` - Test additions

### Commit Messages

Follow conventional commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples:**
```bash
feat(stt): add support for Odia language

Added Odia language support to Whisper STT adapter with 
language code mapping and test cases.

Closes #123

---

fix(search): resolve filtering bug for excluded ingredients

The search was not properly filtering recipes when multiple
ingredients were excluded. Updated the filtering logic to
check all exclusions correctly.

Fixes #456
```

### Keep Your Fork Updated

```bash
# Fetch upstream changes
git fetch upstream

# Merge upstream changes into your main branch
git checkout main
git merge upstream/main

# Push to your fork
git push origin main
```

---

## 💻 Coding Standards

### Python (Backend)

**Style Guide:** Follow PEP 8

```python
# Good
def search_recipes(
    query: str,
    constraints: Optional[QueryConstraints] = None,
    limit: int = 50
) -> List[Recipe]:
    """
    Search for recipes matching the query.
    
    Args:
        query: Search query text
        constraints: Optional filter constraints
        limit: Maximum number of results
        
    Returns:
        List of matching recipes
    """
    # Implementation
    pass

# Bad
def SearchRecipes(q, c=None, l=50):
    # No docstring, unclear names
    pass
```

**Type Hints:**
- Always use type hints for function parameters and return values
- Use `Optional[T]` for nullable values
- Use `List[T]`, `Dict[K, V]` for collections

**Error Handling:**
```python
# Good
try:
    result = await api_call()
except HTTPException:
    raise  # Re-raise HTTP exceptions
except ValueError as e:
    logger.error("validation_failed", error=str(e))
    raise HTTPException(status_code=400, detail=str(e))
except Exception as e:
    logger.error("unexpected_error", error=str(e), exc_info=True)
    raise HTTPException(status_code=500, detail="Internal server error")
```

**Logging:**
```python
# Use structured logging
logger.info(
    "search_completed",
    query=search_text,
    results_count=len(results),
    duration_ms=duration
)
```

### TypeScript (Frontend)

**Style Guide:** Follow Airbnb TypeScript style guide

```typescript
// Good
interface Recipe {
  id: string;
  title: string;
  ingredients: string[];
  diet?: string;
}

async function searchRecipes(query: string): Promise<Recipe[]> {
  const response = await fetch('/api/search', {
    method: 'POST',
    body: JSON.stringify({ query }),
  });
  
  if (!response.ok) {
    throw new Error(`Search failed: ${response.statusText}`);
  }
  
  return response.json();
}

// Bad
async function searchRecipes(q) {
  // No types, poor error handling
  const r = await fetch('/api/search');
  return r.json();
}
```

### Code Formatting

**Python:**
```bash
# Install formatters
pip install black isort

# Format code
black app/api/
isort app/api/

# Check formatting
black --check app/api/
```

**TypeScript:**
```bash
# Install Prettier
npm install --save-dev prettier

# Format code
npm run format

# Check formatting
npm run format:check
```

---

## 🧪 Testing Guidelines

### Backend Tests

```python
# test_search.py
import pytest
from app.api.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_search_endpoint():
    """Test basic search functionality"""
    response = client.post(
        "/search",
        json={"query": {"text": "paneer", "lang": "en"}}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert data["count"] >= 0

def test_search_with_constraints():
    """Test search with NLP constraints"""
    response = client.post(
        "/search",
        json={
            "query": {
                "text": "vegetarian paneer",
                "lang": "en",
                "constraints": {
                    "diet": ["Vegetarian"],
                    "include": ["paneer"]
                }
            }
        }
    )
    
    assert response.status_code == 200
    results = response.json()["results"]
    
    # Verify all results are vegetarian
    for recipe in results:
        assert recipe.get("diet") == "Vegetarian"
```

**Run tests:**
```bash
cd app/api
pytest tests/ -v --cov=app.api
```

### Frontend Tests

```typescript
// SearchInterface.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import SearchInterface from '@/components/SearchInterface';

describe('SearchInterface', () => {
  it('should render search input', () => {
    render(<SearchInterface />);
    const input = screen.getByPlaceholderText(/search recipes/i);
    expect(input).toBeInTheDocument();
  });

  it('should handle search submission', async () => {
    render(<SearchInterface />);
    const input = screen.getByPlaceholderText(/search recipes/i);
    const button = screen.getByRole('button', { name: /search/i });

    fireEvent.change(input, { target: { value: 'paneer' } });
    fireEvent.click(button);

    // Wait for results
    const results = await screen.findByTestId('search-results');
    expect(results).toBeInTheDocument();
  });
});
```

**Run tests:**
```bash
cd app/web
npm test
```

---

## 📚 Documentation

### Code Documentation

**Python docstrings:**
```python
def parse_query(text: str, lang: Language) -> Tuple[QueryConstraints, float]:
    """
    Parse natural language query into structured constraints.
    
    Extracts dietary restrictions, cuisine types, cooking times,
    and ingredient requirements from natural language text.
    
    Args:
        text: Query text in natural language
        lang: Source language code (e.g., 'en', 'hi', 'ta')
        
    Returns:
        Tuple of (constraints, confidence_score)
        - constraints: Extracted query constraints
        - confidence: Float between 0 and 1
        
    Example:
        >>> constraints, conf = parse_query("vegetarian paneer under 30 min", "en")
        >>> print(constraints.diet)
        ['Vegetarian']
        >>> print(constraints.include)
        ['paneer']
        >>> print(constraints.maxCookMinutes)
        30
    """
```

**TypeScript JSDoc:**
```typescript
/**
 * Search for recipes using the backend API
 * 
 * @param query - Search query text
 * @param constraints - Optional filter constraints
 * @returns Promise resolving to search results
 * @throws {Error} If the API request fails
 * 
 * @example
 * ```ts
 * const results = await searchRecipes("paneer tikka", {
 *   diet: ["Vegetarian"],
 *   maxCookMinutes: 30
 * });
 * ```
 */
async function searchRecipes(
  query: string,
  constraints?: QueryConstraints
): Promise<SearchResponse> {
  // Implementation
}
```

### API Documentation

Update `VOICE_SEARCH_API.md` when adding new endpoints.

---

## 🔍 Pull Request Process

### Before Submitting

1. **Update your branch:**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run tests:**
   ```bash
   # Backend
   cd app/api && pytest tests/
   
   # Frontend
   cd app/web && npm test
   ```

3. **Check code quality:**
   ```bash
   # Python
   black --check app/api/
   isort --check app/api/
   
   # TypeScript
   npm run lint
   ```

4. **Update documentation** if needed

### Submitting PR

1. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create Pull Request** on GitHub

3. **Fill PR template:**
   ```markdown
   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update
   
   ## Testing
   - [ ] All tests pass
   - [ ] New tests added
   - [ ] Manual testing completed
   
   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Self-review completed
   - [ ] Comments added for complex code
   - [ ] Documentation updated
   - [ ] No new warnings
   ```

4. **Address review feedback** promptly

### After PR is Merged

```bash
# Update your local main branch
git checkout main
git pull upstream main

# Delete feature branch
git branch -d feature/your-feature-name
git push origin --delete feature/your-feature-name
```

---

## 🎯 Areas for Contribution

### High Priority
- [ ] Frontend voice input UI components
- [ ] Real-time transcription display
- [ ] Language selector component
- [ ] Recording waveform visualization
- [ ] Redis caching layer
- [ ] Response compression

### Medium Priority
- [ ] Additional language support (Assamese, Konkani, etc.)
- [ ] Recipe recommendation engine
- [ ] User authentication
- [ ] Recipe collections/favorites
- [ ] Meal planning features

### Low Priority
- [ ] Dark mode support
- [ ] Accessibility improvements
- [ ] Performance optimizations
- [ ] Additional test coverage

---

## 💬 Questions?

- Open an issue on GitHub
- Check existing documentation in `/docs`
- Review `VOICE_SEARCH_API.md` for API details
- Check `PRODUCTION_STATUS.md` for architecture

---

Thank you for contributing to MMFOOD! 🎉
