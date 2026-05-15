#!/usr/bin/env python3
"""
Single Email Validation Test
Tests email validation without rate limiting issues
"""

import requests
import time

def test_email_single():
    """Test email validation with single request"""
    base_url = "http://127.0.0.1:5000"
    
    print("📧 Single Email Validation Test...")
    print("=" * 50)
    
    # Test valid email
    print("\n📧 Testing valid email: user@example.com")
    try:
        session = requests.Session()
        response = session.get(f"{base_url}/auth/register")
        
        if response.status_code == 200:
            # Extract CSRF token
            import re
            csrf_match = re.search(r'name="csrf_token" value="([^"]+)"', response.text)
            csrf_token = csrf_match.group(1) if csrf_match else ""
            
            reg_data = {
                'username': 'testuser789',
                'email': 'user@example.com',
                'password': 'TestPass123!',
                'confirm_password': 'TestPass123!',
                'role': 'student',
                'csrf_token': csrf_token
            }
            
            response2 = session.post(f"{base_url}/auth/register", data=reg_data)
            
            if response2.status_code == 200:
                if "Registration successful" in response2.text:
                    print("   ✅ PASS - Valid email accepted")
                elif "Email already registered" in response2.text:
                    print("   ✅ PASS - Email already exists (normal)")
                else:
                    print(f"   ❓ UNEXPECTED - Response: {response2.text[:200]}...")
            elif response2.status_code == 429:
                print("   ⏱️ RATE LIMITED - Try again later")
            else:
                print(f"   ❓ UNEXPECTED - Status: {response2.status_code}")
        else:
            print(f"   ❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("📧 Single Email Validation Test Complete!")

if __name__ == "__main__":
    test_email_single()
