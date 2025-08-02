"""
Greenfield Metal Sales - Integration Test Script
Tests the complete flow: Paradigm API → Webhook → BarTender
"""
import json
import requests
import time
import os
import sys
from datetime import datetime

# Load configuration
with open('config.json', 'r') as f:
    config = json.load(f)

class IntegrationTester:
    def __init__(self):
        self.config = config
        self.test_results = []
        
    def log(self, message, status="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {status}: {message}")
        self.test_results.append({"time": timestamp, "status": status, "message": message})
        
    def test_paradigm_connection(self):
        """Test 1: Verify Paradigm API connectivity"""
        self.log("Testing Paradigm API connection...", "TEST")
        try:
            headers = {
                "Authorization": f"Bearer {self.config['paradigm']['bearer_token']}",
                "x-api-key": self.config['paradigm']['api_key'],
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            url = f"{self.config['paradigm']['api_base_url']}/SalesOrder/0/1"
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                self.log("✓ Paradigm API connection successful", "PASS")
                return True
            else:
                self.log(f"✗ Paradigm API returned status {response.status_code}", "FAIL")
                return False
                
        except Exception as e:
            self.log(f"✗ Paradigm API error: {str(e)}", "FAIL")
            return False
            
    def test_webhook_service(self):
        """Test 2: Check if webhook service is running"""
        self.log("Testing webhook service...", "TEST")
        try:
            response = requests.get(f"http://localhost:{self.config['webhook']['port']}/health", timeout=5)
            if response.status_code == 200:
                self.log("✓ Webhook service is running", "PASS")
                return True
            else:
                self.log(f"✗ Webhook service returned status {response.status_code}", "FAIL")
                return False
        except:
            self.log("✗ Webhook service is not running", "FAIL")
            self.log("  Run: python WebhookReceiver/webhook_receiver.py", "INFO")
            return False
            
    def test_bartender_installation(self):
        """Test 3: Verify BarTender is installed"""
        self.log("Testing BarTender installation...", "TEST")
        
        if os.path.exists(self.config['bartender']['executable_path']):
            self.log("✓ BarTender executable found", "PASS")
            
            # Check templates
            template_path = os.path.join(
                self.config['bartender']['templates_path'],
                self.config['bartender']['packing_list_template']
            )
            
            if os.path.exists(template_path):
                self.log("✓ Packing list template found", "PASS")
                return True
            else:
                self.log(f"✗ Template not found: {template_path}", "FAIL")
                return False
        else:
            self.log("✗ BarTender not found at configured path", "FAIL")
            return False
            
    def test_directory_structure(self):
        """Test 4: Verify all required directories exist"""
        self.log("Testing directory structure...", "TEST")
        all_good = True
        
        for path_name, path_value in self.config['paths'].items():
            if os.path.exists(path_value):
                self.log(f"✓ {path_name}: {path_value}", "PASS")
            else:
                self.log(f"✗ Missing: {path_value}", "FAIL")
                os.makedirs(path_value, exist_ok=True)
                self.log(f"  Created: {path_value}", "INFO")
                
        return all_good
        
    def test_sample_order_print(self):
        """Test 5: Send a sample order to webhook"""
        self.log("Testing sample order printing...", "TEST")
        
        if not self.test_webhook_service():
            self.log("Skipping print test - webhook service not running", "SKIP")
            return False
            
        # Sample order data
        sample_order = {
            "orderNumber": "TEST-" + datetime.now().strftime("%Y%m%d-%H%M%S"),
            "customerPO": "TEST-PO-001",
            "shipDate": datetime.now().strftime("%Y-%m-%d"),
            "billToCompany": "Test Customer Inc.",
            "billingAddress": "123 Test Street",
            "billToCity": "Minneapolis",
            "billToState": "MN",
            "billToZIP": "55401",
            "shipToCompany": "Test Customer Inc.",
            "shippingAddress": "123 Test Street",
            "shipToCity": "Minneapolis",
            "shipToState": "MN",
            "shipToZIP": "55401",
            "products": [
                {
                    "productId": "TEST-001",
                    "description": "Test Product - Steel Sheet 4x8",
                    "quantity": 10
                }
            ]
        }
        
        try:
            response = requests.post(
                f"http://localhost:{self.config['webhook']['port']}/paradigm-webhook",
                json=sample_order,
                timeout=30
            )
            
            if response.status_code == 200:
                self.log("✓ Sample order processed successfully", "PASS")
                self.log(f"  Response: {response.json()}", "INFO")
                return True
            else:
                self.log(f"✗ Order processing failed: {response.status_code}", "FAIL")
                return False
                
        except Exception as e:
            self.log(f"✗ Error sending test order: {str(e)}", "FAIL")
            return False
            
    def run_all_tests(self):
        """Run all integration tests"""
        print("="*60)
        print("GREENFIELD METAL SALES - INTEGRATION TEST SUITE")
        print("="*60)
        
        tests = [
            self.test_paradigm_connection,
            self.test_directory_structure,
            self.test_bartender_installation,
            self.test_webhook_service,
            self.test_sample_order_print
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            result = test()
            if result:
                passed += 1
            else:
                failed += 1
                
        print("="*60)
        print(f"RESULTS: {passed} passed, {failed} failed")
        print("="*60)
        
        # Save test results
        with open('test_results.json', 'w') as f:
            json.dump({
                "test_date": datetime.now().isoformat(),
                "passed": passed,
                "failed": failed,
                "results": self.test_results
            }, f, indent=2)
            
        return failed == 0

if __name__ == "__main__":
    tester = IntegrationTester()
    success = tester.run_all_tests()
    
    if not success:
        print("\n⚠️  Some tests failed. Fix issues before proceeding.")
        print("📋 See test_results.json for details")
    else:
        print("\n✅ All tests passed! Ready for deployment.")
        
    sys.exit(0 if success else 1) 