# 🎯 Simple Answer: Secrets vs Variables

## Your Question Answered

**Q: What should be added as Secret vs Environment Variable on GitHub?**

**A: Everything goes in SECRETS! Nothing in Variables!**

---

## Visual Guide

```
┌─────────────────────────────────────────────────────────────┐
│              GitHub Repository Settings                      │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Secrets and variables → Actions                    │    │
│  │                                                      │    │
│  │  ┌─────────────┐         ┌─────────────────┐      │    │
│  │  │   Secrets   │         │    Variables     │      │    │
│  │  │  (Encrypted)│         │  (Plain Text)    │      │    │
│  │  └─────────────┘         └─────────────────┘      │    │
│  │        │                          │                 │    │
│  │        │                          │                 │    │
│  │    ADD HERE! ✅               LEAVE EMPTY ⭕        │    │
│  │        │                          │                 │    │
│  │   All 11 items:                  Nothing!          │    │
│  │   • AZURE_CREDENTIALS            (Optional use)    │    │
│  │   • AZURE_RESOURCE_GROUP                           │    │
│  │   • AZURE_REGION                                   │    │
│  │   • AZURE_SPEECH_KEY                               │    │
│  │   • AZURE_SPEECH_REGION                            │    │
│  │   • AZURE_TRANSLATOR_KEY                           │    │
│  │   • AZURE_TRANSLATOR_REGION                        │    │
│  │   • AZURE_OPENAI_API_KEY                           │    │
│  │   • AZURE_OPENAI_ENDPOINT                          │    │
│  │   • AZURE_OPENAI_DEPLOYMENT_NAME                   │    │
│  │   • REACT_APP_API_URL                              │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## Quick Comparison

| Aspect | Secrets ✅ | Variables ❌ |
|--------|-----------|-------------|
| **What is it?** | Encrypted storage | Plain text storage |
| **Visible in logs?** | No (shows as ***) | Yes (visible) |
| **Who can see?** | Only admins | Anyone with read access |
| **For your project** | **USE THIS!** | Don't use |
| **What to add** | All 11 items | Nothing |

---

## Why All as Secrets?

### 🔴 These are OBVIOUSLY secrets:
- ✅ `AZURE_SPEECH_KEY` - It's called a "KEY"!
- ✅ `AZURE_TRANSLATOR_KEY` - It's called a "KEY"!
- ✅ `AZURE_OPENAI_API_KEY` - It's called a "KEY"!
- ✅ `AZURE_CREDENTIALS` - Contains passwords!

### 🟡 These should ALSO be secrets:
- ✅ `AZURE_RESOURCE_GROUP` - Reveals your infrastructure
- ✅ `AZURE_REGION` - Reveals where your stuff is
- ✅ `AZURE_OPENAI_ENDPOINT` - Your private URL
- ✅ `AZURE_OPENAI_DEPLOYMENT_NAME` - Your config details
- ✅ `REACT_APP_API_URL` - Your backend location

**Rule**: When in doubt → Secret! ✅

---

## What Would Go in Variables? (Not for your project)

Variables are for **public, non-sensitive** config like:

```yaml
# Examples of what COULD go in Variables (but you don't need any!)
APP_NAME: "My Cool App"          # Just a label
NODE_VERSION: "18"                # Public info
ENABLE_DEBUG: "false"             # Feature flag
PUBLIC_URL: "https://example.com" # Already public
```

**For YOUR project**: You don't need variables at all! ✅

---

## Step-by-Step Setup

### 1. Go to Secrets
```
https://github.com/imohweb/AI-Powered-certifications-exams-practice-questions/settings/secrets/actions
```

### 2. Click "New repository secret"

### 3. Add each item as a SECRET (not variable):
```
Name: AZURE_CREDENTIALS
Value: {your JSON from az ad sp create-for-rbac}
[Add secret]

Name: AZURE_RESOURCE_GROUP
Value: your-resource-group-name
[Add secret]

Name: AZURE_REGION
Value: eastus (or your region)
[Add secret]

... repeat for all 11 items
```

### 4. Skip the Variables tab completely! ⭕

---

## Final Checklist

After setup, you should see:

```
✅ Secrets (11)
   ├── AZURE_CREDENTIALS
   ├── AZURE_RESOURCE_GROUP
   ├── AZURE_REGION
   ├── AZURE_SPEECH_KEY
   ├── AZURE_SPEECH_REGION
   ├── AZURE_TRANSLATOR_KEY
   ├── AZURE_TRANSLATOR_REGION
   ├── AZURE_OPENAI_API_KEY
   ├── AZURE_OPENAI_ENDPOINT
   ├── AZURE_OPENAI_DEPLOYMENT_NAME
   └── REACT_APP_API_URL

⭕ Variables (0)
   (Empty - that's correct!)
```

---

## 🎓 Remember

```
🔐 Secrets = Encrypted, Hidden, Secure → USE THESE! ✅
📝 Variables = Plain Text, Visible, Public → DON'T USE ❌
```

**For your project: 11 Secrets, 0 Variables**

That's it! Keep it simple! 🚀

---

**Detailed guide**: [SECRETS_VS_VARIABLES.md](SECRETS_VS_VARIABLES.md)
