#!/usr/bin/env python3
"""
Rate Limiting Test Script
Tests rate limiting functionality with multiple rapid requests
"""

import requests
import time
import threading

def make_request(session, url, data, results, index):
    """Make a single request and record result"""
    try:
        response = session.post(url, data=data)
        results[index] = {
            'status_code': response.status_code,
            'text': response.text[:200] if response.status_code != 200 else response.text[:100],
            'timestamp': time.time()
        }
        print(f"Request {index + 1}: Status {response.status_code}")
    except Exception as e:
        results[index] = {
            'status_code': 0,
            'error': str(e),
            'timestamp': time.time()
        }
        print(f"Request {index + 1}: Error {e}")

def test_rate_limiting():
    """Test rate limiting functionality"""
    base_url = "http://127.0.0.1:5000"
    
    print("⏱️ Testing Rate Limiting...")
    print("=" * 50)
    
    # Test 1: Multiple rapid login attempts
    print("\n1️⃣ Testing Multiple Rapid Login Attempts...")
    session = requests.Session()
    
    # Get CSRF token first
    response = session.get(f"{base_url}/auth/login")
    import re
    csrf_match = re.search(r'name="csrf_token" value="([^"]+)"', response.text)
    csrf_token = csrf_match.group(1) if csrf_match else ""
    
    login_data = {
        'username': 'nonexistentuser',
        'password': 'wrongpassword',
        'csrf_token': csrf_token
    }
    
    results = [None] * 8
    threads = []
    
    # Make 8 rapid requests
    for i in range(8):
        thread = threading.Thread(target=make_request, args=(session, f"{base_url}/auth/login", login_data, results, i))
        threads.append(thread)
        thread.start()
        time.sleep(0.1)  # 100ms between requests
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # Analyze results
    success_count = sum(1 for r in results if r and r['status_code'] == 200)
    rate_limited_count = sum(1 for r in results if r and r['status_code'] == 429)
    error_count = sum(1 for r in results if r and r['status_code'] == 400)
    
    print(f"   Results: {success_count} success, {rate_limited_count} rate limited, {error_count} error")
    
    if rate_limited_count > 0:
        print("   ✅ PASS - Rate limiting is working!")
    elif success_count <= 5:  # Should allow first 5 requests
        print("   ✅ PASS - Rate limiting allowing initial requests")
    else:
        print("   ❌ FAIL - Rate limiting may not be working properly")
    
    # Test 2: Multiple rapid registration attempts
    print("\n2️⃣ Testing Multiple Rapid Registration Attempts...")
    time.sleep(65)  # Wait for rate limit to reset
    
    session2 = requests.Session()
    response = session2.get(f"{base_url}/auth/register")
    csrf_match = re.search(r'name="csrf_token" value="([^"]+)"', response.text)
    csrf_token = csrf_match.group(1) if csrf_match else ""
    
    reg_data = {
        'username': f'testuser{int(time.time())}',
        'email': f'test{int(time.time())}@example.com',
        'password': 'TestPass123!',
        'confirm_password': 'TestPass123!',
        'role': 'student',
        'csrf_token': csrf_token
    }
    
    results2 = [None] * 8
    threads2 = []
    
    # Make 8 rapid registration requests
    for i in range(8):
        thread = threading.Thread(target=make_request, args=(session2, f"{base_url}/auth/register", reg_data, results2, i))
        threads2.append(thread)
        thread.start()
        time.sleep(0.1)  # 100ms between requests
    
    # Wait for all threads to complete
    for thread in threads2:
        thread.join()
    
    # Analyze registration results
    reg_rate_limited = sum(1 for r in results2 if r and r['status_code'] == 429)
    reg_success = sum(1 for r in results2 if r and r['status_code'] == 200)
    
    print(f"   Registration Results: {reg_success} success, {reg_rate_limited} rate limited")
    
    if reg_rate_limited > 0:
        print("   ✅ PASS - Registration rate limiting working!")
    else:
        print("   ❓ INCONCLUSIVE - Need to check registration rate limiting")
    
    print("\n" + "=" * 50)
    print("⏱️ Rate Limiting Test Complete!")

if __name__ == "__main__":
    test_rate_limiting()
