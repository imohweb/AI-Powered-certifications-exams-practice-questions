# GitHub Pages Deployment Fix

## Problem
The frontend deployed to GitHub Pages at `https://imohweb.github.io/AI-Powered-certifications-exams-practice-questions/` is unable to connect to the backend API, resulting in errors:
- "Assessment not found. Please check the certification code and try again."
- "Failed to load assessment: Network Error"

## Root Cause
The frontend is trying to connect to the backend API, but the API URL is not properly configured during the build process. The GitHub Actions workflow needs the backend Container App URL to be available as a secret.

## Solution

### Step 1: Get the Backend Container App URL

The backend is deployed to Azure Container Apps with the name `backend-ai-practice-questions`. You need to get its full URL.

Run this command in your terminal (after logging into Azure CLI):

```bash
az containerapp show \
  --name backend-ai-practice-questions \
  --resource-group <YOUR_RESOURCE_GROUP_NAME> \
  --query properties.configuration.ingress.fqdn \
  --output tsv
```

This will output something like:
```
backend-ai-practice-questions.eastus.azurecontainerapps.io
```

The full URL would be: `https://backend-ai-practice-questions.eastus.azurecontainerapps.io`

### Step 2: Configure GitHub Secrets

You have two options for configuring the backend URL:

#### Option A: Use BACKEND_CONTAINER_APP_URL (Recommended)

Add a new GitHub secret with the complete backend URL:

1. Go to your GitHub repository
2. Click on **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `BACKEND_CONTAINER_APP_URL`
5. Value: `https://backend-ai-practice-questions.<region>.azurecontainerapps.io` (use the URL from Step 1)
6. Click **Add secret**

#### Option B: Ensure CONTAINER_APP_NAME and AZURE_REGION are set

If you already have these secrets configured:
- `CONTAINER_APP_NAME` = `backend-ai-practice-questions`
- `AZURE_REGION` = Your Azure region (e.g., `eastus`, `westus2`, etc.)

The workflow will automatically construct the URL.

### Step 3: Verify CORS Configuration

The backend must allow requests from your GitHub Pages URL. Check that the backend deployment includes:

```
CORS_ORIGINS="https://imohweb.github.io/AI-Powered-certifications-exams-practice-questions"
```

This is already configured in the `.github/workflows/deploy-backend.yml` file.

### Step 4: Redeploy the Frontend

After configuring the secrets, trigger a frontend redeployment:

1. Go to **Actions** tab in GitHub
2. Select the "Deploy Frontend to GitHub Pages" workflow
3. Click **Run workflow** → **Run workflow**

Or simply push a commit to the `frontend/` directory or the workflow file.

### Step 5: Verify the Deployment

After the deployment completes:

1. Check the workflow logs to see the API URL being used:
   - Look for the line: `Frontend will connect to: https://...`

2. Visit your GitHub Pages site: `https://imohweb.github.io/AI-Powered-certifications-exams-practice-questions/`

3. Open browser Developer Tools (F12) → Console tab

4. Try to load an assessment and check for:
   - The API request URL being called
   - Any CORS errors
   - Network responses

### Expected Behavior After Fix

When the frontend is properly configured:
1. The API requests will go to: `https://backend-ai-practice-questions.<region>.azurecontainerapps.io/api/v1/...`
2. No CORS errors should appear
3. Assessments should load successfully

## Updated Frontend Workflow

The `.github/workflows/deploy-frontend.yml` has been updated to:

1. Check for `BACKEND_CONTAINER_APP_URL` secret first
2. Fall back to constructing URL from `CONTAINER_APP_NAME` and `AZURE_REGION`
3. Create a `.env` file with `REACT_APP_API_URL` during build
4. Log the API URL for debugging

## Troubleshooting

### Issue: Still getting "Network Error"

**Check 1: Verify the backend is running**
```bash
curl https://backend-ai-practice-questions.<region>.azurecontainerapps.io/api/v1/assessments/certifications
```

You should get a JSON response with certification data.

**Check 2: Check for CORS errors in browser console**
- If you see "CORS policy" errors, the backend needs to be redeployed with proper CORS configuration
- Redeploy the backend by triggering the backend workflow or pushing to `backend/` directory

**Check 3: Verify the API URL in the built frontend**
- The API URL is embedded during build time in the static JavaScript files
- Check the workflow logs to confirm the correct URL was used during build

### Issue: "Failed to fetch"

This usually means:
1. The backend URL is incorrect
2. The backend Container App is not running
3. The backend ingress is not configured for external access

Verify the backend Container App settings:
```bash
az containerapp show \
  --name backend-ai-practice-questions \
  --resource-group <YOUR_RESOURCE_GROUP_NAME> \
  --query properties.configuration.ingress
```

Ensure `external: true` is set.

## Alternative: Deploy to Azure Static Web Apps

If GitHub Pages continues to have issues, you can deploy the frontend to Azure Static Web Apps instead. This would provide:
- Better integration with Azure services
- Built-in staging environments
- Custom domains
- More control over routing

Let me know if you'd like me to set this up instead.

## Summary

The fix involves:
1. ✅ Frontend workflow updated to properly construct backend API URL
2. ⏳ Configure `BACKEND_CONTAINER_APP_URL` secret in GitHub (or ensure `CONTAINER_APP_NAME` and `AZURE_REGION` are set)
3. ⏳ Redeploy frontend to GitHub Pages
4. ✅ Backend CORS already configured correctly

After Step 2 and 3 are completed, the application should work correctly.
