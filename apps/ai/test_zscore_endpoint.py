"""
Test script for Z-score endpoint
Tests all scenarios from the test plan
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_zscore_endpoint(stream, district, z_score, expected_status=200):
    """Test Z-score endpoint with given parameters"""
    url = f"{BASE_URL}/ai/zscore"
    payload = {
        "stream": stream,
        "district": district,
        "z_score": z_score
    }
    
    print(f"\n{'='*60}")
    print(f"Testing: stream={stream}, district={district}, z_score={z_score}")
    print(f"{'='*60}")
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == expected_status:
            print("✅ Status code matches expected")
        else:
            print(f"❌ Expected {expected_status}, got {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nResponse Structure:")
            print(f"  - success: {data.get('success', 'N/A')}")
            print(f"  - safe courses: {len(data.get('safe', []))}")
            print(f"  - probable courses: {len(data.get('probable', []))}")
            print(f"  - reach courses: {len(data.get('reach', []))}")
            print(f"  - explanation: {len(data.get('explanation', ''))} chars")
            
            # Check if at least one category has data
            has_data = (
                len(data.get('safe', [])) > 0 or
                len(data.get('probable', [])) > 0 or
                len(data.get('reach', [])) > 0
            )
            
            if has_data:
                print("✅ At least one category contains data")
            else:
                print("❌ All categories are empty")
            
            # Show sample courses
            if data.get('safe'):
                print(f"\nSample Safe Course: {data['safe'][0]}")
            if data.get('probable'):
                print(f"Sample Probable Course: {data['probable'][0]}")
            if data.get('reach'):
                print(f"Sample Reach Course: {data['reach'][0]}")
            
            return True, data
        else:
            print(f"Error Response: {response.text}")
            return False, None
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error: Is the FastAPI server running?")
        print("   Start it with: uvicorn main:app --reload --port 8000")
        return False, None
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, None

def main():
    print("🧪 Z-Score Endpoint Test Suite")
    print("="*60)
    
    # Test 1: Valid request (Maths, Colombo, 1.90)
    print("\n📋 TEST 1: Valid Request (Maths, Colombo, 1.90)")
    success1, data1 = test_zscore_endpoint("Maths", "Colombo", 1.90)
    
    # Test 2: Invalid stream
    print("\n📋 TEST 2: Invalid Stream (Biology)")
    success2, _ = test_zscore_endpoint("Biology", "Colombo", 1.90, expected_status=400)
    
    # Test 3: Extreme high Z-score
    print("\n📋 TEST 3: Extreme High Z-score (3.0)")
    success3, data3 = test_zscore_endpoint("Maths", "Colombo", 3.0)
    
    # Test 4: Low Z-score
    print("\n📋 TEST 4: Low Z-score (0.9)")
    success4, data4 = test_zscore_endpoint("Maths", "Colombo", 0.9)
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    print(f"Test 1 (Valid): {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"Test 2 (Invalid stream): {'✅ PASS' if success2 else '❌ FAIL'}")
    print(f"Test 3 (High Z-score): {'✅ PASS' if success3 else '❌ FAIL'}")
    print(f"Test 4 (Low Z-score): {'✅ PASS' if success4 else '❌ FAIL'}")
    
    if success1 and success2 and success3 and success4:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️ Some tests failed. Review output above.")
        return 1

if __name__ == "__main__":
    exit(main())

