# Azure Static Web App Deployment Guide

## Overview
This guide covers deploying the React frontend to Azure Static Web Apps, which is better suited for static frontends than Azure Web App (Node.js).

## Current Status
✅ Azure Static Web App created: `frontend-ai-practice-static`  
✅ URL: https://lively-dune-0486f060f.2.azurestaticapps.net  
✅ Backend CORS updated to allow Static Web App  
✅ Deployment workflow created  
⏳ GitHub secret needs configuration  
⏳ Deployment pending

---

## Step 1: Add GitHub Secret

### Option A: Using GitHub Web UI (Recommended)

1. **Go to GitHub Secrets**
   ```
   https://github.com/imohweb/AI-Powered-certifications-exams-practice-questions/settings/environments
   ```

2. **Select Environment**
   - Click on `cert-practice-question-env`

3. **Add Secret**
   - Click "Add secret"
   - Name: `AZURE_STATIC_WEB_APPS_API_TOKEN`
   - Value: (Copy the token below)

4. **Deployment Token**
   ```
   c615a4275ce0313cc907648a47eea95067173d362fdef089c42bff3f178271d002-e7538fca-dfec-4c47-ac86-ab1b072cbb5000f23070486f060f
   ```

5. **Save Secret**
   - Click "Add secret" to save

### Option B: Using GitHub CLI

```bash
# Install GitHub CLI if not installed
# brew install gh (macOS)

# Authenticate
gh auth login

# Add secret to environment
gh secret set AZURE_STATIC_WEB_APPS_API_TOKEN \
  --env cert-practice-question-env \
  --repo imohweb/AI-Powered-certifications-exams-practice-questions \
  --body "c615a4275ce0313cc907648a47eea95067173d362fdef089c42bff3f178271d002-e7538fca-dfec-4c47-ac86-ab1b072cbb5000f23070486f060f"
```

---

## Step 2: Deploy Frontend

### Manual Trigger

1. **Go to Actions**
   ```
   https://github.com/imohweb/AI-Powered-certifications-exams-practice-questions/actions/workflows/deploy-frontend-static-webapp.yml
   ```

2. **Run Workflow**
   - Click "Run workflow" dropdown
   - Select branch: `main`
   - Click "Run workflow" button

3. **Monitor Deployment**
   - Click on the running workflow
   - Watch the build and deploy steps
   - Deployment takes ~2-3 minutes

### Automatic Trigger

The workflow automatically runs on:
- Push to `main` branch (changes to `frontend/` directory)
- Pull request to `main` (changes to `frontend/` directory)

---

## Step 3: Verify Deployment

### Test Static Web App

1. **Access Frontend**
   ```
   https://lively-dune-0486f060f.2.azurestaticapps.net
   ```

2. **Test Features**
   - ✅ Homepage loads
   - ✅ Start Assessment button works
   - ✅ Questions load from backend
   - ✅ Voice command works
   - ✅ Navigation works

3. **Check Backend Connection**
   - Open browser console (F12)
   - Look for API calls to backend
   - Verify no CORS errors

### Troubleshoot Issues

If deployment fails:

```bash
# Check workflow logs
gh run list --workflow=deploy-frontend-static-webapp.yml --limit 1

# View latest run details
gh run view --log
```

If CORS errors occur:

```bash
# Verify backend CORS settings
az webapp config appsettings list \
  --name backend-ai-practice-questions-app \
  --resource-group RG-foundry-resource \
  --query "[?name=='CORS_ORIGINS'].value" \
  -o tsv
```

Expected output:
```
["https://imohweb.github.io","https://frontend-ai-practice-questions-app.azurewebsites.net","https://lively-dune-0486f060f.2.azurestaticapps.net"]
```

---

## Step 4: Clean Up (Optional)

### Delete Failed Web App

If the frontend Web App (`frontend-ai-practice-questions-app`) is no longer needed:

```bash
# Delete the Web App
az webapp delete \
  --name frontend-ai-practice-questions-app \
  --resource-group RG-foundry-resource

# Delete the Web App deployment workflow (optional)
rm .github/workflows/deploy-frontend-webapp.yml
git add .github/workflows/deploy-frontend-webapp.yml
git commit -m "Remove failed frontend Web App deployment workflow"
git push origin main
```

