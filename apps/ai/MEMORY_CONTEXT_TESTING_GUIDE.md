# Memory and Context System - Testing Guide

## 🎯 Overview

This guide will help you test the memory and context system to verify:
- ✅ Memory is being stored in MongoDB
- ✅ Context is automatically detected from messages
- ✅ University context switching works
- ✅ Stage detection works
- ✅ Course detection works
- ✅ System prompt is enhanced with context

---

## 📋 Prerequisites

### 1. FastAPI Server Running
```powershell
cd apps/ai
uvicorn main:app --reload --port 8000
```

**Verify:** Check startup logs for:
- ✅ MongoDB connected successfully
- ✅ ZScore tool initialized
- ✅ No errors

### 2. MongoDB Connected
```powershell
curl http://localhost:8000/health
```

**Expected:**
```json
{
  "status": "healthy",
  "database": "connected",
  "gemini_api": "configured"
}
```

### 3. Backend API Running (Optional, for full integration)
```powershell
cd apps/api
npm run dev
```

---

## 🧪 Test Method 1: Direct API Testing (Recommended)

### Step 1: Test University Detection

**Request:**
```powershell
$body = @{
    message = "I'm selected to University of Jaffna"
    userId = "test_user_001"
    sessionId = "test_session_001"
    context = @{}
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/ai/chat" -Method Post -Body $body -ContentType "application/json"
$response | ConvertTo-Json -Depth 5
```

**Expected Response:**
- ✅ Status: 200 OK
- ✅ `context.university` = "University of Jaffna"
- ✅ Response mentions Jaffna or acknowledges the selection

**Check Logs:**
Look for in FastAPI terminal:
```
INFO: Updated university context: University of Jaffna
```

---

### Step 2: Test University Context Persistence

**Request (Same session, different message):**
```powershell
$body = @{
    message = "Where is the library?"
    userId = "test_user_001"
    sessionId = "test_session_001"
    context = @{}
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/ai/chat" -Method Post -Body $body -ContentType "application/json"
$response | ConvertTo-Json -Depth 5
```

**Expected Response:**
- ✅ Status: 200 OK
- ✅ `context.university` = "University of Jaffna" (persisted from previous message)
- ✅ Response mentions "University of Jaffna" or "Jaffna" library
- ✅ Answer is Jaffna-specific

**What to Look For:**
- Response should say something like: "The library at University of Jaffna is located at..." or "At University of Jaffna, the library..."
- NOT a generic answer about libraries in general

---

### Step 3: Test Stage Detection

**Request:**
```powershell
$body = @{
    message = "I got my A/L results"
    userId = "test_user_002"
    sessionId = "test_session_002"
    context = @{}
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/ai/chat" -Method Post -Body $body -ContentType "application/json"
$response | ConvertTo-Json -Depth 5
```

**Expected Response:**
- ✅ Status: 200 OK
- ✅ `context.stage` = "pre-application"
- ✅ Response acknowledges A/L results

**Check Logs:**
```
INFO: Detected stage: pre-application
INFO: Updated stage context: pre-application
```

---

### Step 4: Test Multiple Context Updates

**Request:**
```powershell
$body = @{
    message = "I'm selected to University of Colombo for Computer Science"
    userId = "test_user_003"
    sessionId = "test_session_003"
    context = @{}
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/ai/chat" -Method Post -Body $body -ContentType "application/json"
$response | ConvertTo-Json -Depth 5
```

**Expected Response:**
- ✅ Status: 200 OK
- ✅ `context.university` = "University of Colombo"
- ✅ `context.course` = "Computer Science"
- ✅ `context.stage` = "selected" (if detected)

**Check Logs:**
```
INFO: Detected university: University of Colombo
INFO: Updated university context: University of Colombo
INFO: Detected course: Computer Science
INFO: Updated course context: Computer Science
```

---

## 🧪 Test Method 2: MongoDB Verification

### Step 1: Check Memory Storage

**Connect to MongoDB:**
```javascript
// Using MongoDB Compass or mongosh
use unimate
db.memories.find({userId: "test_user_001"}).pretty()
```

**Expected Document:**
```json
{
  "_id": ObjectId("..."),
  "userId": "test_user_001",
  "sessionId": "test_session_001",
  "shortTerm": [
    {
      "role": "user",
      "content": "I'm selected to University of Jaffna",
      "timestamp": "2025-01-10T..."
    },
    {
      "role": "assistant",
      "content": "...",
      "timestamp": "2025-01-10T..."
    }
  ],
  "longTerm": {
    "university": "University of Jaffna",
    "course": null,
    "stage": "selected",
    "preferences": {}
  },
  "createdAt": ISODate("2025-01-10T..."),
  "updatedAt": ISODate("2025-01-10T...")
}
```

**✅ Pass Criteria:**
- Document exists
- `longTerm.university` = "University of Jaffna"
- `shortTerm` contains messages
- `updatedAt` is recent

---

