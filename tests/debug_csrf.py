#!/usr/bin/env python3
"""
Detailed CSRF Debug Test
"""

import requests
import json

def debug_csrf():
    """Debug CSRF protection in detail"""
    base_url = "http://127.0.0.1:5000"
    
    print("🔍 Debugging CSRF Protection...")
    print("=" * 50)
    
    # Test 1: Get login page and extract CSRF token
    print("\n1️⃣ Getting CSRF Token...")
    try:
        session = requests.Session()
        response = session.get(f"{base_url}/auth/login")
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            # Extract CSRF token from form
            import re
            csrf_match = re.search(r'name="csrf_token" value="([^"]+)"', response.text)
            if csrf_match:
                csrf_token = csrf_match.group(1)
                print(f"✅ CSRF Token: {csrf_token}")
                
                # Test 2: Submit with valid token
                print("\n2️⃣ Testing with valid CSRF token...")
                login_data = {
                    'username': 'testuser',
                    'password': 'testpass123',
                    'csrf_token': csrf_token
                }
                
                response2 = session.post(f"{base_url}/auth/login", data=login_data)
                print(f"Status Code: {response2.status_code}")
                print(f"Response Text: {response2.text[:500]}...")
                
                # Test 3: Submit with invalid token
                print("\n3️⃣ Testing with invalid CSRF token...")
                login_data_invalid = {
                    'username': 'testuser',
                    'password': 'testpass123',
                    'csrf_token': 'invalid_token_12345'
                }
                
                response3 = session.post(f"{base_url}/auth/login", data=login_data_invalid)
                print(f"Status Code: {response3.status_code}")
                print(f"Response Text: {response3.text[:500]}...")
                
            else:
                print("❌ No CSRF token found in form")
        else:
            print(f"❌ Failed to get login page: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_csrf()
