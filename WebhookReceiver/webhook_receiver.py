from flask import Flask, request, jsonify
import json
import os
import win32com.client
from datetime import datetime
import time
import logging
import traceback
import sys

# Load configuration
CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
with open(CONFIG_FILE, 'r') as f:
    config = json.load(f)

# Set up logging with more detail
log_dir = config['paths']['logs_path']
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_filename = os.path.join(log_dir, f'webhook_receiver_{datetime.now().strftime("%Y%m%d")}.log')
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration from config.json
BARTENDER_PATH = config['bartender']['executable_path']
PACKING_LIST_TEMPLATE = os.path.join(config['bartender']['templates_path'], config['bartender']['packing_list_template'])
PRODUCT_LABEL_TEMPLATE = os.path.join(config['bartender']['templates_path'], config['bartender']['product_label_template'])
DATA_PATH = config['paths']['data_path']
ARCHIVE_PATH = config['paths']['archive_path']
ERROR_PATH = config['paths']['error_path']

# Ensure all paths exist
for path in [DATA_PATH, ARCHIVE_PATH, ERROR_PATH]:
    if not os.path.exists(path):
        os.makedirs(path)
        logger.info(f"Created directory: {path}")

@app.route('/', methods=['GET'])
def home():
    """Home page with service information"""
    return '''
    <html>
        <head>
            <title>Greenfield Metal Sales - Label Print Service</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background-color: #f0f0f0; }
                .container { background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                h1 { color: #2c3e50; }
                .status { color: #27ae60; font-weight: bold; }
                .endpoint { background-color: #ecf0f1; padding: 10px; margin: 10px 0; border-radius: 5px; font-family: monospace; }
                .info { color: #7f8c8d; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🏭 Greenfield Metal Sales - Label Print Service</h1>
                <p class="status">✅ Service is running</p>
                <p class="info">This service receives order data from Paradigm ERP and automatically prints shipping labels.</p>
                
                <h2>Available Endpoints:</h2>
                <div class="endpoint">GET /health - Health check endpoint</div>
                <div class="endpoint">POST /paradigm-webhook - Main webhook for Paradigm ERP</div>
                <div class="endpoint">POST /test-print - Test printing with sample data</div>
                <div class="endpoint">GET /logs - View recent logs</div>
                <div class="endpoint">GET /stats - View printing statistics</div>
                
                <p class="info">Service started: ''' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '''</p>
            </div>
        </body>
    </html>
    '''

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify service is running"""
    try:
        # Check if BarTender is accessible
        bartender_exists = os.path.exists(BARTENDER_PATH)
        templates_exist = os.path.exists(PACKING_LIST_TEMPLATE) and os.path.exists(PRODUCT_LABEL_TEMPLATE)
        
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "Greenfield Label Print Service",
            "version": "1.0.0",
            "checks": {
                "bartender_installed": bartender_exists,
                "templates_exist": templates_exist,
                "data_directory": os.path.exists(DATA_PATH),
                "archive_directory": os.path.exists(ARCHIVE_PATH)
            }
        }
        
        # Determine overall health
        if not all(health_status["checks"].values()):
            health_status["status"] = "degraded"
            
        return jsonify(health_status), 200
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/paradigm-webhook', methods=['POST'])
def receive_order():
    """Main webhook endpoint to receive orders from Paradigm ERP"""
    
    start_time = time.time()
    
    try:
        # Log incoming request
        logger.info("="*50)
        logger.info("Received webhook request from Paradigm ERP")
        
        # Get JSON data from request
        order_data = request.json
        if not order_data:
            logger.error("No JSON data received in request")
            return jsonify({"status": "error", "message": "No data received"}), 400
            
        order_number = order_data.get('orderNumber', 'Unknown')
        logger.info(f"Processing order: {order_number}")
        logger.debug(f"Order data: {json.dumps(order_data, indent=2)}")
        
        # Validate required fields
        required_fields = ['orderNumber', 'billToCompany', 'shipToCompany', 'products']
        missing_fields = [field for field in required_fields if field not in order_data]
        if missing_fields:
            error_msg = f"Missing required fields: {', '.join(missing_fields)}"
            logger.error(error_msg)
            return jsonify({"status": "error", "message": error_msg}), 400
        
        # Add timestamp and additional fields
        order_data['printDateTime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        order_data['printerName'] = 'Zebra ZT610'
        order_data['serviceVersion'] = '1.0.0'
        
        # Generate QR code data
        qr_data = {
            "orderNumber": order_data.get('orderNumber'),
            "customerPO": order_data.get('customerPO', ''),
            "shipDate": order_data.get('shipDate', ''),
            "trackingURL": f"https://track.greenfieldmetalsales.com/order/{order_data.get('orderNumber')}"
        }
        order_data['qrCodeData'] = json.dumps(qr_data)
        
        # Generate barcode data
        order_data['barcodeData'] = f"ORD-{order_data.get('orderNumber')}-1"
        
        # Calculate total quantity
        total_quantity = sum(item.get('quantity', 0) for item in order_data.get('products', []))
        order_data['totalQuantity'] = total_quantity
        
        # Format product list for display
        product_list = ""
        for product in order_data.get('products', []):
            product_id = product.get('productId', 'N/A').ljust(20)
            description = product.get('description', 'N/A')[:40].ljust(40)
            quantity = str(product.get('quantity', 0)).rjust(10)
            product_list += f"{product_id}{description}{quantity}\n"
        order_data['productListFormatted'] = product_list
        
        # Save order data to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]  # Include milliseconds
        filename = f"order_{order_number}_{timestamp}.json"
        filepath = os.path.join(DATA_PATH, filename)
        
        with open(filepath, 'w') as f:
            json.dump(order_data, f, indent=2)
        
        logger.info(f"Order data saved to: {filepath}")
        
        # Print labels
        labels_printed = print_labels(order_data, filepath, timestamp)
        
        if labels_printed['success']:
            # Archive the file
            archive_path = os.path.join(ARCHIVE_PATH, filename)
            os.rename(filepath, archive_path)
            logger.info(f"Order file archived to: {archive_path}")
            
            # Calculate processing time
            processing_time = round(time.time() - start_time, 2)
            
            # Success response
            response_data = {
                "status": "success",
                "message": "Labels printed successfully",
                "orderNumber": order_number,
                "labelsCount": labels_printed['count'],
                "processingTime": f"{processing_time}s",
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Order {order_number} completed successfully in {processing_time}s")
            return jsonify(response_data), 200
            
        else:
            # Error occurred during printing
            return jsonify({
                "status": "error",
                "message": "Failed to print labels",
                "error": labels_printed['error'],
                "orderNumber": order_number
            }), 500
            
    except Exception as e:
        logger.error(f"General error processing order: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Save error report
        save_error_report(order_data if 'order_data' in locals() else {}, str(e), traceback.format_exc())
        
        return jsonify({
            "status": "error",
            "message": "Failed to process webhook",
            "error": str(e)
        }), 500

def print_labels(order_data, filepath, timestamp):
    """Handle the actual printing of labels"""
    try:
        logger.info("Initializing BarTender...")
        
        # Check if templates exist
        if not os.path.exists(PACKING_LIST_TEMPLATE):
            raise FileNotFoundError(f"Packing list template not found: {PACKING_LIST_TEMPLATE}")
        if not os.path.exists(PRODUCT_LABEL_TEMPLATE):
            raise FileNotFoundError(f"Product label template not found: {PRODUCT_LABEL_TEMPLATE}")
        
        # Initialize BarTender
        btapp = win32com.client.Dispatch("BarTender.Application")
        btapp.Visible = False  # Run in background
        
        labels_printed = 0
        
        # Print packing list
        logger.info("Opening packing list template...")
        format_doc = btapp.Formats.Open(PACKING_LIST_TEMPLATE, False, "")
        
        # Log template information
        logger.debug(f"Template opened: {format_doc.FileName}")
        logger.debug(f"Printer: {format_doc.PrinterName}")
        
        # Print the packing list
        logger.info("Printing packing list...")
        format_doc.PrintOut(False, False)
        format_doc.Close(1)  # SaveChanges = 1 (Yes)
        labels_printed += 1
        
        logger.info("Packing list printed successfully")
        
        # Print individual product labels
        product_count = len(order_data.get('products', []))
        logger.info(f"Printing {product_count} product labels...")
        
        for idx, product in enumerate(order_data.get('products', [])):
            # Create product-specific data
            product_data = {
                **order_data,  # Include all order data
                'currentProduct': product,
                'productIndex': idx + 1,
                'totalProducts': product_count,
                'productBarcode': f"PRD-{product.get('productId')}-{order_data.get('orderNumber')}"
            }
            
            # Save product data
            product_filename = f"product_{order_data.get('orderNumber')}_{idx}_{timestamp}.json"
            product_filepath = os.path.join(DATA_PATH, product_filename)
            
            with open(product_filepath, 'w') as f:
                json.dump(product_data, f, indent=2)
            
            # Print product label
            logger.debug(f"Printing label for product: {product.get('productId')}")
            product_format = btapp.Formats.Open(PRODUCT_LABEL_TEMPLATE, False, "")
            
            # Print based on quantity
            quantity = product.get('quantity', 1)
            for _ in range(min(quantity, 10)):  # Limit to 10 labels per product
                product_format.PrintOut(False, False)
                labels_printed += 1
            
            product_format.Close(1)
            
            # Archive product JSON
            archive_product_path = os.path.join(ARCHIVE_PATH, product_filename)
            os.rename(product_filepath, archive_product_path)
        
        # Close BarTender
        btapp.Quit(1)  # SaveChanges = 1 (Yes)
        
        logger.info(f"All {labels_printed} labels printed successfully")
        
        return {'success': True, 'count': labels_printed}
        
    except Exception as e:
        logger.error(f"Error printing labels: {str(e)}")
        logger.error(traceback.format_exc())
        return {'success': False, 'error': str(e), 'count': 0}

def save_error_report(order_data, error, traceback_str):
    """Save detailed error report for troubleshooting"""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        error_filename = f"error_{timestamp}.json"
        error_filepath = os.path.join(ERROR_PATH, error_filename)
        
        error_data = {
            "timestamp": datetime.now().isoformat(),
            "orderNumber": order_data.get('orderNumber', 'Unknown'),
            "error": error,
            "traceback": traceback_str,
            "orderData": order_data,
            "systemInfo": {
                "pythonVersion": sys.version,
                "platform": sys.platform,
                "workingDirectory": os.getcwd()
            }
        }
        
        with open(error_filepath, 'w') as f:
            json.dump(error_data, f, indent=2)
            
        logger.info(f"Error report saved: {error_filepath}")
        
    except Exception as e:
        logger.error(f"Failed to save error report: {str(e)}")

@app.route('/test-print', methods=['POST'])
def test_print():
    """Test endpoint with sample data"""
    
    logger.info("Test print requested")
    
    sample_order = {
        "orderNumber": f"TEST-{datetime.now().strftime('%H%M%S')}",
        "customerPO": "PO-2024-TEST",
        "shipDate": datetime.now().strftime('%Y-%m-%d'),
        "carrier": "FedEx Ground",
        "trackingNumber": "1234567890123456",
        "packageCount": 1,
        "totalPackages": 1,
        "weight": "25.5 lbs",
        "billToCompany": "Test Customer Inc.",
        "billingAddress": "123 Test Street",
        "billToCity": "Minneapolis",
        "billToState": "MN",
        "billToZIP": "55401",
        "shipToCompany": "Test Recipient Corp.",
        "shippingAddress": "456 Delivery Ave",
        "shipToCity": "St. Paul",
        "shipToState": "MN",
        "shipToZIP": "55102",
        "products": [
            {
                "productId": "MTL-001",
                "description": "Steel Plate 1/4\" x 12\" x 24\"",
                "quantity": 2
            },
            {
                "productId": "MTL-002",
                "description": "Aluminum Angle 2\" x 2\" x 1/4\" x 8'",
                "quantity": 3
            },
            {
                "productId": "MTL-003",
                "description": "Stainless Steel Sheet 16ga 4' x 8'",
                "quantity": 1
            }
        ]
    }
    
    # Use custom data if provided
    if request.json:
        sample_order.update(request.json)
    
    # Forward to main webhook handler
    request.json = sample_order
    return receive_order()

@app.route('/logs', methods=['GET'])
def view_logs():
    """View recent log entries"""
    try:
        log_file = os.path.join('C:/BarTenderIntegration/Logs/', 
                               f'webhook_receiver_{datetime.now().strftime("%Y%m%d")}.log')
        
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                lines = f.readlines()
                # Get last 100 lines
                recent_lines = lines[-100:] if len(lines) > 100 else lines
                
            return '<pre>' + ''.join(recent_lines) + '</pre>', 200
        else:
            return "No logs found for today", 404
            
    except Exception as e:
        return f"Error reading logs: {str(e)}", 500

@app.route('/stats', methods=['GET'])
def view_stats():
    """View printing statistics"""
    try:
        # Count files in archive
        archive_files = os.listdir(ARCHIVE_PATH)
        order_count = len([f for f in archive_files if f.startswith('order_')])
        product_count = len([f for f in archive_files if f.startswith('product_')])
        
        # Count today's files
        today = datetime.now().strftime('%Y%m%d')
        today_files = [f for f in archive_files if today in f]
        
        stats = {
            "totalOrders": order_count,
            "totalProductLabels": product_count,
            "ordersToday": len([f for f in today_files if f.startswith('order_')]),
            "labelsToday": len(today_files),
            "archiveSize": f"{sum(os.path.getsize(os.path.join(ARCHIVE_PATH, f)) for f in archive_files) / 1024:.2f} KB",
            "lastUpdate": datetime.now().isoformat()
        }
        
        return jsonify(stats), 200
        
    except Exception as e:
        logger.error(f"Error generating stats: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Startup message
    print("\n" + "="*60)
    print("🏭 GREENFIELD METAL SALES - LABEL PRINT SERVICE")
    print("="*60)
    print(f"Service Version: 1.0.0")
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nEndpoints:")
    print(f"  Webhook URL: http://localhost:{config['webhook']['port']}/paradigm-webhook")
    print(f"  Health Check: http://localhost:{config['webhook']['port']}/health")
    print(f"  Test Print: http://localhost:{config['webhook']['port']}/test-print")
    print(f"  View Logs: http://localhost:{config['webhook']['port']}/logs")
    print(f"  Statistics: http://localhost:{config['webhook']['port']}/stats")
    print(f"\nLog Location: {log_filename}")
    print("\nPress Ctrl+C to stop the service")
    print("="*60 + "\n")
    
    # Run the Flask app
    app.run(host=config['webhook']['host'], port=config['webhook']['port'], debug=False)

