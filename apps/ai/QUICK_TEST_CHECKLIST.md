# Quick Test Checklist - Z-Score Endpoint

## ⚡ 5-Minute Quick Test

### 1. Health Check (30 seconds)
```powershell
curl http://localhost:8000/health
```
✅ Database: "connected"  
✅ Status: "healthy"

---

### 2. Data Check (30 seconds)
```powershell
python test_zscore_data.py
```
✅ Records: > 3000

---

### 3. Basic Request (1 minute)
```powershell
$body = @{stream='Maths'; district='Colombo'; z_score=1.90} | ConvertTo-Json
Invoke-RestMethod -Uri 'http://localhost:8000/ai/zscore' -Method Post -Body $body -ContentType 'application/json'
```
✅ Status: 200 OK  
✅ Has safe/probable/reach courses  
✅ Has explanation

---

### 4. Invalid Request (30 seconds)
```powershell
$body = @{stream='Biology'; district='Colombo'; z_score=1.90} | ConvertTo-Json
try { Invoke-RestMethod -Uri 'http://localhost:8000/ai/zscore' -Method Post -Body $body -ContentType 'application/json' } catch { Write-Host "Status: $($_.Exception.Response.StatusCode)" }
```
✅ Status: 400 Bad Request

---

### 5. Edge Cases (2 minutes)
```powershell
# High Z-score
$body = @{stream='Maths'; district='Colombo'; z_score=3.0} | ConvertTo-Json
$r = Invoke-RestMethod -Uri 'http://localhost:8000/ai/zscore' -Method Post -Body $body -ContentType 'application/json'
Write-Host "High Z: Safe=$($r.safe.Count), Reach=$($r.reach.Count)"

# Low Z-score
$body = @{stream='Maths'; district='Colombo'; z_score=0.9} | ConvertTo-Json
$r = Invoke-RestMethod -Uri 'http://localhost:8000/ai/zscore' -Method Post -Body $body -ContentType 'application/json'
Write-Host "Low Z: Safe=$($r.safe.Count), Reach=$($r.reach.Count)"
```
✅ High Z: Mostly Safe  
✅ Low Z: Mostly Reach

---

## ✅ All Quick Tests Pass = System Working!

---

## 📋 Full Test Suite

For comprehensive testing, see: `MANUAL_TESTING_GUIDE.md`

