# Week 1 Incremental Improvements Plan

## Current State ✅
- Basic label printing working
- Service deployed and stable
- AI monitoring active (but not actionable yet)

## Priority 1: Email Alerts (Day 1-2)
**Why**: Get notified of issues without checking dashboard

### Implementation:
```python
# Add to modules/shared/email_notifier.py
def send_alert(subject, body):
    # Use existing company SMTP
    pass

# Trigger on:
# - Service errors (>3 in 5 minutes)
# - Printer offline
# - AI anomaly detection
```

### Test:
- Simulate printer offline
- Send test anomaly order

## Priority 2: Zebra Scanner App MVP (Day 3-4)
**Why**: Complete the original vision - scan to print

### Implementation:
1. Deploy basic Android app to TC200J:
   - Single button: "Scan Order"
   - Calls: `http://192.168.12.28:5001/scan-print/{barcode}`
   
2. Add endpoint to webhook service:
```python
@app.route('/scan-print/<barcode>')
def scan_print(barcode):
    # Lookup order by barcode
    # Print label
    return jsonify({"status": "printed"})
```

### Test:
- Scan real order barcode
- Verify label prints

## Priority 3: AI Reorder Suggestions (Day 5)
**Why**: Turn AI data into actionable insights

### Implementation:
```python
# Daily report at 4 PM
def generate_reorder_report():
    low_stock = ai.get_low_stock_items()
    high_velocity = ai.get_high_demand_items()
    
    # Email report to purchasing
    send_alert("Daily Reorder Suggestions", report)
```

### Test:
- Process 20+ orders
- Verify report accuracy

## Success Metrics
- [ ] Zero manual intervention for normal orders
- [ ] <2 minute response to print issues
- [ ] 1 successful scan-to-print per day
- [ ] 1 actionable AI suggestion per week

## Next Week Preview
- Multi-label support (packing list + product labels)
- Historical analytics dashboard
- Paradigm inventory sync

---

**Remember**: [[memory:2833106]] Deploy minimal, test thoroughly, high confidence before claiming success! 