from flask import Flask, request, jsonify
import requests
import json
import logging
import os
import csv
import win32com.client
from datetime import datetime

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Paradigm API Configuration (WORKING!)
API_BASE_URL = "https://greenfieldapi.para-apps.com/api"
API_KEY = "nVPsQFBteV&GEd7*8n0%RliVjksag8"
BEARER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJVc2VyTmFtZSI6IldlYl9BZG1pbiIsIlN0clBhcmFkaWdtVXNlciI6IldlYl9BZG1pbiIsIlN0ckZpcnN0TmFtZSI6IldlYiIsIlN0ckxhc3ROYW1lIjoiQWRtaW4iLCJleHAiOjE3NTI4Mjk3NDAsImlzcyI6IlBhcmFkaWdtIiwiYXVkIjoiUGFyYWRpZ20ifQ.hO_49X_jO5AKQmHz468jp80j6jYlZ8HNLLi8P2qwQUM"

# Create headers for API calls
HEADERS = {
    "Authorization": f"Bearer {BEARER_TOKEN}",
    "x-api-key": API_KEY,
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# Paths
DATA_PATH = "C:/BarTenderIntegration/Data/OrderData/"
TEMPLATES_PATH = "C:/BarTenderIntegration/Templates/"
BARTENDER_PATH = "C:/Program Files/Seagull/BarTender 11.4/BarTend.exe"

def get_all_orders():
    """Get all orders from Paradigm"""
    try:
        # Get orders with pagination (skip=0, take=100)
        url = f"{API_BASE_URL}/SalesOrder/0/100"
        response = requests.get(url, headers=HEADERS, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Failed to get orders: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"Error getting orders: {str(e)}")
        return None

def find_order_by_number(order_number):
    """Find a specific order by order number"""
    try:
        logger.info(f"Searching for order: {order_number}")
        
        # Get all orders
        orders = get_all_orders()
        if not orders:
            return None
        
        # Search for the specific order
        for order in orders:
            if (order.get('strOrderNumber') == order_number or 
                order.get('strOrderNumber', '').upper() == order_number.upper()):
                logger.info(f"Found order: {order_number}")
                return order
        
        logger.warning(f"Order {order_number} not found")
        return None
        
    except Exception as e:
        logger.error(f"Error finding order {order_number}: {str(e)}")
        return None

def get_order_details(order_id):
    """Get order line items/details"""
    try:
        # Try to get order details - we may need to explore the API more
        # For now, we'll use the order data we have
        url = f"{API_BASE_URL}/SalesOrderDetail/{order_id}"
        response = requests.get(url, headers=HEADERS, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.warning(f"Could not get order details for {order_id}: {response.status_code}")
            return []
            
    except Exception as e:
        logger.warning(f"Error getting order details: {str(e)}")
        return []

def format_order_for_bartender(order_data, order_details=None):
    """Format Paradigm order data for BarTender"""
    try:
        # Extract customer information
        customer_name = order_data.get('strCustomerName', '')
        
        # Format the data for BarTender
        formatted_data = {
            'orderNumber': order_data.get('strOrderNumber', ''),
            'customerPO': order_data.get('strCustomerPO', ''),
            'orderDate': order_data.get('dtOrderDate', ''),
            'customerName': customer_name,
            'billToCompany': customer_name,
            'billToAddress': order_data.get('strBillToAddress1', ''),
            'billToCity': order_data.get('strBillToCity', ''),
            'billToState': order_data.get('strBillToState', ''),
            'billToZIP': order_data.get('strBillToZip', ''),
            'shipToCompany': order_data.get('strShipToCompany', customer_name),
            'shipToAddress': order_data.get('strShipToAddress1', ''),
            'shipToCity': order_data.get('strShipToCity', ''),
            'shipToState': order_data.get('strShipToState', ''),
            'shipToZIP': order_data.get('strShipToZip', ''),
            'totalAmount': order_data.get('decTotal', 0),
            'products': []
        }
        
        # Add order details/line items if available
        if order_details:
            for detail in order_details:
                product = {
                    'productId': detail.get('strItemNumber', ''),
                    'description': detail.get('strDescription', ''),
                    'quantity': detail.get('decQuantity', 0),
                    'unitPrice': detail.get('decUnitPrice', 0),
                    'extendedPrice': detail.get('decExtendedPrice', 0)
                }
                formatted_data['products'].append(product)
        else:
            # If no details available, create a placeholder
            formatted_data['products'].append({
                'productId': 'N/A',
                'description': 'Order details not available',
                'quantity': 1,
                'unitPrice': formatted_data['totalAmount'],
                'extendedPrice': formatted_data['totalAmount']
            })
        
        return formatted_data
        
    except Exception as e:
        logger.error(f"Error formatting order data: {str(e)}")
        return None

def create_bartender_csv(order_data, filename):
    """Create CSV file for BarTender"""
    try:
        filepath = os.path.join(DATA_PATH, filename)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            # Write order header
            writer = csv.writer(csvfile)
            
            # Header row
            writer.writerow([
                'orderNumber', 'customerPO', 'orderDate', 'customerName',
                'billToCompany', 'billToAddress', 'billToCity', 'billToState', 'billToZIP',
                'shipToCompany', 'shipToAddress', 'shipToCity', 'shipToState', 'shipToZIP',
                'totalAmount'
            ])
            
            # Data row
            writer.writerow([
                order_data['orderNumber'], order_data['customerPO'], order_data['orderDate'],
                order_data['customerName'], order_data['billToCompany'], order_data['billToAddress'],
                order_data['billToCity'], order_data['billToState'], order_data['billToZIP'],
                order_data['shipToCompany'], order_data['shipToAddress'], order_data['shipToCity'],
                order_data['shipToState'], order_data['shipToZIP'], order_data['totalAmount']
            ])
            
            # Empty row
            writer.writerow([])
            
            # Products header
            writer.writerow(['productId', 'description', 'quantity', 'unitPrice', 'extendedPrice'])
            
            # Products data
            for product in order_data['products']:
                writer.writerow([
                    product['productId'], product['description'], product['quantity'],
                    product['unitPrice'], product['extendedPrice']
                ])
        
        logger.info(f"CSV created: {filepath}")
        return filepath
        
    except Exception as e:
        logger.error(f"Error creating CSV: {str(e)}")
        return None

@app.route('/')
def home():
    return '''
    <h1>🏭 Greenfield Metal Sales - Paradigm Integration</h1>
    <p><strong>Status:</strong> ✅ Connected to Paradigm API</p>
    <p><strong>Base URL:</strong> https://greenfieldapi.para-apps.com/api</p>
    
    <h2>Available Endpoints:</h2>
    <ul>
        <li><code>GET /api/orders</code> - List all orders</li>
        <li><code>GET /api/order/&lt;order_number&gt;</code> - Get specific order</li>
        <li><code>POST /api/print-label</code> - Print label for order</li>
        <li><code>GET /api/test</code> - Test API connection</li>
    </ul>
    
    <h2>Usage Examples:</h2>
    <p><code>/api/order/0005915</code> - Get order details</p>
    <p><code>/api/print-label</code> with JSON: <code>{"order_number": "0005915"}</code></p>
    '''

@app.route('/api/test')
def test_connection():
    """Test Paradigm API connection"""
    try:
        orders = get_all_orders()
        if orders:
            return jsonify({
                "status": "success",
                "message": "Connected to Paradigm API",
                "orders_found": len(orders),
                "sample_order": orders[0] if orders else None
            })
        else:
            return jsonify({
                "status": "error",
                "message": "Could not retrieve orders"
            }), 500
            
    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": str(e)
        }), 500

