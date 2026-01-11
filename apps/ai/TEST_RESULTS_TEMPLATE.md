# Z-Score Endpoint - Test Results

**Date:** _______________  
**Tester:** _______________  
**Environment:** Development / Staging / Production

---

## Pre-Checks

### Test 0.1: Server Health
- [ ] Status: healthy
- [ ] Database: connected
- [ ] Gemini API: configured
- **Result:** ✅ PASS / ❌ FAIL
- **Notes:** _______________

### Test 0.2: MongoDB Data
- [ ] Records: > 3000
- [ ] Data check script passes
- **Result:** ✅ PASS / ❌ FAIL
- **Notes:** _______________

---

## Basic Functionality

### Test 1: Valid Request (Maths, Colombo, 1.90)
- [ ] Status: 200 OK
- [ ] Response has all fields
- [ ] At least one category has data
- [ ] Explanation present
- **Result:** ✅ PASS / ❌ FAIL
- **Response Time:** _____ ms
- **Notes:** _______________

### Test 2: Different Stream (Bio, Gampaha, 1.75)
- [ ] Status: 200 OK
- [ ] Different courses returned
- **Result:** ✅ PASS / ❌ FAIL
- **Notes:** _______________

### Test 3: Without District
- [ ] Status: 200 OK
- [ ] Works without district parameter
- **Result:** ✅ PASS / ❌ FAIL
- **Notes:** _______________

---

## Verification Checks

### Check 1: Data Loaded
- [ ] At least one category has data
- **Result:** ✅ PASS / ❌ FAIL
- **Notes:** _______________

### Check 2: Prediction Accuracy
- [ ] Top universities in Reach/Probable (not Safe)
- **Result:** ✅ PASS / ❌ FAIL
- **Notes:** _______________

### Check 3: Category Logic
- [ ] Safe: z_score > (avg + 0.5)
- [ ] Probable: z_score between (avg - 0.3) and (avg + 0.5)
- [ ] Reach: z_score < (avg - 0.3)
- **Result:** ✅ PASS / ❌ FAIL
- **Notes:** _______________

### Check 4: LLM Explanation
- [ ] Explanation present (> 50 chars)
- [ ] Mentions stream, district, Z-score
- [ ] Human-readable
- **Result:** ✅ PASS / ❌ FAIL
- **Notes:** _______________

### Check 5: Prediction History
- [ ] Stored in MongoDB (if userId provided)
- [ ] Correct structure
- **Result:** ✅ PASS / ❌ FAIL
- **Notes:** _______________

---

## Negative Tests

### Test N1: Invalid Stream
- [ ] Status: 400 Bad Request
- [ ] Error message about invalid stream
- **Result:** ✅ PASS / ❌ FAIL
- **Notes:** _______________

### Test N2: Missing Stream
- [ ] Status: 422 Unprocessable Entity
- **Result:** ✅ PASS / ❌ FAIL
- **Notes:** _______________

### Test N3: Missing Z-score
- [ ] Status: 422 Unprocessable Entity
- **Result:** ✅ PASS / ❌ FAIL
- **Notes:** _______________

### Test N4: Z-score Too High (10.0)
- [ ] Status: 400 Bad Request
- [ ] Error about range
- **Result:** ✅ PASS / ❌ FAIL
- **Notes:** _______________

### Test N5: Z-score Too Low (-10.0)
- [ ] Status: 400 Bad Request
- [ ] Error about range
- **Result:** ✅ PASS / ❌ FAIL
- **Notes:** _______________

---

## Edge Cases

### Test E1: High Z-score (3.0)
- [ ] Status: 200 OK
- [ ] Mostly Safe courses
- **Result:** ✅ PASS / ❌ FAIL
- **Notes:** _______________

### Test E2: Low Z-score (0.9)
- [ ] Status: 200 OK
- [ ] Mostly Reach courses
- **Result:** ✅ PASS / ❌ FAIL
- **Notes:** _______________

### Test E3: All Streams
- [ ] Bio: ✅ / ❌
- [ ] Maths: ✅ / ❌
- [ ] Arts: ✅ / ❌
- [ ] Commerce: ✅ / ❌
- [ ] Technology: ✅ / ❌
- **Result:** ✅ PASS / ❌ FAIL
- **Notes:** _______________

---

## Performance

### Test P1: Response Time
- [ ] < 3000ms
- **Average Time:** _____ ms
- **Result:** ✅ PASS / ❌ FAIL
- **Notes:** _______________

### Test P2: Concurrent Requests
- [ ] All 5 requests succeed
- **Result:** ✅ PASS / ❌ FAIL
- **Notes:** _______________

---

## Integration

### Test I1: Chat Interface
- [ ] AI calls tool automatically
- [ ] Response formatted correctly
- [ ] Explanation in chat format
- **Result:** ✅ PASS / ❌ FAIL
- **Notes:** _______________

---

## Issues Found

### Issue 1:
**Description:** _______________  
**Severity:** Critical / High / Medium / Low  
**Status:** Open / Fixed / Won't Fix  
**Notes:** _______________

### Issue 2:
**Description:** _______________  
**Severity:** Critical / High / Medium / Low  
**Status:** Open / Fixed / Won't Fix  
**Notes:** _______________

---

## Summary

**Total Tests:** _____  
**Passed:** _____  
**Failed:** _____  
**Pass Rate:** _____%

**Overall Status:** ✅ PASS / ❌ FAIL / ⚠️ PARTIAL

**Critical Issues:** _____  
**High Priority Issues:** _____  
**Medium Priority Issues:** _____  
**Low Priority Issues:** _____

---

## Recommendations

1. _______________
2. _______________
3. _______________

---

*Test completed by: _______________*

