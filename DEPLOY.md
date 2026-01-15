# Deploy RAG Pipeline to Azure Container Apps

## Prerequisites
- Azure CLI installed
- Docker Desktop installed (optional, Azure builds for you)
- Azure subscription

## Quick Deploy

Run the deployment script:
```bash
deploy.bat
```

This will:
1. Login to Azure
2. Create resource group
3. Create container registry
4. Build and push Docker image
5. Create container app environment
6. Deploy the application
7. Show the app URL

## Manual Steps

### 1. Login to Azure
```bash
az login
```

### 2. Create Resource Group
```bash
az group create --name rag-pipeline-rg --location eastus
```

### 3. Create Container Registry
```bash
az acr create --resource-group rag-pipeline-rg --name ragpipelineacr --sku Basic
```

### 4. Build and Push Image
```bash
az acr build --registry ragpipelineacr --image rag-pipeline:latest .
```

### 5. Create Container App Environment
```bash
az containerapp env create --name rag-env --resource-group rag-pipeline-rg --location eastus
```

### 6. Deploy Container App
```bash
az containerapp create \
  --name rag-pipeline-api \
  --resource-group rag-pipeline-rg \
  --environment rag-env \
  --image ragpipelineacr.azurecr.io/rag-pipeline:latest \
  --target-port 8000 \
  --ingress external \
  --registry-server ragpipelineacr.azurecr.io \
  --cpu 1.0 \
  --memory 2.0Gi \
  --min-replicas 1 \
  --max-replicas 3
```

### 7. Get App URL
```bash
az containerapp show --name rag-pipeline-api --resource-group rag-pipeline-rg --query properties.configuration.ingress.fqdn -o tsv
```

## Update React UI

After deployment, update React UI to use the Azure URL:

**File:** `react-ui/src/App.js`
```javascript
const API_URL = 'https://your-app-url.azurecontainerapps.io';
```

## Deploy React UI

### Option 1: Azure Static Web Apps
```bash
cd react-ui
npm run build
az staticwebapp create --name rag-ui --resource-group rag-pipeline-rg --source ./build --location eastus
```

### Option 2: Azure Storage Static Website
```bash
cd react-ui
npm run build

# Create storage account
az storage account create --name ragpipelinestorage --resource-group rag-pipeline-rg --location eastus --sku Standard_LRS

# Enable static website
az storage blob service-properties update --account-name ragpipelinestorage --static-website --index-document index.html

# Upload files
az storage blob upload-batch --account-name ragpipelinestorage --source ./build --destination '$web'

# Get URL
az storage account show --name ragpipelinestorage --resource-group rag-pipeline-rg --query "primaryEndpoints.web" -o tsv
```

## Environment Variables

The container uses `.env` file. For production, set environment variables in Azure:

```bash
az containerapp update --name rag-pipeline-api --resource-group rag-pipeline-rg \
  --set-env-vars \
    AZURE_OPENAI_ENDPOINT=<value> \
    AZURE_OPENAI_KEY=<value> \
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT=<value> \
    AZURE_OPENAI_CHAT_DEPLOYMENT=<value> \
    AZURE_OPENAI_API_VERSION=<value> \
    AZURE_SPEECH_KEY=<value> \
    AZURE_SPEECH_REGION=<value>
```

## Update Deployment

To update the app:
```bash
# Rebuild image
az acr build --registry ragpipelineacr --image rag-pipeline:latest .

# Restart app (pulls new image)
az containerapp update --name rag-pipeline-api --resource-group rag-pipeline-rg --image ragpipelineacr.azurecr.io/rag-pipeline:latest
```

## Monitor

View logs:
```bash
az containerapp logs show --name rag-pipeline-api --resource-group rag-pipeline-rg --follow
```

## Cost Estimate

- Container Apps: ~$15-30/month (1 vCPU, 2GB RAM)
- Container Registry: ~$5/month (Basic tier)
- Static Web App: Free tier available

**Total: ~$20-35/month**

## Cleanup

Delete all resources:
```bash
az group delete --name rag-pipeline-rg --yes
```
