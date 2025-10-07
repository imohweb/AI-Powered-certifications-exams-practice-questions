# Deployment Guide

This guide explains how to deploy the AI-Powered Certification Practice Questions application to production.

## Table of Contents
- [Architecture Overview](#architecture-overview)
- [Prerequisites](#prerequisites)
- [GitHub Secrets Configuration](#github-secrets-configuration)
- [Backend Deployment](#backend-deployment)
- [Frontend Deployment](#frontend-deployment)
- [Post-Deployment](#post-deployment)
- [Rollback Procedures](#rollback-procedures)
- [Monitoring](#monitoring)

## Architecture Overview

### Backend
- **Hosting**: Azure Container Apps
- **Container Registry**: Azure Container Registry (ACR) - `iacstudioregistry`
- **Repository Name**: `ai-powered-practice-questions-backend`
- **Container App**: `backend-ai-powered-practice-questions`
- **Environment**: `iac-studio-env`
- **CI/CD**: GitHub Actions

### Frontend
- **Hosting**: GitHub Pages
- **Build**: React production build
- **CI/CD**: GitHub Actions

## Prerequisites

### Azure Resources
1. **Azure Container Registry**: `iacstudioregistry`
2. **Container App Environment**: `iac-studio-env`
3. **Resource Group**: Your Azure resource group
4. **Azure Services**:
   - Azure Speech Service
   - Azure Translator Service
   - Azure OpenAI Service

### GitHub Repository
- Repository: `https://github.com/imohweb/AI-Powered-certifications-exams-practice-questions`
- Branches:
  - `main`: Production branch (protected)
  - `develop`: Development branch (protected)
  - Feature branches: `feature/yourfirstname`

## GitHub Secrets Configuration

You need to configure the following secrets in your GitHub repository:

### Navigate to Secrets
1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**

### Required Secrets

#### Azure Credentials
```
AZURE_CREDENTIALS
```
Value: JSON object from Azure service principal
```json
{
  "clientId": "your-client-id",
  "clientSecret": "your-client-secret",
  "subscriptionId": "your-subscription-id",
  "tenantId": "your-tenant-id"
}
```

To create the service principal:
```bash
az ad sp create-for-rbac --name "github-actions-ai-practice-questions" \
  --role contributor \
  --scopes /subscriptions/{subscription-id}/resourceGroups/{resource-group} \
  --sdk-auth
```

#### Azure Resource Configuration
```
AZURE_RESOURCE_GROUP
```
Value: Your Azure resource group name

```
AZURE_REGION
```
Value: Azure region (e.g., `eastus`, `westeurope`)

#### Azure Speech Service
```
AZURE_SPEECH_KEY
```
Value: Your Azure Speech Service API key

```
AZURE_SPEECH_REGION
```
Value: Your Speech Service region (e.g., `northeurope`)

#### Azure Translator Service
```
AZURE_TRANSLATOR_KEY
```
Value: Your Azure Translator Service API key

```
AZURE_TRANSLATOR_REGION
```
Value: Your Translator Service region

#### Azure OpenAI Service
```
AZURE_OPENAI_API_KEY
```
Value: Your Azure OpenAI API key

```
AZURE_OPENAI_ENDPOINT
```
Value: Your Azure OpenAI endpoint URL

```
AZURE_OPENAI_DEPLOYMENT_NAME
```
Value: Your OpenAI deployment name

#### Frontend Configuration
```
REACT_APP_API_URL
```
Value: Your backend API URL (will be provided after backend deployment)
Format: `https://backend-ai-powered-practice-questions.{region}.azurecontainerapps.io`

## Backend Deployment

### Automatic Deployment

The backend deploys automatically when:
1. Code is pushed to the `main` branch
2. Changes are made in the `backend/` directory
3. Manual trigger via GitHub Actions

### Deployment Process

1. **Build Number**: Automatically generated based on Git commit count
2. **Docker Image**: Built and tagged with build number
3. **ACR Push**: Image pushed to `iacstudioregistry.azurecr.io/ai-powered-practice-questions-backend:{BUILD_NUMBER}`
4. **Latest Tag**: Also tagged as `:latest`
5. **Container App**: Updated automatically with new image
6. **Old Images**: Retained in ACR for rollback

### Workflow File
`.github/workflows/deploy-backend.yml`

### Manual Deployment

To trigger manually:
1. Go to **Actions** tab in GitHub
2. Select **Deploy Backend to Azure Container Apps**
3. Click **Run workflow**
4. Select `main` branch
5. Click **Run workflow**

### Verify Backend Deployment

After deployment:
```bash
# Get the Container App URL
az containerapp show \
  --name backend-ai-powered-practice-questions \
  --resource-group {your-resource-group} \
  --query properties.configuration.ingress.fqdn \
  --output tsv

# Test the API
curl https://{fqdn}/health
curl https://{fqdn}/api/v1/certifications
```

## Frontend Deployment

### Automatic Deployment

The frontend deploys automatically when:
1. Code is pushed to the `main` branch
2. Changes are made in the `frontend/` directory
3. Manual trigger via GitHub Actions

### Deployment Process

1. **Build**: React app built for production
2. **Environment**: Production environment variables injected
3. **GitHub Pages**: Built files deployed to GitHub Pages
4. **URL**: Available at `https://imohweb.github.io/AI-Powered-certifications-exams-practice-questions/`

### Workflow File
`.github/workflows/deploy-frontend.yml`

### Manual Deployment

To trigger manually:
1. Go to **Actions** tab in GitHub
2. Select **Deploy Frontend to GitHub Pages**
3. Click **Run workflow**
4. Select `main` branch
5. Click **Run workflow**

### GitHub Pages Configuration

Ensure GitHub Pages is enabled:
1. Go to **Settings** → **Pages**
2. Source: **GitHub Actions**
3. The site will be published at the repository URL

## Post-Deployment

### 1. Update Frontend API URL

After backend is deployed, update the frontend secret:

```
REACT_APP_API_URL=https://backend-ai-powered-practice-questions.{region}.azurecontainerapps.io
```

Then redeploy the frontend.

### 2. Test the Application

1. **Navigate to frontend URL**
2. **Select a certification**
3. **Start assessment**
4. **Test voice features**
5. **Test multilingual support**
6. **Check audio generation**

### 3. Monitor Logs

#### Backend Logs
```bash
# Stream logs
az containerapp logs show \
  --name backend-ai-powered-practice-questions \
  --resource-group {your-resource-group} \
  --follow

# View recent logs
az containerapp logs show \
  --name backend-ai-powered-practice-questions \
  --resource-group {your-resource-group} \
  --tail 100
```

#### Frontend Logs
Check browser console for any errors

## Rollback Procedures

### Backend Rollback

If you need to rollback to a previous version:

```bash
# List available images
az acr repository show-tags \
  --name iacstudioregistry \
  --repository ai-powered-practice-questions-backend \
  --orderby time_desc

# Rollback to specific version
az containerapp update \
  --name backend-ai-powered-practice-questions \
  --resource-group {your-resource-group} \
  --image iacstudioregistry.azurecr.io/ai-powered-practice-questions-backend:{previous-build-number}
```

### Frontend Rollback

1. Go to **Actions** tab
2. Find the successful deployment you want to restore
3. Click **Re-run jobs**

## Monitoring

### Backend Metrics

View in Azure Portal:
1. Navigate to Container App
2. Click **Metrics**
3. Monitor:
   - CPU usage
   - Memory usage
   - Request count
   - Response time
   - Error rate

### Health Checks

The backend includes a health endpoint:
```
GET /health
```

Returns:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-10-06T12:00:00Z"
}
```

### Alerts

Set up alerts in Azure Portal:
1. Container App → **Alerts**
2. Create alert rules for:
   - High CPU usage (>80%)
   - High memory usage (>80%)
   - High error rate (>5%)
   - Low availability (<99%)

## Troubleshooting

### Backend Issues

**Container won't start:**
```bash
# Check logs
az containerapp logs show \
  --name backend-ai-powered-practice-questions \
  --resource-group {your-resource-group} \
  --follow

# Check replica status
az containerapp replica list \
  --name backend-ai-powered-practice-questions \
  --resource-group {your-resource-group}
```

**Environment variables not set:**
```bash
# List current environment variables
az containerapp show \
  --name backend-ai-powered-practice-questions \
  --resource-group {your-resource-group} \
  --query properties.template.containers[0].env
```

### Frontend Issues

**Build fails:**
- Check Node.js version (should be 18)
- Verify all dependencies are in package.json
- Check for TypeScript errors

**API calls fail:**
- Verify REACT_APP_API_URL is correct
- Check CORS configuration on backend
- Verify backend is accessible

## Security Best Practices

1. **Never commit secrets** to the repository
2. **Use GitHub Secrets** for all sensitive data
3. **Rotate secrets** regularly
4. **Enable branch protection** on `main` and `develop`
5. **Require PR reviews** before merging
6. **Use HTTPS** for all communications
7. **Monitor access logs** regularly

## Scaling

### Backend Scaling

Current configuration:
- Min replicas: 1
- Max replicas: 3

To adjust:
```bash
az containerapp update \
  --name backend-ai-powered-practice-questions \
  --resource-group {your-resource-group} \
  --min-replicas 2 \
  --max-replicas 5
```

### Resource Limits

Current configuration:
- CPU: 1.0 cores
- Memory: 2.0 Gi

To adjust:
```bash
az containerapp update \
  --name backend-ai-powered-practice-questions \
  --resource-group {your-resource-group} \
  --cpu 2.0 \
  --memory 4.0Gi
```

## Support

For deployment issues:
1. Check GitHub Actions logs
2. Check Azure Container App logs
3. Review this deployment guide
4. Open an issue on GitHub

---

**Last Updated**: October 6, 2025
