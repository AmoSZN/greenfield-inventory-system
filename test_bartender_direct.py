"""
Direct BarTender Test - Verify printing works before webhook integration
"""
import os
import subprocess
import csv
from datetime import datetime
import json

# Load configuration
with open('config.json', 'r') as f:
    config = json.load(f)

def test_bartender_cli():
    """Test BarTender command line printing"""
    print("="*60)
    print("BARTENDER DIRECT TEST - COMMAND LINE METHOD")
    print("="*60)
    
    # Check BarTender exists
    bartender_exe = config['bartender']['executable_path']
    if not os.path.exists(bartender_exe):
        print(f"❌ ERROR: BarTender not found at: {bartender_exe}")
        return False
        
    print(f"[OK] BarTender found at: {bartender_exe}")
    
    # Check template exists locally
    local_template = os.path.join("Templates", "PackingList.btw")
    if os.path.exists(local_template):
        print(f"[OK] Local template found: {local_template}")
        template_path = os.path.abspath(local_template)
    else:
        # Try C:\BarTenderIntegration path
        template_path = os.path.join(config['bartender']['templates_path'], config['bartender']['packing_list_template'])
        if not os.path.exists(template_path):
            print(f"❌ ERROR: Template not found at: {template_path}")
            return False
    
    print(f"[OK] Using template: {template_path}")
    
    # Create test CSV data
    csv_filename = f"test_order_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    csv_path = os.path.abspath(csv_filename)
    
    csv_data = {
        'OrderNumber': 'TEST-001',
        'CustomerPO': 'TEST-PO-001',
        'ShipDate': datetime.now().strftime('%Y-%m-%d'),
        'BillToCompany': 'Test Company Inc.',
        'BillingAddress': '123 Test Street',
        'BillToCity': 'Minneapolis',
        'BillToState': 'MN',
        'BillToZIP': '55401',
        'ShipToCompany': 'Test Shipping Co.',
        'ShippingAddress': '456 Ship Lane',
        'ShipToCity': 'St. Paul',
        'ShipToState': 'MN',
        'ShipToZIP': '55102',
        'TotalQuantity': '25',
        'PrintDateTime': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Write CSV
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_data.keys())
        writer.writeheader()
        writer.writerow(csv_data)
    
    print(f"[OK] Created test CSV: {csv_path}")
    
    # Test 1: Just open BarTender (no print)
    print("\nTest 1: Opening BarTender UI...")
    cmd_open = [bartender_exe, f"/F={template_path}"]
    print(f"Command: {' '.join(cmd_open)}")
    
    try:
        result = subprocess.run(cmd_open, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("[OK] BarTender opened successfully")
        else:
            print(f"❌ Error: {result.stderr}")
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    input("\nPress Enter to continue to print test...")
    
    # Test 2: Print to default printer
    print("\nTest 2: Printing to default printer...")
    cmd_print = [
        bartender_exe,
        f"/F={template_path}",
        f"/D={csv_path}",
        "/P",      # Print
        "/C=1",    # 1 copy
        "/X"       # Close after printing
    ]
    
    print(f"Command: {' '.join(cmd_print)}")
    
    try:
        result = subprocess.run(cmd_print, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("[OK] Print command executed successfully")
        else:
            print(f"❌ Print error: {result.stderr}")
            print(f"Return code: {result.returncode}")
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    # Clean up
    if os.path.exists(csv_path):
        os.remove(csv_path)
        print(f"[OK] Cleaned up test CSV")
    
    print("\n" + "="*60)
    return True

def test_bartender_preview():
    """Test opening BarTender in preview mode"""
    print("\nTest 3: Opening in Print Preview mode...")
    
    bartender_exe = config['bartender']['executable_path']
    local_template = os.path.join("Templates", "PackingList.btw")
    template_path = os.path.abspath(local_template) if os.path.exists(local_template) else os.path.join(config['bartender']['templates_path'], config['bartender']['packing_list_template'])
    
    # Create simple CSV
    csv_path = "preview_test.csv"
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['OrderNumber', 'CustomerPO', 'ShipToCompany'])
        writer.writerow(['PREVIEW-001', 'PO-PREVIEW', 'Preview Test Company'])
    
    cmd_preview = [
        bartender_exe,
        f"/F={template_path}",
        f"/D={csv_path}",
        "/PRN=Preview"  # Open in print preview
    ]
    
    print(f"Command: {' '.join(cmd_preview)}")
    
    try:
        subprocess.Popen(cmd_preview)
        print("[OK] BarTender opened in preview mode")
        print("Check if the label looks correct in BarTender preview window")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    input("\nPress Enter to clean up...")
    if os.path.exists(csv_path):
        os.remove(csv_path)

if __name__ == "__main__":
    # Run the tests
    test_bartender_cli()
    
    print("\n" + "-"*60)
    response = input("\nWould you like to test Print Preview mode? (y/n): ")
    if response.lower() == 'y':
        test_bartender_preview()
    
    print("\nTest complete!") 