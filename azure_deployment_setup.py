#!/usr/bin/env python3
"""
Azure Cloud Deployment Setup for Greenfield Inventory System
State-of-the-art architecture with real-time sync
"""

import os
import json
import subprocess

print("🚀 Azure Cloud Deployment Setup")
print("=" * 60)

# Azure configuration
config = {
    "resource_group": "greenfield-inventory-rg",
    "location": "eastus",
    "app_name": "greenfield-inventory-api",
    "storage_account": "greenfieldinventory",
    "cosmos_db": "greenfield-inventory-db",
    "service_bus": "greenfield-events",
    "function_app": "greenfield-sync-functions"
}

def check_azure_cli():
    """Check if Azure CLI is installed"""
    try:
        result = subprocess.run(['az', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Azure CLI is installed")
            return True
    except:
        pass
    
    print("❌ Azure CLI not found")
    print("\nTo install:")
    print("1. Download from: https://aka.ms/installazurecliwindows")
    print("2. Or run: winget install Microsoft.AzureCLI")
    return False

def create_deployment_template():
    """Create ARM template for deployment"""
    template = {
        "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
        "contentVersion": "1.0.0.0",
        "parameters": {
            "appName": {
                "type": "string",
                "defaultValue": config["app_name"]
            }
        },
        "resources": [
            {
                "type": "Microsoft.Web/serverfarms",
                "apiVersion": "2021-02-01",
                "name": "[concat(parameters('appName'), '-plan')]",
                "location": "[resourceGroup().location]",
                "sku": {
                    "name": "B1",
                    "tier": "Basic"
                },
                "properties": {
                    "reserved": True
                }
            },
            {
                "type": "Microsoft.Web/sites",
                "apiVersion": "2021-02-01",
                "name": "[parameters('appName')]",
                "location": "[resourceGroup().location]",
                "dependsOn": [
                    "[resourceId('Microsoft.Web/serverfarms', concat(parameters('appName'), '-plan'))]"
                ],
                "properties": {
                    "serverFarmId": "[resourceId('Microsoft.Web/serverfarms', concat(parameters('appName'), '-plan'))]",
                    "siteConfig": {
                        "linuxFxVersion": "PYTHON|3.9",
                        "appSettings": [
                            {
                                "name": "PARADIGM_BASE_URL",
                                "value": "https://greenfieldapi.para-apps.com"
                            },
                            {
                                "name": "PARADIGM_API_KEY",
                                "value": "nVPsQFBteV&GEd7*8n0%RliVjksag8"
                            }
                        ]
                    }
                }
            },
            {
                "type": "Microsoft.ServiceBus/namespaces",
                "apiVersion": "2021-11-01",
                "name": "[concat(parameters('appName'), '-events')]",
                "location": "[resourceGroup().location]",
                "sku": {
                    "name": "Basic"
                },
                "properties": {}
            }
        ]
    }
    
    with open('azure-deploy.json', 'w') as f:
        json.dump(template, f, indent=2)
    
    print("✅ Created deployment template: azure-deploy.json")

def create_deployment_scripts():
    """Create deployment scripts"""
    
    # PowerShell deployment script
    ps_script = f"""
# Greenfield Inventory - Azure Deployment Script
$resourceGroup = "{config['resource_group']}"
$location = "{config['location']}"
$appName = "{config['app_name']}"

Write-Host "🚀 Deploying Greenfield Inventory to Azure" -ForegroundColor Cyan

# Login to Azure
Write-Host "Logging into Azure..." -ForegroundColor Yellow
az login

# Create resource group
Write-Host "Creating resource group..." -ForegroundColor Yellow
az group create --name $resourceGroup --location $location

# Deploy template
Write-Host "Deploying resources..." -ForegroundColor Yellow
az deployment group create `
    --resource-group $resourceGroup `
    --template-file azure-deploy.json `
    --parameters appName=$appName

# Configure GitHub Actions for CI/CD
Write-Host "Setting up CI/CD..." -ForegroundColor Yellow
az webapp deployment source config `
    --name $appName `
    --resource-group $resourceGroup `
    --repo-url https://github.com/yourusername/greenfield-inventory `
    --branch main `
    --manual-integration

Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host "🌐 Your app URL: https://${{appName}}.azurewebsites.net" -ForegroundColor Cyan
"""
    
    with open('deploy-to-azure.ps1', 'w') as f:
        f.write(ps_script)
    
    print("✅ Created deployment script: deploy-to-azure.ps1")

def create_docker_config():
    """Create Docker configuration for containerization"""
    
    dockerfile = """FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose ports
EXPOSE 8000 5005

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run the application
CMD ["python", "cloud_inventory_system.py"]
"""
    
    with open('Dockerfile', 'w') as f:
        f.write(dockerfile)
    
    # Docker compose for local testing
    compose = """version: '3.8'

services:
  inventory-api:
    build: .
    ports:
      - "8000:8000"
      - "5005:5005"
    environment:
      - PARADIGM_BASE_URL=https://greenfieldapi.para-apps.com
      - PARADIGM_API_KEY=nVPsQFBteV&GEd7*8n0%RliVjksag8
      - AZURE_STORAGE_CONNECTION_STRING=${AZURE_STORAGE_CONNECTION_STRING}
    volumes:
      - ./data:/app/data
    restart: unless-stopped

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - inventory-api
    restart: unless-stopped
"""
    
    with open('docker-compose.yml', 'w') as f:
        f.write(compose)
    
    print("✅ Created Docker configuration")

# Run setup
if __name__ == "__main__":
    if check_azure_cli():
        create_deployment_template()
        create_deployment_scripts()
        create_docker_config()
        
        print("\n📋 Next Steps:")
        print("1. Run: .\\deploy-to-azure.ps1")
        print("2. Configure Paradigm webhooks to Azure URL")
        print("3. Monitor via Azure Portal")
    else:
        print("\n⚠️  Please install Azure CLI first")