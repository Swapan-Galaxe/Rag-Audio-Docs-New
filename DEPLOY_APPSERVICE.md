# Deploy to Azure App Service (No Docker)

## Easiest Way - Direct Deploy from Portal

### Step 1: Prepare Files

Create a zip file with these files:
- `api_server.py`
- `rag_summarizer.py`
- `requirements.txt`
- `.env`

### Step 2: Create App Service

1. Go to https://portal.azure.com
2. Click "Create a resource"
3. Search "Web App"
4. Click "Create"

5. Fill in:
   - Resource Group: Create new "rag-pipeline-rg"
   - Name: `rag-pipeline-api` (must be unique)
   - Publish: **Code**
   - Runtime stack: **Python 3.11** or **Python 3.12**
   - Operating System: **Linux**
   - Region: East US
   - Pricing plan: Basic B1 (~$13/month)

6. Click "Review + Create" → "Create"


### Step 3: Configure App

1. Go to your App Service
2. Click "Configuration" in left menu
3. Click "General settings"
4. Set:
   - Startup Command: `gunicorn --bind 0.0.0.0:8000 --timeout 300 api_server:app`
5. Click "Save"

### Step 4: Add Environment Variables

1. Still in "Configuration"
2. Click "Application settings"
3. Add these (click "+ New application setting" for each):
   ```
   AZURE_OPENAI_ENDPOINT=https://azureopenaiswapan.openai.azure.com/
   AZURE_OPENAI_KEY=your-key
   AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
   AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o-mini
   AZURE_OPENAI_API_VERSION=2024-08-01-preview
   AZURE_SPEECH_KEY=your-key
   AZURE_SPEECH_REGION=eastus
   ```
4. Click "Save"

### Step 5: Deploy Code

**Option A: Zip Deploy (Easiest)**
1. Zip your files: `api_server.py`, `rag_summarizer.py`, `requirements.txt`
2. In App Service, click "Deployment Center"
3. Select "Local Git" or "External Git"
4. Or use Azure CLI:
   ```bash
   az webapp deployment source config-zip --resource-group rag-pipeline-rg --name rag-pipeline-api --src app.zip
   ```

**Option B: FTP Upload**
1. In App Service, click "Deployment Center"
2. Click "FTP credentials"
3. Copy FTP hostname, username, password
4. Use FileZilla or any FTP client to upload files to `/site/wwwroot/`

**Option C: GitHub (Best for updates)**
1. Push code to GitHub
2. In App Service → "Deployment Center"
3. Select "GitHub"
4. Authorize and select your repository
5. Auto-deploys on every push!

### Step 6: Get App URL

1. Go to App Service "Overview"
2. Copy "Default domain"
3. Example: `https://rag-pipeline-api.azurewebsites.net`

### Step 7: Update React UI

Edit `react-ui/.env`:
```
REACT_APP_API_URL=https://rag-pipeline-api.azurewebsites.net
```

Rebuild:
```bash
cd react-ui
npm run build
```

### Step 8: Deploy React UI

**Azure Static Web Apps (Free tier):**
1. Create "Static Web App" in Portal
2. Connect to GitHub or upload build folder
3. Done!

## Quick Deploy Script

If you have Azure CLI:
```bash
# Create App Service
az webapp up --name rag-pipeline-api --resource-group rag-pipeline-rg --runtime "PYTHON:3.9" --sku B1

# Set environment variables
az webapp config appsettings set --name rag-pipeline-api --resource-group rag-pipeline-rg --settings @env-vars.json
```

## Advantages

✅ No Docker needed
✅ No local build required
✅ Direct file upload
✅ Auto-scaling available
✅ Easy updates via FTP/Git
✅ Built-in monitoring

## Cost

- App Service B1: ~$13/month
- Static Web App: Free tier available

**Total: ~$13/month**

## Monitor

View logs:
1. App Service → "Log stream"
2. Or "Diagnose and solve problems"

## Update App

- **FTP**: Upload new files
- **GitHub**: Push to repository
- **Zip**: Upload new zip file
