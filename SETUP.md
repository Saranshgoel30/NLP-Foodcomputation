# Quick Setup Guide 🚀

## Step 1: Get an LLM API Key (Optional but Recommended)

### DeepSeek (Recommended - Most Cost-Effective)

1. Go to https://platform.deepseek.com
2. Sign up for account
3. Navigate to API Keys section
4. Create new API key
5. Copy the key (starts with `sk-`)

**Cost**: $0.14 input / $0.55 output per 1M tokens  
**Quality**: Excellent for recipe understanding  
**Speed**: Very fast  

### Alternative: OpenAI

1. Go to https://platform.openai.com
2. Sign up and add payment method
3. Navigate to API Keys
4. Create new key
5. Copy the key

**Cost**: $0.15 input / $0.6 output per 1M tokens  
**Quality**: Excellent, well-known  

### Alternative: Groq

1. Go to https://console.groq.com
2. Sign up for account
3. Navigate to API Keys
4. Create new key
5. Copy the key

**Cost**: $0.075 input / $0.3 output per 1M tokens  
**Speed**: Fastest option  

---

## Step 2: Configure Environment

### Windows PowerShell

```powershell
# Navigate to project
cd "C:\Users\saran\OneDrive - Ashoka University (1)\Documents\Ashoka\Capstone\NLP-Foodcomputation"

# Create .env file from example
Copy-Item .env.example .env

# Edit .env file (use notepad or VS Code)
notepad .env

# Add your key:
# DEEPSEEK_API_KEY=sk-your-actual-key-here
```

### Or Set Environment Variable Directly

```powershell
# For current session
$env:DEEPSEEK_API_KEY="sk-your-actual-key-here"

# Or permanently (requires restart)
[Environment]::SetEnvironmentVariable("DEEPSEEK_API_KEY", "sk-your-actual-key-here", "User")
```

---

## Step 3: Start Services

### Terminal 1: Backend

```powershell
# Navigate to backend
cd "C:\Users\saran\OneDrive - Ashoka University (1)\Documents\Ashoka\Capstone\NLP-Foodcomputation\app\api"

# Start backend
python main.py
```

**Expected output:**
```
✅ LLM Service initialized with DeepSeek (deepseek-chat)
🧠 Enhanced Query Parser initialized
   LLM Mode: ENABLED
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Terminal 2: Frontend

```powershell
# Navigate to frontend
cd "C:\Users\saran\OneDrive - Ashoka University (1)\Documents\Ashoka\Capstone\NLP-Foodcomputation\frontend"

# Start frontend
npm run dev
```

**Expected output:**
```
▲ Next.js 14.x.x
- Local:        http://localhost:3000
```

---

## Step 4: Test LLM Integration

### Option A: Use Test Script

```powershell
# Navigate to project root
cd "C:\Users\saran\OneDrive - Ashoka University (1)\Documents\Ashoka\Capstone\NLP-Foodcomputation"

# Run tests
python scripts\test_llm.py
```

**You should see:**
- System stats showing LLM enabled
- Query understanding results
- Translation examples
- Ingredient extraction

### Option B: Test via Browser

1. Open http://localhost:3000
2. Try these queries:
   - "jain recipes without tomatoes"
   - "pyaz ke bina sabzi"
   - "quick pasta under 20 minutes"

### Option C: Test via API

```powershell
# Test query understanding
curl "http://localhost:8000/api/analyze?q=jain%20recipes%20without%20tomatoes"

# Test translation
curl "http://localhost:8000/api/translate?text=chicken%20curry&target_lang=Hindi"

# Test search
curl "http://localhost:8000/api/search?q=quick%20pasta%20under%2020%20minutes"
```

---

## Step 5: Verify Everything Works

### Check Backend Status

```powershell
curl http://localhost:8000/api/stats
```

**Expected response:**
```json
{
  "total_recipes": "9600+",
  "search_type": "LLM-Enhanced Semantic Search",
  "llm_enabled": true,
  "llm_provider": "DeepSeek",
  "llm_model": "deepseek-chat"
}
```

### Check Frontend

1. Open http://localhost:3000
2. You should see the search interface
3. Try a search query
4. Results should appear quickly

---

## Troubleshooting 🔧

### "No LLM API key found"

**Solution:**
- Check .env file exists and has correct key
- Verify key format: `DEEPSEEK_API_KEY=sk-...`
- Restart backend after adding key
- System will work with rule-based fallback if no key

### "Module not found" errors

**Solution:**
```powershell
# Reinstall dependencies
cd app\api
pip install -r requirements.txt
```

### Backend won't start

**Solution:**
```powershell
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Kill process if needed (replace PID)
taskkill /PID <PID> /F

# Restart backend
python main.py
```

### Frontend won't start

**Solution:**
```powershell
# Reinstall dependencies
cd frontend
Remove-Item -Recurse -Force node_modules
npm install
npm run dev
```

### LLM calls failing

**Solution:**
- Verify API key is correct
- Check internet connection
- Verify you have credits in account
- System will fallback to rule-based parsing

### Slow responses

**Solution:**
- First query takes 1-2s (normal)
- Subsequent queries use cache (~100ms)
- Consider using Groq for fastest responses
- Cache persists for 1 hour

---

## Cost Monitoring 💰

### Check Usage

**DeepSeek:**
1. Go to https://platform.deepseek.com
2. Navigate to Usage/Billing
3. View token usage and costs

**OpenAI:**
1. Go to https://platform.openai.com/usage
2. View usage dashboard

**Groq:**
1. Go to https://console.groq.com
2. View usage statistics

### Typical Costs

For 1,000 queries:
- Simple searches: ~$0.07
- Complex queries: ~$0.21
- Mixed usage: ~$0.15

Very affordable! 🎉

---

## Next Steps 🎯

1. ✅ **Working**: Basic search should work now
2. 🧠 **With LLM**: Add API key for enhanced features
3. 🎨 **Customize**: Edit prompts in `app/api/llm_config.py`
4. 📊 **Monitor**: Check costs and usage
5. 🚀 **Deploy**: Ready for production!

---

## Quick Reference

### Important Files

```
.env                        # API keys (create from .env.example)
app/api/main.py            # Backend entry point
app/api/llm_config.py      # LLM configuration
app/api/llm_service.py     # LLM service logic
app/api/enhanced_query_parser.py  # Query parser
frontend/app/page.tsx      # Frontend entry point
```

### Important URLs

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Typesense: http://localhost:8108

### Key Commands

```powershell
# Start backend
cd app\api; python main.py

# Start frontend
cd frontend; npm run dev

# Test LLM
python scripts\test_llm.py

# Check stats
curl http://localhost:8000/api/stats
```

---

**Need Help?** Check the logs in your terminal for detailed information!

**Ready to go!** 🎉
