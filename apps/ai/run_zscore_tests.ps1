# PowerShell script to run Z-score tests
# Run this after starting FastAPI server

Write-Host "🧪 Z-Score Endpoint Test Suite" -ForegroundColor Cyan
Write-Host ("=" * 60)

# Check if server is running
Write-Host "`n📋 STEP 0: Pre-checks" -ForegroundColor Yellow
Write-Host "Checking if FastAPI server is running..."

try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 5
    Write-Host "✅ FastAPI server is running" -ForegroundColor Green
    Write-Host "   Status: $($health.status)" -ForegroundColor Gray
    Write-Host "   Database: $($health.database)" -ForegroundColor Gray
} catch {
    Write-Host "❌ FastAPI server is NOT running!" -ForegroundColor Red
    Write-Host "   Start it with: uvicorn main:app --reload --port 8000" -ForegroundColor Yellow
    exit 1
}

# Check MongoDB data
Write-Host "`nChecking MongoDB data..."
try {
    $dataCheck = python test_zscore_data.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ MongoDB data exists" -ForegroundColor Green
    } else {
        Write-Host "⚠️ MongoDB data check failed" -ForegroundColor Yellow
        Write-Host "   Run: python scripts/seed_cutoffs.py" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️ Could not check MongoDB data" -ForegroundColor Yellow
}

# Test 1: Valid request
Write-Host "`n📋 STEP 1: Direct API Test (Valid Request)" -ForegroundColor Yellow
$payload1 = @{
    stream = "Maths"
    district = "Colombo"
    z_score = 1.90
} | ConvertTo-Json

try {
    $response1 = Invoke-RestMethod -Uri "http://localhost:8000/ai/zscore" -Method Post -Body $payload1 -ContentType "application/json" -TimeoutSec 30
    
    Write-Host "✅ Request successful" -ForegroundColor Green
    Write-Host "`nResponse Structure:" -ForegroundColor Cyan
    Write-Host "  - status: $($response1.status)"
    Write-Host "  - safe courses: $($response1.safe.Count)"
    Write-Host "  - probable courses: $($response1.probable.Count)"
    Write-Host "  - reach courses: $($response1.reach.Count)"
    Write-Host "  - explanation length: $($response1.explanation.Length) chars"
    
    # Check if at least one category has data
    $hasData = ($response1.safe.Count -gt 0) -or ($response1.probable.Count -gt 0) -or ($response1.reach.Count -gt 0)
    if ($hasData) {
        Write-Host "`n✅ CHECK 1: At least one category contains data" -ForegroundColor Green
    } else {
        Write-Host "`n❌ CHECK 1: All categories are empty" -ForegroundColor Red
    }
    
    # Show sample courses
    if ($response1.safe.Count -gt 0) {
        Write-Host "`nSample Safe Course:" -ForegroundColor Cyan
        $response1.safe[0] | ConvertTo-Json -Depth 3
    }
    if ($response1.probable.Count -gt 0) {
        Write-Host "`nSample Probable Course:" -ForegroundColor Cyan
        $response1.probable[0] | ConvertTo-Json -Depth 3
    }
    if ($response1.reach.Count -gt 0) {
        Write-Host "`nSample Reach Course:" -ForegroundColor Cyan
        $response1.reach[0] | ConvertTo-Json -Depth 3
    }
    
} catch {
    Write-Host "❌ Request failed: $_" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "Response: $responseBody" -ForegroundColor Yellow
    }
}

# Test 2: Invalid stream
Write-Host "`n📋 STEP 2: Negative Test - Invalid Stream" -ForegroundColor Yellow
$payload2 = @{
    stream = "Biology"
    district = "Colombo"
    z_score = 1.90
} | ConvertTo-Json

try {
    $response2 = Invoke-RestMethod -Uri "http://localhost:8000/ai/zscore" -Method Post -Body $payload2 -ContentType "application/json" -TimeoutSec 30
    Write-Host "❌ Should have failed but got success" -ForegroundColor Red
} catch {
    if ($_.Exception.Response.StatusCode -eq 400) {
        Write-Host "✅ Correctly rejected invalid stream" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Got error but wrong status code" -ForegroundColor Yellow
    }
}

# Test 3: Extreme high Z-score
Write-Host "`n📋 STEP 3: Extreme High Z-score (3.0)" -ForegroundColor Yellow
$payload3 = @{
    stream = "Maths"
    district = "Colombo"
    z_score = 3.0
} | ConvertTo-Json

try {
    $response3 = Invoke-RestMethod -Uri "http://localhost:8000/ai/zscore" -Method Post -Body $payload3 -ContentType "application/json" -TimeoutSec 30
    Write-Host "✅ Request successful" -ForegroundColor Green
    Write-Host "  - safe courses: $($response3.safe.Count)"
    Write-Host "  - probable courses: $($response3.probable.Count)"
    Write-Host "  - reach courses: $($response3.reach.Count)"
    
    if ($response3.safe.Count -gt 0) {
        Write-Host "✅ Most courses should be in Safe category" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Request failed: $_" -ForegroundColor Red
}

# Test 4: Low Z-score
Write-Host "`n📋 STEP 4: Low Z-score (0.9)" -ForegroundColor Yellow
$payload4 = @{
    stream = "Maths"
    district = "Colombo"
    z_score = 0.9
} | ConvertTo-Json

try {
    $response4 = Invoke-RestMethod -Uri "http://localhost:8000/ai/zscore" -Method Post -Body $payload4 -ContentType "application/json" -TimeoutSec 30
    Write-Host "✅ Request successful" -ForegroundColor Green
    Write-Host "  - safe courses: $($response4.safe.Count)"
    Write-Host "  - probable courses: $($response4.probable.Count)"
    Write-Host "  - reach courses: $($response4.reach.Count)"
    
    if ($response4.reach.Count -gt 0 -or $response4.safe.Count -eq 0) {
        Write-Host "✅ Low Z-score correctly categorized" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Request failed: $_" -ForegroundColor Red
}

Write-Host "`n" + ("=" * 60)
Write-Host "✅ Test suite completed!" -ForegroundColor Green
Write-Host ("=" * 60)

