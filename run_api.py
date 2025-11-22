"""
Simple runner for the FastAPI backend
"""
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Food Intelligence API Server...")
    print("📡 API Docs: http://localhost:8000/docs")
    print("💚 Health Check: http://localhost:8000/")
    print("\n⏳ Loading embedding model (this may take a moment)...\n")
    
    uvicorn.run("app.api.main:app", host="0.0.0.0", port=8000, reload=True)
