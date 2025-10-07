# Visual Guide: GitHub Secrets Flow

## 🎯 Overview: Where Secrets Go

```
┌─────────────────────────────────────────────────────────────────┐
│                    GitHub Repository                             │
│     imohweb/AI-Powered-certifications-exams-practice-questions  │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │            GitHub Secrets (Settings)                    │    │
│  │  Encrypted storage for sensitive configuration          │    │
│  └────────────────────────────────────────────────────────┘    │
│                          │                                       │
│           ┌──────────────┴──────────────┐                       │
│           ▼                              ▼                       │
│  ┌──────────────────┐          ┌──────────────────┐           │
│  │  Backend Workflow│          │ Frontend Workflow │           │
│  │   (deploy-       │          │   (deploy-        │           │
│  │    backend.yml)  │          │    frontend.yml)  │           │
│  └──────────────────┘          └──────────────────┘           │
└─────────────────────────────────────────────────────────────────┘
           │                              │
           ▼                              ▼
┌────────────────────┐          ┌──────────────────┐
│  Azure Container   │          │  GitHub Pages    │
│      Apps          │          │   (Frontend)     │
│   (Backend API)    │          │                  │
└────────────────────┘          └──────────────────┘
```

---

## 📋 Secrets Breakdown by Purpose

### Group 1: Azure Infrastructure (Deploy Resources)
Used by GitHub Actions to login and deploy to Azure

```
┌─────────────────────────────────────────────────┐
│  AZURE_CREDENTIALS                              │  ← Service Principal JSON
│  AZURE_RESOURCE_GROUP                           │  ← Where to deploy
│  AZURE_REGION                                   │  ← Which region
└─────────────────────────────────────────────────┘
                    │
                    ▼
         Used by: GitHub Actions workflows
         Purpose: Deploy to Azure
```

### Group 2: Azure Speech Service (Text-to-Speech)
Used by backend application to generate audio

```
┌─────────────────────────────────────────────────┐
│  AZURE_SPEECH_KEY                               │  ← API Key
│  AZURE_SPEECH_REGION                            │  ← Service location
└─────────────────────────────────────────────────┘
                    │
                    ▼
         Injected into: Container App as environment variable
         Used by: Backend app (azure_speech.py)
         Purpose: Generate speech audio
```

### Group 3: Azure Translator (Language Translation)
Used by backend application to translate questions

```
┌─────────────────────────────────────────────────┐
│  AZURE_TRANSLATOR_KEY                           │  ← API Key
│  AZURE_TRANSLATOR_REGION                        │  ← Service location
└─────────────────────────────────────────────────┘
                    │
                    ▼
         Injected into: Container App as environment variable
         Used by: Backend app (azure_translator.py)
         Purpose: Translate text to other languages
```

### Group 4: Azure OpenAI (AI Question Generation)
Used by backend application to generate practice questions

```
┌─────────────────────────────────────────────────┐
│  AZURE_OPENAI_API_KEY                           │  ← API Key
│  AZURE_OPENAI_ENDPOINT                          │  ← Service URL
│  AZURE_OPENAI_DEPLOYMENT_NAME                   │  ← Model name
└─────────────────────────────────────────────────┘
                    │
                    ▼
         Injected into: Container App as environment variable
         Used by: Backend app (ai_question_generator.py)
         Purpose: Generate AI practice questions
```

### Group 5: Frontend Configuration (Connect to Backend)
Used by frontend to communicate with backend API

```
┌─────────────────────────────────────────────────┐
│  REACT_APP_API_URL                              │  ← Backend URL
└─────────────────────────────────────────────────┘
                    │
                    ▼
         Injected into: Frontend .env file during build
         Used by: React app (axios API calls)
         Purpose: Connect to backend API
```

---

## 🔄 Deployment Flow with Secrets

### Backend Deployment

```
1. Developer pushes code to main branch
         │
         ▼
2. GitHub Actions workflow triggered
         │
         ▼
3. Workflow reads secrets:
   ├── AZURE_CREDENTIALS → Login to Azure
   ├── AZURE_RESOURCE_GROUP → Target resource group
   └── AZURE_REGION → Target region
         │
         ▼
4. Build Docker image
         │
         ▼
5. Push to Azure Container Registry
         │
         ▼
6. Create/Update Container App with secrets:
   ├── AZURE_SPEECH_KEY → Env var: AZURE_SPEECH_KEY
   ├── AZURE_SPEECH_REGION → Env var: AZURE_SPEECH_REGION
   ├── AZURE_TRANSLATOR_KEY → Env var: AZURE_TRANSLATOR_KEY
   ├── AZURE_TRANSLATOR_REGION → Env var: AZURE_TRANSLATOR_REGION
   ├── AZURE_OPENAI_API_KEY → Env var: AZURE_OPENAI_API_KEY
   ├── AZURE_OPENAI_ENDPOINT → Env var: AZURE_OPENAI_ENDPOINT
   └── AZURE_OPENAI_DEPLOYMENT_NAME → Env var: AZURE_OPENAI_DEPLOYMENT_NAME
         │
         ▼
7. Backend API running with all secrets as environment variables
```

