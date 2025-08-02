#!/usr/bin/env python3
"""
Comprehensive System Test Suite
"""

import requests
import json
import time
import csv
from datetime import datetime

def test_system():
    """Run comprehensive system tests"""
    
    print("🧪 COMPREHENSIVE SYSTEM TEST SUITE")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    results = []
    
    def test_endpoint(name, method, url, data=None, expected_status=200):
        """Test a single endpoint"""
        try:
            if method == "GET":
                response = requests.get(f"{base_url}{url}", timeout=10)
            elif method == "POST":
                response = requests.post(f"{base_url}{url}", json=data, timeout=10)
            
            success = response.status_code == expected_status
            results.append({
                "test": name,
                "status": "✅ PASS" if success else "❌ FAIL",
                "code": response.status_code,
                "expected": expected_status
            })
            
            if success:
                print(f"   ✅ {name}")
            else:
                print(f"   ❌ {name} - Got {response.status_code}, expected {expected_status}")
                
            return success, response
            
        except Exception as e:
            results.append({
                "test": name,
                "status": "❌ ERROR",
                "code": "N/A",
                "expected": expected_status,
                "error": str(e)
            })
            print(f"   ❌ {name} - Error: {e}")
            return False, None
    
    # Test 1: Basic System Health
    print("\n1️⃣ SYSTEM HEALTH TESTS")
    test_endpoint("Dashboard Load", "GET", "/")
    test_endpoint("API Stats", "GET", "/api/stats")
    test_endpoint("Update History", "GET", "/api/history")
    
    # Test 2: Search Functionality
    print("\n2️⃣ SEARCH FUNCTIONALITY")
    test_endpoint("Search by ID", "GET", "/api/search?q=1015B")
    test_endpoint("Search by Description", "GET", "/api/search?q=screws")
    test_endpoint("Search Aluminum Products", "GET", "/api/search?q=aluminum")
    test_endpoint("Empty Search", "GET", "/api/search?q=")
    
    # Test 3: Inventory Updates
    print("\n3️⃣ INVENTORY UPDATE TESTS")
    
    # Test quantity update (should be local only)
    success, response = test_endpoint("Quantity Update", "POST", "/api/update", {
        "product_id": "1015B",
        "updates": {"quantity": 999}
    })
    
    if success and response:
        result = response.json()
        if "locally only" in result.get('data', '').lower():
            print("      ✅ Proper local-only warning shown")
        else:
            print("      ⚠️  Warning message unclear")
    
    # Test description update (should sync to Paradigm)
    success, response = test_endpoint("Description Update", "POST", "/api/update", {
        "product_id": "1015B", 
        "updates": {"description": f"Test Description Update - {datetime.now().strftime('%H:%M:%S')}"}
    })
    
    if success and response:
        result = response.json()
        if "paradigm" in result.get('data', '').lower():
            print("      ✅ Paradigm sync confirmed")
        else:
            print("      ⚠️  Paradigm sync unclear")
    
    # Test mixed update
    test_endpoint("Mixed Update", "POST", "/api/update", {
        "product_id": "1015B",
        "updates": {
            "quantity": 888,
            "description": f"Mixed Update Test - {datetime.now().strftime('%H:%M:%S')}"
        }
    })
    
    # Test 4: Product Validation
    print("\n4️⃣ PRODUCT VALIDATION")
    test_endpoint("Valid Product", "POST", "/api/validate", {"product_id": "1015B"})
    test_endpoint("Invalid Product", "POST", "/api/validate", {"product_id": "INVALID123"})
    
    # Test 5: Natural Language Processing
    print("\n5️⃣ NATURAL LANGUAGE TESTS")
    nl_commands = [
        "Add 50 units to product 1015B",
        "Update 1020B quantity to 200",
        "Set description for 1010AG to Premium Aluminum Grade A",
        "Increase inventory for 1025AW by 100 units"
    ]
    
    for i, command in enumerate(nl_commands, 1):
        test_endpoint(f"NL Command {i}", "POST", "/api/natural", {"command": command})
    
    # Test 6: Error Handling
    print("\n6️⃣ ERROR HANDLING TESTS")
    test_endpoint("Missing Product ID", "POST", "/api/update", {"updates": {"quantity": 100}}, 400)
    test_endpoint("Invalid JSON", "POST", "/api/update", "invalid json", 400)
    test_endpoint("Empty Update", "POST", "/api/update", {"product_id": "1015B", "updates": {}}, 400)
    
    # Test 7: Performance Tests
    print("\n7️⃣ PERFORMANCE TESTS")
    start_time = time.time()
    
    # Rapid fire searches
    for i in range(10):
        test_endpoint(f"Rapid Search {i+1}", "GET", f"/api/search?q=101{i}")
    
    search_time = time.time() - start_time
    print(f"      📊 10 searches completed in {search_time:.2f}s")
    
    # Test 8: Data Integrity
    print("\n8️⃣ DATA INTEGRITY TESTS")
    
    # Get current stats
    success, response = test_endpoint("Current Stats", "GET", "/api/stats")
    if success and response:
        stats = response.json()
        items_count = stats.get('items_loaded', 0)
        print(f"      📊 Items in database: {items_count:,}")
        
        if items_count > 39000:
            print("      ✅ Full inventory loaded")
        else:
            print("      ⚠️  Inventory may be incomplete")
    
    # Summary Report
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY REPORT")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = len([r for r in results if "✅" in r["status"]])
    failed_tests = len([r for r in results if "❌" in r["status"]])
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests} ✅")
    print(f"Failed: {failed_tests} ❌")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    # Detailed Results
    print(f"\n📋 DETAILED RESULTS:")
    for result in results:
        status_icon = "✅" if "✅" in result["status"] else "❌"
        print(f"   {status_icon} {result['test']:<30} {result['code']}")
        if 'error' in result:
            print(f"      Error: {result['error']}")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"test_report_{timestamp}.json"
    
    with open(report_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": f"{(passed_tests/total_tests)*100:.1f}%"
            },
            "results": results
        }, f, indent=2)
    
    print(f"\n💾 Report saved: {report_file}")
    
    # Recommendations
    print(f"\n🎯 RECOMMENDATIONS:")
    if failed_tests == 0:
        print("   🎉 All tests passed! System is ready for production.")
    elif failed_tests < 3:
        print("   ⚠️  Minor issues detected. Review failed tests.")
    else:
        print("   🚨 Multiple failures detected. System needs attention.")
    
    print(f"\n🌐 System Access:")
    print(f"   Local: http://localhost:8000")
    print(f"   Network: http://192.168.12.78:8000")

if __name__ == "__main__":
    test_system()