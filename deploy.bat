@echo off
echo ========================================
echo Azure Container Deployment
echo ========================================

REM Configuration
set RESOURCE_GROUP=rag-pipeline-rg
set LOCATION=eastus
set ACR_NAME=ragpipelineacr
set APP_NAME=rag-pipeline-api
set ENV_NAME=rag-env

echo.
echo Step 1: Login to Azure
az login
if %errorlevel% neq 0 exit /b %errorlevel%

echo.
echo Step 2: Create Resource Group
az group create --name %RESOURCE_GROUP% --location %LOCATION%

echo.
echo Step 3: Create Container Registry
az acr create --resource-group %RESOURCE_GROUP% --name %ACR_NAME% --sku Basic

echo.
echo Step 4: Build and Push Docker Image
az acr build --registry %ACR_NAME% --image rag-pipeline:latest .

echo.
echo Step 5: Create Container App Environment
az containerapp env create --name %ENV_NAME% --resource-group %RESOURCE_GROUP% --location %LOCATION%

echo.
echo Step 6: Deploy Container App
az containerapp create ^
  --name %APP_NAME% ^
  --resource-group %RESOURCE_GROUP% ^
  --environment %ENV_NAME% ^
  --image %ACR_NAME%.azurecr.io/rag-pipeline:latest ^
  --target-port 8000 ^
  --ingress external ^
  --registry-server %ACR_NAME%.azurecr.io ^
  --cpu 1.0 ^
  --memory 2.0Gi ^
  --min-replicas 1 ^
  --max-replicas 3

echo.
echo Step 7: Get App URL
az containerapp show --name %APP_NAME% --resource-group %RESOURCE_GROUP% --query properties.configuration.ingress.fqdn -o tsv

echo.
echo ========================================
echo Deployment Complete!
echo ========================================
echo.
echo Next: Update React UI API_URL with the URL above
echo.
pause
