# Complete List of Environment Secrets

## Overview
This document lists **ALL 15 secrets** that need to be added to your GitHub Environment: `cert-practice-question-env`

---

## 📍 Location
**GitHub Repository** → **Settings** → **Environments** → **cert-practice-question-env** → **Add Secret**

---

## 🔐 Required Secrets (15 Total)

### 1️⃣ Azure Authentication (4 secrets)

#### `AZURE_CREDENTIALS`
**Description:** Azure Service Principal credentials for authentication  
**Format:** JSON object  
**Example:**
```json
{
  "clientId": "12345678-1234-1234-1234-123456789abc",
  "clientSecret": "your-client-secret-value",
  "subscriptionId": "87654321-4321-4321-4321-cba987654321",
  "tenantId": "abcdef12-3456-7890-abcd-ef1234567890"
}
```
**How to Get:**
- Go to: Azure Portal → Entra ID → App Registrations → Your App
- Client ID: Copy "Application (client) ID"
- Tenant ID: Copy "Directory (tenant) ID"
- Client Secret: Go to "Certificates & secrets" → Create new secret
- Subscription ID: Azure Portal → Subscriptions

---

#### `AZURE_RESOURCE_GROUP`
**Description:** Resource group containing your Container App and Container App Environment  
**Format:** String  
**Example:** `rg-container-apps-prod`  
**How to Get:**
- Azure Portal → Resource Groups → Find the group with your Container App

---

#### `AZURE_REGION`
**Description:** Azure region where resources are deployed  
**Format:** String (lowercase, no spaces)  
**Example:** `eastus`, `westus2`, `westeurope`  
**How to Get:**
- Azure Portal → Your Resource Group → Overview → Location

---

### 2️⃣ Container Configuration (4 secrets)

#### `ACR_NAME`
**Description:** Azure Container Registry name (without .azurecr.io)  
**Format:** String  
**Example:** `iacstudioregistry`  
**How to Get:**
- Azure Portal → Container Registries → Your Registry → Copy name

---

#### `IMAGE_NAME`
**Description:** Docker image name for your backend application  
**Format:** String  
**Example:** `ai-powered-practice-questions-backend`  
**Note:** This is your custom name for the image

---

#### `CONTAINER_APP_NAME`
**Description:** Name of your Azure Container App  
**Format:** String  
**Example:** `backend-ai-powered-practice-questions`  
**How to Get:**
- Azure Portal → Container Apps → Your App → Copy name

---

#### `CONTAINER_APP_ENV`
**Description:** Name of your Container App Environment  
**Format:** String  
**Example:** `iac-studio-env`  
**How to Get:**
- Azure Portal → Container Apps → Environments → Your Environment → Copy name

---

### 3️⃣ Azure AI Services (6 secrets)

#### `AZURE_SPEECH_KEY`
**Description:** Azure Speech Service API key  
**Format:** String (32 characters)  
**Example:** `1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p`  
**How to Get:**
- Azure Portal → Your Speech Service → Keys and Endpoint → KEY 1 or KEY 2

---

#### `AZURE_SPEECH_REGION`
**Description:** Azure Speech Service region  
**Format:** String (lowercase)  
**Example:** `eastus`, `westeurope`  
**How to Get:**
- Azure Portal → Your Speech Service → Keys and Endpoint → Location/Region

---

#### `AZURE_TRANSLATOR_KEY`
**Description:** Azure Translator Service API key  
**Format:** String (32 characters)  
**Example:** `9z8y7x6w5v4u3t2s1r0q9p8o7n6m5l4k`  
**How to Get:**
- Azure Portal → Your Translator Service → Keys and Endpoint → KEY 1 or KEY 2

---

#### `AZURE_TRANSLATOR_REGION`
**Description:** Azure Translator Service region  
**Format:** String (lowercase)  
**Example:** `eastus`, `global`  
**How to Get:**
- Azure Portal → Your Translator Service → Keys and Endpoint → Location/Region

---

#### `AZURE_OPENAI_API_KEY`
**Description:** Azure OpenAI Service API key  
**Format:** String (32 characters)  
**Example:** `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6`  
**How to Get:**
- Azure Portal → Your Azure OpenAI Service → Keys and Endpoint → KEY 1 or KEY 2

---

