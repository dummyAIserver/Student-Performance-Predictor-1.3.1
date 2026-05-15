#!/usr/bin/env python3
"""
CSRF Protection Test Script
Tests CSRF token generation and validation
"""

import requests
import re
from bs4 import BeautifulSoup

def test_csrf_protection():
    """Test CSRF protection functionality"""
    base_url = "http://127.0.0.1:5000"
    
    print("🧪 Testing CSRF Protection...")
    print("=" * 50)
    
    # Test 1: Check if CSRF token is generated in login form
    print("\n1️⃣ Testing CSRF Token Generation...")
    try:
        response = requests.get(f"{base_url}/auth/login")
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            csrf_token = soup.find('input', {'name': 'csrf_token'})
            
            if csrf_token and csrf_token.get('value'):
                print(f"✅ CSRF Token Found: {csrf_token['value'][:20]}...")
            else:
                print("❌ No CSRF Token Found")
        else:
            print(f"❌ Login Page Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error accessing login page: {e}")
    
    # Test 2: Test CSRF protection with invalid token
    print("\n2️⃣ Testing CSRF Token Validation...")
    try:
        session = requests.Session()
        login_data = {
            'username': 'testuser',
            'password': 'testpass',
            'csrf_token': 'invalid_token_12345'
        }
        
        response = session.post(f"{base_url}/auth/login", data=login_data)
        
        if response.status_code == 200:
            if "Invalid CSRF token" in response.text:
                print("✅ CSRF Protection Working - Invalid token rejected")
            else:
                print("❌ CSRF Protection Failed - Invalid token accepted")
        else:
            print(f"❌ Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing CSRF validation: {e}")
    
    # Test 3: Test CSRF protection without token
    print("\n3️⃣ Testing CSRF Protection Without Token...")
    try:
        login_data_no_token = {
            'username': 'testuser',
            'password': 'testpass'
        }
        
        response = session.post(f"{base_url}/auth/login", data=login_data_no_token)
        
        if response.status_code == 200:
            if "Invalid CSRF token" in response.text:
                print("✅ CSRF Protection Working - Missing token rejected")
            else:
                print("❌ CSRF Protection Failed - Missing token accepted")
        else:
            print(f"❌ Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing CSRF without token: {e}")
    
    print("\n" + "=" * 50)
    print("🧪 CSRF Protection Test Complete!")

if __name__ == "__main__":
    test_csrf_protection()
