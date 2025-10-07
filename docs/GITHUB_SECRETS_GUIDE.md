# GitHub Secrets and Environment Variables Guide

This guide explains what information you need to configure in GitHub for your deployment.

## 📍 Where to Configure

### GitHub Secrets (Repository Level)
**Location**: Repository → Settings → Secrets and variables → Actions → Repository secrets

These are **encrypted** secrets used by GitHub Actions workflows. They are never exposed in logs.

### GitHub Environments (Optional - For Advanced Setup)
**Location**: Repository → Settings → Environments

Used for environment-specific configurations (production, staging, etc.) with additional protection rules.

---

## 🔐 Required GitHub Secrets

### 1. Azure Infrastructure Secrets

#### `AZURE_CREDENTIALS` 
**What it is**: JSON object containing Azure service principal credentials  
**Why needed**: Allows GitHub Actions to authenticate with Azure and deploy resources  
**Format**:
```json
{
  "clientId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "clientSecret": "your~secret~value",
  "subscriptionId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "tenantId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
}
```

**How to get it**:
```bash
# Create service principal with contributor role
az ad sp create-for-rbac \
  --name "github-actions-ai-practice-questions" \
  --role contributor \
  --scopes /subscriptions/{your-subscription-id}/resourceGroups/{your-resource-group} \
  --sdk-auth
```

Copy the entire JSON output and paste it as the secret value.

---

#### `AZURE_RESOURCE_GROUP`
**What it is**: Name of your Azure resource group  
**Why needed**: Tells GitHub Actions where to deploy your resources  
**Example**: `rg-ai-practice-questions` or `my-resource-group`

**How to get it**:
```bash
# List your resource groups
az group list --output table

# Or create a new one
az group create --name rg-ai-practice-questions --location eastus
```

---

#### `AZURE_REGION`
**What it is**: Azure region where your resources are located  
**Why needed**: Specifies deployment location  
**Example**: `eastus`, `westeurope`, `northeurope`, `westus2`

**Common regions**:
- `eastus` - East US
- `westeurope` - West Europe
- `northeurope` - North Europe
- `southeastasia` - Southeast Asia
- `westus2` - West US 2

---

### 2. Azure Speech Service Secrets

#### `AZURE_SPEECH_KEY`
**What it is**: API key for Azure Speech Service (also called "Key 1" or "Key 2")  
**Why needed**: Authenticates API calls to generate speech audio  
**Format**: 32-character alphanumeric string  
**Example**: `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6`

**How to get it**:
1. Azure Portal → Your Speech Service resource → Keys and Endpoint
2. Copy either Key 1 or Key 2
3. Or via CLI:
```bash
az cognitiveservices account keys list \
  --name your-speech-service-name \
  --resource-group your-resource-group
```

---

#### `AZURE_SPEECH_REGION`
**What it is**: Region where your Speech Service is deployed  
**Why needed**: Specifies which regional endpoint to use  
**Example**: `northeurope`, `eastus`, `westeurope`

**How to get it**:
1. Azure Portal → Your Speech Service resource → Overview → Location
2. Or via CLI:
```bash
az cognitiveservices account show \
  --name your-speech-service-name \
  --resource-group your-resource-group \
  --query location -o tsv
```

---

### 3. Azure Translator Service Secrets

#### `AZURE_TRANSLATOR_KEY`
**What it is**: API key for Azure Translator Service  
**Why needed**: Authenticates API calls to translate text  
**Format**: 32-character alphanumeric string  
**Example**: `x1y2z3a4b5c6d7e8f9g0h1i2j3k4l5m6`

**How to get it**:
1. Azure Portal → Your Translator resource → Keys and Endpoint
2. Copy either Key 1 or Key 2
3. Or via CLI:
```bash
az cognitiveservices account keys list \
  --name your-translator-service-name \
  --resource-group your-resource-group
```

---

#### `AZURE_TRANSLATOR_REGION`
**What it is**: Region where your Translator Service is deployed  
**Why needed**: Specifies which regional endpoint to use  
**Example**: `northeurope`, `global`

