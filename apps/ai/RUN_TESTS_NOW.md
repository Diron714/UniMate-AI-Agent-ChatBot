# 🚀 Run Memory and Context Tests - Quick Start

## ⚡ Quick Start

### Step 1: Start FastAPI Server

Open a terminal and run:
```powershell
cd apps/ai
uvicorn main:app --reload --port 8000
```

**Wait for:** "Application startup complete" and "✅ MongoDB connected successfully"

---

### Step 2: Run Tests

**Option A: Automated Python Test (Recommended)**
```powershell
# In a NEW terminal (keep server running)
cd apps/ai
python test_memory_context.py
```

**Option B: Quick PowerShell Test**
```powershell
# In a NEW terminal (keep server running)
cd apps/ai
.\QUICK_MEMORY_TEST.ps1
```

---

## ✅ Expected Results

### Python Test Output:
```
Memory and Context System Tests
============================================================

============================================================
TEST 1: University Detection
============================================================
Status: 200
University in context: University of Jaffna
[PASS] University detected correctly

============================================================
TEST 2: Context Persistence
============================================================
Status: 200
University in context: University of Jaffna
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

## 🔍 What to Check

1. **FastAPI Terminal Logs:**
   - Look for: "Detected university: University of Jaffna"
   - Look for: "Updated university context: University of Jaffna"
   - Look for: "Detected stage: pre-application"

2. **Test Results:**
   - All 5 tests should show `[PASS]`
   - Total should be `5/5 tests passed`

3. **MongoDB (Optional):**
   ```javascript
   use unimate
   db.memories.find().pretty()
   ```
   - Should see memory documents for test users
   - `longTerm.university` should be set

---

## 🐛 If Tests Fail

### Server Not Running
**Error:** `Cannot connect to server`

**Fix:** Start server in separate terminal:
```powershell
cd apps/ai
uvicorn main:app --reload --port 8000
```

### MongoDB Not Connected
**Error:** `database: "disconnected"`

**Fix:**
1. Check `.env` file has `MONGODB_URI`
2. Restart FastAPI server
3. Check startup logs

### University Not Detected
**Symptom:** `context.university` is null

**Fix:** Check FastAPI logs for detection messages. Try different phrasings in test.

---

## 📝 Test Files

- `test_memory_context.py` - Automated Python test (5 tests)
- `QUICK_MEMORY_TEST.ps1` - Quick PowerShell test (3 tests)
- `MEMORY_CONTEXT_TESTING_GUIDE.md` - Complete testing guide
- `TEST_EXECUTION_SUMMARY.md` - Detailed execution instructions

---

**Ready to test? Start the server and run the tests!** 🚀

