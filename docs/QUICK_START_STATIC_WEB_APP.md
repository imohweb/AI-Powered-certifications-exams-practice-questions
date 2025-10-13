# Quick Start: Deploy Frontend to Azure Static Web App

## ⚡ Fast Track (3 Steps)

### 1️⃣ Add GitHub Secret

**Go to:** https://github.com/imohweb/AI-Powered-certifications-exams-practice-questions/settings/environments

1. Click `cert-practice-question-env`
2. Click "Add secret"
3. Name: `AZURE_STATIC_WEB_APPS_API_TOKEN`
4. Value:
   ```
   c615a4275ce0313cc907648a47eea95067173d362fdef089c42bff3f178271d002-e7538fca-dfec-4c47-ac86-ab1b072cbb5000f23070486f060f
   ```
5. Click "Add secret"

### 2️⃣ Deploy

**Go to:** https://github.com/imohweb/AI-Powered-certifications-exams-practice-questions/actions/workflows/deploy-frontend-static-webapp.yml

1. Click "Run workflow"
2. Select `main` branch
3. Click "Run workflow"
4. Wait ~2-3 minutes

### 3️⃣ Test

**Open:** https://lively-dune-0486f060f.2.azurestaticapps.net

✅ Should load homepage  
✅ Should fetch assessments from backend  
✅ Should work without CORS errors

---

## 🎯 Key URLs

| Resource | URL |
|----------|-----|
| **Frontend (Static Web App)** | https://lively-dune-0486f060f.2.azurestaticapps.net |
| **Backend API** | https://backend-ai-practice-questions-app.azurewebsites.net |
| **GitHub Actions** | https://github.com/imohweb/AI-Powered-certifications-exams-practice-questions/actions |
| **GitHub Secrets** | https://github.com/imohweb/AI-Powered-certifications-exams-practice-questions/settings/environments |
| **Azure Portal** | https://portal.azure.com → RG-foundry-resource |

---

## 🔧 Quick Troubleshooting

### Deployment Failed?

```bash
# Check workflow run
gh run list --workflow=deploy-frontend-static-webapp.yml --limit 1

# View logs
gh run view --log
```

**Common issues:**
- ❌ Secret not added → Add `AZURE_STATIC_WEB_APPS_API_TOKEN` secret
- ❌ Build failed → Check `frontend/` for syntax errors
- ❌ Wrong branch → Ensure deploying from `main` branch

### CORS Errors?

```bash
# Verify backend CORS
az webapp config appsettings list \
  --name backend-ai-practice-questions-app \
  --resource-group RG-foundry-resource \
  --query "[?name=='CORS_ORIGINS'].value" \
  -o tsv
```

**Should include:** `https://lively-dune-0486f060f.2.azurestaticapps.net`

### Backend Not Responding?

```bash
# Check backend health
curl https://backend-ai-practice-questions-app.azurewebsites.net/

# Check backend logs
az webapp log tail \
  --name backend-ai-practice-questions-app \
  --resource-group RG-foundry-resource
```

---

## 📋 What's Configured

✅ **Azure Static Web App Created**
- Name: `frontend-ai-practice-static`
- Resource Group: `RG-foundry-resource`
- Location: `eastus2`
- Tier: `Free`

✅ **Backend CORS Updated**
- Allows: GitHub Pages, Web App, Static Web App

✅ **Workflow Created**
- File: `.github/workflows/deploy-frontend-static-webapp.yml`
- Triggers: Push to `main` (frontend changes), Manual

✅ **Environment Variables Set**
- Frontend: `REACT_APP_API_BASE_URL` (backend URL)
- Backend: All Azure service credentials

---

## 🧹 Optional Cleanup

### Delete Old Frontend Web App

```bash
# Delete the failed Web App deployment
az webapp delete \
  --name frontend-ai-practice-questions-app \
  --resource-group RG-foundry-resource

# Remove workflow file
rm .github/workflows/deploy-frontend-webapp.yml
git add .github/workflows/deploy-frontend-webapp.yml
git commit -m "Remove failed frontend Web App workflow"
git push origin main
```

---

## 📚 Full Documentation

For detailed information, see:
- `docs/STATIC_WEB_APP_DEPLOYMENT.md` - Complete deployment guide
- `docs/FRONTEND_WEBAPP_DEPLOYMENT.md` - General frontend deployment info
- `docs/GITHUB_SECRETS_GUIDE.md` - GitHub secrets management

---

## 🚀 Deployment Token

**Save this token securely (already added to workflow):**

```
c615a4275ce0313cc907648a47eea95067173d362fdef089c42bff3f178271d002-e7538fca-dfec-4c47-ac86-ab1b072cbb5000f23070486f060f
```

**To regenerate:**
```bash
az staticwebapp secrets list \
  --name frontend-ai-practice-static \
  --resource-group RG-foundry-resource \
  --query "properties.apiKey" \
  -o tsv
```

---

## ✨ Why Static Web App?

**Better than Azure Web App for React:**
- ✅ No server needed
- ✅ Global CDN distribution
- ✅ Free tier available
- ✅ Automatic HTTPS
- ✅ Built-in preview environments
- ✅ Simpler deployment
- ✅ No node_modules issues

**Previous Web App issues:**
- ❌ Express module errors
- ❌ Complex deployment
- ❌ Runtime management
- ❌ Cost sharing App Service Plan
