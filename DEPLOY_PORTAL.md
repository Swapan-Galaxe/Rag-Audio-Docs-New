# Deploy via Azure Portal (No CLI)

## Step 1: Create Container Registry

1. Go to https://portal.azure.com
2. Click "Create a resource"
3. Search "Container Registry"
4. Click "Create"
5. Fill in:
   - Resource Group: Create new "rag-pipeline-rg"
   - Registry name: `ragpipelineacr`
   - Location: East US
   - SKU: Basic
6. Click "Review + Create" → "Create"

## Step 2: Build Docker Image Locally

1. Install Docker Desktop: https://www.docker.com/products/docker-desktop
2. Open terminal in `c:\rag_pipeline`
3. Build image:
   ```bash
   docker build -t rag-pipeline:latest .
   ```

## Step 3: Push to Azure Container Registry

1. In Azure Portal, go to your Container Registry
2. Click "Access keys" in left menu
3. Enable "Admin user"
4. Copy Username and Password

5. In terminal, login:
   ```bash
   docker login ragpipelineacr.azurecr.io
   Username: <paste username>
   Password: <paste password>
   ```

6. Tag and push:
   ```bash
   docker tag rag-pipeline:latest ragpipelineacr.azurecr.io/rag-pipeline:latest
   docker push ragpipelineacr.azurecr.io/rag-pipeline:latest
   ```

## Step 4: Create Container App

1. In Azure Portal, click "Create a resource"
2. Search "Container Apps"
3. Click "Create"
4. Fill in:
   - Resource Group: `rag-pipeline-rg`
   - Container app name: `rag-pipeline-api`
   - Region: East US
5. Click "Next: Container"

6. Container settings:
   - Name: `rag-pipeline`
   - Image source: Azure Container Registry
   - Registry: `ragpipelineacr`
   - Image: `rag-pipeline`
   - Image tag: `latest`
   - CPU: 1.0
   - Memory: 2.0 Gi

7. Click "Next: Ingress"

8. Ingress settings:
   - Enable ingress: ✓
   - Ingress traffic: Accepting traffic from anywhere
   - Ingress type: HTTP
   - Target port: `8000`

9. Click "Review + Create" → "Create"

## Step 5: Get App URL

1. Go to your Container App in Azure Portal
2. Click "Overview"
3. Copy "Application Url"
4. Example: `https://rag-pipeline-api.azurecontainerapps.io`

## Step 6: Update React UI

1. Edit `react-ui/.env`:
   ```
   REACT_APP_API_URL=https://rag-pipeline-api.azurecontainerapps.io
   ```

2. Rebuild React:
   ```bash
   cd react-ui
   npm run build
   ```

## Step 7: Deploy React UI

### Option A: Azure Static Web Apps (Portal)

1. In Azure Portal, create "Static Web App"
2. Resource Group: `rag-pipeline-rg`
3. Name: `rag-ui`
4. Deployment: Other
5. After creation, go to resource
6. Click "Browse" → Upload `react-ui/build` folder contents

### Option B: Azure Storage (Portal)

1. Create "Storage Account"
   - Name: `ragpipelinestorage`
   - Resource Group: `rag-pipeline-rg`

2. Go to storage account → "Static website"
3. Enable static website
4. Index document: `index.html`
5. Save

6. Go to "Containers" → "$web"
7. Upload all files from `react-ui/build`

8. Go back to "Static website" to get URL

## Done!

Your app is deployed:
- Backend API: Container App URL
- Frontend UI: Static Web App or Storage URL

## Update App

To update backend:
1. Rebuild Docker image locally
2. Push to Container Registry
3. In Container App → "Revision management" → "Create new revision"

To update frontend:
1. Rebuild React: `npm run build`
2. Upload new files to Static Web App or Storage