@app.route('/api/orders')
def list_orders():
    """Get all orders from Paradigm"""
    try:
        orders = get_all_orders()
        if orders:
            # Return simplified list
            order_list = []
            for order in orders:
                order_list.append({
                    'orderNumber': order.get('strOrderNumber'),
                    'customerName': order.get('strCustomerName'),
                    'orderDate': order.get('dtOrderDate'),
                    'total': order.get('decTotal')
                })
            
            return jsonify({
                "status": "success",
                "orders": order_list
            })
        else:
            return jsonify({
                "status": "error",
                "message": "No orders found"
            }), 404
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/order/<order_number>')
def get_order(order_number):
    """Get specific order by order number"""
    try:
        logger.info(f"API request for order: {order_number}")
        
        # Find the order
        order_data = find_order_by_number(order_number)
        if not order_data:
            return jsonify({
                "status": "error",
                "message": f"Order {order_number} not found"
            }), 404
        
        # Try to get order details
        order_id = order_data.get('intOrderId')
        order_details = get_order_details(order_id) if order_id else None
        
        # Format for BarTender
        formatted_data = format_order_for_bartender(order_data, order_details)
        if not formatted_data:
            return jsonify({
                "status": "error",
                "message": "Failed to format order data"
            }), 500
        
        # Create CSV file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_filename = f"order_{order_number}_{timestamp}.csv"
        csv_path = create_bartender_csv(formatted_data, csv_filename)
        
        return jsonify({
            "status": "success",
            "order": formatted_data,
            "csv_file": csv_path,
            "raw_paradigm_data": order_data
        })
        
    except Exception as e:
        logger.error(f"Error getting order {order_number}: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/print-label', methods=['POST'])
def print_label():
    """Print label for specified order"""
    try:
        data = request.json
        order_number = data.get('order_number')
        
        if not order_number:
            return jsonify({
                "status": "error",
                "message": "order_number is required"
            }), 400
        
        # Get order data
        order_response = get_order(order_number)
        if order_response[1] != 200:
            return order_response
        
        order_info = order_response[0].get_json()
        csv_file = order_info.get('csv_file')
        
        if not csv_file or not os.path.exists(csv_file):
            return jsonify({
                "status": "error",
                "message": "CSV file not found"
            }), 500
        
        # Print with BarTender
        try:
            btapp = win32com.client.Dispatch("BarTender.Application")
            btapp.Visible = False
            
            template_path = os.path.join(TEMPLATES_PATH, "PackingList.btw")
            if not os.path.exists(template_path):
                return jsonify({
                    "status": "error",
                    "message": f"Template not found: {template_path}"
                }), 500
            
            format_doc = btapp.Formats.Open(template_path, False, "")
            format_doc.PrintOut(False, False)
            format_doc.Close(1)
            btapp.Quit(1)
            
            return jsonify({
                "status": "success",
                "message": f"Label printed for order {order_number}",
                "csv_file": csv_file
            })
            
        except Exception as bt_error:
            return jsonify({
                "status": "error",
                "message": f"BarTender error: {str(bt_error)}"
            }), 500
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    # Create directories
    os.makedirs(DATA_PATH, exist_ok=True)
    
    print("="*60)
    print("🏭 GREENFIELD METAL SALES - PARADIGM INTEGRATION")
    print("="*60)
    print(f"API Base: {API_BASE_URL}")
    print(f"Local URL: http://localhost:5003")
    print(f"Test: http://localhost:5003/api/test")
    print(f"Orders: http://localhost:5003/api/orders")
    print("="*60)
    
    app.run(host='0.0.0.0', port=5003, debug=True)
