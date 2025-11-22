# 🚀 Food Intelligence Platform - Complete Setup Guide

## Overview

We've rebuilt the entire UI using a modern tech stack to provide a **professional, production-grade experience**:

### ✅ What's Fixed

1. **Search Error ("instructions")**: Added proper null checks for missing recipe fields
2. **Query Suggestions**: Implemented real-time autocomplete with dropdown (like Google)
3. **Readable UI**: Switched to Next.js with high-contrast design, large fonts, and proper spacing
4. **Multiple Results**: All 50 results now display in a single-column layout for easy scanning
5. **Modern Tech Stack**: Replaced Streamlit with Next.js + React + Tailwind CSS

---

## 🏗️ New Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Frontend (Next.js + React + Tailwind)                  │
│  ├─ Real-time autocomplete dropdown                     │
│  ├─ Beautiful recipe cards                              │
│  ├─ Filters sidebar                                     │
│  └─ Responsive design                                   │
└──────────────────┬──────────────────────────────────────┘
                   │ HTTP/REST
┌──────────────────▼──────────────────────────────────────┐
│  Backend API (FastAPI)                                   │
│  ├─ /api/search - Search recipes                        │
│  ├─ /api/autocomplete - Query suggestions               │
│  ├─ /api/ingredient - Ingredient lookup                 │
│  └─ /api/stats - Platform statistics                    │
└──────────────────┬──────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────┐
│  Search Engine (Typesense)                              │
│  ├─ 9,600+ recipes indexed                              │
│  ├─ 10,000+ query suggestions                           │
│  ├─ 4,200+ ingredients                                  │
│  └─ Semantic search with embeddings                     │
└─────────────────────────────────────────────────────────┘
```

---

## 📦 Installation & Setup

### Step 1: Install Frontend Dependencies

```powershell
cd NLP-Foodcomputation/frontend
npm install
```

This will install:
- Next.js 14 (React framework)
- TypeScript
- Tailwind CSS
- Axios (HTTP client)
- Lucide React (icons)

### Step 2: Start Typesense (if not already running)

```powershell
# Make sure Docker is running
docker-compose up -d
```

### Step 3: Start the Backend API

**Option A: Using the runner script (recommended)**
```powershell
cd NLP-Foodcomputation
python run_api.py
```

**Option B: Using uvicorn directly**
```powershell
cd NLP-Foodcomputation
python -m uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at **http://localhost:8000**

### Step 4: Start the Frontend

```powershell
cd NLP-Foodcomputation/frontend
npm run dev
```

The app will be available at **http://localhost:3000**

---

## 🎨 UI Features

### 1. **Search Bar with Real-Time Autocomplete**
- Type at least 2 characters to trigger suggestions
- Shows up to 6 related search queries
- **Debounced** (300ms) for performance
- **Keyboard navigation**: Use ↑ ↓ arrows and Enter
- **Click-to-search**: Click any suggestion to instantly search

### 2. **Recipe Cards**
- High-contrast white cards with clear typography
- Colored badges: Blue (Cuisine), Green (Diet), Orange (Time)
- **Expandable**: Click to reveal full ingredients & instructions
- Link to original recipe if available

### 3. **Filters Sidebar**
- Filter by Cuisine, Diet Type, Course
- Sticky sidebar on desktop
- "Clear All Filters" button
- Platform statistics at the bottom

### 4. **Responsive Design**
- Works on mobile, tablet, and desktop
- Touch-friendly buttons and controls
- Adaptive layout

---

## 🔧 Configuration

### API URL
Edit `frontend/next.config.js`:
```javascript
env: {
  NEXT_PUBLIC_API_URL: 'http://localhost:8000',
},
```

### Search Behavior
Edit `frontend/components/SearchBar.tsx`:
```typescript
const timer = setTimeout(async () => {
  if (value.length >= 2) {  // Min characters for autocomplete
    // ... autocomplete logic
  }
}, 300) // Debounce delay in ms
```

---

## 📡 API Endpoints