**How to get it**:
1. Azure Portal → Your Translator resource → Overview → Location
2. Note: Some translator services use `global` as the region

---

### 4. Azure OpenAI Service Secrets

#### `AZURE_OPENAI_API_KEY`
**What it is**: API key for Azure OpenAI Service  
**Why needed**: Authenticates API calls to generate AI practice questions  
**Format**: Long alphanumeric string  
**Example**: `abc123def456...`

**How to get it**:
1. Azure Portal → Your OpenAI resource → Keys and Endpoint
2. Copy either Key 1 or Key 2
3. Or via CLI:
```bash
az cognitiveservices account keys list \
  --name your-openai-service-name \
  --resource-group your-resource-group
```

---

#### `AZURE_OPENAI_ENDPOINT`
**What it is**: Full URL endpoint for your Azure OpenAI resource  
**Why needed**: Tells the application where to send API requests  
**Format**: `https://your-resource-name.openai.azure.com/`  
**Example**: `https://oia-speech-service.openai.azure.com/`

**How to get it**:
1. Azure Portal → Your OpenAI resource → Keys and Endpoint → Endpoint
2. Or via CLI:
```bash
az cognitiveservices account show \
  --name your-openai-service-name \
  --resource-group your-resource-group \
  --query properties.endpoint -o tsv
```

---

#### `AZURE_OPENAI_DEPLOYMENT_NAME`
**What it is**: Name of your GPT model deployment  
**Why needed**: Specifies which model to use for generating questions  
**Example**: `gpt-4`, `speech-service-gpt-4.1`, `gpt-35-turbo`

**How to get it**:
1. Azure OpenAI Studio → Deployments → Copy the deployment name
2. Or via Azure Portal → Your OpenAI resource → Model deployments

---

### 5. Frontend Configuration Secret

#### `REACT_APP_API_URL`
**What it is**: Full URL of your deployed backend API  
**Why needed**: Tells the frontend where to make API requests  
**Format**: `https://your-backend-url.azurecontainerapps.io`  
**Example**: `https://backend-ai-powered-practice-questions.northeurope.azurecontainerapps.io`

**⚠️ Important**: Add this AFTER backend is deployed!

**How to get it**:
```bash
# After backend deployment, run:
az containerapp show \
  --name backend-ai-powered-practice-questions \
  --resource-group your-resource-group \
  --query properties.configuration.ingress.fqdn \
  --output tsv

# The output will be something like:
# backend-ai-powered-practice-questions.northeurope.azurecontainerapps.io

# Add https:// prefix when adding to GitHub Secrets:
# https://backend-ai-powered-practice-questions.northeurope.azurecontainerapps.io
```

---

## 📝 Step-by-Step: Adding Secrets to GitHub

### 1. Navigate to Repository Settings
```
1. Go to: https://github.com/imohweb/AI-Powered-certifications-exams-practice-questions
2. Click "Settings" tab (top right)
3. In left sidebar: Secrets and variables → Actions
4. Click "New repository secret" button
```

### 2. Add Each Secret
For each secret listed above:
```
1. Click "New repository secret"
2. Name: Enter the secret name exactly as shown (e.g., AZURE_SPEECH_KEY)
3. Value: Paste the secret value
4. Click "Add secret"
```

### 3. Verify Secrets Added
After adding all secrets, you should see:
```
✅ AZURE_CREDENTIALS
✅ AZURE_RESOURCE_GROUP
✅ AZURE_REGION
✅ AZURE_SPEECH_KEY
✅ AZURE_SPEECH_REGION
✅ AZURE_TRANSLATOR_KEY
✅ AZURE_TRANSLATOR_REGION
✅ AZURE_OPENAI_API_KEY
✅ AZURE_OPENAI_ENDPOINT
✅ AZURE_OPENAI_DEPLOYMENT_NAME
✅ REACT_APP_API_URL (add after backend deployment)
```

---

## 🔍 How Secrets Are Used in Workflows