---

## Architecture Comparison

### Azure Web App (Node.js) - Previous Approach
❌ Requires Express server  
❌ Need to manage Node.js runtime  
❌ Deployment issues with node_modules  
❌ More complex configuration  
❌ Higher cost (shares App Service Plan)

### Azure Static Web App - New Approach
✅ No server needed (CDN)  
✅ Designed for static frontends  
✅ Simple deployment with GitHub Actions  
✅ Built-in preview environments  
✅ Free tier available  
✅ Global CDN distribution  
✅ Automatic HTTPS  
✅ Custom domains support

---

## Configuration Details

### Workflow File
`.github/workflows/deploy-frontend-static-webapp.yml`

Key settings:
- **App location**: `frontend`
- **Output location**: `build`
- **Skip app build**: `true` (we build before deployment)
- **Backend URL**: Set via `REACT_APP_API_BASE_URL` env var

### Backend CORS Settings

Allowed origins:
1. `https://imohweb.github.io` - GitHub Pages (backup)
2. `https://frontend-ai-practice-questions-app.azurewebsites.net` - Web App (old)
3. `https://lively-dune-0486f060f.2.azurestaticapps.net` - Static Web App (new)

### Environment Variables

Frontend (set in workflow):
- `REACT_APP_API_BASE_URL`: Backend API URL

Backend (set in Azure):
- `AZURE_OPENAI_KEY`: OpenAI API key
- `AZURE_OPENAI_DEPLOYMENT`: Model deployment name
- `AZURE_OPENAI_ENDPOINT`: OpenAI endpoint
- `AZURE_SPEECH_KEY`: Speech service key
- `AZURE_SPEECH_REGION`: Speech service region
- `AZURE_TRANSLATOR_KEY`: Translator service key
- `AZURE_TRANSLATOR_REGION`: Translator service region
- `CORS_ORIGINS`: Allowed frontend origins (JSON array)

---

## Useful Commands

### Check Static Web App Status

```bash
# Get Static Web App details
az staticwebapp show \
  --name frontend-ai-practice-static \
  --resource-group RG-foundry-resource

# List deployments
az staticwebapp environment list \
  --name frontend-ai-practice-static \
  --resource-group RG-foundry-resource

# Get deployment token (if needed again)
az staticwebapp secrets list \
  --name frontend-ai-practice-static \
  --resource-group RG-foundry-resource \
  --query "properties.apiKey" \
  -o tsv
```

### Update Backend CORS (if needed)

```bash
# Add new origin
az webapp config appsettings set \
  --name backend-ai-practice-questions-app \
  --resource-group RG-foundry-resource \
  --settings CORS_ORIGINS='["https://imohweb.github.io","https://frontend-ai-practice-questions-app.azurewebsites.net","https://lively-dune-0486f060f.2.azurestaticapps.net","https://new-origin.com"]'
```

### Test Backend API

```bash
# Health check
curl https://backend-ai-practice-questions-app.azurewebsites.net/

# Get assessments
curl https://backend-ai-practice-questions-app.azurewebsites.net/api/assessments/
```

---

## Next Steps

1. ✅ Commit workflow changes
2. **Add GitHub secret** ⬅️ YOU ARE HERE
3. **Deploy frontend**
4. Test functionality
5. (Optional) Delete old Web App
6. Update DNS/custom domain if needed

---

## Support

### Documentation
- [Azure Static Web Apps Docs](https://docs.microsoft.com/en-us/azure/static-web-apps/)
- [GitHub Actions for Static Web Apps](https://docs.microsoft.com/en-us/azure/static-web-apps/github-actions-workflow)

### Troubleshooting
See `docs/FRONTEND_WEBAPP_DEPLOYMENT.md` for general troubleshooting tips.

### Resources
- Resource Group: `RG-foundry-resource`
- Location: `eastus2`
- Backend: `backend-ai-practice-questions-app`
- Frontend Static Web App: `frontend-ai-practice-static`
- App Service Plan: `backend-ai-practice-plan` (B1 tier)
