# Z-Score Endpoint - Complete Manual Testing Guide

## 📋 Table of Contents
1. [Pre-Checks](#pre-checks)
2. [Basic Functionality Tests](#basic-functionality-tests)
3. [Verification Checks](#verification-checks)
4. [Negative Tests](#negative-tests)
5. [Edge Cases](#edge-cases)
6. [Data Accuracy Tests](#data-accuracy-tests)
7. [Performance Tests](#performance-tests)
8. [Integration Tests](#integration-tests)

---

## 🔍 Pre-Checks

### Test 0.1: Server Health Check
**Command:**
```powershell
curl http://localhost:8000/health
```

**Expected Result:**
```json
{
  "status": "healthy",
  "database": "connected",
  "gemini_api": "configured"
}
```

**✅ Pass Criteria:**
- Status is "healthy"
- Database is "connected" (not "disconnected")
- Gemini API is "configured"

---

### Test 0.2: MongoDB Data Verification
**Command:**
```powershell
python test_zscore_data.py
```

**Expected Result:**
```
Records: 3130
✅ Data is loaded correctly
```

**✅ Pass Criteria:**
- Records count > 3000
- No errors

---

### Test 0.3: Server Startup Logs
**Check terminal where FastAPI is running**

**Expected Logs:**
```
✅ MongoDB connected successfully
✅ ZScore tool initialized
INFO: Application startup complete.
```

**✅ Pass Criteria:**
- No errors about MongoDB connection
- ZScore tool initialized successfully
- No warnings about missing environment variables

---

## 🧪 Basic Functionality Tests

### Test 1: Valid Request - Maths Stream, Colombo District
**Request:**
```powershell
$body = @{
    stream = "Maths"
    district = "Colombo"
    z_score = 1.90
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/ai/zscore" -Method Post -Body $body -ContentType "application/json"
```

**Expected Response Structure:**
```json
{
  "status": "success",
  "success": true,
  "input": {
    "stream": "Maths",
    "district": "Colombo",
    "z_score": 1.9
  },
  "safe": [
    {
      "course": "Engineering",
      "university": "Moratuwa",
      "avg_cutoff": 1.85,
      "min_cutoff": 1.80,
      "max_cutoff": 1.90,
      "years_data": 5,
      "trend": "increasing",
      "district": "Colombo"
    }
  ],
  "probable": [...],
  "reach": [...],
  "explanation": "With a Z-score of 1.9...",
  "message": "Found X safe, Y probable, and Z reach courses"
}
```

**✅ Pass Criteria:**
- Status code: 200 OK
- `status` field is "success"
- `input` field contains request parameters
- At least one category (safe/probable/reach) has data
- `explanation` is present and readable (50+ characters)
- All course objects have required fields

---

### Test 2: Valid Request - Bio Stream, Different District
**Request:**
```powershell
$body = @{
    stream = "Bio"
    district = "Gampaha"
    z_score = 1.75
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/ai/zscore" -Method Post -Body $body -ContentType "application/json"
```

**Expected:**
- Status: 200 OK
- Response contains Bio stream courses
- District-specific results for Gampaha

**✅ Pass Criteria:**
- Different courses than Colombo district
- Results are relevant to Bio stream

---

### Test 3: Valid Request - Without District
**Request:**
```powershell
$body = @{
    stream = "Maths"
    z_score = 1.90
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/ai/zscore" -Method Post -Body $body -ContentType "application/json"
```

**Expected:**
- Status: 200 OK
- Results from all districts
- `input.district` shows "All districts"

**✅ Pass Criteria:**
- Works without district parameter
- Returns broader results

---

## ✅ Verification Checks

### Check 1: Cut-off Data Loaded
**What to Check:**
- Look at response arrays: `safe`, `probable`, `reach`
- At least one must contain data

**Expected:**
```json
{
  "safe": [/* at least 1 course */],
  "probable": [/* at least 1 course */],
  "reach": [/* may be empty or have courses */]
}
```

**✅ Pass:** At least one category has data

**❌ Fail:** All categories are empty
- **Possible causes:**
  - Stream/district mismatch
  - Z-score out of range
  - Data not seeded for that combination

---

### Check 2: Prediction Accuracy
**Test Case:** Z = 1.90, Maths, Colombo

**What to Check:**
- Top universities (Moratuwa, Colombo CS) should appear in **Reach** or **Probable**
- They should **NOT** be in **Safe**

**Expected Logic:**
- **Safe:** Lower-ranked universities (Z > avg + 0.5)
- **Probable:** Mid-tier universities (Z between avg - 0.3 and avg + 0.5)
- **Reach:** Top universities (Z < avg - 0.3)

**✅ Pass:** Moratuwa/Colombo CS in Reach/Probable, not Safe

**❌ Fail:** Top universities in Safe category
- **Possible cause:** Logic error in categorization

---

### Check 3: Category Logic Sanity
**Rules to Verify:**
- **Safe:** `z_score > (avg_cutoff + 0.5)`
- **Probable:** `z_score >= (avg_cutoff - 0.3) AND z_score <= (avg_cutoff + 0.5)`
- **Reach:** `z_score >= (avg_cutoff - 1.0) AND z_score < (avg_cutoff - 0.3)`

**Test Method:**
1. Pick a course from Safe category
2. Check: `z_score > (course.avg_cutoff + 0.5)` should be true
3. Pick a course from Probable category
4. Check: `(course.avg_cutoff - 0.3) <= z_score <= (course.avg_cutoff + 0.5)` should be true

**✅ Pass:** All categories follow the rules correctly

**❌ Fail:** Courses don't match their category rules

---

### Check 4: LLM Explanation Quality
**What to Check:**
- Explanation is present
- Length > 50 characters
- Mentions stream, district, and Z-score
- Human-readable (not robotic)
- Provides advice

**Good Example:**
```
"With a Z-score of 1.9 in the Maths stream for Colombo district, 
you have a probable chance of securing admission to several 
engineering programs. Based on historical data..."
```

**Bad Example:**
```
"Z-score 1.9. Stream: Maths. Courses found."
```

**✅ Pass:** Explanation is comprehensive and helpful

**❌ Fail:** Explanation missing, too short, or robotic

---

### Check 5: Prediction History Storage
**Test with userId:**
```powershell
$body = @{
    stream = "Maths"
    district = "Colombo"
    z_score = 1.90
    userId = "test_user_123"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/ai/zscore" -Method Post -Body $body -ContentType "application/json"
```

**Verify in MongoDB:**
```javascript
use unimate
db.zscore_predictions.find({userId: "test_user_123"}).sort({createdAt: -1}).limit(1).pretty()
```

**Expected Document:**
```json
{
  "_id": ObjectId("..."),
  "userId": "test_user_123",
  "z_score": 1.9,
  "stream": "Maths",
  "district": "Colombo",
  "result": {
    "safe_count": 5,
    "probable_count": 10,
    "reach_count": 3
  },
  "createdAt": ISODate("2025-01-10T...")
}
```

**✅ Pass:** Document exists with correct structure

**❌ Fail:** Document not found or structure incorrect

---

## ❌ Negative Tests

### Test N1: Invalid Stream
**Request:**
```powershell
$body = @{
    stream = "Biology"  # Invalid - should be "Bio"
    district = "Colombo"
    z_score = 1.90
} | ConvertTo-Json

try {
    Invoke-RestMethod -Uri "http://localhost:8000/ai/zscore" -Method Post -Body $body -ContentType "application/json"
} catch {
    Write-Host "Status: $($_.Exception.Response.StatusCode)"
    $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
    $responseBody = $reader.ReadToEnd()
    Write-Host "Response: $responseBody"
}
```

**Expected:**
- Status code: 400 Bad Request
- Error message: "Invalid stream. Must be one of: Bio, Maths, Arts, Commerce, Technology"

**✅ Pass:** Correctly rejects invalid stream

---

### Test N2: Missing Required Field (stream)
**Request:**
```powershell
$body = @{
    district = "Colombo"
    z_score = 1.90
    # stream is missing
} | ConvertTo-Json

try {
    Invoke-RestMethod -Uri "http://localhost:8000/ai/zscore" -Method Post -Body $body -ContentType "application/json"
} catch {
    Write-Host "Status: $($_.Exception.Response.StatusCode)"
}
```

**Expected:**
- Status code: 422 Unprocessable Entity (FastAPI validation error)
- Error about missing required field

**✅ Pass:** Correctly rejects missing stream

---

### Test N3: Missing Required Field (z_score)
**Request:**
```powershell
$body = @{
    stream = "Maths"
    district = "Colombo"
    # z_score is missing
} | ConvertTo-Json
```

**Expected:**
- Status code: 422 Unprocessable Entity
- Error about missing z_score

**✅ Pass:** Correctly rejects missing z_score

---

### Test N4: Invalid Z-score Range (Too High)
**Request:**
```powershell
$body = @{
    stream = "Maths"
    district = "Colombo"
    z_score = 10.0  # Too high (valid range: -5 to 5)
} | ConvertTo-Json
```

**Expected:**
- Status code: 400 Bad Request
- Error: "Z-score must be between -5 and 5"

**✅ Pass:** Correctly rejects out-of-range Z-score

---

### Test N5: Invalid Z-score Range (Too Low)
**Request:**
```powershell
$body = @{
    stream = "Maths"
    district = "Colombo"
    z_score = -10.0  # Too low
} | ConvertTo-Json
```

**Expected:**
- Status code: 400 Bad Request
- Error: "Z-score must be between -5 and 5"

**✅ Pass:** Correctly rejects out-of-range Z-score

---

### Test N6: Invalid Data Type (z_score as string)
**Request:**
```powershell
$body = @{
    stream = "Maths"
    district = "Colombo"
    z_score = "1.90"  # String instead of number
} | ConvertTo-Json
```

**Expected:**
- Status code: 422 Unprocessable Entity
- Validation error about type

**✅ Pass:** Correctly rejects wrong data type

---

## 🔬 Edge Cases

### Test E1: Extreme High Z-score (3.0)
**Request:**
```powershell
$body = @{
    stream = "Maths"
    district = "Colombo"
    z_score = 3.0
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/ai/zscore" -Method Post -Body $body -ContentType "application/json"
Write-Host "Safe: $($response.safe.Count)"
Write-Host "Probable: $($response.probable.Count)"
Write-Host "Reach: $($response.reach.Count)"
```

**Expected:**
- Status: 200 OK
- Most/all courses in **Safe** category
- Very few or none in **Reach**

**✅ Pass:** High Z-score correctly categorized

---

### Test E2: Extreme Low Z-score (0.9)
**Request:**
```powershell
$body = @{
    stream = "Maths"
    district = "Colombo"
    z_score = 0.9
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/ai/zscore" -Method Post -Body $body -ContentType "application/json"
Write-Host "Safe: $($response.safe.Count)"
Write-Host "Probable: $($response.probable.Count)"
Write-Host "Reach: $($response.reach.Count)"
```

**Expected:**
- Status: 200 OK
- Most courses in **Reach** category
- Very few or none in **Safe**

**✅ Pass:** Low Z-score correctly categorized

---

### Test E3: Boundary Z-score (Exactly at threshold)
**Request:**
```powershell
# Test with a Z-score that's exactly at a threshold
$body = @{
    stream = "Maths"
    district = "Colombo"
    z_score = 1.85  # Common cut-off value
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/ai/zscore" -Method Post -Body $body -ContentType "application/json"
```

**Expected:**
- Status: 200 OK
- Courses properly categorized
- No errors with boundary values

**✅ Pass:** Boundary values handled correctly

---

### Test E4: All Streams Test
**Test each stream:**
```powershell
$streams = @("Bio", "Maths", "Arts", "Commerce", "Technology")

foreach ($stream in $streams) {
    Write-Host "`nTesting stream: $stream"
    $body = @{
        stream = $stream
        district = "Colombo"
        z_score = 1.90
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/ai/zscore" -Method Post -Body $body -ContentType "application/json"
        Write-Host "  ✅ Success - Safe: $($response.safe.Count), Probable: $($response.probable.Count), Reach: $($response.reach.Count)"
    } catch {
        Write-Host "  ❌ Failed: $_"
    }
}
```

**Expected:**
- All streams return 200 OK
- Each stream has different courses
- No errors

**✅ Pass:** All streams work correctly

---

### Test E5: Different Districts
**Test multiple districts:**
```powershell
$districts = @("Colombo", "Gampaha", "Kandy", "Jaffna")

foreach ($district in $districts) {
    Write-Host "`nTesting district: $district"
    $body = @{
        stream = "Maths"
        district = $district
        z_score = 1.90
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/ai/zscore" -Method Post -Body $body -ContentType "application/json"
        Write-Host "  ✅ Success - Results: $($response.safe.Count + $response.probable.Count + $response.reach.Count) courses"
    } catch {
        Write-Host "  ❌ Failed: $_"
    }
}
```

**Expected:**
- All districts return 200 OK
- District-specific results (may vary)
- No errors

**✅ Pass:** District filtering works

---

## 📊 Data Accuracy Tests

### Test D1: Course Data Completeness
**Check a sample course from response:**
```powershell
$body = @{
    stream = "Maths"
    district = "Colombo"
    z_score = 1.90
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/ai/zscore" -Method Post -Body $body -ContentType "application/json"

# Check first safe course
if ($response.safe.Count -gt 0) {
    $course = $response.safe[0]
    Write-Host "Course: $($course.course)"
    Write-Host "University: $($course.university)"
    Write-Host "Avg Cut-off: $($course.avg_cutoff)"
    Write-Host "Min Cut-off: $($course.min_cutoff)"
    Write-Host "Max Cut-off: $($course.max_cutoff)"
    Write-Host "Years Data: $($course.years_data)"
    Write-Host "Trend: $($course.trend)"
    Write-Host "District: $($course.district)"
}
```

**Expected:**
- All fields present
- `avg_cutoff` is between `min_cutoff` and `max_cutoff`
- `years_data` > 0
- `trend` is one of: "increasing", "stable", "decreasing"

**✅ Pass:** All fields valid and complete

---

### Test D2: Trend Calculation
**Verify trends make sense:**
```powershell
# Get courses with different trends
$body = @{
    stream = "Maths"
    district = "Colombo"
    z_score = 1.90
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/ai/zscore" -Method Post -Body $body -ContentType "application/json"

# Check trends
$increasing = ($response.safe + $response.probable + $response.reach) | Where-Object { $_.trend -eq "increasing" }
$stable = ($response.safe + $response.probable + $response.reach) | Where-Object { $_.trend -eq "stable" }
$decreasing = ($response.safe + $response.probable + $response.reach) | Where-Object { $_.trend -eq "decreasing" }

Write-Host "Increasing: $($increasing.Count)"
Write-Host "Stable: $($stable.Count)"
Write-Host "Decreasing: $($decreasing.Count)"
```

**Expected:**
- Trends are calculated (not all "stable")
- Trends make sense based on historical data

**✅ Pass:** Trends are varied and logical

---

### Test D3: Cut-off Range Validation
**Verify min <= avg <= max:**
```powershell
$body = @{
    stream = "Maths"
    district = "Colombo"
    z_score = 1.90
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/ai/zscore" -Method Post -Body $body -ContentType "application/json"

$allCourses = $response.safe + $response.probable + $response.reach
$invalid = $allCourses | Where-Object { 
    $_.min_cutoff -gt $_.avg_cutoff -or 
    $_.max_cutoff -lt $_.avg_cutoff -or
    $_.min_cutoff -gt $_.max_cutoff
}

if ($invalid.Count -eq 0) {
    Write-Host "✅ All cut-off ranges are valid"
} else {
    Write-Host "❌ Found $($invalid.Count) courses with invalid ranges"
}
```

**Expected:**
- All courses have valid ranges: `min <= avg <= max`

**✅ Pass:** All ranges are valid

---

## ⚡ Performance Tests

### Test P1: Response Time
**Measure response time:**
```powershell
$body = @{
    stream = "Maths"
    district = "Colombo"
    z_score = 1.90
} | ConvertTo-Json

$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/ai/zscore" -Method Post -Body $body -ContentType "application/json"
    $stopwatch.Stop()
    Write-Host "Response time: $($stopwatch.ElapsedMilliseconds) ms"
} catch {
    Write-Host "Request failed"
}
```

**Expected:**
- Response time < 3000ms (3 seconds)
- Ideally < 1000ms

**✅ Pass:** Response time acceptable

---

### Test P2: Concurrent Requests
**Test multiple simultaneous requests:**
```powershell
$body = @{
    stream = "Maths"
    district = "Colombo"
    z_score = 1.90
} | ConvertTo-Json

$jobs = 1..5 | ForEach-Object {
    Start-Job -ScriptBlock {
        param($body)
        $response = Invoke-RestMethod -Uri "http://localhost:8000/ai/zscore" -Method Post -Body $body -ContentType "application/json"
        return $response.status
    } -ArgumentList $body
}

$results = $jobs | Wait-Job | Receive-Job
$jobs | Remove-Job

Write-Host "Successful requests: $(($results | Where-Object { $_ -eq 'success' }).Count) / 5"
```

**Expected:**
- All 5 requests succeed
- No errors or timeouts

**✅ Pass:** Handles concurrent requests

---

## 🔗 Integration Tests

### Test I1: Chat Interface Integration
**Test via frontend chat:**

1. Start frontend: `cd apps/web && npm run dev`
2. Start backend: `cd apps/api && npm run dev`
3. Login to the application
4. In chat, ask: **"What courses can I get with Z-score 1.9 in Maths stream, Colombo district?"**

**Expected:**
- AI calls `zscore_predict` tool automatically
- Response shows same categories (safe/probable/reach)
- Friendly explanation in chat format
- Sources cited

**✅ Pass:** Chat integration works

---

### Test I2: Tool Called by AI
**Verify tool is registered and callable:**

Check if the tool appears in available tools when AI processes the request.

**Expected:**
- Tool is registered
- AI can call it automatically
- Results are formatted for chat

**✅ Pass:** Tool integration works

---

## 📝 Test Results Template

Use this template to record your test results:

```
Test ID: [Test Name]
Date: [Date]
Status: ✅ PASS / ❌ FAIL / ⚠️ PARTIAL

Request:
[Request details]

Response:
[Response details]

Issues Found:
[Any issues]

Notes:
[Additional notes]
```

---

## 🎯 Quick Test Checklist

Use this checklist for quick verification:

- [ ] Server health check passes
- [ ] MongoDB data exists (3130+ records)
- [ ] Valid request returns 200 OK
- [ ] Response has all required fields
- [ ] At least one category has data
- [ ] Explanation is present and readable
- [ ] Invalid stream returns 400
- [ ] Missing fields return 422
- [ ] Out-of-range Z-score returns 400
- [ ] High Z-score (3.0) returns mostly Safe
- [ ] Low Z-score (0.9) returns mostly Reach
- [ ] All streams work
- [ ] Response time < 3 seconds
- [ ] Chat integration works

---

## 🐛 Common Issues & Solutions

### Issue: All categories empty
**Possible causes:**
- Stream/district name mismatch
- No data for that combination
- Z-score out of range

**Solution:**
- Check MongoDB: `db.cutoffs.find({stream: "Maths", district: "Colombo"})`
- Verify stream name (case-sensitive)
- Try different district or remove district parameter

---

### Issue: 503 Service Unavailable
**Possible causes:**
- MongoDB not connected
- Server needs restart

**Solution:**
- Check MongoDB connection in startup logs
- Restart FastAPI server

---

### Issue: 404 Not Found
**Possible causes:**
- No data for that stream/district
- Data not seeded

**Solution:**
- Run: `python scripts/seed_cutoffs.py`
- Check data exists in MongoDB

---

### Issue: Explanation missing or poor quality
**Possible causes:**
- Gemini API key not set
- Gemini API error
- Fallback explanation used

**Solution:**
- Check `GEMINI_API_KEY` in `.env`
- Check Gemini API status
- Fallback should still provide basic explanation

---

## ✅ Success Criteria

All tests pass when:
1. ✅ All pre-checks pass
2. ✅ Valid requests return 200 with data
3. ✅ Invalid requests return appropriate errors
4. ✅ Edge cases handled correctly
5. ✅ Data is accurate and complete
6. ✅ Performance is acceptable
7. ✅ Integration works

---

*Last Updated: January 10, 2025*