#### `AZURE_OPENAI_ENDPOINT`
**Description:** Azure OpenAI Service endpoint URL  
**Format:** URL (HTTPS)  
**Example:** `https://your-openai-service.openai.azure.com/`  
**How to Get:**
- Azure Portal → Your Azure OpenAI Service → Keys and Endpoint → Endpoint

---

#### `AZURE_OPENAI_DEPLOYMENT_NAME`
**Description:** Name of your Azure OpenAI model deployment  
**Format:** String  
**Example:** `gpt-4`, `gpt-35-turbo`  
**How to Get:**
- Azure Portal → Your Azure OpenAI Service → Model deployments → Deployment name

---

### 4️⃣ Frontend Configuration (1 secret)

#### `REACT_APP_API_URL`
**Description:** Backend API URL for frontend to connect to  
**Format:** URL (HTTPS, no trailing slash)  
**Example:** `https://backend-ai-powered-practice-questions.proudhill-12345678.eastus.azurecontainerapps.io`  
**How to Get:**
- After backend deployment, get from: Azure Portal → Your Container App → Overview → Application Url
- **OR** Wait for first backend deployment to complete and check the workflow output

---

## ✅ Quick Checklist

Use this checklist to track your progress:

- [ ] `AZURE_CREDENTIALS` (JSON with clientId, clientSecret, subscriptionId, tenantId)
- [ ] `AZURE_RESOURCE_GROUP`
- [ ] `AZURE_REGION`
- [ ] `ACR_NAME`
- [ ] `IMAGE_NAME`
- [ ] `CONTAINER_APP_NAME`
- [ ] `CONTAINER_APP_ENV`
- [ ] `AZURE_SPEECH_KEY`
- [ ] `AZURE_SPEECH_REGION`
- [ ] `AZURE_TRANSLATOR_KEY`
- [ ] `AZURE_TRANSLATOR_REGION`
- [ ] `AZURE_OPENAI_API_KEY`
- [ ] `AZURE_OPENAI_ENDPOINT`
- [ ] `AZURE_OPENAI_DEPLOYMENT_NAME`
- [ ] `REACT_APP_API_URL`

**Total: 15 secrets**

---

## 📝 Important Notes

### Service Principal Permissions
Your Azure Service Principal (AZURE_CREDENTIALS) needs the following permissions:
- **Contributor** role on the resource group containing Container App
- **AcrPush** role on the Azure Container Registry
- Access to read Container App Environment

### Azure AI Services Location
- Azure AI Services (OpenAI, Speech, Translator) can be in a **different resource group**
- The workflow doesn't access them directly - it only passes API keys to the Container App
- Your backend application code will use the API keys to connect to these services

### Security Best Practices
- ✅ All values should be added as **Secrets** (not Variables)
- ✅ Never commit these values to your repository
- ✅ Use Key 1 or Key 2 from Azure services (you can rotate them)
- ✅ Client secrets expire - set reminders to rotate them

---

## 🔄 Order of Operations

1. **Add secrets 1-7 first** (Authentication + Container Config)
2. **Run backend workflow** to deploy Container App
3. **Get the Container App URL** from deployment output
4. **Add secrets 8-14** (Azure AI Services)
5. **Add secret 15** (`REACT_APP_API_URL` using the URL from step 3)
6. **Run frontend workflow** to deploy frontend

---

## 📚 Related Documentation

- [GITHUB_SECRETS_GUIDE.md](./GITHUB_SECRETS_GUIDE.md) - Comprehensive guide with examples
- [SECRETS_QUICK_REFERENCE.md](./SECRETS_QUICK_REFERENCE.md) - Quick lookup table
- [DEPLOYMENT.md](./DEPLOYMENT.md) - Full deployment guide
- [PRE_DEPLOYMENT_CHECKLIST.md](./PRE_DEPLOYMENT_CHECKLIST.md) - Pre-deployment verification

---

## 🆘 Troubleshooting

### If backend deployment fails:
1. Verify `AZURE_CREDENTIALS` JSON is valid (use a JSON validator)
2. Check Service Principal has required permissions
3. Verify `AZURE_RESOURCE_GROUP` and `AZURE_REGION` are correct
4. Ensure Container App Environment exists in the resource group

### If frontend deployment fails:
1. Verify `REACT_APP_API_URL` is correct and accessible
2. Check backend is deployed and running
3. Ensure URL has HTTPS and no trailing slash

---

**Last Updated:** 7 October 2025  
**Environment Name:** `cert-practice-question-env`  
**Total Secrets Required:** 15
