# Food Intelligence Platform - Modern UI

A beautiful, modern Next.js frontend with real-time autocomplete for the Food Intelligence Platform.

## 🚀 Tech Stack

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide React** - Beautiful icons
- **Axios** - HTTP client

## ✨ Features

1. **Real-time Autocomplete** - Google-like search suggestions as you type
2. **Keyboard Navigation** - Arrow keys + Enter support in autocomplete
3. **Beautiful UI** - High-contrast, accessible design with gradient headers
4. **Responsive** - Works perfectly on mobile, tablet, and desktop
5. **Fast** - Optimized with debouncing and React performance best practices
6. **Filter Sidebar** - Filter by cuisine, diet, course
7. **Recipe Cards** - Expandable cards with ingredients and instructions

## 📦 Installation

### Step 1: Install Dependencies

```powershell
cd frontend
npm install
```

### Step 2: Start the Backend API

The frontend needs the FastAPI backend running on port 8000:

```powershell
# From the root directory
cd ..
python -m uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000
```

###Step 3: Start the Frontend

```powershell
cd frontend
npm run dev
```

The app will be available at **http://localhost:3000**

## 🎨 UI Features

### Search Bar with Autocomplete
- Type at least 2 characters to see suggestions
- 300ms debounce for performance
- Clickable suggestions or use arrow keys + Enter
- Shows loading spinner while fetching

### Recipe Cards
- High-contrast design with clear typography
- Colored badges for cuisine, diet, course, time
- Expandable to show full ingredients and instructions
- Link to original recipe if available

### Filters
- Sticky sidebar on desktop
- Instant filtering without page reload
- Clear all filters button

## 🔧 Configuration

Edit `next.config.js` to change the API URL:

```javascript
env: {
  NEXT_PUBLIC_API_URL: 'http://localhost:8000', // Change this to your API URL
},
```

## 📁 Project Structure

```
frontend/
├── app/
│   ├── layout.tsx         # Root layout
│   ├── page.tsx          # Home page (main app)
│   └── globals.css        # Global styles
├── components/
│   ├── SearchBar.tsx      # Search with autocomplete
│   ├── RecipeCard.tsx     # Recipe display card
│   └── FilterSidebar.tsx  # Filters sidebar
├── package.json
├── tailwind.config.ts     # Tailwind configuration
└── next.config.js         # Next.js configuration
```

## 🎯 How It Works

1. **User Types Query** → Debounced API call to `/api/autocomplete`
2. **Suggestions Appear** → Dropdown shows up to 6 related searches
3. **User Clicks/Presses Enter** → API call to `/api/search`
4. **Results Display** → Beautiful recipe cards with all details
5. **User Applies Filters** → New search with filter parameters

## 🐛 Troubleshooting

### Port 3000 Already in Use

```powershell
npm run dev -- -p 3001
```

### API Connection Issues

Make sure the FastAPI backend is running:
```powershell
python -m uvicorn app.api.main:app --reload
```

Check the browser console for CORS errors. The backend should have CORS enabled for `http://localhost:3000`.

### Lint Errors

The TypeScript errors you see are normal until you run `npm install`. They will disappear once dependencies are installed.

## 🚀 Production Build

```powershell
npm run build
npm run start
```

## 📝 API Endpoints Used

- `GET /api/search?q=query&limit=50&cuisine=&diet=&course=` - Search recipes
- `GET /api/autocomplete?q=query&limit=6` - Get query suggestions
- `GET /api/stats` - Get platform statistics

## 🎨 Color Scheme

- Primary: Purple (#667eea to #764ba2)
- Accents: Blue (#3b82f6), Green (#16a34a), Orange (#ea580c)
- Background: White (#ffffff) with subtle gradients
- Text: Dark gray (#111827) for maximum readability

---

**Note**: This is a modern, production-ready frontend that replaces the Streamlit UI. It provides a much better user experience with real-time autocomplete, better performance, and a professional design.
