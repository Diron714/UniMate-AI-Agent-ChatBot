# Z-Score Endpoint Testing Summary

## 🎯 Test Status

### ✅ Code Implementation: COMPLETE
All code changes have been implemented and are ready for testing.

### ⚠️ Prerequisites: REQUIRED
Before running tests, ensure:

1. **MongoDB is connected**
   - Set `MONGODB_URI` in `apps/ai/.env`
   - Verify connection in FastAPI startup logs

2. **Cut-off data is seeded**
   - Run: `python scripts/seed_cutoffs.py`
   - Expected: > 3000 records in `cutoffs` collection

3. **FastAPI server is running**
   - Command: `uvicorn main:app --reload --port 8000`
   - Verify: `curl http://localhost:8000/health`

---

## 📋 Changes Made

### 1. Added ZScore Tool Initialization Logging
**File:** `apps/ai/main.py`
- Added startup logging to verify ZScore tool initialization
- Logs: "✅ ZScore tool initialized" on successful startup

### 2. Added Count Method to CutoffModel
**File:** `apps/ai/app/models/cutoff.py`
- Added `count()` method to check total records
- Returns: `int` (number of records)

### 3. Enhanced Response Format
**File:** `apps/ai/app/routes/zscore.py`
- Added `status: "success"` field (for test compatibility)
- Added `input` field with request parameters
- Fixed timestamp field name: `createdAt` (was `timestamp`)
- Fixed result storage structure

### 4. Improved Error Handling
**File:** `apps/ai/app/routes/zscore.py`
- Better error codes: 503 for service unavailable, 404 for no data
- Clearer error messages

### 5. Created Test Scripts
- `test_zscore_data.py` - Check MongoDB data count
- `test_zscore_endpoint.py` - Python test suite
- `run_zscore_tests.ps1` - PowerShell test script

---

## 🧪 Test Plan

### STEP 0: Pre-Checks

#### 0.1 FastAPI Server Status
```bash
curl http://localhost:8000/health
```
**Expected:**
- Status: "healthy"
- Database: "connected" (not "disconnected")
- Gemini API: "configured"

#### 0.2 MongoDB Data Verification
```bash
cd apps/ai
python test_zscore_data.py
```
**Expected:**
```
Records: > 3000
✅ Data is loaded correctly
```

**If 0 records:**
- Run: `python scripts/seed_cutoffs.py`
- Verify MongoDB connection in `.env`

---

### STEP 1: Direct API Test (Valid Request)

**Request:**
```bash
# PowerShell
$body = @{stream='Maths'; district='Colombo'; z_score=1.90} | ConvertTo-Json
Invoke-RestMethod -Uri 'http://localhost:8000/ai/zscore' -Method Post -Body $body -ContentType 'application/json'

# Or use curl (if available)
curl -X POST http://localhost:8000/ai/zscore ^
  -H "Content-Type: application/json" ^
  -d "{\"stream\":\"Maths\",\"district\":\"Colombo\",\"z_score\":1.90}"
```

**Expected Response:**
```json
{
  "status": "success",
  "success": true,
  "input": {
    "stream": "Maths",
    "district": "Colombo",
    "z_score": 1.9
  },
  "safe": [...],
  "probable": [...],
  "reach": [...],
  "explanation": "...",
  "message": "..."
}
```

**Checks:**
- ✅ Status code: 200
- ✅ At least one category (safe/probable/reach) contains data
- ✅ Explanation is present and readable
- ✅ Response structure matches expected format

---

### STEP 2: Verification Checks

#### ✅ CHECK 1: Cut-off Data Loaded
- Verify `safe`, `probable`, or `reach` arrays contain data
- If all empty → data not loaded or stream/district mismatch

#### ✅ CHECK 2: Prediction Accuracy
For Z = 1.90 (Maths, Colombo):
- **Safe**: Lower-ranked universities (Z > avg + 0.5)
- **Probable**: Mid-tier universities (Z between avg - 0.3 and avg + 0.5)
- **Reach**: Top universities like Moratuwa, Colombo CS (Z < avg - 0.3)

**Expected:**
- Moratuwa/Colombo CS should appear in **Reach** or **Probable**
- **NOT** in Safe

#### ✅ CHECK 3: Category Logic
- **Safe**: `z_score > (avg_cutoff + 0.5)`
- **Probable**: `z_score >= (avg_cutoff - 0.3) AND z_score <= (avg_cutoff + 0.5)`
- **Reach**: `z_score >= (avg_cutoff - 1.0) AND z_score < (avg_cutoff - 0.3)`

