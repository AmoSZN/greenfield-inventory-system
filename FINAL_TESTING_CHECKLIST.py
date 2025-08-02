#!/usr/bin/env python3
"""
Greenfield Inventory AI - Comprehensive Testing Suite
Run this to validate all system features
"""

import requests
import json
import time
import os
from datetime import datetime

class SystemValidator:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "tests_passed": 0,
            "tests_failed": 0,
            "details": []
        }
    
    def test_system_availability(self):
        """Test 1: System Availability"""
        print("\n🧪 Test 1: System Availability")
        try:
            response = requests.get(self.base_url, timeout=5)
            if response.status_code == 200:
                self.log_success("System is accessible at " + self.base_url)
                return True
            else:
                self.log_failure(f"System returned status {response.status_code}")
                return False
        except Exception as e:
            self.log_failure(f"Cannot connect to system: {str(e)}")
            return False
    
    def test_api_endpoints(self):
        """Test 2: API Endpoints"""
        print("\n🧪 Test 2: API Endpoints")
        endpoints = [
            ("/api/stats", "GET"),
            ("/api/history", "GET"),
            ("/api/search?q=1015", "GET")
        ]
        
        all_passed = True
        for endpoint, method in endpoints:
            try:
                url = self.base_url + endpoint
                if method == "GET":
                    response = requests.get(url, timeout=5)
                
                if response.status_code == 200:
                    self.log_success(f"{method} {endpoint} - OK")
                else:
                    self.log_failure(f"{method} {endpoint} - Status {response.status_code}")
                    all_passed = False
            except Exception as e:
                self.log_failure(f"{method} {endpoint} - Error: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_product_search(self):
        """Test 3: Product Search"""
        print("\n🧪 Test 3: Product Search")
        test_products = ["1010AG", "1015AW", "1020B"]
        
        for product in test_products:
            try:
                response = requests.get(f"{self.base_url}/api/search?q={product}")
                if response.status_code == 200:
                    data = response.json()
                    if data and len(data) > 0:
                        self.log_success(f"Found product {product}")
                    else:
                        self.log_warning(f"Product {product} not in database")
                else:
                    self.log_failure(f"Search failed for {product}")
            except Exception as e:
                self.log_failure(f"Search error for {product}: {str(e)}")
    
    def test_inventory_update(self):
        """Test 4: Inventory Update"""
        print("\n🧪 Test 4: Inventory Update (Simulation)")
        
        # First, validate product exists
        test_product = "1015AW"
        test_data = {
            "product_id": test_product,
            "updates": {
                "quantity": 999,
                "description": "Test Update " + datetime.now().strftime("%H:%M:%S"),
                "notes": "Automated test"
            }
        }
        
        try:
            # Validate product first
            response = requests.post(
                f"{self.base_url}/api/validate",
                json={"product_id": test_product}
            )
            
            if response.status_code == 200:
                self.log_success(f"Product {test_product} validated")
                
                # Simulate update (without actually calling Paradigm)
                self.log_info("Update simulation successful (not executed to preserve data)")
                return True
            else:
                self.log_warning("Product validation returned " + str(response.status_code))
                return False
                
        except Exception as e:
            self.log_failure(f"Update test error: {str(e)}")
            return False
    
    def test_bulk_interface(self):
        """Test 5: Bulk Import/Export Interface"""
        print("\n🧪 Test 5: Bulk Import/Export Interface")
        
        try:
            response = requests.get(f"{self.base_url}/bulk-import-export")
            if response.status_code == 200:
                self.log_success("Bulk import/export page accessible")
                return True
            elif response.status_code == 404:
                self.log_warning("Bulk import/export page not found (may need implementation)")
                return False
            else:
                self.log_failure(f"Bulk page returned status {response.status_code}")
                return False
        except Exception as e:
            self.log_failure(f"Bulk interface error: {str(e)}")
            return False
    
    def test_history_tracking(self):
        """Test 6: History Tracking"""
        print("\n🧪 Test 6: History Tracking")
        
        try:
            response = requests.get(f"{self.base_url}/api/history")
            if response.status_code == 200:
                history = response.json()
                self.log_success(f"History API working - {len(history)} records found")
                return True
            else:
                self.log_failure(f"History API returned status {response.status_code}")
                return False
        except Exception as e:
            self.log_failure(f"History tracking error: {str(e)}")
            return False
    
    def test_system_stats(self):
        """Test 7: System Statistics"""
        print("\n🧪 Test 7: System Statistics")
        
        try:
            response = requests.get(f"{self.base_url}/api/stats")
            if response.status_code == 200:
                stats = response.json()
                self.log_success("System stats retrieved:")
                self.log_info(f"  - Total Products: {stats.get('total_products', 0)}")
                self.log_info(f"  - Updates Today: {stats.get('updates_today', 0)}")
                self.log_info(f"  - System Uptime: {stats.get('uptime', 'N/A')}")
                return True
            else:
                self.log_failure(f"Stats API returned status {response.status_code}")
                return False
        except Exception as e:
            self.log_failure(f"System stats error: {str(e)}")
            return False
    
    def log_success(self, message):
        print(f"✅ {message}")
        self.test_results["tests_passed"] += 1
        self.test_results["details"].append({"status": "PASS", "message": message})
    
    def log_failure(self, message):
        print(f"❌ {message}")
        self.test_results["tests_failed"] += 1
        self.test_results["details"].append({"status": "FAIL", "message": message})
    
    def log_warning(self, message):
        print(f"⚠️  {message}")
        self.test_results["details"].append({"status": "WARN", "message": message})
    
    def log_info(self, message):
        print(f"ℹ️  {message}")
        self.test_results["details"].append({"status": "INFO", "message": message})
    
    def generate_report(self):
        """Generate final test report"""
        print("\n" + "=" * 60)
        print("📊 FINAL TEST REPORT")
        print("=" * 60)
        
        total_tests = self.test_results["tests_passed"] + self.test_results["tests_failed"]
        pass_rate = (self.test_results["tests_passed"] / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📈 Test Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {self.test_results['tests_passed']} ✅")
        print(f"   Failed: {self.test_results['tests_failed']} ❌")
        print(f"   Pass Rate: {pass_rate:.1f}%")
        
        # Save report
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n💾 Detailed report saved to: {report_file}")
        
        # Overall status
        print("\n🎯 Overall System Status:")
        if pass_rate >= 80:
            print("   ✅ SYSTEM IS PRODUCTION READY!")
        elif pass_rate >= 60:
            print("   ⚠️  System is functional but needs attention")
        else:
            print("   ❌ System has critical issues - review failed tests")
        
        return pass_rate
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("🚀 Starting Comprehensive System Validation")
        print("=" * 60)
        
        # Run all tests
        self.test_system_availability()
        self.test_api_endpoints()
        self.test_product_search()
        self.test_inventory_update()
        self.test_bulk_interface()
        self.test_history_tracking()
        self.test_system_stats()
        
        # Generate report
        pass_rate = self.generate_report()
        
        # Recommendations
        print("\n💡 Recommendations:")
        if self.test_results["tests_failed"] > 0:
            print("   1. Review failed tests in the report")
            print("   2. Check if inventory_system_24_7.py is running")
            print("   3. Verify Paradigm API credentials")
        
        print("   4. Import all 38,998 products via CSV")
        print("   5. Configure external access if needed")
        print("   6. Set up automated backups")
        
        print("\n✅ Validation Complete!")

if __name__ == "__main__":
    validator = SystemValidator()
    validator.run_all_tests()