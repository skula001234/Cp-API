#!/usr/bin/env python3
"""
Simple test script for ClassPlus Decoder API endpoints
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_index():
    """Test the main page loads"""
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✓ Index page: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"✗ Index page error: {e}")
        return False

def test_decode_endpoint():
    """Test the decode endpoint with invalid data"""
    try:
        data = {"token": "test", "encrypted_url": "test"}
        response = requests.post(f"{BASE_URL}/api/decode", json=data)
        print(f"✓ Decode endpoint: {response.status_code}")
        return response.status_code in [400, 401]  # Expected to fail with invalid data
    except Exception as e:
        print(f"✗ Decode endpoint error: {e}")
        return False

def test_keys_endpoint():
    """Test the keys endpoint with invalid data"""
    try:
        data = {"token": "test", "video_url": "test"}
        response = requests.post(f"{BASE_URL}/api/get-keys", json=data)
        print(f"✓ Keys endpoint: {response.status_code}")
        return response.status_code in [400, 401]  # Expected to fail with invalid data
    except Exception as e:
        print(f"✗ Keys endpoint error: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing ClassPlus Decoder API...")
    print("=" * 40)
    
    tests = [
        ("Index Page", test_index),
        ("Decode Endpoint", test_decode_endpoint),
        ("Keys Endpoint", test_keys_endpoint),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\nTesting {test_name}...")
        if test_func():
            passed += 1
            print(f"✓ {test_name} passed")
        else:
            print(f"✗ {test_name} failed")
    
    print("\n" + "=" * 40)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! The API is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the application logs.")

if __name__ == "__main__":
    main()