### Step 2: Verify Short-Term Memory Limit

**Send 12 messages in the same session:**
```powershell
for ($i = 1; $i -le 12; $i++) {
    $body = @{
        message = "Message $i"
        userId = "test_user_004"
        sessionId = "test_session_004"
        context = @{}
    } | ConvertTo-Json
    
    Invoke-RestMethod -Uri "http://localhost:8000/ai/chat" -Method Post -Body $body -ContentType "application/json" | Out-Null
    Start-Sleep -Milliseconds 500
}
```

**Check MongoDB:**
```javascript
db.memories.findOne({userId: "test_user_004", sessionId: "test_session_004"})
```

**Expected:**
- ✅ `shortTerm` array has exactly 10 messages (not 12)
- ✅ Only the last 10 messages are kept

---

## 🧪 Test Method 3: Complete Flow Test

### Test Scenario: New User Journey

**Step 1: Pre-Application Stage**
```powershell
$body = @{
    message = "I got my A/L results. What courses can I apply for?"
    userId = "new_user_001"
    sessionId = "session_001"
    context = @{}
} | ConvertTo-Json

$r1 = Invoke-RestMethod -Uri "http://localhost:8000/ai/chat" -Method Post -Body $body -ContentType "application/json"
Write-Host "Stage: $($r1.context.stage)"
```

**Expected:** `stage = "pre-application"`

---

**Step 2: Selection Stage**
```powershell
$body = @{
    message = "I got selected to University of Jaffna!"
    userId = "new_user_001"
    sessionId = "session_001"
    context = $r1.context
} | ConvertTo-Json

$r2 = Invoke-RestMethod -Uri "http://localhost:8000/ai/chat" -Method Post -Body $body -ContentType "application/json"
Write-Host "University: $($r2.context.university)"
Write-Host "Stage: $($r2.context.stage)"
```

**Expected:**
- `university = "University of Jaffna"`
- `stage = "selected"`

---

**Step 3: University-Specific Question**
```powershell
$body = @{
    message = "Where is the library?"
    userId = "new_user_001"
    sessionId = "session_001"
    context = $r2.context
} | ConvertTo-Json

$r3 = Invoke-RestMethod -Uri "http://localhost:8000/ai/chat" -Method Post -Body $body -ContentType "application/json"
Write-Host "Response: $($r3.message.Substring(0, [Math]::Min(200, $r3.message.Length)))"
```

**Expected:**
- Response mentions "University of Jaffna" or "Jaffna"
- Answer is specific to Jaffna, not generic

---

**Step 4: Verify Context Persisted**
```powershell
$body = @{
    message = "What are the hostel rules?"
    userId = "new_user_001"
    sessionId = "session_001"
    context = @{}
} | ConvertTo-Json

$r4 = Invoke-RestMethod -Uri "http://localhost:8000/ai/chat" -Method Post -Body $body -ContentType "application/json"
Write-Host "University (from context): $($r4.context.university)"
```

**Expected:**
- `context.university = "University of Jaffna"` (persisted)
- Response is Jaffna-specific

---

## 🧪 Test Method 4: Python Script Testing

### Create Test Script

**File: `test_memory_context.py`**
```python
"""
Test script for memory and context system
"""
import requests
import json
import time

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
    
    response = requests.post(f"{BASE_URL}/ai/chat", json=payload)
    data = response.json()
    
    print(f"Status: {response.status_code}")
    print(f"University in context: {data.get('context', {}).get('university')}")
    print(f"Response preview: {data.get('message', '')[:100]}...")
    
    assert response.status_code == 200, "Request failed"
    assert data.get('context', {}).get('university') == "University of Jaffna", "University not detected"
    print("✅ PASS: University detected correctly")

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
    
    response = requests.post(f"{BASE_URL}/ai/chat", json=payload)
    data = response.json()
    
    print(f"Status: {response.status_code}")
    print(f"University in context: {data.get('context', {}).get('university')}")
    print(f"Response preview: {data.get('message', '')[:100]}...")
    
    assert response.status_code == 200, "Request failed"
    assert data.get('context', {}).get('university') == "University of Jaffna", "University context not persisted"
    assert "jaffna" in data.get('message', '').lower() or "university of jaffna" in data.get('message', '').lower(), "Response not Jaffna-specific"
    print("✅ PASS: Context persisted and used")

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
    
    response = requests.post(f"{BASE_URL}/ai/chat", json=payload)
    data = response.json()
    
    print(f"Status: {response.status_code}")
    print(f"Stage in context: {data.get('context', {}).get('stage')}")
    
    assert response.status_code == 200, "Request failed"
    assert data.get('context', {}).get('stage') == "pre-application", "Stage not detected"
    print("✅ PASS: Stage detected correctly")

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
    
    response = requests.post(f"{BASE_URL}/ai/chat", json=payload)
    data = response.json()
    
    print(f"Status: {response.status_code}")
    print(f"Course in context: {data.get('context', {}).get('course')}")
    
    assert response.status_code == 200, "Request failed"
    assert data.get('context', {}).get('course') == "Computer Science", "Course not detected"
    print("✅ PASS: Course detected correctly")

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
    
    response = requests.post(f"{BASE_URL}/ai/chat", json=payload)
    data = response.json()
    
    context = data.get('context', {})
    print(f"Status: {response.status_code}")
    print(f"University: {context.get('university')}")
    print(f"Course: {context.get('course')}")
    print(f"Stage: {context.get('stage')}")
    
    assert response.status_code == 200, "Request failed"
    assert context.get('university') == "University of Colombo", "University not detected"
    assert context.get('course') == "Computer Science", "Course not detected"
    print("✅ PASS: Multiple context fields detected")

if __name__ == "__main__":
    print("🧪 Memory and Context System Tests")
    print("="*60)
    
    try:
        test_university_detection()
        time.sleep(1)
        test_context_persistence()
        time.sleep(1)
        test_stage_detection()
        time.sleep(1)
        test_course_detection()
        time.sleep(1)
        test_multiple_context()
        
        print("\n" + "="*60)
        print("🎉 ALL TESTS PASSED!")
        print("="*60)
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
```

