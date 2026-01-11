# Quick Memory and Context System Test
# Run this after starting FastAPI server

Write-Host "🧪 Quick Memory and Context Test" -ForegroundColor Cyan
Write-Host ("=" * 60)

# Check server
Write-Host "`nChecking server..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 5
    if ($health.status -ne "healthy") {
        Write-Host "❌ Server is not healthy" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Server is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Cannot connect to server" -ForegroundColor Red
    Write-Host "   Start server: cd apps/ai && uvicorn main:app --reload --port 8000" -ForegroundColor Yellow
    exit 1
}

# Test 1: University Detection
Write-Host "`n📋 TEST 1: University Detection" -ForegroundColor Yellow
$body1 = @{
    message = "I am selected to University of Jaffna"
    userId = "quick_test_001"
    sessionId = "session_001"
    context = @{}
} | ConvertTo-Json

try {
    $r1 = Invoke-RestMethod -Uri "http://localhost:8000/ai/chat" -Method Post -Body $body1 -ContentType "application/json" -TimeoutSec 30
    Write-Host "✅ Request successful" -ForegroundColor Green
    Write-Host "   University: $($r1.context.university)" -ForegroundColor Cyan
    if ($r1.context.university -eq "University of Jaffna") {
        Write-Host "   ✅ PASS: University detected" -ForegroundColor Green
    } else {
        Write-Host "   ❌ FAIL: University not detected correctly" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Request failed: $_" -ForegroundColor Red
}

Start-Sleep -Seconds 1

# Test 2: Context Persistence
Write-Host "`n📋 TEST 2: Context Persistence" -ForegroundColor Yellow
$body2 = @{
    message = "Where is the library?"
    userId = "quick_test_001"
    sessionId = "session_001"
    context = @{}
} | ConvertTo-Json

try {
    $r2 = Invoke-RestMethod -Uri "http://localhost:8000/ai/chat" -Method Post -Body $body2 -ContentType "application/json" -TimeoutSec 30
    Write-Host "✅ Request successful" -ForegroundColor Green
    Write-Host "   University: $($r2.context.university)" -ForegroundColor Cyan
    Write-Host "   Response preview: $($r2.message.Substring(0, [Math]::Min(100, $r2.message.Length)))..." -ForegroundColor Gray
    
    if ($r2.context.university -eq "University of Jaffna") {
        Write-Host "   ✅ PASS: Context persisted" -ForegroundColor Green
        if ($r2.message -match "jaffna|Jaffna") {
            Write-Host "   ✅ PASS: Response is Jaffna-specific" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️ WARNING: Response may not be Jaffna-specific" -ForegroundColor Yellow
        }
    } else {
        Write-Host "   ❌ FAIL: Context not persisted" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Request failed: $_" -ForegroundColor Red
}

Start-Sleep -Seconds 1

# Test 3: Stage Detection
Write-Host "`n📋 TEST 3: Stage Detection" -ForegroundColor Yellow
$body3 = @{
    message = "I got my A/L results"
    userId = "quick_test_002"
    sessionId = "session_002"
    context = @{}
} | ConvertTo-Json

try {
    $r3 = Invoke-RestMethod -Uri "http://localhost:8000/ai/chat" -Method Post -Body $body3 -ContentType "application/json" -TimeoutSec 30
    Write-Host "✅ Request successful" -ForegroundColor Green
    Write-Host "   Stage: $($r3.context.stage)" -ForegroundColor Cyan
    
    if ($r3.context.stage -eq "pre-application") {
        Write-Host "   ✅ PASS: Stage detected correctly" -ForegroundColor Green
    } else {
        Write-Host "   ❌ FAIL: Stage not detected or incorrect" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Request failed: $_" -ForegroundColor Red
}

Write-Host "`n" + ("=" * 60)
Write-Host "✅ Quick test completed!" -ForegroundColor Green
Write-Host ("=" * 60)
Write-Host "`nFor comprehensive testing, run: python test_memory_context.py" -ForegroundColor Cyan

