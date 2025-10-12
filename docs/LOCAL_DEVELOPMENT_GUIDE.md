# Local Development Guide

## Overview
This guide explains how to run the Microsoft Certification Practice Assessment application locally for development and testing before deploying to Azure.

## Prerequisites
- Python 3.8+ with venv
- Node.js 16+ and npm
- Azure OpenAI API access
- Azure Speech Service access (optional, for voice features)
- Azure Translator Service access (optional, for translation features)

## Quick Start

### 1. Backend Setup

#### Navigate to backend directory
```bash
cd backend
```

#### Activate virtual environment
```bash
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows
```

#### Verify environment variables
Ensure `backend/.env` contains:
```properties
# Required for AI question generation
AZURE_OPENAI_KEY=<your-key>
AZURE_OPENAI_ENDPOINT=<your-endpoint>
AZURE_OPENAI_DEPLOYMENT=<your-deployment-name>

# Optional for voice features
AZURE_SPEECH_KEY=<your-key>
AZURE_SPEECH_REGION=<your-region>
AZURE_SPEECH_ENDPOINT=<your-endpoint>

# Optional for translation
AZURE_TRANSLATOR_KEY=<your-key>
AZURE_TRANSLATOR_ENDPOINT=<your-endpoint>
AZURE_TRANSLATOR_REGION=<your-region>
```

#### Start the backend server
```bash
python main.py
```

The backend should start on `http://localhost:8000`

#### Verify backend is running
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "services": {
    "api": "operational",
    "azure_speech": "operational",
    "database": "operational"
  }
}
```

### 2. Frontend Setup

#### Navigate to frontend directory
```bash
cd frontend
```

#### Verify environment variables
Ensure `frontend/.env` contains:
```properties
# Backend API Configuration
REACT_APP_API_URL=http://localhost:8000
REACT_APP_API_BASE_URL=http://localhost:8000/api/v1

# Development Configuration
REACT_APP_ENV=development
```

#### Remove GitHub Pages homepage setting
Edit `package.json` and ensure the `homepage` field is **removed** or commented out:
```json
{
  "name": "ms-cert-practice-frontend",
  "version": "1.0.0",
  "private": true,
  // "homepage": "...",  <- This should NOT be present for local dev
  "dependencies": {
    ...
  }
}
```

#### Start the development server
```bash
npm start
```

The frontend should start on `http://localhost:3001` and automatically open in your browser.

## Testing the Application

### 1. Access the Application
Open your browser and navigate to: `http://localhost:3001`

### 2. Test Question Generation
1. Click on any certification exam (e.g., AZ-104)
2. Wait for the AI to generate 50 practice questions (this may take 30-60 seconds)
3. Verify questions are displayed correctly

### 3. Test API Endpoints Manually

#### List available certifications
```bash
curl http://localhost:8000/api/v1/assessments/certifications
```

#### Generate questions for a specific certification
```bash
curl http://localhost:8000/api/v1/assessments/AZ-104
```

Note: This will take 30-60 seconds as it generates 50 questions using AI.

## Common Issues and Solutions

### Issue: Backend shows "Address already in use"
**Solution:** Check if backend is already running:
```bash
lsof -i :8000
# Kill the existing process
kill <PID>
```

### Issue: Frontend shows 404 errors for API calls
**Solution:** 
1. Verify backend is running on port 8000
2. Check `frontend/.env` has correct `REACT_APP_API_BASE_URL`
3. Ensure `package.json` does NOT have a `homepage` field
4. Restart the frontend dev server

### Issue: Frontend not generating questions
**Causes:**
1. Backend not running
2. Missing Azure OpenAI credentials
3. Frontend calling wrong API URL

**Solution:**
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check backend logs for errors
3. Open browser DevTools (F12) → Network tab → Check API calls
4. Verify API calls go to `http://localhost:8000/api/v1/...`

### Issue: Questions take too long to generate
**Expected Behavior:** Generating 50 questions typically takes 30-60 seconds on first request (not cached).

**If it takes longer:**
1. Check Azure OpenAI service status
2. Check network connectivity
3. Review backend logs for timeout errors

## Development Workflow

### Making Changes

#### Backend Changes
1. Edit files in `backend/app/`
2. Backend will auto-reload if `debug=True` in settings
3. Test changes via API or frontend

#### Frontend Changes  
1. Edit files in `frontend/src/`
2. Frontend dev server will auto-reload
3. Changes appear immediately in browser

### Before Deployment
1. Test all major features locally
2. Verify environment variables are set correctly
3. Test with different certification exams
4. Check browser console for errors
5. Review backend logs

## Deployment Preparation

### For Azure App Service (Backend)
1. Ensure `backend/.env` variables are set as App Service Configuration
2. Use `startup.txt` command: `uvicorn main:app --host 0.0.0.0 --port 8000`
3. Test locally first to verify all APIs work

### For Azure Static Web App (Frontend)
1. Update `package.json` with correct `homepage` for deployment
2. Set environment variables in Static Web App configuration
3. Build and test production bundle locally:
   ```bash
   npm run build
   npm run serve  # Test the production build
   ```

### For GitHub Pages (Frontend - Alternative)
1. Update `package.json` with GitHub Pages URL:
   ```json
   "homepage": "https://yourusername.github.io/repository-name"
   ```
2. Build and deploy:
   ```bash
   npm run build
   npm run deploy
   ```

## Port Reference
- **Backend:** `http://localhost:8000`
- **Frontend (Dev):** `http://localhost:3001`
- **Frontend (Production):** `http://localhost:8080` (when using `npm run serve`)

## API Endpoints Reference

### Health Check
- `GET /health` - Check backend health status

### Assessments
- `GET /api/v1/assessments/certifications` - List all certifications
- `GET /api/v1/assessments/{code}` - Get/generate questions for certification

### Audio (Voice Features)
- `POST /api/v1/audio/text-to-speech` - Convert text to speech
- `GET /api/v1/audio/voices` - List available voices

### Sessions
- `POST /api/v1/sessions/start` - Start practice session
- `GET /api/v1/sessions/{id}` - Get session details

## Support
For issues, check:
1. Backend terminal for error logs
2. Frontend terminal for compilation errors
3. Browser DevTools → Console for frontend errors
4. Browser DevTools → Network for API call failures

---
Last Updated: October 10, 2025
