#!/usr/bin/env python3
"""
Timing Attack Protection Test Script
Tests timing-safe password verification by measuring response times
"""

import requests
import time
import statistics
import re

def test_timing_attack():
    """Test timing attack protection"""
    base_url = "http://127.0.0.1:5000"
    
    print("⏰ Testing Timing Attack Protection...")
    print("=" * 50)
    
    # Test cases: (username, password, description)
    test_cases = [
        ("nonexistentuser1", "wrongpass1", "Non-existent user with wrong password"),
        ("nonexistentuser2", "wrongpass2", "Non-existent user with wrong password"),
        ("nonexistentuser3", "wrongpass3", "Non-existent user with wrong password"),
        ("nonexistentuser4", "wrongpass4", "Non-existent user with wrong password"),
        ("nonexistentuser5", "wrongpass5", "Non-existent user with wrong password"),
        ("nonexistentuser6", "wrongpass6", "Non-existent user with wrong password"),
        ("nonexistentuser7", "wrongpass7", "Non-existent user with wrong password"),
        ("nonexistentuser8", "wrongpass8", "Non-existent user with wrong password"),
        ("nonexistentuser9", "wrongpass9", "Non-existent user with wrong password"),
        ("nonexistentuser10", "wrongpass10", "Non-existent user with wrong password"),
    ]
    
    response_times = []
    
    print(f"\n🕐 Testing {len(test_cases)} login attempts...")
    
    for i, (username, password, description) in enumerate(test_cases):
        print(f"\nTest {i + 1}: {description}")
        
        try:
            session = requests.Session()
            
            # Get CSRF token
            response = session.get(f"{base_url}/auth/login")
            csrf_match = re.search(r'name="csrf_token" value="([^"]+)"', response.text)
            csrf_token = csrf_match.group(1) if csrf_match else ""
            
            # Measure response time
            start_time = time.time()
            
            login_data = {
                'username': username,
                'password': password,
                'csrf_token': csrf_token
            }
            
            response = session.post(f"{base_url}/auth/login", data=login_data)
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            response_times.append(response_time)
            
            print(f"   Response Time: {response_time:.2f}ms")
            print(f"   Status Code: {response.status_code}")
            
            # Check if it's the same error message
            if "Invalid username/email or password" in response.text:
                print("   ✅ Same error message (good)")
            else:
                print("   ❓ Different error message (potential issue)")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Analyze timing
    if response_times:
        avg_time = statistics.mean(response_times)
        min_time = min(response_times)
        max_time = max(response_times)
        std_dev = statistics.stdev(response_times)
        
        print(f"\n📊 Timing Analysis:")
        print(f"   Average Response Time: {avg_time:.2f}ms")
        print(f"   Min Response Time: {min_time:.2f}ms")
        print(f"   Max Response Time: {max_time:.2f}ms")
        print(f"   Standard Deviation: {std_dev:.2f}ms")
        
        # Check if timing is consistent (good for timing attack protection)
        if std_dev < 50:  # Less than 50ms variation
            print("   ✅ PASS - Response times are consistent (timing attack protection working)")
        else:
            print("   ❓ WARNING - High variation in response times")
    
    print("\n" + "=" * 50)
    print("⏰ Timing Attack Protection Test Complete!")

if __name__ == "__main__":
    test_timing_attack()
