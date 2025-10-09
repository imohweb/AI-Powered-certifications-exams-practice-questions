# Frontend Azure Web App Deployment Guide

## Overview
This document describes the new frontend deployment to Azure Web App instead of GitHub Pages.

## Architecture

### Frontend Web App
- **Name**: `frontend-ai-practice-questions-app`
- **URL**: https://frontend-ai-practice-questions-app.azurewebsites.net
- **Runtime**: Node.js 20 LTS
- **Server**: Express.js serving static React build
- **App Service Plan**: `backend-ai-practice-plan` (shared with backend, B1 tier)

### Backend Web App
- **Name**: `backend-ai-practice-questions-app`
- **URL**: https://backend-ai-practice-questions-app.azurewebsites.net
- **Runtime**: Python 3.11
- **Framework**: FastAPI with Uvicorn
- **App Service Plan**: `backend-ai-practice-plan` (B1 tier)

## CORS Configuration

The backend now allows requests from two origins:
```json
[
  "https://imohweb.github.io",
  "https://frontend-ai-practice-questions-app.azurewebsites.net"
]
```

## Deployment Workflows

### 1. Backend Deployment
**File**: `.github/workflows/deploy-backend-webapp.yml`

**Triggers**:
- Push to `main` branch with changes in `backend/` directory
- Manual workflow dispatch

**Key Steps**:
1. Login to Azure
2. Check if Web App exists, create if needed
3. Create/verify App Service Plan
4. Configure logging and startup command
5. Set environment variables (Azure AI services, CORS)
6. Deploy using `az webapp up` (auto-installs dependencies with Oryx)
7. Test health endpoint

**Environment Variables Set**:
- `CORS_ORIGINS` - Allowed origins for CORS
- `AZURE_SPEECH_KEY` - Azure Speech Service key
- `AZURE_SPEECH_REGION` - Azure Speech Service region
- `AZURE_TRANSLATOR_KEY` - Azure Translator key
- `AZURE_TRANSLATOR_REGION` - Azure Translator region
- `AZURE_OPENAI_KEY` - Azure OpenAI API key (note: not AZURE_OPENAI_API_KEY)
- `AZURE_OPENAI_ENDPOINT` - Azure OpenAI endpoint URL
- `AZURE_OPENAI_DEPLOYMENT` - Azure OpenAI deployment name (note: not AZURE_OPENAI_DEPLOYMENT_NAME)

### 2. Frontend Deployment
**File**: `.github/workflows/deploy-frontend-webapp.yml`

**Triggers**:
- Push to `main` branch with changes in `frontend/` directory
- Manual workflow dispatch

**Key Steps**:
1. Login to Azure
2. Check if Web App exists, create if needed (uses same App Service Plan)
3. Configure logging and startup command (`npm run serve`)
4. Install dependencies
5. Create `.env` file with backend URL
6. Build React app
7. Deploy entire frontend directory using `az webapp up`
8. Test frontend availability

**How it Works**:
- Builds the React app into the `build/` directory
- Includes `server.js` (Express server) to serve the static files
- Express handles React Router by returning `index.html` for all routes
- Startup command: `npm run serve` runs the Express server

## Frontend Server (server.js)

```javascript
const express = require('express');
const path = require('path');
const app = express();

// Serve static files
app.use(express.static(path.join(__dirname, 'build')));

// Handle React routing
app.get('/*', function (req, res) {
  res.sendFile(path.join(__dirname, 'build', 'index.html'));
});

const PORT = process.env.PORT || 8080;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
```

## Key Fixes Applied

### 1. CORS Issue
**Problem**: Frontend origin didn't match CORS configuration
**Solution**: Changed CORS_ORIGINS from full URL path to just the origin (protocol + domain)
- ❌ `https://imohweb.github.io/AI-Powered-certifications-exams-practice-questions`
- ✅ `https://imohweb.github.io`

### 2. Missing Dependencies
**Problem**: Backend failed with "uvicorn: not found"
**Solution**: Switched from `az webapp deployment source config-zip` to `az webapp up` which triggers Oryx build

### 3. Azure OpenAI Not Working
**Problem**: Environment variable names didn't match config.py expectations
**Solution**: Renamed variables to match Pydantic field names:
- `AZURE_OPENAI_API_KEY` → `AZURE_OPENAI_KEY`
- `AZURE_OPENAI_DEPLOYMENT_NAME` → `AZURE_OPENAI_DEPLOYMENT`

### 4. Node.js Runtime
**Problem**: `NODE:18-lts` not supported
**Solution**: Updated to `NODE:20-lts` (currently supported runtime)

## Deployment Steps

### Deploy Backend
1. Go to: https://github.com/imohweb/AI-Powered-certifications-exams-practice-questions/actions/workflows/deploy-backend-webapp.yml
2. Click "Run workflow"
3. Select `main` branch
4. Click "Run workflow"
5. Wait for completion (~5-10 minutes)
6. Test: https://backend-ai-practice-questions-app.azurewebsites.net/health

### Deploy Frontend
1. Go to: https://github.com/imohweb/AI-Powered-certifications-exams-practice-questions/actions/workflows/deploy-frontend-webapp.yml
2. Click "Run workflow"
3. Select `main` branch
4. Click "Run workflow"
5. Wait for completion (~3-5 minutes)
6. Test: https://frontend-ai-practice-questions-app.azurewebsites.net

## Testing

### Backend Health Check
```bash
curl https://backend-ai-practice-questions-app.azurewebsites.net/health
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

### Frontend Availability
```bash
curl -I https://frontend-ai-practice-questions-app.azurewebsites.net
```

Expected: HTTP 200 OK

### CORS Test
```bash
curl -H "Origin: https://frontend-ai-practice-questions-app.azurewebsites.net" \
  -I https://backend-ai-practice-questions-app.azurewebsites.net/api/v1/assessments/AZ-104
```

Expected headers:
```
access-control-allow-origin: https://frontend-ai-practice-questions-app.azurewebsites.net
access-control-allow-credentials: true
```

## Troubleshooting

### Backend Issues

**Check logs**:
```bash
az webapp log tail --name backend-ai-practice-questions-app --resource-group RG-foundry-resource
```

**Download logs**:
```bash
az webapp log download --name backend-ai-practice-questions-app --resource-group RG-foundry-resource --log-file backend-logs.zip
```

**Restart app**:
```bash
az webapp restart --name backend-ai-practice-questions-app --resource-group RG-foundry-resource
```

### Frontend Issues

**Check logs**:
```bash
az webapp log tail --name frontend-ai-practice-questions-app --resource-group RG-foundry-resource
```

**Restart app**:
```bash
az webapp restart --name frontend-ai-practice-questions-app --resource-group RG-foundry-resource
```

## Cost Considerations

Both frontend and backend share the same **B1 App Service Plan**:
- **Cost**: ~$13.14/month (single plan for both apps)
- **Specs**: 1.75 GB RAM, 1 vCPU
- **Benefit**: More economical than two separate plans

## Next Steps

1. **Deploy Backend**: Trigger backend workflow to apply OpenAI fix
2. **Deploy Frontend**: Trigger frontend workflow to create new Web App
3. **Test End-to-End**: Verify assessments load correctly
4. **Monitor**: Check logs for any issues
5. **Optional**: Update DNS/custom domain if needed
