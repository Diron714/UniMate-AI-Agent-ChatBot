# Memory and Context System - Test Execution Summary

## ⚠️ Prerequisites

Before running tests, ensure:

1. **FastAPI Server is Running:**
   ```powershell
   cd apps/ai
   uvicorn main:app --reload --port 8000
   ```

2. **MongoDB is Connected:**
   - Check startup logs for: "✅ MongoDB connected successfully"
   - Verify health: `curl http://localhost:8000/health`

3. **Server Health Check:**
   ```powershell
   curl http://localhost:8000/health
   ```
   Expected: `{"status":"healthy","database":"connected","gemini_api":"configured"}`

---

## 🧪 Test Execution Instructions

### Option 1: Automated Python Test (Recommended)

**Command:**
```powershell
cd apps/ai
python test_memory_context.py
```

**What it tests:**
1. ✅ University Detection - "I'm selected to University of Jaffna"
2. ✅ Context Persistence - "Where is the library?" (should remember Jaffna)
3. ✅ Stage Detection - "I got my A/L results" (should detect "pre-application")
4. ✅ Course Detection - "I'm studying Computer Science"
5. ✅ Multiple Context - Detects university, course, and stage together

**Expected Output:**
```
Memory and Context System Tests
============================================================

============================================================
TEST 1: University Detection
============================================================
Status: 200
University in context: University of Jaffna
Response preview: ...
[PASS] University detected correctly

============================================================
TEST 2: Context Persistence
============================================================
Status: 200
University in context: University of Jaffna
Response preview: ...
[PASS] Context persisted and used

============================================================
TEST 3: Stage Detection
============================================================
Status: 200
Stage in context: pre-application
[PASS] Stage detected correctly

============================================================
TEST 4: Course Detection
============================================================
Status: 200
Course in context: Computer Science
[PASS] Course detected correctly

============================================================
TEST 5: Multiple Context Updates
============================================================
Status: 200
University: University of Colombo
Course: Computer Science
Stage: selected
[PASS] Multiple context fields detected

============================================================
📊 TEST SUMMARY
============================================================
[PASS]: University Detection
[PASS]: Context Persistence
[PASS]: Stage Detection
[PASS]: Course Detection
[PASS]: Multiple Context

Total: 5/5 tests passed

[SUCCESS] ALL TESTS PASSED!
```

---

### Option 2: Quick PowerShell Test

**Command:**
```powershell
cd apps/ai
.\QUICK_MEMORY_TEST.ps1
```

**What it tests:**
1. Server health check
2. University detection
3. Context persistence
4. Stage detection

**Expected Output:**
```
🧪 Quick Memory and Context Test
============================================================

Checking server...
✅ Server is running

📋 TEST 1: University Detection
✅ Request successful
   University: University of Jaffna
   ✅ PASS: University detected

📋 TEST 2: Context Persistence
✅ Request successful
   University: University of Jaffna
   Response preview: ...
   ✅ PASS: Context persisted
   ✅ PASS: Response is Jaffna-specific

📋 TEST 3: Stage Detection
✅ Request successful
   Stage: pre-application
   ✅ PASS: Stage detected correctly

============================================================
✅ Quick test completed!
============================================================
```

---

### Option 3: Manual API Testing

**Test 1: University Detection**
```powershell
$body = @{
    message = "I am selected to University of Jaffna"
    userId = "test_user_001"
    sessionId = "test_session_001"
    context = @{}
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/ai/chat" -Method Post -Body $body -ContentType "application/json"
Write-Host "University: $($response.context.university)"
# Expected: "University of Jaffna"
```

**Test 2: Context Persistence**
```powershell
$body2 = @{
    message = "Where is the library?"
    userId = "test_user_001"
    sessionId = "test_session_001"
    context = @{}
} | ConvertTo-Json

$response2 = Invoke-RestMethod -Uri "http://localhost:8000/ai/chat" -Method Post -Body $body2 -ContentType "application/json"
Write-Host "University: $($response2.context.university)"
Write-Host "Response: $($response2.message.Substring(0, [Math]::Min(150, $response2.message.Length)))"
# Expected: University = "University of Jaffna", Response mentions Jaffna
```

**Test 3: Stage Detection**
```powershell
$body3 = @{
    message = "I got my A/L results"
    userId = "test_user_002"
    sessionId = "test_session_002"
    context = @{}
} | ConvertTo-Json

$response3 = Invoke-RestMethod -Uri "http://localhost:8000/ai/chat" -Method Post -Body $body3 -ContentType "application/json"
Write-Host "Stage: $($response3.context.stage)"
# Expected: "pre-application"
```

