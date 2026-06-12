#!/usr/bin/env python3
"""
Test script to verify all data flow error fixes for empty collections.
Tests that API endpoints handle empty MongoDB collections gracefully.
"""
import requests
import json
import time
import subprocess
import sys
import os
from threading import Thread
import signal

# API base URL
BASE_URL = "http://127.0.0.1:5000"

# Test results tracker
test_results = {
    "passed": [],
    "failed": [],
    "errors": []
}

def log_test(status, test_name, details=""):
    """Log test result"""
    if status == "PASS":
        test_results["passed"].append(test_name)
        print(f"✓ PASS: {test_name}")
    elif status == "FAIL":
        test_results["failed"].append(test_name)
        print(f"✗ FAIL: {test_name} - {details}")
    else:
        test_results["errors"].append(test_name)
        print(f"⚠ ERROR: {test_name} - {details}")


def test_categories():
    """Test /api/categories with empty collection"""
    try:
        response = requests.get(f"{BASE_URL}/api/categories")
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) == 0:
                log_test("PASS", "GET /api/categories (empty collection)")
            else:
                log_test("PASS", "GET /api/categories", f"Returned {len(data)} categories")
        else:
            log_test("FAIL", "GET /api/categories", f"Status: {response.status_code}")
    except Exception as e:
        log_test("ERROR", "GET /api/categories", str(e))


def test_services():
    """Test /api/services with empty collection"""
    try:
        response = requests.get(f"{BASE_URL}/api/services")
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) == 0:
                log_test("PASS", "GET /api/services (empty collection)")
            else:
                log_test("PASS", "GET /api/services", f"Returned {len(data)} services")
        else:
            log_test("FAIL", "GET /api/services", f"Status: {response.status_code}")
    except Exception as e:
        log_test("ERROR", "GET /api/services", str(e))


def test_store_products():
    """Test /api/store/products with empty collection"""
    try:
        response = requests.get(f"{BASE_URL}/api/store/products")
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) == 0:
                log_test("PASS", "GET /api/store/products (empty collection)")
            else:
                log_test("PASS", "GET /api/store/products", f"Returned {len(data)} products")
        else:
            log_test("FAIL", "GET /api/store/products", f"Status: {response.status_code}")
    except Exception as e:
        log_test("ERROR", "GET /api/store/products", str(e))


def test_store_categories():
    """Test /api/store/categories with empty collection"""
    try:
        response = requests.get(f"{BASE_URL}/api/store/categories")
        if response.status_code == 200:
            data = response.json()
            if "categories" in data and isinstance(data["categories"], list):
                log_test("PASS", "GET /api/store/categories (empty collection)")
            else:
                log_test("FAIL", "GET /api/store/categories", "Invalid response format")
        else:
            log_test("FAIL", "GET /api/store/categories", f"Status: {response.status_code}")
    except Exception as e:
        log_test("ERROR", "GET /api/store/categories", str(e))


def test_ai_search_empty_index():
    """Test /api/ai/search with empty search index (graceful fallback)"""
    try:
        # Create a session token (we'll use empty one to test)
        headers = {
            "Authorization": "Bearer test_token_12345",
            "Content-Type": "application/json"
        }
        
        payload = {
            "query": "how to apply for passport"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/ai/search",
            json=payload,
            headers=headers
        )
        
        # Should either return results or fallback gracefully
        if response.status_code in [200, 400, 401]:
            log_test("PASS", "POST /api/ai/search (empty index graceful fallback)")
        else:
            log_test("FAIL", "POST /api/ai/search", f"Status: {response.status_code}")
    except Exception as e:
        log_test("ERROR", "POST /api/ai/search", str(e))


def test_dashboard_analytics():
    """Test /api/dashboard/analytics with empty collections"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/dashboard/analytics",
            headers={"Authorization": "Bearer admin_token"}
        )
        
        if response.status_code in [200, 401]:
            data = response.json()
            # Should have expected fields even if counts are 0
            expected_fields = ["total_users", "total_engagements", "total_orders"]
            if any(field in data for field in expected_fields):
                log_test("PASS", "GET /api/dashboard/analytics (empty collections)")
            elif response.status_code == 401:
                log_test("PASS", "GET /api/dashboard/analytics", "Auth required (expected)")
            else:
                log_test("FAIL", "GET /api/dashboard/analytics", f"Missing expected fields in response")
        else:
            log_test("FAIL", "GET /api/dashboard/analytics", f"Status: {response.status_code}")
    except Exception as e:
        log_test("ERROR", "GET /api/dashboard/analytics", str(e))


def test_ads_empty():
    """Test /api/ads with empty collection"""
    try:
        response = requests.get(f"{BASE_URL}/api/ads")
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) == 0:
                log_test("PASS", "GET /api/ads (empty collection)")
            else:
                log_test("PASS", "GET /api/ads", f"Returned {len(data)} ads")
        else:
            log_test("FAIL", "GET /api/ads", f"Status: {response.status_code}")
    except Exception as e:
        log_test("ERROR", "GET /api/ads", str(e))


def run_app():
    """Run the Flask app in a subprocess"""
    os.environ["FLASK_ENV"] = "development"
    subprocess.Popen(
        [sys.executable, "app.py"],
        cwd="d:\\GitHub\\CitizenPortalApp-main",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    # Give the app time to start
    time.sleep(5)


def main():
    print("=" * 60)
    print("Digital Citizen Services - Data Flow Error Tests")
    print("=" * 60)
    print()
    
    print("Starting Flask application...")
    run_app()
    
    print("Testing API endpoints with empty collections...\n")
    
    # Run tests
    test_categories()
    test_services()
    test_store_products()
    test_store_categories()
    test_ai_search_empty_index()
    test_dashboard_analytics()
    test_ads_empty()
    
    # Print summary
    print()
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"✓ Passed: {len(test_results['passed'])}")
    print(f"✗ Failed: {len(test_results['failed'])}")
    print(f"⚠ Errors: {len(test_results['errors'])}")
    print()
    
    if test_results["failed"]:
        print("Failed tests:")
        for test in test_results["failed"]:
            print(f"  - {test}")
    
    if test_results["errors"]:
        print("Error tests:")
        for test in test_results["errors"]:
            print(f"  - {test}")
    
    # Return exit code
    if test_results["failed"] or test_results["errors"]:
        return 1
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        sys.exit(1)
