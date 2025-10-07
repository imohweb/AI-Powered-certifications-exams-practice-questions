# Pre-Deployment Checklist

Complete this checklist before deploying to production.

## ☑️ Azure Resources

- [ ] Azure Container Registry `iacstudioregistry` exists and accessible
- [ ] Container App Environment `iac-studio-env` exists and accessible
- [ ] Resource Group created and accessible
- [ ] Azure Speech Service configured and API keys obtained
- [ ] Azure Translator Service configured and API keys obtained
- [ ] Azure OpenAI Service configured and deployment created
- [ ] Service Principal created with appropriate permissions

## ☑️ GitHub Repository Setup

- [ ] Repository is accessible at `https://github.com/imohweb/AI-Powered-certifications-exams-practice-questions`
- [ ] You have admin access to the repository
- [ ] `main` branch exists
- [ ] `develop` branch exists

## ☑️ GitHub Secrets Configuration

Navigate to **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

### Azure Infrastructure Secrets
- [ ] `AZURE_CREDENTIALS` - Service principal JSON (from `az ad sp create-for-rbac`)
- [ ] `AZURE_RESOURCE_GROUP` - Your resource group name
- [ ] `AZURE_REGION` - Azure region (e.g., `eastus`, `westeurope`)

### Azure Service Secrets
- [ ] `AZURE_SPEECH_KEY` - Speech Service API key
- [ ] `AZURE_SPEECH_REGION` - Speech Service region
- [ ] `AZURE_TRANSLATOR_KEY` - Translator Service API key
- [ ] `AZURE_TRANSLATOR_REGION` - Translator Service region
- [ ] `AZURE_OPENAI_API_KEY` - OpenAI API key
- [ ] `AZURE_OPENAI_ENDPOINT` - OpenAI endpoint URL
- [ ] `AZURE_OPENAI_DEPLOYMENT_NAME` - OpenAI deployment name

### Frontend Secret (Add after backend deployment)
- [ ] `REACT_APP_API_URL` - Backend API URL (e.g., `https://backend-ai-powered-practice-questions.{region}.azurecontainerapps.io`)

## ☑️ Branch Protection

Navigate to **Settings** → **Branches** → **Add branch protection rule**

### Main Branch Protection
- [ ] Branch name pattern: `main`
- [ ] Require a pull request before merging
- [ ] Require approvals (at least 1)
- [ ] Require status checks to pass before merging
- [ ] Require branches to be up to date before merging
- [ ] Do not allow bypassing the above settings
- [ ] Restrict who can push to matching branches
- [ ] Do not allow force pushes
- [ ] Do not allow deletions

### Develop Branch Protection
- [ ] Branch name pattern: `develop`
- [ ] Same settings as main branch

## ☑️ GitHub Pages Setup

Navigate to **Settings** → **Pages**

- [ ] Source is set to **GitHub Actions**
- [ ] Custom domain (optional): configured if needed

## ☑️ Local Development Tested

- [ ] Backend runs locally without errors
- [ ] Frontend runs locally without errors
- [ ] API calls work correctly
- [ ] Voice features work correctly
- [ ] All tests pass
- [ ] No console errors

## ☑️ Code Review

- [ ] All code committed and pushed
- [ ] No sensitive data in code (keys, passwords, etc.)
- [ ] `.env` files are in `.gitignore`
- [ ] Docker files are correct
- [ ] GitHub Actions workflows are correct
- [ ] Documentation is up to date

## ☑️ Deployment Files

- [ ] `backend/Dockerfile` exists and is correct
- [ ] `backend/.dockerignore` exists and is correct
- [ ] `.github/workflows/deploy-backend.yml` exists and is correct
- [ ] `.github/workflows/deploy-frontend.yml` exists and is correct
- [ ] `frontend/package.json` has correct `homepage` field

## ☑️ Documentation

- [ ] `README.md` updated with deployment information
- [ ] `docs/DEPLOYMENT.md` reviewed
- [ ] `docs/QUICK_DEPLOY.md` reviewed
- [ ] `docs/DEPLOYMENT_SETUP_SUMMARY.md` reviewed

## 🚀 Ready to Deploy

Once all checkboxes are marked:

### Step 1: Deploy Backend
```bash
git add .
git commit -m "feat: Ready for deployment"
git push origin main
```

Monitor deployment at: **Actions** tab → **Deploy Backend to Azure Container Apps**

### Step 2: Get Backend URL
```bash
az containerapp show \
  --name backend-ai-powered-practice-questions \
  --resource-group {your-resource-group} \
  --query properties.configuration.ingress.fqdn \
  --output tsv
```

### Step 3: Add Backend URL Secret
Add `REACT_APP_API_URL` to GitHub Secrets with value: `https://{backend-fqdn}`

### Step 4: Deploy Frontend
```bash
git push origin main
```

Monitor deployment at: **Actions** tab → **Deploy Frontend to GitHub Pages**

### Step 5: Verify
- Backend Health: `https://{backend-fqdn}/health`
- Backend API: `https://{backend-fqdn}/api/v1/certifications`
- Frontend: `https://imohweb.github.io/AI-Powered-certifications-exams-practice-questions/`

## 📞 Support

If you encounter issues:
1. Check GitHub Actions logs
2. Review `docs/DEPLOYMENT.md`
3. Check Azure Container App logs
4. Open an issue on GitHub

---

**Date**: ____________

**Completed by**: ____________

**Deployment Status**: [ ] Ready  [ ] In Progress  [ ] Complete
