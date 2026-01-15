# Install Azure CLI

## Windows Installation

### Option 1: MSI Installer (Recommended)
1. Download: https://aka.ms/installazurecliwindows
2. Run the installer
3. Restart terminal
4. Verify: `az --version`

### Option 2: PowerShell
```powershell
Invoke-WebRequest -Uri https://aka.ms/installazurecliwindows -OutFile .\AzureCLI.msi
Start-Process msiexec.exe -Wait -ArgumentList '/I AzureCLI.msi /quiet'
```

### Option 3: Winget
```bash
winget install -e --id Microsoft.AzureCLI
```

## After Installation

1. **Restart terminal**
2. **Verify installation:**
   ```bash
   az --version
   ```

3. **Login to Azure:**
   ```bash
   az login
   ```

4. **Run deployment:**
   ```bash
   deploy.bat
   ```

## Alternative: Use Azure Portal

If you prefer not to install CLI, deploy manually via Azure Portal:

### 1. Create Container Registry
- Go to portal.azure.com
- Create "Container Registry"
- Name: `ragpipelineacr`
- SKU: Basic

### 2. Build Image Locally
```bash
docker build -t rag-pipeline:latest .
docker tag rag-pipeline:latest ragpipelineacr.azurecr.io/rag-pipeline:latest
docker push ragpipelineacr.azurecr.io/rag-pipeline:latest
```

### 3. Create Container App
- Go to portal.azure.com
- Create "Container App"
- Select your container registry
- Image: `rag-pipeline:latest`
- Port: 8000
- Enable external ingress

Done!
