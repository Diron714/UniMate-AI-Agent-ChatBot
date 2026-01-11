# Quick Z-Score Test Script
Write-Host "Z-Score Test" -ForegroundColor Cyan
Write-Host ("=" * 60)

# Step 1: Check data
Write-Host "`nStep 1: Checking MongoDB data..." -ForegroundColor Yellow
python test_zscore_data.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "Data check failed!" -ForegroundColor Red
    exit 1
}

# Step 2: Test endpoint
Write-Host "`nStep 2: Testing Z-score endpoint..." -ForegroundColor Yellow
$body = @{
    stream = "Maths"
    district = "Colombo"
    z_score = 1.90
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/ai/zscore" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 30
    
    Write-Host "Request successful!" -ForegroundColor Green
    Write-Host "`nResponse Summary:" -ForegroundColor Cyan
    Write-Host "  Status: $($response.status)"
    Write-Host "  Safe courses: $($response.safe.Count)"
    Write-Host "  Probable courses: $($response.probable.Count)"
    Write-Host "  Reach courses: $($response.reach.Count)"
    
    # Verify checks
    $allChecks = $true
    
    if ($response.status -eq "success") {
        Write-Host "`nCHECK 1: Status is success - PASS" -ForegroundColor Green
    } else {
        Write-Host "`nCHECK 1: Status check - FAIL" -ForegroundColor Red
        $allChecks = $false
    }
    
    $hasData = ($response.safe.Count -gt 0) -or ($response.probable.Count -gt 0) -or ($response.reach.Count -gt 0)
    if ($hasData) {
        Write-Host "CHECK 2: At least one category has data - PASS" -ForegroundColor Green
    } else {
        Write-Host "CHECK 2: All categories empty - FAIL" -ForegroundColor Red
        $allChecks = $false
    }
    
    if ($response.explanation -and $response.explanation.Length -gt 50) {
        Write-Host "CHECK 3: Explanation present - PASS" -ForegroundColor Green
    } else {
        Write-Host "CHECK 3: Explanation missing - FAIL" -ForegroundColor Red
        $allChecks = $false
    }
    
    # Show sample courses
    if ($response.safe.Count -gt 0) {
        Write-Host "`nSample Safe Course:" -ForegroundColor Cyan
        Write-Host "  Course: $($response.safe[0].course)"
        Write-Host "  University: $($response.safe[0].university)"
        Write-Host "  Avg Cut-off: $($response.safe[0].avg_cutoff)"
    }
    
    if ($response.probable.Count -gt 0) {
        Write-Host "`nSample Probable Course:" -ForegroundColor Cyan
        Write-Host "  Course: $($response.probable[0].course)"
        Write-Host "  University: $($response.probable[0].university)"
        Write-Host "  Avg Cut-off: $($response.probable[0].avg_cutoff)"
    }
    
    if ($response.reach.Count -gt 0) {
        Write-Host "`nSample Reach Course:" -ForegroundColor Cyan
        Write-Host "  Course: $($response.reach[0].course)"
        Write-Host "  University: $($response.reach[0].university)"
        Write-Host "  Avg Cut-off: $($response.reach[0].avg_cutoff)"
    }
    
    Write-Host "`n" + ("=" * 60)
    if ($allChecks) {
        Write-Host "ALL CHECKS PASSED!" -ForegroundColor Green
    } else {
        Write-Host "Some checks failed. Review above." -ForegroundColor Yellow
    }
    Write-Host ("=" * 60)
    
} catch {
    Write-Host "Request failed!" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Yellow
    
    if ($_.Exception.Response.StatusCode -eq 503) {
        Write-Host "`nService Unavailable - MongoDB may not be connected" -ForegroundColor Yellow
        Write-Host "Solution: Restart FastAPI server" -ForegroundColor Cyan
        Write-Host "Command: uvicorn main:app --reload --port 8000" -ForegroundColor Cyan
    } elseif ($_.Exception.Response.StatusCode -eq 404) {
        Write-Host "`nNo data found for this query" -ForegroundColor Yellow
    }
    
    exit 1
}
