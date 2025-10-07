# Quick Deployment Guide

This is a quick reference for deploying the application. For detailed information, see [DEPLOYMENT.md](DEPLOYMENT.md).

## Prerequisites Checklist

- [ ] Azure Container Registry (`iacstudioregistry`) exists
- [ ] Container App Environment (`iac-studio-env`) exists
- [ ] Azure services configured (Speech, Translator, OpenAI)
- [ ] GitHub repository forked/cloned
- [ ] GitHub secrets configured

## GitHub Secrets Required

### Azure Credentials & Resources
- `AZURE_CREDENTIALS` - Service principal JSON
- `AZURE_RESOURCE_GROUP` - Resource group name
- `AZURE_REGION` - Azure region

### Azure Services
- `AZURE_SPEECH_KEY` - Speech Service key
- `AZURE_SPEECH_REGION` - Speech Service region
- `AZURE_TRANSLATOR_KEY` - Translator key
- `AZURE_TRANSLATOR_REGION` - Translator region
- `AZURE_OPENAI_API_KEY` - OpenAI key
- `AZURE_OPENAI_ENDPOINT` - OpenAI endpoint
- `AZURE_OPENAI_DEPLOYMENT_NAME` - OpenAI deployment

### Frontend
- `REACT_APP_API_URL` - Backend API URL (add after backend deployment)

## Deployment Steps

### 1. Deploy Backend

```bash
# Push to main branch (automatic deployment)
git push origin main

# Or trigger manually via GitHub Actions UI
```

**Wait for deployment to complete** (~5-10 minutes)

### 2. Get Backend URL

```bash
az containerapp show \
  --name backend-ai-powered-practice-questions \
  --resource-group {your-resource-group} \
  --query properties.configuration.ingress.fqdn \
  --output tsv
```

### 3. Add Backend URL to GitHub Secrets

Add `REACT_APP_API_URL` with value: `https://{fqdn}`

### 4. Deploy Frontend

```bash
# Push to main branch (automatic deployment)
git push origin main

# Or trigger manually via GitHub Actions UI
```

**Wait for deployment to complete** (~3-5 minutes)

### 5. Access Application

Frontend URL: `https://imohweb.github.io/AI-Powered-certifications-exams-practice-questions/`

## Quick Verification

```bash
# Test backend health
curl https://{backend-fqdn}/health

# Test backend API
curl https://{backend-fqdn}/api/v1/certifications

# Open frontend in browser
open https://imohweb.github.io/AI-Powered-certifications-exams-practice-questions/
```

## Troubleshooting

### Backend Not Starting
```bash
# Check logs
az containerapp logs show \
  --name backend-ai-powered-practice-questions \
  --resource-group {your-resource-group} \
  --follow
```

### Frontend Build Fails
- Check GitHub Actions logs
- Verify Node.js version (18)
- Check for TypeScript errors

### API Calls Fail
- Verify `REACT_APP_API_URL` is set correctly
- Check backend CORS configuration
- Ensure backend is accessible

## Rollback

### Backend
```bash
# List versions
az acr repository show-tags \
  --name iacstudioregistry \
  --repository ai-powered-practice-questions-backend

# Rollback
az containerapp update \
  --name backend-ai-powered-practice-questions \
  --resource-group {your-resource-group} \
  --image iacstudioregistry.azurecr.io/ai-powered-practice-questions-backend:{version}
```

### Frontend
Re-run previous successful deployment from GitHub Actions

## Need Help?

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.