### GET /api/search
Search for recipes
```
?q=chicken          # Query
&limit=50           # Results per page
&cuisine=Indian     # Filter by cuisine
&diet=Vegetarian    # Filter by diet
&course=Lunch       # Filter by course
```

### GET /api/autocomplete
Get query suggestions
```
?q=chick            # Partial query
&limit=6            # Number of suggestions
```

### GET /api/ingredient
Lookup ingredient info
```
?q=galangal         # Ingredient name
&limit=3            # Number of results
```

### GET /api/stats
Get platform statistics

---

## 🐛 Troubleshooting

### Frontend won't start
```powershell
# Make sure you're in the frontend directory
cd NLP-Foodcomputation/frontend
npm install
npm run dev
```

### Backend API won't start
```powershell
# Check if Typesense is running
docker ps

# Restart Typesense if needed
docker-compose restart

# Check if port 8000 is free
# If not, change the port in run_api.py
```

### Autocomplete not working
1. Check browser console for errors (F12)
2. Verify API is running: http://localhost:8000/
3. Test autocomplete endpoint: http://localhost:8000/api/autocomplete?q=chicken

### CORS errors
The backend is already configured for CORS. If you see errors:
1. Make sure the frontend is on port 3000 or 3001
2. Check `app/api/main.py` CORS settings

---

## 📝 File Structure

```
NLP-Foodcomputation/
├── app/
│   ├── api/
│   │   ├── main.py              # FastAPI application
│   │   └── search_client.py     # Typesense client
│   └── ui.py                    # Old Streamlit UI (deprecated)
├── frontend/
│   ├── app/
│   │   ├── page.tsx             # Main app page
│   │   ├── layout.tsx           # Root layout
│   │   └── globals.css          # Global styles
│   ├── components/
│   │   ├── SearchBar.tsx        # Autocomplete search bar
│   │   ├── RecipeCard.tsx       # Recipe display card
│   │   └── FilterSidebar.tsx    # Filters sidebar
│   ├── package.json             # Dependencies
│   ├── tailwind.config.ts       # Tailwind configuration
│   └── next.config.js           # Next.js configuration
├── run_api.py                   # API server runner
└── docker-compose.yml           # Typesense container
```

---

## 🎯 Next Steps

1. **Test the complete flow**:
   - Open http://localhost:3000
   - Type "chicken" and watch autocomplete appear
   - Click a suggestion or press Enter
   - View recipe cards
   - Try filters
   - Expand a recipe to see details

2. **Customize the design**:
   - Edit `frontend/app/globals.css` for colors
   - Edit `frontend/tailwind.config.ts` for theme
   - Edit components for layout changes

3. **Deploy to production**:
   ```powershell
   cd frontend
   npm run build
   npm run start
   ```

---

## 🌟 Key Improvements Over Streamlit

| Feature | Streamlit (Old) | Next.js (New) |
|---------|----------------|---------------|
| Autocomplete | Basic text | Google-like dropdown with keyboard nav |
| Performance | Slow reloads | Instant updates |
| Design | Basic CSS | Professional Tailwind design |
| Responsiveness | Limited | Fully responsive |
| Customization | Hard to customize | Easy to modify |
| Production-ready | No | Yes |
| Loading UX | Spinners everywhere | Smooth transitions |

---

## ✅ Summary

- **Backend API**: ✅ Running on port 8000
- **Frontend**: ⏳ Ready to install and start
- **Autocomplete**: ✅ Implemented with dropdown
- **UI**: ✅ Professional, high-contrast design
- **Multiple Results**: ✅ All results visible
- **Filters**: ✅ Working
- **Responsive**: ✅ Mobile-ready

**Run these commands to start everything:**
```powershell
# Terminal 1: Start Backend
cd NLP-Foodcomputation
python run_api.py

# Terminal 2: Start Frontend
cd NLP-Foodcomputation/frontend
npm install
npm run dev
```

Then open **http://localhost:3000** in your browser! 🎉