**Run the test:**
```powershell
cd apps/ai
python test_memory_context.py
```

---

## 📊 Expected Test Results Summary

| Test | Expected Result | Pass Criteria |
|------|----------------|---------------|
| University Detection | `context.university = "University of Jaffna"` | ✅ Detected and stored |
| Context Persistence | `context.university` persists in next message | ✅ Context remembered |
| Stage Detection | `context.stage = "pre-application"` | ✅ Stage detected |
| Course Detection | `context.course = "Computer Science"` | ✅ Course detected |
| Multiple Context | All fields detected simultaneously | ✅ All fields set |
| MongoDB Storage | Memory document exists with correct data | ✅ Stored correctly |
| Short-Term Limit | Only last 10 messages kept | ✅ Limited to 10 |

---

## 🔍 Verification Checklist

After running tests, verify:

- [ ] **Memory Documents Created**
  - Check MongoDB: `db.memories.find().pretty()`
  - Documents exist for test users
  - `longTerm` contains university/course/stage

- [ ] **Context Detection Logs**
  - Check FastAPI terminal logs
  - See "Detected university: ..." messages
  - See "Updated university context: ..." messages

- [ ] **Context in Responses**
  - `context` field in response contains detected values
  - University persists across messages in same session

- [ ] **System Prompt Enhancement**
  - Responses are university-specific when context is set
  - Generic questions get context-aware answers

- [ ] **Short-Term Memory**
  - Messages stored in `shortTerm` array
  - Limited to 10 messages
  - Contains both user and assistant messages

---

## 🐛 Troubleshooting

### Issue: University Not Detected
**Symptoms:**
- `context.university` is null after mentioning university

**Solutions:**
1. Check logs for detection messages
2. Verify university name matches patterns in `context_service.py`
3. Try different phrasings: "Jaffna University", "University of Jaffna", "I'm at Jaffna"

### Issue: Context Not Persisting
**Symptoms:**
- Context is detected but lost in next message

**Solutions:**
1. Verify MongoDB connection
2. Check memory service is updating correctly
3. Ensure same `userId` and `sessionId` are used

### Issue: Response Not University-Specific
**Symptoms:**
- Context is set but response is generic

**Solutions:**
1. Check system prompt enhancement in logs
2. Verify context is passed to LLM
3. Check if RAG tool is filtering by university

---

## ✅ Success Criteria

All tests pass when:
1. ✅ University is detected from messages
2. ✅ Context persists across messages
3. ✅ Stage is detected correctly
4. ✅ Course is detected correctly
5. ✅ Memory is stored in MongoDB
6. ✅ Responses are context-aware
7. ✅ Short-term memory is limited to 10 messages

---

## 📝 Quick Test Commands

### PowerShell One-Liners

**Test University Detection:**
```powershell
$body = @{message="I'm selected to Jaffna"; userId="test1"; sessionId="s1"; context=@{}} | ConvertTo-Json; Invoke-RestMethod -Uri "http://localhost:8000/ai/chat" -Method Post -Body $body -ContentType "application/json" | Select-Object -ExpandProperty context
```

**Test Context Persistence:**
```powershell
$body = @{message="Where is library?"; userId="test1"; sessionId="s1"; context=@{}} | ConvertTo-Json; (Invoke-RestMethod -Uri "http://localhost:8000/ai/chat" -Method Post -Body $body -ContentType "application/json").context.university
```

**Test Stage Detection:**
```powershell
$body = @{message="I got A/L results"; userId="test2"; sessionId="s2"; context=@{}} | ConvertTo-Json; (Invoke-RestMethod -Uri "http://localhost:8000/ai/chat" -Method Post -Body $body -ContentType "application/json").context.stage
```

---

*Testing Guide - January 10, 2025*