### Backend Deployment Workflow
```yaml
# .github/workflows/deploy-backend.yml

# Secrets are accessed using ${{ secrets.SECRET_NAME }}

- name: Log in to Azure
  uses: azure/login@v1
  with:
    creds: ${{ secrets.AZURE_CREDENTIALS }}  # ← Uses AZURE_CREDENTIALS

- name: Create Container App
  run: |
    az containerapp create \
      --name backend-ai-powered-practice-questions \
      --resource-group ${{ secrets.AZURE_RESOURCE_GROUP }} \  # ← Uses AZURE_RESOURCE_GROUP
      --secrets \
        azure-speech-key=${{ secrets.AZURE_SPEECH_KEY }} \     # ← Uses AZURE_SPEECH_KEY
        azure-speech-region=${{ secrets.AZURE_SPEECH_REGION }} # ← Uses AZURE_SPEECH_REGION
        # ... and so on
```

### Frontend Deployment Workflow
```yaml
# .github/workflows/deploy-frontend.yml

- name: Create .env file
  run: |
    echo "REACT_APP_API_URL=${{ secrets.REACT_APP_API_URL }}" > .env  # ← Uses REACT_APP_API_URL
```

---

## ⚠️ Important Security Notes

### DO NOT:
- ❌ Commit secrets to your repository
- ❌ Include secrets in code files
- ❌ Share secrets in public channels
- ❌ Use the same secrets for development and production (if possible)
- ❌ Hardcode API keys in source code

### DO:
- ✅ Use GitHub Secrets for all sensitive data
- ✅ Rotate secrets regularly
- ✅ Use service principals with minimal required permissions
- ✅ Monitor access logs
- ✅ Delete unused service principals
- ✅ Use different Azure resources for dev/staging/production

---

## 🧪 Testing Your Secrets

After adding all secrets, you can test by:

1. **Trigger a manual workflow run**:
   ```
   Actions tab → Deploy Backend to Azure Container Apps → Run workflow
   ```

2. **Check the workflow logs**:
   - Secrets will show as `***` in logs
   - Verify no errors related to authentication

3. **Common errors**:
   - `Invalid credentials` → Check AZURE_CREDENTIALS format
   - `Resource group not found` → Check AZURE_RESOURCE_GROUP name
   - `Unauthorized` → Check API keys are correct
   - `Region not supported` → Check region names match

---

## 📋 Quick Checklist

Before deployment, verify you have:

```
□ AZURE_CREDENTIALS (JSON from az ad sp create-for-rbac)
□ AZURE_RESOURCE_GROUP (resource group name)
□ AZURE_REGION (e.g., eastus)
□ AZURE_SPEECH_KEY (from Speech Service)
□ AZURE_SPEECH_REGION (where Speech Service is deployed)
□ AZURE_TRANSLATOR_KEY (from Translator Service)
□ AZURE_TRANSLATOR_REGION (where Translator is deployed)
□ AZURE_OPENAI_API_KEY (from OpenAI Service)
□ AZURE_OPENAI_ENDPOINT (OpenAI endpoint URL)
□ AZURE_OPENAI_DEPLOYMENT_NAME (GPT model deployment name)
□ REACT_APP_API_URL (backend URL - add after backend deploys)
```

---

## 🆘 Troubleshooting

### "Secret not found" error
- Ensure secret name matches exactly (case-sensitive)
- Check you're in the correct repository
- Verify you have admin access

### "Authentication failed" error
- Verify AZURE_CREDENTIALS JSON format is correct
- Check service principal has correct permissions
- Ensure subscription ID is correct

### "Resource not found" error
- Verify resource names and regions are correct
- Check resources exist in Azure Portal
- Ensure resource group name is correct

---

## 📞 Need Help?

1. Check secret names match exactly
2. Verify all secrets are added
3. Review GitHub Actions logs
4. Check Azure Portal for resource details
5. Refer to `docs/DEPLOYMENT.md` for more details

---

**Last Updated**: October 7, 2025
