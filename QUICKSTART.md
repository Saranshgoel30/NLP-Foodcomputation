# Quick Start Guide

## Initial Setup

### 1. API Setup (Backend)

```powershell
# Run the setup script
.\setup-api.ps1

# Or manually:
cd app\api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.template .env
# Edit .env with your credentials
```

### 2. Web Setup (Frontend)

```powershell
# Run the setup script
.\setup-web.ps1

# Or manually:
cd app\web
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
```

### 3. Start Development Servers

**Terminal 1 - API:**
```powershell
cd app\api
.\.venv\Scripts\Activate.ps1
python main.py
```

**Terminal 2 - Web:**
```powershell
cd app\web
npm run dev
```

### 4. Access the Application

- **Web Interface**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Testing the Application

### Test Queries

Try these example searches:

1. **Simple ingredient**: "chicken recipe"
2. **With exclusion**: "walnuts without banana"
3. **Time constraint**: "Chinese chicken under 30 minutes"
4. **Dietary filter**: "Jain dal without rajma"
5. **Colloquial**: "no onion no garlic sabzi"

### Using Voice Input

1. Click the microphone button
2. Allow microphone access
3. Speak your query clearly
4. Click again to stop recording
5. Results will appear after transcription

## Running Tests

```powershell
# API tests
cd app\api
pytest

# Web tests (when implemented)
cd app\web
npm test
```

## Docker Deployment

```powershell
cd app\infra
docker-compose up -d
```

## Troubleshooting

### API won't start
- Check Python version (3.11+)
- Verify .env file exists and has correct values
- Check if port 8000 is available

### Web won't start
- Check Node version (20+)
- Run `npm install` again
- Check if port 3000 is available

### No results from search
- Verify GraphDB is accessible
- Check network connectivity
- Review API logs for errors

## Next Steps

- Read the full [API Documentation](./app/api/API.md)
- Review [SPARQL Patterns](./app/api/SPARQL.md)
- Explore the codebase structure
- Customize translations and filters