### Frontend Deployment

```
1. Developer pushes code to main branch
         │
         ▼
2. GitHub Actions workflow triggered
         │
         ▼
3. Workflow reads secrets:
   └── REACT_APP_API_URL → Backend API URL
         │
         ▼
4. Create .env file:
   REACT_APP_API_URL=https://backend-xxx.azurecontainerapps.io
         │
         ▼
5. Build React app (includes env vars in bundle)
         │
         ▼
6. Deploy to GitHub Pages
         │
         ▼
7. Frontend can now call backend API
```

---

## 🔍 Secret Usage in Code

### How Backend Receives Secrets

```python
# backend/app/core/config.py

import os

class Settings(BaseSettings):
    # These are read from environment variables
    # which are injected by GitHub Actions during deployment
    
    AZURE_SPEECH_KEY: str = os.getenv("AZURE_SPEECH_KEY")
    AZURE_SPEECH_REGION: str = os.getenv("AZURE_SPEECH_REGION")
    AZURE_TRANSLATOR_KEY: str = os.getenv("AZURE_TRANSLATOR_KEY")
    AZURE_TRANSLATOR_REGION: str = os.getenv("AZURE_TRANSLATOR_REGION")
    AZURE_OPENAI_API_KEY: str = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_DEPLOYMENT_NAME: str = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

# GitHub Actions injects these during deployment:
# az containerapp create --secrets \
#   azure-speech-key=${{ secrets.AZURE_SPEECH_KEY }} \
#   azure-speech-region=${{ secrets.AZURE_SPEECH_REGION }}
```

### How Frontend Receives Secrets

```javascript
// frontend/src/services/api.ts

// During build, REACT_APP_API_URL is baked into the bundle
const API_BASE_URL = process.env.REACT_APP_API_URL;

// GitHub Actions creates .env file before build:
// echo "REACT_APP_API_URL=${{ secrets.REACT_APP_API_URL }}" > .env
```

---

## 📊 Summary Table

| Secret | Used By | When | How Accessed |
|--------|---------|------|--------------|
| AZURE_CREDENTIALS | GitHub Actions | Deploy time | Workflow login step |
| AZURE_RESOURCE_GROUP | GitHub Actions | Deploy time | Deployment target |
| AZURE_REGION | GitHub Actions | Deploy time | Deployment location |
| AZURE_SPEECH_KEY | Backend App | Runtime | Environment variable |
| AZURE_SPEECH_REGION | Backend App | Runtime | Environment variable |
| AZURE_TRANSLATOR_KEY | Backend App | Runtime | Environment variable |
| AZURE_TRANSLATOR_REGION | Backend App | Runtime | Environment variable |
| AZURE_OPENAI_API_KEY | Backend App | Runtime | Environment variable |
| AZURE_OPENAI_ENDPOINT | Backend App | Runtime | Environment variable |
| AZURE_OPENAI_DEPLOYMENT_NAME | Backend App | Runtime | Environment variable |
| REACT_APP_API_URL | Frontend App | Build time | Baked into bundle |

---

## ⚠️ Security Best Practices

### ✅ DO:
```
✓ Store ALL sensitive data in GitHub Secrets
✓ Use service principals with minimal permissions
✓ Rotate secrets regularly
✓ Use different secrets for dev/staging/production
✓ Review who has access to secrets
```

### ❌ DON'T:
```
✗ Commit secrets to code
✗ Share secrets in chat/email
✗ Print secrets in logs
✗ Use production secrets in development
✗ Give service principals more permissions than needed
```

---

## 🎓 Understanding the Flow

Think of GitHub Secrets like this:

```
You have a safe (GitHub Secrets) 🔐
  │
  ├─ Some keys open Azure (AZURE_CREDENTIALS)
  ├─ Some keys open Azure services (API keys)
  └─ Some tell where to find things (URLs, regions)

When you deploy:
  1. GitHub Actions uses keys to open Azure
  2. Creates a container for your backend
  3. Gives backend the Azure service keys
  4. Backend uses those keys to call Azure services
  5. Frontend knows where to find backend (REACT_APP_API_URL)

Everything stays secure! 🛡️
```

---

## 📞 Quick Help

**"I can't find where to add secrets"**
→ Repository Settings → Secrets and variables → Actions

**"Where do I get AZURE_CREDENTIALS?"**
→ Run: `az ad sp create-for-rbac --sdk-auth`

**"Where do I get API keys?"**
→ Azure Portal → Your service → Keys and Endpoint

**"When do I add REACT_APP_API_URL?"**
→ AFTER backend is deployed, get URL with:
   `az containerapp show --name backend-ai-powered-practice-questions --query properties.configuration.ingress.fqdn`

---

**Need more details?** See [GITHUB_SECRETS_GUIDE.md](GITHUB_SECRETS_GUIDE.md)
