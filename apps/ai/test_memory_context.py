"""
Test script for memory and context system
"""
import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"

def test_university_detection():
    """Test 1: University detection"""
    print("\n" + "="*60)
    print("TEST 1: University Detection")
    print("="*60)
    
    payload = {
        "message": "I'm selected to University of Jaffna",
        "userId": "test_user_001",
        "sessionId": "test_session_001",
        "context": {}
    }
    
    try:
        response = requests.post(f"{BASE_URL}/ai/chat", json=payload, timeout=30)
        data = response.json()
        
        print(f"Status: {response.status_code}")
        print(f"University in context: {data.get('context', {}).get('university')}")
        print(f"Response preview: {data.get('message', '')[:100]}...")
        
        assert response.status_code == 200, "Request failed"
        assert data.get('context', {}).get('university') == "University of Jaffna", "University not detected"
        print("[PASS] University detected correctly")
        return True
    except AssertionError as e:
        print(f"[FAIL] {e}")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def test_context_persistence():
    """Test 2: Context persistence"""
    print("\n" + "="*60)
    print("TEST 2: Context Persistence")
    print("="*60)
    
    payload = {
        "message": "Where is the library?",
        "userId": "test_user_001",
        "sessionId": "test_session_001",
        "context": {}
    }
    
    try:
        response = requests.post(f"{BASE_URL}/ai/chat", json=payload, timeout=30)
        data = response.json()
        
        print(f"Status: {response.status_code}")
        print(f"University in context: {data.get('context', {}).get('university')}")
        print(f"Response preview: {data.get('message', '')[:100]}...")
        
        assert response.status_code == 200, "Request failed"
        assert data.get('context', {}).get('university') == "University of Jaffna", "University context not persisted"
        message_lower = data.get('message', '').lower()
        assert "jaffna" in message_lower or "university of jaffna" in message_lower, "Response not Jaffna-specific"
        print("[PASS] Context persisted and used")
        return True
    except AssertionError as e:
        print(f"[FAIL] {e}")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def test_stage_detection():
    """Test 3: Stage detection"""
    print("\n" + "="*60)
    print("TEST 3: Stage Detection")
    print("="*60)
    
    payload = {
        "message": "I got my A/L results",
        "userId": "test_user_002",
        "sessionId": "test_session_002",
        "context": {}
    }
    
    try:
        response = requests.post(f"{BASE_URL}/ai/chat", json=payload, timeout=30)
        data = response.json()
        
        print(f"Status: {response.status_code}")
        print(f"Stage in context: {data.get('context', {}).get('stage')}")
        
        assert response.status_code == 200, "Request failed"
        assert data.get('context', {}).get('stage') == "pre-application", "Stage not detected"
        print("[PASS] Stage detected correctly")
        return True
    except AssertionError as e:
        print(f"[FAIL] {e}")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def test_course_detection():
    """Test 4: Course detection"""
    print("\n" + "="*60)
    print("TEST 4: Course Detection")
    print("="*60)
    
    payload = {
        "message": "I'm studying Computer Science",
        "userId": "test_user_003",
        "sessionId": "test_session_003",
        "context": {}
    }
    
    try:
        response = requests.post(f"{BASE_URL}/ai/chat", json=payload, timeout=30)
        data = response.json()
        
        print(f"Status: {response.status_code}")
        print(f"Course in context: {data.get('context', {}).get('course')}")
        
        assert response.status_code == 200, "Request failed"
        assert data.get('context', {}).get('course') == "Computer Science", "Course not detected"
        print("[PASS] Course detected correctly")
        return True
    except AssertionError as e:
        print(f"[FAIL] {e}")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def test_multiple_context():
    """Test 5: Multiple context updates"""
    print("\n" + "="*60)
    print("TEST 5: Multiple Context Updates")
    print("="*60)
    
    payload = {
        "message": "I'm selected to University of Colombo for Computer Science",
        "userId": "test_user_004",
        "sessionId": "test_session_004",
        "context": {}
    }
    
    try:
        response = requests.post(f"{BASE_URL}/ai/chat", json=payload, timeout=30)
        data = response.json()
        
        context = data.get('context', {})
        print(f"Status: {response.status_code}")
        print(f"University: {context.get('university')}")
        print(f"Course: {context.get('course')}")
        print(f"Stage: {context.get('stage')}")
        
        assert response.status_code == 200, "Request failed"
        assert context.get('university') == "University of Colombo", "University not detected"
        assert context.get('course') == "Computer Science", "Course not detected"
        print("[PASS] Multiple context fields detected")
        return True
    except AssertionError as e:
        print(f"[FAIL] {e}")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def main():
    print("Memory and Context System Tests")
    print("="*60)
    
    # Check if server is running
    try:
        health = requests.get(f"{BASE_URL}/health", timeout=5)
        if health.status_code != 200:
            print("[ERROR] Server is not healthy. Please start FastAPI server.")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("[ERROR] Cannot connect to server. Please start FastAPI server:")
        print("   cd apps/ai && uvicorn main:app --reload --port 8000")
        sys.exit(1)
    
    results = []
    
    try:
        results.append(("University Detection", test_university_detection()))
        time.sleep(1)
        results.append(("Context Persistence", test_context_persistence()))
        time.sleep(1)
        results.append(("Stage Detection", test_stage_detection()))
        time.sleep(1)
        results.append(("Course Detection", test_course_detection()))
        time.sleep(1)
        results.append(("Multiple Context", test_multiple_context()))
        
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "[PASS]" if result else "[FAIL]"
            print(f"{status}: {test_name}")
        
        print(f"\nTotal: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n[SUCCESS] ALL TESTS PASSED!")
            return 0
        else:
            print(f"\n[WARNING] {total - passed} test(s) failed")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n[WARNING] Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

