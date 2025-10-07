# GitHub Secrets vs Environment Variables - What Goes Where?

## 🔐 TL;DR - Quick Answer

### **GitHub Secrets (Encrypted)** ✅
**ALL 11 items should be added as SECRETS**, not environment variables!

### **GitHub Environment Variables (Plain Text)** ❌
**NOTHING sensitive should go here!**

---

## 📚 Detailed Explanation

### What Are GitHub Secrets?
**Location**: Repository → Settings → Secrets and variables → Actions → **Secrets** tab

- ✅ **Encrypted** - Values are encrypted and never visible after saving
- ✅ **Secure** - Never exposed in logs (shown as `***`)
- ✅ **Required for** - Passwords, API keys, credentials, tokens, private URLs
- ✅ **Accessed in workflows** - `${{ secrets.SECRET_NAME }}`

### What Are GitHub Environment Variables?
**Location**: Repository → Settings → Secrets and variables → Actions → **Variables** tab

- ⚠️ **Plain text** - Values are stored in plain text
- ⚠️ **Visible** - Anyone with read access can see them
- ⚠️ **Not encrypted** - Shown in logs
- ✅ **Good for** - Non-sensitive configuration (app names, public URLs, feature flags)
- ✅ **Accessed in workflows** - `${{ vars.VARIABLE_NAME }}`

---

## 🎯 For Your Project

### ✅ Add as SECRETS (All sensitive data)

| Item | Type | Why Secret? |
|------|------|-------------|
| `AZURE_CREDENTIALS` | Secret | Contains client secret (password) |
| `AZURE_RESOURCE_GROUP` | Secret | Reveals infrastructure details |
| `AZURE_REGION` | Secret | Reveals infrastructure location |
| `AZURE_SPEECH_KEY` | Secret | API key (password equivalent) |
| `AZURE_SPEECH_REGION` | Secret | Service location info |
| `AZURE_TRANSLATOR_KEY` | Secret | API key (password equivalent) |
| `AZURE_TRANSLATOR_REGION` | Secret | Service location info |
| `AZURE_OPENAI_API_KEY` | Secret | API key (password equivalent) |
| `AZURE_OPENAI_ENDPOINT` | Secret | Private endpoint URL |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | Secret | Deployment configuration |
| `REACT_APP_API_URL` | Secret | Backend URL (could reveal infrastructure) |

### ❌ Add as VARIABLES (Non-sensitive, optional)

You *could* add these as variables if needed, but they're optional:

| Item | Type | Example | Purpose |
|------|------|---------|---------|
| `APP_NAME` | Variable | `ai-practice-questions` | Informational |
| `NODE_VERSION` | Variable | `18` | Build configuration |
| `ENVIRONMENT` | Variable | `production` | Environment label |
| `ENABLE_ANALYTICS` | Variable | `true` | Feature flag |

**Note**: For your project, you don't need any variables - everything sensitive goes in secrets!

---

## 🔍 Why Everything Should Be Secrets in Your Case

### 1. **API Keys** - Obviously Secret! ✅
```
AZURE_SPEECH_KEY
AZURE_TRANSLATOR_KEY
AZURE_OPENAI_API_KEY
```
**Why**: These are like passwords. Anyone with these can use (and abuse) your Azure services and rack up costs!

### 2. **AZURE_CREDENTIALS** - Obviously Secret! ✅
```json
{
  "clientId": "xxx",
  "clientSecret": "xxx",  ← This is a password!
  "subscriptionId": "xxx",
  "tenantId": "xxx"
}
```
**Why**: Contains client secret - literally a password to your Azure subscription!

### 3. **Resource Names and Regions** - Should Be Secret! ✅
```
AZURE_RESOURCE_GROUP
AZURE_REGION
AZURE_SPEECH_REGION
AZURE_TRANSLATOR_REGION
```
**Why**: Reveals your infrastructure setup. Attackers could:
- Scan your specific region for vulnerabilities
- Target your resource groups
- Understand your architecture
- Launch targeted attacks

### 4. **Endpoint URLs** - Should Be Secret! ✅
```
AZURE_OPENAI_ENDPOINT
REACT_APP_API_URL
```
**Why**: Private URLs shouldn't be public. Even though URLs will be visible in browser network requests, keeping them secret in GitHub:
- Prevents automated scanning
- Hides infrastructure from repository viewers
- Adds a layer of security by obscurity

### 5. **Deployment Names** - Should Be Secret! ✅
```
AZURE_OPENAI_DEPLOYMENT_NAME
```
**Why**: Reveals which AI models you're using and configuration details

---

## 📊 Comparison Table

| Feature | Secrets | Variables |
|---------|---------|-----------|
| **Encryption** | ✅ Yes, encrypted at rest | ❌ No, plain text |
| **Visibility in logs** | Hidden (shows as `***`) | Visible |
| **Who can see?** | Only admins | Anyone with read access |
| **Best for** | Passwords, keys, credentials | Public config, flags |
| **Your project needs** | All 11 items | Nothing (optional only) |

---

## 🎓 Real-World Example

