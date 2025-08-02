# 🌐 **AZURE ACCOUNT SETUP GUIDE**

## **STEP 1: Create Free Azure Account**

### **Option A: Azure Free Account (Recommended)**
1. **Go to**: https://azure.microsoft.com/free/
2. **Click**: "Start free"
3. **Sign in** with your Microsoft account (or create one)
4. **You get**:
   - $200 credit for 30 days
   - 12 months of free services
   - Always free services

### **Option B: Azure for Business**
If you have Microsoft 365 for business:
- You might already have Azure access
- Check: https://portal.azure.com
- Sign in with your work email

## **STEP 2: Initial Setup**

### **Required Information:**
- ✅ Credit card (for verification only, won't be charged)
- ✅ Phone number for verification
- ✅ Email address

### **During Signup:**
1. **Region**: Select "United States"
2. **Support Plan**: Choose "Basic (Free)"
3. **Agree** to terms

## **STEP 3: Install Azure CLI**

### **Windows (Easy Method):**
```powershell
# Option 1: Using winget (recommended)
winget install Microsoft.AzureCLI

# Option 2: Download installer
Start-Process "https://aka.ms/installazurecliwindows"
```

### **Verify Installation:**
```powershell
# Restart PowerShell, then:
az --version
```

## **STEP 4: Deploy Your System**

### **Quick Deployment Script:**
I'll create this for you once Azure CLI is installed:

```powershell
# Login to Azure
az login

# Create resource group
az group create --name greenfield-inventory --location eastus

# Deploy the app
az webapp up --name greenfield-inventory-app --runtime "PYTHON:3.9"
```

## **STEP 5: Estimated Costs**

### **Free Tier (First Year):**
- **App Service**: Free (F1 tier)
- **Database**: Free (if under 250MB)
- **Total**: $0/month

### **Production Tier (After Free Period):**
- **App Service**: ~$55/month (B1 tier)
- **Database**: ~$5/month
- **Storage**: ~$2/month
- **Total**: ~$62/month

### **Enterprise Tier (Optional):**
- **App Service**: ~$210/month (S1 tier)
- **Database**: ~$150/month (with backup)
- **Total**: ~$360/month

## **QUICK START CHECKLIST**

- [ ] Create Azure account
- [ ] Verify email and phone
- [ ] Install Azure CLI
- [ ] Run `az login`
- [ ] Deploy the app

## **BENEFITS OF AZURE**

1. **Reliability**: 99.95% uptime SLA
2. **Global**: Deploy close to your customers
3. **Scalable**: Handle growth automatically
4. **Secure**: Enterprise-grade security
5. **Integrated**: Works with Office 365

## **ALTERNATIVE: Start with Ngrok**

If you want to test webhooks before Azure:

```powershell
# Download ngrok
Invoke-WebRequest -Uri "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip" -OutFile "ngrok.zip"
Expand-Archive ngrok.zip

# Run ngrok
.\ngrok http 8000

# You'll get a public URL like: https://abc123.ngrok.io
# Use this URL for Paradigm webhooks temporarily
```

---

**Ready to proceed?** Let me know:
1. Azure account created? (Yes/No)
2. Azure CLI installed? (Yes/No)
3. Want to try ngrok first? (Yes/No)