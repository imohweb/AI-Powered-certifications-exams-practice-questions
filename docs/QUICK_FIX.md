# Quick Fix: Configure Backend URL Secret

## The Problem
Your frontend deployment is failing to connect to the backend because it doesn't know the backend URL.

## The Solution (2 minutes)

### Option 1: Add BACKEND_CONTAINER_APP_URL Secret (Recommended)

1. **Get your backend URL:**
   ```bash
   az containerapp show \
     --name backend-ai-practice-questions \
     --resource-group <YOUR_RESOURCE_GROUP_NAME> \
     --query properties.configuration.ingress.fqdn \
     --output tsv
   ```
   
   This outputs something like: `backend-ai-practice-questions.eastus.azurecontainerapps.io`

2. **Add the secret to GitHub:**
   - Go to: `https://github.com/imohweb/certifications-exams-practice-questions/settings/secrets/actions`
   - Click: **New repository secret**
   - Name: `BACKEND_CONTAINER_APP_URL`
   - Value: `https://backend-ai-practice-questions.<region>.azurecontainerapps.io` (use the actual URL from step 1 with `https://` prefix)
   - Click: **Add secret**

3. **Redeploy the frontend:**
   - Go to: `https://github.com/imohweb/certifications-exams-practice-questions/actions`
   - Click: **Deploy Frontend to GitHub Pages** workflow
   - Click: **Run workflow** → **Run workflow**

### Option 2: Use Existing Secrets

If you already have these secrets configured:
- `CONTAINER_APP_NAME` (should be: `backend-ai-practice-questions`)
- `AZURE_REGION` (e.g., `eastus`, `westus2`, etc.)

Then just redeploy the frontend - the workflow will construct the URL automatically.

## Verify It Worked

After the workflow completes:

1. Check the **workflow summary** - it will show the backend API URL being used
2. Visit: `https://imohweb.github.io/AI-Powered-certifications-exams-practice-questions/`
3. The application should now load correctly

## Still Having Issues?

Run this test to verify your backend is accessible:

```bash
curl https://backend-ai-practice-questions.<region>.azurecontainerapps.io/api/v1/assessments/certifications
```

If this returns JSON data, your backend is working fine. If not:
1. Check if the Container App is running
2. Verify ingress is set to "external"
3. Check the backend deployment logs

## Summary

✅ **What was fixed:**
- Updated frontend workflow to properly configure backend API URL
- Added better logging and error reporting
- Updated deployment summary to show API URL

⏳ **What you need to do:**
- Add `BACKEND_CONTAINER_APP_URL` secret to GitHub (or verify `CONTAINER_APP_NAME` and `AZURE_REGION` secrets exist)
- Redeploy the frontend

That's it! The fix should take less than 5 minutes to implement.