### ❌ WRONG - Mixing Secrets and Variables
```yaml
# DON'T DO THIS!
env:
  API_KEY: ${{ vars.API_KEY }}  # ❌ API key as variable - INSECURE!
  APP_NAME: ${{ secrets.APP_NAME }}  # ❌ Non-sensitive as secret - overkill
```

### ✅ CORRECT - All Sensitive as Secrets
```yaml
# DO THIS!
env:
  API_KEY: ${{ secrets.API_KEY }}  # ✅ Sensitive data as secret
  RESOURCE_GROUP: ${{ secrets.AZURE_RESOURCE_GROUP }}  # ✅ Infrastructure info as secret
```

---

## 🛡️ Security Best Practice

**When in doubt, use Secrets!**

It's better to be overly cautious:
- ✅ Secret that's not super sensitive → No harm done, just extra security
- ❌ Variable that should be secret → **SECURITY BREACH!**

---

## 📝 Your Setup Instructions

### Step 1: Add ALL as Secrets
Go to: https://github.com/imohweb/AI-Powered-certifications-exams-practice-questions/settings/secrets/actions

Click "New repository secret" and add:

```
✅ AZURE_CREDENTIALS (Secret)
✅ AZURE_RESOURCE_GROUP (Secret)
✅ AZURE_REGION (Secret)
✅ AZURE_SPEECH_KEY (Secret)
✅ AZURE_SPEECH_REGION (Secret)
✅ AZURE_TRANSLATOR_KEY (Secret)
✅ AZURE_TRANSLATOR_REGION (Secret)
✅ AZURE_OPENAI_API_KEY (Secret)
✅ AZURE_OPENAI_ENDPOINT (Secret)
✅ AZURE_OPENAI_DEPLOYMENT_NAME (Secret)
✅ REACT_APP_API_URL (Secret - add after backend deployment)
```

### Step 2: Don't Add Anything as Variables
Unless you have non-sensitive configuration, leave the Variables tab empty.

---

## 🔐 How They're Used in Your Workflows

### Backend Workflow (deploy-backend.yml)
```yaml
- name: Log in to Azure
  uses: azure/login@v1
  with:
    creds: ${{ secrets.AZURE_CREDENTIALS }}  # ← SECRET

- name: Create Container App
  run: |
    az containerapp create \
      --name backend-ai-powered-practice-questions \
      --resource-group ${{ secrets.AZURE_RESOURCE_GROUP }} \  # ← SECRET
      --secrets \
        azure-speech-key=${{ secrets.AZURE_SPEECH_KEY }} \    # ← SECRET
        # All others are also SECRETS
```

### Frontend Workflow (deploy-frontend.yml)
```yaml
- name: Create .env file
  run: |
    echo "REACT_APP_API_URL=${{ secrets.REACT_APP_API_URL }}" > .env  # ← SECRET
```

---

## 🎯 Summary

### For Your Project:

| What | Where | Count |
|------|-------|-------|
| **Secrets** | Settings → Secrets → Repository secrets | **11 items** |
| **Variables** | Settings → Variables → Repository variables | **0 items** |

### The Rule:
```
If it's sensitive, private, or reveals infrastructure → SECRET ✅
If it's public, non-sensitive configuration → VARIABLE ✅
When in doubt → SECRET ✅
```

---

## ⚠️ Common Misconceptions

### Myth 1: "Only passwords should be secrets"
**FALSE!** ❌
- API keys → Secret
- Endpoint URLs → Secret
- Resource names → Secret
- Region info → Secret
- Anything that reveals infrastructure → Secret

### Myth 2: "Variables are just for organization"
**FALSE!** ❌
- Variables are for **non-sensitive** configuration only
- Variables are **plain text** and **visible** to all
- Variables should **never** contain sensitive data

### Myth 3: "Backend URL can be a variable since it's public"
**MISLEADING!** ⚠️
- Yes, frontend will expose it in network requests
- BUT keeping it secret in GitHub prevents:
  - Repository scanners from finding it
  - Attackers from easily mapping your infrastructure
  - Automated attacks targeting your specific setup
- Use Secret for defense in depth!

---

## 📞 Quick Decision Tree

```
Is this data:
├─ A password/key/token? → SECRET ✅
├─ A URL/endpoint? → SECRET ✅
├─ A resource name? → SECRET ✅
├─ A region/location? → SECRET ✅
├─ Part of credentials? → SECRET ✅
├─ Infrastructure info? → SECRET ✅
└─ Just a public label/flag? → VARIABLE (or nothing)
```

---

## ✅ Final Answer for Your Project

**Add ALL 11 items as SECRETS**
**Add NOTHING as VARIABLES**

That's it! Simple and secure! 🔐

---

**See also**:
- [GITHUB_SECRETS_GUIDE.md](GITHUB_SECRETS_GUIDE.md) - How to get secret values
- [SECRETS_QUICK_REFERENCE.md](SECRETS_QUICK_REFERENCE.md) - Quick lookup table
- [SECRETS_VISUAL_GUIDE.md](SECRETS_VISUAL_GUIDE.md) - Visual diagrams
