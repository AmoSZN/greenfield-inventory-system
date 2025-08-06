# 🚀 **COMPLETE RENDER DEPLOYMENT GUIDE**

## **STEP-BY-STEP INSTRUCTIONS**

### **STEP 1: Create Render Account**
1. Go to https://render.com
2. Click "Get Started for Free"
3. Sign up with your GitHub account
4. Authorize Render to access your repositories

### **STEP 2: Create New Web Service**
1. Click "New +" button
2. Select "Web Service"
3. Connect your GitHub repository: `AmoSZN/greenfield-ai-suite`
4. Click "Connect"

### **STEP 3: Configure Service Settings**
- **Name**: `greenfield-inventory-system`
- **Environment**: `Python 3`
- **Region**: Choose closest to you (US East recommended)
- **Branch**: `master`
- **Root Directory**: Leave blank (root of repository)
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python app.py`

### **STEP 4: Set Environment Variables**
Click "Environment" tab and add these variables:

```
PARADIGM_BASE_URL=https://greenfieldapi.para-apps.com
PARADIGM_API_KEY=YOUR_PARADIGM_API_KEY_HERE
PARADIGM_USERNAME=mattamundson
PARADIGM_PASSWORD=Morrison216!
ANTHROPIC_API_KEY=YOUR_ANTHROPIC_API_KEY_HERE
```

### **STEP 5: Deploy**
1. Click "Create Web Service"
2. Wait for deployment (5-10 minutes)
3. Your system will be live at: `https://your-app-name.onrender.com`

### **STEP 6: Test Your Live System**
1. Visit your live URL
2. Test the inventory search
3. Try natural language commands
4. Verify Paradigm ERP connection

## **TROUBLESHOOTING**

### **If Build Fails:**
- Check the build logs in Render dashboard
- Verify all files are committed to GitHub
- Ensure requirements.txt exists

### **If App Won't Start:**
- Check the logs in Render dashboard
- Verify environment variables are set correctly
- Ensure app.py exists and is correct

### **If Connection Issues:**
- Verify Paradigm credentials are correct
- Check if Paradigm API is accessible from Render's servers

## **POST-DEPLOYMENT**

### **Custom Domain (Optional):**
1. Go to your service settings
2. Click "Custom Domains"
3. Add your domain name
4. Update DNS records

### **Monitoring:**
- View logs in Render dashboard
- Set up alerts for downtime
- Monitor performance metrics

## **SUCCESS INDICATORS**
✅ Build completes successfully
✅ App starts without errors
✅ Web interface loads
✅ Can search for products
✅ Natural language commands work
✅ Paradigm ERP connection successful