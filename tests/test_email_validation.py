#!/usr/bin/env python3
"""
Email Validation Test Script
Tests improved email validation with various edge cases
"""

import requests
import re

def test_email_validation():
    """Test email validation functionality"""
    base_url = "http://127.0.0.1:5000"
    
    print("📧 Testing Email Validation...")
    print("=" * 50)
    
    # Test cases: (email, expected_result, description)
    test_cases = [
        ("user@example.com", True, "Valid email"),
        ("test.user@domain.co.uk", True, "Valid email with subdomain"),
        ("user+tag@example.org", True, "Valid email with plus tag"),
        ("user123@test-domain.com", True, "Valid email with numbers"),
        ("invalid-email", False, "Missing @ symbol"),
        ("@example.com", False, "Missing username"),
        ("user@", False, "Missing domain"),
        ("user@.com", False, "Missing domain name"),
        ("user@example.", False, "Missing TLD"),
        ("user.example.com", False, "Multiple @ symbols"),
        ("user@example.c", False, "TLD too short"),
        ("a@b", False, "Too short - old validation would pass"),
        ("user name@example.com", False, "Space in username"),
        ("user@ex ample.com", False, "Space in domain"),
        ("user@ex-ample.com", True, "Valid with hyphen in domain"),
        ("user_name@example.com", True, "Valid with underscore in username"),
        ("user@example-domain.com", True, "Valid with hyphen in domain"),
    ]
    
    for email, should_pass, description in test_cases:
        print(f"\n📧 Testing: {email}")
        print(f"   Description: {description}")
        print(f"   Expected: {'PASS' if should_pass else 'FAIL'}")
        
        try:
            # Test registration with this email
            session = requests.Session()
            response = session.get(f"{base_url}/auth/register")
            
            if response.status_code == 200:
                # Extract CSRF token
                import re
                csrf_match = re.search(r'name="csrf_token" value="([^"]+)"', response.text)
                csrf_token = csrf_match.group(1) if csrf_match else ""
                
                # Submit registration form
                reg_data = {
                    'username': f'testuser_{hash(email) % 10000}',
                    'email': email,
                    'password': 'TestPass123!',
                    'confirm_password': 'TestPass123!',
                    'role': 'student',
                    'csrf_token': csrf_token
                }
                
                response2 = session.post(f"{base_url}/auth/register", data=reg_data)
                
                if "Please enter a valid email address" in response2.text:
                    print(f"   ✅ {'PASS' if not should_pass else 'FAIL'} - Email validation working correctly")
                elif should_pass and response2.status_code == 200:
                    print(f"   ✅ PASS - Email accepted as expected")
                elif not should_pass and "Please enter a valid email address" in response2.text:
                    print(f"   ✅ PASS - Email rejected as expected")
                else:
                    print(f"   ❓ UNEXPECTED - Response: {response2.status_code}")
            else:
                print(f"   ❌ Error accessing registration page: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error testing email: {e}")
    
    print("\n" + "=" * 50)
    print("📧 Email Validation Test Complete!")

if __name__ == "__main__":
    test_email_validation()
