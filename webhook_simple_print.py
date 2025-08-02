"""
Simplified Webhook with BarTender Printing
Focus on getting printing working reliably
"""
from flask import Flask, request, jsonify
import json
import os
import subprocess
from datetime import datetime
import traceback

# Load configuration
with open('config.json', 'r') as f:
    config = json.load(f)

app = Flask(__name__)

# Ensure directories exist
for path in config['paths'].values():
    os.makedirs(path, exist_ok=True)

def log_message(message, level="INFO"):
    """Simple logging"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")

def create_csv_data(order_data):
    """Create CSV data for BarTender"""
    csv_path = os.path.join(
        config['paths']['data_path'],
        f"order_{order_data.get('orderNumber', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    )
    
    # Write CSV with order data
    with open(csv_path, 'w') as f:
        # Header
        f.write("OrderNumber,CustomerPO,ShipToCompany,BillToCompany,ShipDate\n")
        # Data
        f.write(f"{order_data.get('orderNumber', '')},")
        f.write(f"{order_data.get('customerPO', '')},")
        f.write(f"{order_data.get('shipToCompany', '')},")
        f.write(f"{order_data.get('billToCompany', '')},")
        f.write(f"{order_data.get('shipDate', datetime.now().strftime('%Y-%m-%d'))}\n")
    
    return csv_path

def print_label(order_data):
    """Print label using BarTender CLI"""
    try:
        # Create CSV
        csv_path = create_csv_data(order_data)
        log_message(f"Created CSV: {csv_path}")
        
        # Get template path
        local_template = os.path.join("Templates", "PackingList.btw")
        if os.path.exists(local_template):
            template_path = os.path.abspath(local_template)
        else:
            template_path = "C:\\BarTenderIntegration\\Templates\\PackingList.btw"
        
        log_message(f"Using template: {template_path}")
        
        # Build command - use silent mode to avoid UI
        cmd = [
            config['bartender']['executable_path'],
            f"/F={template_path}",
            f"/D={csv_path}",
            "/P",        # Print
            "/C=1",      # 1 copy
            "/X",        # Close when done
            "/MIN"       # Minimize window
        ]
        
        log_message(f"Executing: {' '.join(cmd)}")
        
        # Run BarTender with timeout
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            log_message("Print successful!")
            # Archive CSV
            archive_path = os.path.join(config['paths']['archive_path'], os.path.basename(csv_path))
            os.rename(csv_path, archive_path)
            return True, "Printed successfully"
        else:
            error = f"BarTender error (code {result.returncode}): {result.stderr or 'Unknown error'}"
            log_message(error, "ERROR")
            return False, error
            
    except subprocess.TimeoutExpired:
        error = "Print timeout - BarTender may be waiting for user input"
        log_message(error, "ERROR")
        return False, error
    except Exception as e:
        error = f"Print error: {str(e)}"
        log_message(error, "ERROR")
        log_message(traceback.format_exc(), "ERROR")
        return False, error

@app.route('/')
def home():
    return '''
    <h1>Greenfield Label Service - Simple Version</h1>
    <p>Status: Running</p>
    <p>Endpoints:</p>
    <ul>
        <li>/health - Health check</li>
        <li>/paradigm-webhook - Receive orders (POST)</li>
        <li>/test-print - Test printing (GET)</li>
    </ul>
    '''

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/paradigm-webhook', methods=['POST'])
def webhook():
    """Receive order and print label"""
    try:
        order_data = request.get_json()
        if not order_data:
            return jsonify({"status": "error", "message": "No data"}), 400
        
        order_number = order_data.get('orderNumber', 'Unknown')
        log_message(f"Received order: {order_number}")
        
        # Save order
        json_path = os.path.join(
            config['paths']['data_path'],
            f"order_{order_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(json_path, 'w') as f:
            json.dump(order_data, f, indent=2)
        
        # Print label
        success, message = print_label(order_data)
        
        if success:
            # Archive JSON
            archive_json = os.path.join(config['paths']['archive_path'], os.path.basename(json_path))
            os.rename(json_path, archive_json)
            
            return jsonify({
                "status": "success",
                "message": f"Order {order_number} printed",
                "details": message
            })
        else:
            return jsonify({
                "status": "error",
                "message": message
            }), 500
            
    except Exception as e:
        log_message(f"Webhook error: {str(e)}", "ERROR")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/test-print')
def test_print():
    """Test printing with sample data"""
    test_order = {
        "orderNumber": f"TEST-{datetime.now().strftime('%H%M%S')}",
        "customerPO": "TEST-PO-123",
        "shipToCompany": "Test Shipping Company",
        "billToCompany": "Test Billing Company",
        "shipDate": datetime.now().strftime('%Y-%m-%d')
    }
    
    log_message("Test print requested")
    success, message = print_label(test_order)
    
    if success:
        return jsonify({
            "status": "success",
            "message": "Test label printed",
            "order": test_order
        })
    else:
        return jsonify({
            "status": "error", 
            "message": message,
            "order": test_order
        }), 500

if __name__ == '__main__':
    print("="*60)
    print("GREENFIELD LABEL SERVICE - SIMPLE VERSION")
    print("="*60)
    print(f"Port: {config['webhook']['port']}")
    print(f"BarTender: {config['bartender']['executable_path']}")
    print("="*60)
    
    app.run(host='0.0.0.0', port=config['webhook']['port'], debug=True) 