✅ No overlap, no gaps

#### ✅ CHECK 4: LLM Explanation
- Human-readable explanation
- Mentions stream, district, trend
- Advice tone (not robotic)
- 2-3 paragraphs

#### ✅ CHECK 5: Prediction History Storage
**Check MongoDB:**
```javascript
use unimate
db.zscore_predictions.find().sort({createdAt:-1}).limit(1)
```

**Expected:**
```json
{
  "userId": "...",
  "z_score": 1.9,
  "stream": "Maths",
  "district": "Colombo",
  "result": {
    "safe_count": 5,
    "probable_count": 10,
    "reach_count": 3
  },
  "createdAt": ISODate("...")
}
```

---

### STEP 3: Negative Tests

#### 3.1 Invalid Stream
```json
{
  "stream": "Biology",
  "district": "Colombo",
  "z_score": 1.90
}
```
**Expected:** 400 Bad Request with error message

#### 3.2 Extreme High Z-score
```json
{
  "stream": "Maths",
  "district": "Colombo",
  "z_score": 3.0
}
```
**Expected:** Most/all courses in Safe category

#### 3.3 Low Z-score
```json
{
  "stream": "Maths",
  "district": "Colombo",
  "z_score": 0.9
}
```
**Expected:** Mostly Reach or empty Safe category

---

### STEP 4: Chat Integration Test

**Test via Frontend:**
1. Open chat interface
2. Ask: "What courses can I get with Z-score 1.9 in Maths stream, Colombo district?"
3. Verify:
   - AI calls `zscore_predict` tool
   - Same categories returned
   - Friendly explanation
   - Sources cited

---

## 🔧 Troubleshooting

### Issue: "Prediction service is currently unavailable"
**Cause:** MongoDB not connected
**Fix:**
1. Check `MONGODB_URI` in `apps/ai/.env`
2. Verify MongoDB Atlas connection
3. Check network/firewall settings

### Issue: "No historical cut-off data found"
**Cause:** Data not seeded
**Fix:**
1. Run: `python scripts/seed_cutoffs.py`
2. Verify: `python test_zscore_data.py` shows > 3000 records

### Issue: All categories empty
**Possible Causes:**
1. Stream name mismatch (check normalization)
2. District name mismatch
3. No data for that stream/district combination
4. Z-score out of range

**Fix:**
- Check data: `db.cutoffs.find({stream: "Maths", district: "Colombo"})`
- Verify stream normalization in code
- Check district spelling

### Issue: 503 Service Unavailable
**Cause:** MongoDB connection failed
**Fix:**
- Check MongoDB URI
- Verify network connectivity
- Check MongoDB Atlas IP whitelist

---

## 📊 Expected Test Results

### Valid Request (Maths, Colombo, 1.90)
- **Status:** 200 OK
- **Safe:** 5-15 courses
- **Probable:** 10-20 courses
- **Reach:** 3-10 courses
- **Explanation:** Present and readable

### Invalid Stream
- **Status:** 400 Bad Request
- **Error:** "Invalid stream. Must be one of: Bio, Maths, Arts, Commerce, Technology"

### High Z-score (3.0)
- **Status:** 200 OK
- **Safe:** Most/all courses
- **Probable:** Few or none
- **Reach:** None

### Low Z-score (0.9)
- **Status:** 200 OK
- **Safe:** None or very few
- **Probable:** Few
- **Reach:** Most courses

---

## ✅ Success Criteria

All tests pass when:
1. ✅ FastAPI server running
2. ✅ MongoDB connected
3. ✅ Data seeded (> 3000 records)
4. ✅ Valid request returns 200 with data
5. ✅ Invalid stream returns 400
6. ✅ Categories are logically correct
7. ✅ Explanation is generated
8. ✅ Prediction history stored (if userId provided)

---

## 📝 Next Steps

1. **Set up MongoDB connection**
   - Add `MONGODB_URI` to `apps/ai/.env`
   - Verify connection in startup logs

2. **Seed cut-off data**
   - Run: `python scripts/seed_cutoffs.py`
   - Verify: `python test_zscore_data.py`

3. **Run test suite**
   - PowerShell: `.\run_zscore_tests.ps1`
   - Python: `python test_zscore_endpoint.py`

4. **Test via chat interface**
   - Start frontend and backend
   - Test natural language queries

---

**Status:** ✅ Code ready, ⚠️ Requires MongoDB setup and data seeding

