# ☁️ **AZURE CLOUD DEPLOYMENT GUIDE**

## **🚀 QUICK DEPLOYMENT STEPS**

### **1. Restart PowerShell**
```powershell
# Close this window and open a new PowerShell as Administrator
# Then navigate back to this folder:
cd "C:\Users\mattm\OneDrive\Greenfield Metal Sales\Barcode Scanner"
```

### **2. Login to Azure**
```powershell
az login
# This will open a browser - login with your Microsoft account
```

### **3. Deploy to Azure**
```powershell
python azure_deployment_setup.py
```

---

## **📋 WHAT WILL BE DEPLOYED**

### **Azure Resources:**
- ✅ **App Service**: Hosts the inventory system
- ✅ **PostgreSQL Database**: Production database
- ✅ **Redis Cache**: For performance
- ✅ **Application Insights**: Monitoring
- ✅ **Key Vault**: Secure credential storage

### **Features Enabled:**
- ✅ **Public URL**: `https://greenfield-inventory-[random].azurewebsites.net`
- ✅ **SSL Certificate**: Automatic HTTPS
- ✅ **Auto-scaling**: Handles traffic spikes
- ✅ **Backup & Recovery**: Automated backups
- ✅ **99.95% Uptime**: Azure SLA

---

## **💰 ESTIMATED COSTS**

### **Free Tier (First 12 months):**
- **App Service**: Free (F1 tier)
- **Database**: Free (if under 250MB)
- **Total**: **$0/month**

### **Production Tier:**
- **App Service**: ~$55/month (B1 tier)
- **Database**: ~$25/month (Basic tier)
- **Redis**: ~$15/month (Basic tier)
- **Total**: **~$95/month**

### **Enterprise Tier:**
- **App Service**: ~$210/month (S1 tier)
- **Database**: ~$150/month (Standard tier)
- **Redis**: ~$75/month (Standard tier)
- **Total**: **~$435/month**

---

## **🔧 MANUAL DEPLOYMENT (Alternative)**

If the automated script doesn't work:

### **1. Create Resource Group**
```powershell
az group create --name greenfield-inventory --location eastus
```

### **2. Create App Service**
```powershell
az appservice plan create --name greenfield-plan --resource-group greenfield-inventory --sku B1 --is-linux
az webapp create --resource-group greenfield-inventory --plan greenfield-plan --name greenfield-inventory-app --runtime "PYTHON|3.9"
```

### **3. Deploy Code**
```powershell
# Zip the application
Compress-Archive -Path .\* -DestinationPath deployment.zip

# Deploy to Azure
az webapp deployment source config-zip --resource-group greenfield-inventory --name greenfield-inventory-app --src deployment.zip
```

### **4. Configure Environment**
```powershell
az webapp config appsettings set --resource-group greenfield-inventory --name greenfield-inventory-app --settings @azure-settings.json
```

---

## **🌐 POST-DEPLOYMENT**

### **1. Update Webhook URLs**
Once deployed, update webhook URLs in Paradigm:
- **Old**: `https://95891b50740f.ngrok-free.app/webhook/paradigm`
- **New**: `https://greenfield-inventory-app.azurewebsites.net/webhook/paradigm`

### **2. Import Data**
```powershell
# The system will automatically import your 39,193 products
# Or upload via the web interface
```

### **3. Configure SSL & Custom Domain (Optional)**
```powershell
# Add custom domain like inventory.greenfieldmetal.com
az webapp config hostname add --webapp-name greenfield-inventory-app --resource-group greenfield-inventory --hostname inventory.greenfieldmetal.com
```

---

## **🎯 BENEFITS OF AZURE DEPLOYMENT**

### **✅ Reliability:**
- 99.95% uptime SLA
- Automatic failover
- Global CDN

### **✅ Security:**
- SSL certificates
- Azure Key Vault integration
- Network security groups

### **✅ Scalability:**
- Auto-scaling based on demand
- Load balancing
- Global deployment

### **✅ Monitoring:**
- Application Insights
- Real-time logs
- Performance metrics

---

## **🚨 TROUBLESHOOTING**

### **If deployment fails:**
1. Check Azure CLI is installed: `az --version`
2. Verify login: `az account show`
3. Check permissions: Need Contributor role
4. Try manual steps above

### **If app doesn't start:**
1. Check logs: `az webapp log tail --name greenfield-inventory-app --resource-group greenfield-inventory`
2. Verify environment variables
3. Check database connection

---

**Ready to deploy?** 
1. Restart PowerShell as Administrator
2. Run `az login`
3. Run `python azure_deployment_setup.py`