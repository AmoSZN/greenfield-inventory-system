# 🚀 Greenfield Metal Sales - Integrated Scanner & AI System

**Status:** ✅ FULLY OPERATIONAL - Scanner and AI modules working together!

---

## 📊 System Architecture

```
┌─────────────────────────────────────────────┐
│          PARADIGM ERP                       │
│          (Order Source)                     │
└────────────────┬────────────────────────────┘
                 │ Webhook
                 ▼
┌─────────────────────────────────────────────┐
│         INTEGRATED SYSTEM                    │
│  ┌─────────────────┬────────────────────┐  │
│  │  Scanner Module │    AI Module       │  │
│  │                 │                    │  │
│  │  • Webhook      │  • Order Analysis  │  │
│  │  • Label Print  │  • Anomaly Detect  │  │
│  │  • Barcode Scan │  • Inventory Pred  │  │
│  │                 │  • Reorder Alerts  │  │
│  └─────────┬───────┴──────────┬─────────┘  │
│            │   Event Bus       │            │
│            └───────┬───────────┘            │
└────────────────────┴────────────────────────┘
                     │
                     ▼
              ┌──────────────┐
              │  BarTender   │
              │  (Printing)  │
              └──────────────┘
```

---

## 🎯 Key Features

### Scanner Module
- ✅ Receives orders from Paradigm ERP
- ✅ Automatically prints shipping labels
- ✅ Publishes events for AI analysis
- ✅ Failover mode for critical operations

### AI Module  
- ✅ Real-time order analysis
- ✅ Anomaly detection (unusual orders)
- ✅ Inventory level tracking
- ✅ Reorder point suggestions
- ✅ Demand forecasting foundation

### Integration Benefits
- 📊 AI learns from every scan and order
- 🚨 Instant alerts for unusual patterns
- 📈 Predictive inventory management
- 🔄 Continuous improvement through data

---

## 🚀 Running the System

### Option 1: Full Integrated Mode (Recommended)
```bash
python main_app.py
```
This runs both Scanner and AI modules together.

### Option 2: Scanner-Only Mode (Failover)
```bash
python scanner_only_mode.py
```
Use this if AI issues occur but scanning must continue.

### Option 3: Simple Webhook (Most Stable)
```bash
python webhook_simple_print.py
```
Basic label printing without AI features.

---

## 📡 System Endpoints

- **Webhook:** `http://localhost:5001/paradigm-webhook`
- **Health Check:** `http://localhost:5001/health`
- **System Status:** `http://localhost:5001/system/status`
- **AI Report:** `http://localhost:5001/system/ai/report`
- **Test Print:** `http://localhost:5001/test-print`

---

## 🧪 Testing the Integrated System

### 1. Check System Status
```powershell
Invoke-RestMethod -Uri "http://localhost:5001/system/status" | ConvertTo-Json -Depth 5
```

### 2. Test Label Printing
```powershell
Invoke-RestMethod -Uri "http://localhost:5001/test-print" | ConvertTo-Json
```

### 3. Get AI Inventory Report
```powershell
Invoke-RestMethod -Uri "http://localhost:5001/system/ai/report" | ConvertTo-Json
```

### 4. Send Test Order with Anomaly
```powershell
$anomalyOrder = @{
    orderNumber = "TEST-ANOMALY-001"
    customerPO = "UNUSUAL-PO"
    billToCompany = "New Unknown Customer"
    shipToCompany = "New Unknown Customer"
    products = @(
        @{
            productId = "STEEL-XXL"
            description = "Unusual Product"
            quantity = 9999
        }
    )
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "http://localhost:5001/paradigm-webhook" `
    -Body $anomalyOrder -ContentType "application/json"
```

---

## 🔧 Configuration

### Enable/Disable AI
In `config.json`:
```json
"ai": {
    "enabled": true,  // Set to false to disable AI
    "anomaly_detection": true,
    "reorder_automation": false
}
```

### Adjust AI Sensitivity
```json
"ai": {
    "prediction_threshold": 0.8  // Lower = more sensitive
}
```

---

## 📊 Monitoring & Insights

### Real-time Monitoring
The AI module tracks:
- Order velocity (orders per day)
- Unusual order patterns
- New customers
- Inventory levels
- Reorder suggestions

### View Current Insights
Visit: `http://localhost:5001/system/status`

---

## 🚨 Troubleshooting

### AI Module Issues
1. Check AI logs: `C:\BarTenderIntegration\Logs\ai\`
2. Disable AI temporarily: Set `"enabled": false` in config
3. Use failover mode: `python scanner_only_mode.py`

### Scanner Module Issues
1. Check scanner logs: `C:\BarTenderIntegration\Logs\scanner\`
2. Verify BarTender is running
3. Test with: `python test_bartender_direct.py`

### Performance Issues
1. AI processing is asynchronous - won't slow scanning
2. Event bus handles load balancing
3. Can disable AI features if needed

---

## 🎯 What Happens When an Order Arrives

1. **Order Received** → Scanner module webhook
2. **Event Published** → "ORDER_RECEIVED" event
3. **AI Analysis** → Patterns, anomalies, predictions
4. **Label Printed** → Scanner module prints
5. **Event Published** → "LABEL_PRINTED" event
6. **AI Learning** → Updates models and predictions

---

## 📈 Future Enhancements

### Short Term (Already Foundation Exists)
- [ ] Email alerts for anomalies
- [ ] Web dashboard for insights
- [ ] Historical trend analysis
- [ ] Multi-location inventory

### Long Term
- [ ] Machine learning predictions
- [ ] Automated reordering
- [ ] Integration with suppliers
- [ ] Mobile app for scanning

---

## 🏆 Benefits of Combined System

1. **No Manual Intervention** - Fully automated
2. **Intelligent Insights** - AI learns your patterns
3. **Early Warning System** - Catch issues before they happen
4. **Scalable Architecture** - Grows with your business
5. **Failover Protection** - Scanner works even if AI fails

---

**Your integrated system is ready for production use!**

The modular design allows you to:
- Run combined for maximum intelligence
- Separate modules if needed later
- Scale each component independently
- Add new features easily

Next step: Let it run and watch the AI learn your business patterns! 