---

## ✅ Success Criteria

All tests pass when:

1. **University Detection:**
   - ✅ Status: 200 OK
   - ✅ `context.university` = "University of Jaffna"
   - ✅ Logs show: "Detected university: University of Jaffna"

2. **Context Persistence:**
   - ✅ Status: 200 OK
   - ✅ `context.university` persists across messages
   - ✅ Response mentions the university (Jaffna-specific answer)

3. **Stage Detection:**
   - ✅ Status: 200 OK
   - ✅ `context.stage` = "pre-application"
   - ✅ Logs show: "Detected stage: pre-application"

4. **Course Detection:**
   - ✅ Status: 200 OK
   - ✅ `context.course` = "Computer Science"
   - ✅ Logs show: "Detected course: Computer Science"

5. **Multiple Context:**
   - ✅ Status: 200 OK
   - ✅ All context fields detected (university, course, stage)
   - ✅ All fields stored correctly

---

## 🔍 Verification Steps

### 1. Check FastAPI Logs

Look for these messages in the terminal where FastAPI is running:

```
INFO: Detected university: University of Jaffna
INFO: Updated university context: University of Jaffna
INFO: Detected stage: pre-application
INFO: Updated stage context: pre-application
INFO: Detected course: Computer Science
INFO: Updated course context: Computer Science
```

### 2. Check MongoDB

```javascript
use unimate
db.memories.find({userId: "test_user_001"}).pretty()
```

**Expected Document:**
```json
{
  "userId": "test_user_001",
  "sessionId": "test_session_001",
  "shortTerm": [
    {
      "role": "user",
      "content": "I am selected to University of Jaffna",
      "timestamp": "..."
    },
    {
      "role": "assistant",
      "content": "...",
      "timestamp": "..."
    }
  ],
  "longTerm": {
    "university": "University of Jaffna",
    "course": null,
    "stage": "selected",
    "preferences": {}
  },
  "createdAt": ISODate("..."),
  "updatedAt": ISODate("...")
}
```

### 3. Check Response Context

Verify that the `context` field in API responses contains:
- `university`: Detected university name
- `course`: Detected course name (if any)
- `stage`: Detected stage (if any)
- `preferences`: User preferences object

---

## 🐛 Troubleshooting

### Issue: Server Not Running
**Error:** `Cannot connect to server`

**Solution:**
```powershell
cd apps/ai
uvicorn main:app --reload --port 8000
```

### Issue: MongoDB Not Connected
**Error:** `database: "disconnected"` in health check

**Solution:**
1. Check `MONGODB_URI` in `.env` file
2. Restart FastAPI server
3. Verify connection in startup logs

### Issue: University Not Detected
**Symptom:** `context.university` is null

**Solutions:**
1. Try different phrasings:
   - "I'm at Jaffna University"
   - "University of Jaffna"
   - "I'm selected to Jaffna"
2. Check logs for detection messages
3. Verify university name matches patterns in `context_service.py`

### Issue: Context Not Persisting
**Symptom:** Context detected but lost in next message

**Solutions:**
1. Ensure same `userId` and `sessionId` are used
2. Check MongoDB for memory documents
3. Verify memory service is updating correctly

---

## 📊 Test Results Template

After running tests, record results:

```
Test Date: _______________
Server Status: ✅ Running / ❌ Not Running
MongoDB Status: ✅ Connected / ❌ Disconnected

Test Results:
[ ] Test 1: University Detection - ✅ PASS / ❌ FAIL
[ ] Test 2: Context Persistence - ✅ PASS / ❌ FAIL
[ ] Test 3: Stage Detection - ✅ PASS / ❌ FAIL
[ ] Test 4: Course Detection - ✅ PASS / ❌ FAIL
[ ] Test 5: Multiple Context - ✅ PASS / ❌ FAIL

Total: ___/5 tests passed

Issues Found:
1. _______________
2. _______________

Notes:
_______________
```

---

## 🚀 Next Steps After Testing

1. **If all tests pass:**
   - ✅ Memory and context system is working correctly
   - ✅ Ready for integration testing
   - ✅ Can proceed to next features

2. **If tests fail:**
   - Review error messages
   - Check FastAPI logs
   - Verify MongoDB connection
   - Check memory documents in MongoDB
   - Review troubleshooting section

3. **Integration Testing:**
   - Test via frontend chat interface
   - Verify end-to-end flow
   - Test with real user scenarios

---

*Test Execution Summary - January 10, 2025*

