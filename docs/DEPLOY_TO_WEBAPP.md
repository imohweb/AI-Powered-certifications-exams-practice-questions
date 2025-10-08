# Deploy Backend to Azure Web App (Alternative Approach)

## Why Azure Web App Instead of Container Apps?

Azure Web App for Containers is:
- ✅ More stable and mature service
- ✅ Better logging and diagnostics
- ✅ Simpler configuration
- ✅ Same Docker container support
- ✅ Built-in health monitoring
- ✅ Easier troubleshooting

## What Changed

### 1. **New Workflow File**
- Created: `.github/workflows/deploy-backend-webapp.yml`
- This deploys to Azure Web App instead of Container Apps
- Old workflow (deploy-backend.yml) is still there but won't be triggered

### 2. **Fixed Dockerfile**
- Added `curl` to system dependencies
- Fixed health check to use `curl` instead of Python `requests` library
- Increased start period to 40s to give the app more time to start

### 3. **Backend URL Will Change**
- **Old:** `https://backend-ai-practice-questions.{region}.azurecontainerapps.io`
- **New:** `https://backend-ai-practice-questions-app.azurewebsites.net`

## Deployment Steps

### Step 1: Run the New Workflow

1. Go to: https://github.com/imohweb/certifications-exams-practice-questions/actions
2. Select: **"Deploy Backend to Azure Web App"** (the new workflow)
3. Click: **"Run workflow"** → **"Run workflow"**

### Step 2: Monitor the Deployment

The workflow will:
1. Build the Docker image
2. Push to Azure Container Registry
3. Create App Service Plan (B1 tier - $13/month)
4. Create Web App
5. Configure environment variables
6. Deploy the container
7. Run health checks
8. Display deployment summary with the new URL

### Step 3: Update GitHub Secret

After deployment succeeds, the summary will show the new backend URL.

1. Go to: https://github.com/imohweb/certifications-exams-practice-questions/settings/secrets/actions
2. Find: `BACKEND_CONTAINER_APP_URL`
3. Update value to: `https://backend-ai-practice-questions-app.azurewebsites.net`
4. Click: **Update secret**

### Step 4: Redeploy Frontend

1. Go to: https://github.com/imohweb/certifications-exams-practice-questions/actions
2. Select: **"Deploy Frontend to GitHub Pages"**
3. Click: **"Run workflow"** → **"Run workflow"**

This will rebuild the frontend with the new backend URL.

## Testing the Backend

After deployment, test these endpoints:

```bash
# Health check
curl https://backend-ai-practice-questions-app.azurewebsites.net/health

# List certifications
curl https://backend-ai-practice-questions-app.azurewebsites.net/api/v1/assessments/certifications

# API docs (if debug mode is on)
# Visit: https://backend-ai-practice-questions-app.azurewebsites.net/docs
```

## Required Azure Resources

The new deployment will create:
1. **App Service Plan**: `backend-ai-practice-plan` (B1 tier)
2. **Web App**: `backend-ai-practice-questions-app`

These use your existing:
- Azure Container Registry (for Docker images)
- Azure OpenAI, Speech, and Translator services (credentials from secrets)

## Cost Comparison

| Service | Container Apps | Web App (B1) |
|---------|---------------|--------------|
| Monthly Cost | ~$20-30 | ~$13 |
| Minimum Instances | 0-1 | 1 (always on) |
| Scaling | Automatic | Manual/Auto |
| Startup Time | Slower (cold start) | Faster (always warm) |
| Stability | Good | Excellent |

## Troubleshooting

### If Deployment Fails

1. **Check the workflow logs** in GitHub Actions
2. **View Web App logs:**
   ```bash
   az webapp log tail \
     --name backend-ai-practice-questions-app \
     --resource-group RG-foundry-resource
   ```

3. **Check container logs:**
   ```bash
   az webapp log download \
     --name backend-ai-practice-questions-app \
     --resource-group RG-foundry-resource
   ```

### If Health Check Fails

The workflow will still complete but will show "HEALTH_CHECK=FAILED". This could mean:
- App is starting up (wait 1-2 minutes and check again)
- Configuration error (check environment variables)
- Code error (check application logs)

### Common Issues

**Issue:** "Image pull failed"
- **Fix:** Ensure ACR credentials are configured (workflow handles this automatically)

**Issue:** "App keeps restarting"
- **Fix:** Check logs for Python errors, missing dependencies, or configuration issues

**Issue:** "502 Bad Gateway"
- **Fix:** App hasn't started yet - wait 30-60 seconds after deployment

## Rollback Plan

If the new Web App doesn't work, you can:
1. Keep using the old Container App approach
2. Or revert the Dockerfile changes
3. Or try a different Azure region

## Summary

✅ **Created:** New workflow for Azure Web App deployment  
✅ **Fixed:** Dockerfile health check issue  
✅ **Ready:** Deploy with one click via GitHub Actions  
⏳ **Next:** Run the workflow and update the frontend

The new approach should be more reliable and easier to troubleshoot!
