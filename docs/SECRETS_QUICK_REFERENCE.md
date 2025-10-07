# GitHub Secrets Quick Reference

## 📍 Location
**Repository** → **Settings** → **Secrets and variables** → **Actions** → **Repository secrets**

---

## 🔐 11 Required Secrets

| # | Secret Name | Example Value | Where to Get It |
|---|-------------|---------------|-----------------|
| 1 | `AZURE_CREDENTIALS` | `{"clientId":"xxx",...}` | `az ad sp create-for-rbac --sdk-auth` |
| 2 | `AZURE_RESOURCE_GROUP` | `rg-ai-practice` | Your Azure resource group name |
| 3 | `AZURE_REGION` | `eastus` | Azure region (e.g., eastus, westeurope) |
| 4 | `AZURE_SPEECH_KEY` | `a1b2c3d4...` | Speech Service → Keys and Endpoint |
| 5 | `AZURE_SPEECH_REGION` | `northeurope` | Speech Service → Location |
| 6 | `AZURE_TRANSLATOR_KEY` | `x1y2z3a4...` | Translator → Keys and Endpoint |
| 7 | `AZURE_TRANSLATOR_REGION` | `northeurope` | Translator → Location |
| 8 | `AZURE_OPENAI_API_KEY` | `abc123def...` | OpenAI → Keys and Endpoint |
| 9 | `AZURE_OPENAI_ENDPOINT` | `https://xxx.openai.azure.com/` | OpenAI → Endpoint URL |
| 10 | `AZURE_OPENAI_DEPLOYMENT_NAME` | `gpt-4` | OpenAI Studio → Deployment name |
| 11 | `REACT_APP_API_URL` | `https://backend-xxx.azurecontainerapps.io` | Get after backend deploys |

---

## 🎯 Purpose of Each Secret

### Azure Infrastructure (Used by GitHub Actions to deploy)
- **AZURE_CREDENTIALS**: Login to Azure
- **AZURE_RESOURCE_GROUP**: Where to deploy
- **AZURE_REGION**: Which region to use

### Azure Services (Used by Backend Application)
- **AZURE_SPEECH_KEY + AZURE_SPEECH_REGION**: Generate audio
- **AZURE_TRANSLATOR_KEY + AZURE_TRANSLATOR_REGION**: Translate questions
- **AZURE_OPENAI_API_KEY + AZURE_OPENAI_ENDPOINT + AZURE_OPENAI_DEPLOYMENT_NAME**: Generate questions

### Frontend Configuration
- **REACT_APP_API_URL**: Connect frontend to backend

---

## ⚡ Quick Setup Commands

### 1. Create Service Principal (for AZURE_CREDENTIALS)
```bash
az ad sp create-for-rbac \
  --name "github-actions-ai-practice-questions" \
  --role contributor \
  --scopes /subscriptions/{subscription-id}/resourceGroups/{resource-group} \
  --sdk-auth
```
Copy entire JSON output → Add as `AZURE_CREDENTIALS`

### 2. Get Speech Service Key
```bash
az cognitiveservices account keys list \
  --name {your-speech-service-name} \
  --resource-group {your-resource-group}
```
Copy Key 1 → Add as `AZURE_SPEECH_KEY`

### 3. Get Translator Key
```bash
az cognitiveservices account keys list \
  --name {your-translator-service-name} \
  --resource-group {your-resource-group}
```
Copy Key 1 → Add as `AZURE_TRANSLATOR_KEY`

### 4. Get OpenAI Key
```bash
az cognitiveservices account keys list \
  --name {your-openai-service-name} \
  --resource-group {your-resource-group}
```
Copy Key 1 → Add as `AZURE_OPENAI_API_KEY`

### 5. Get Backend URL (AFTER backend deployment)
```bash
az containerapp show \
  --name backend-ai-powered-practice-questions \
  --resource-group {your-resource-group} \
  --query properties.configuration.ingress.fqdn \
  --output tsv
```
Add `https://` prefix → Add as `REACT_APP_API_URL`

---

## ✅ Verification Checklist

After adding all secrets, you should see this in GitHub:

```
Secrets (11)
├── AZURE_CREDENTIALS              ✅
├── AZURE_RESOURCE_GROUP           ✅
├── AZURE_REGION                   ✅
├── AZURE_SPEECH_KEY               ✅
├── AZURE_SPEECH_REGION            ✅
├── AZURE_TRANSLATOR_KEY           ✅
├── AZURE_TRANSLATOR_REGION        ✅
├── AZURE_OPENAI_API_KEY           ✅
├── AZURE_OPENAI_ENDPOINT          ✅
├── AZURE_OPENAI_DEPLOYMENT_NAME   ✅
└── REACT_APP_API_URL              ✅ (after backend deployment)
```

---

## 🚨 Common Mistakes to Avoid

❌ **Wrong secret name** (case-sensitive!)
- `azure_credentials` ← Wrong
- `AZURE_CREDENTIALS` ← Correct

❌ **Missing https:// prefix**
- `backend-xxx.azurecontainerapps.io` ← Wrong for REACT_APP_API_URL
- `https://backend-xxx.azurecontainerapps.io` ← Correct

❌ **Wrong JSON format for AZURE_CREDENTIALS**
- Must be complete JSON from `az ad sp create-for-rbac --sdk-auth`
- Don't modify or format the JSON

❌ **Trailing spaces or newlines in secrets**
- Copy values carefully
- No extra whitespace

---

## 📚 Detailed Guide

For complete information, see: [GITHUB_SECRETS_GUIDE.md](GITHUB_SECRETS_GUIDE.md)

---

**Quick Access**: https://github.com/imohweb/AI-Powered-certifications-exams-practice-questions/settings/secrets/actions
