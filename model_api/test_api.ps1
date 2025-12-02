# Ollama Models API 測試腳本
# 啟動指令：python main.py

Write-Host "=== Ollama Models API 測試 ===" -ForegroundColor Cyan
Write-Host ""

# 檢查 Server 是否啟動
try {
    Invoke-RestMethod -Uri http://127.0.0.1:6000/health -TimeoutSec 2 | Out-Null
    Write-Host "Server 已啟動" -ForegroundColor Green
} catch {
    Write-Host "Server 未啟動，請先執行: python main.py" -ForegroundColor Red
    exit 1
}
Write-Host ""

# 健康檢查
Write-Host "健康檢查" -ForegroundColor Yellow
$health = Invoke-RestMethod -Uri http://127.0.0.1:6000/health
Write-Host "健康狀態: $($health.status)" -ForegroundColor Green
Write-Host ""

Write-Host "準備同時發送兩個請求..." -ForegroundColor Yellow
Write-Host "- 請求 1: mistral"
Write-Host "- 請求 2: llama3.2"
Write-Host ""

$body1 = @{
    prompt = "簡單介紹一下自己"
    model = "mistral"
} | ConvertTo-Json

$body2 = @{
    prompt = "簡單介紹一下自己"
    model = "llama3.2"
} | ConvertTo-Json

# 記錄開始時間
$startTime = Get-Date
Write-Host "開始時間: $($startTime.ToString('HH:mm:ss'))" -ForegroundColor Gray
Write-Host ""

# 同時發送兩個請求（背景執行）
Write-Host "發送請求 1 (mistral)..." -ForegroundColor Cyan
$job1 = Start-Job -ScriptBlock {
    param($body)
    $response = Invoke-RestMethod -Uri http://127.0.0.1:6000/api/v1/completion `
        -Method Post -Body $body -ContentType "application/json"
    return @{
        model = $response.model
        time = Get-Date
        response = $response.response
    }
} -ArgumentList $body1

Write-Host "發送請求 2 (llama3.2)..." -ForegroundColor Cyan
$job2 = Start-Job -ScriptBlock {
    param($body)
    $response = Invoke-RestMethod -Uri http://127.0.0.1:6000/api/v1/completion `
        -Method Post -Body $body -ContentType "application/json"
    return @{
        model = $response.model
        time = Get-Date
        response = $response.response
    }
} -ArgumentList $body2

Write-Host ""
Write-Host "等待兩個請求完成..." -ForegroundColor Yellow
Write-Host ""

# 等待兩個請求完成
Wait-Job $job1, $job2 | Out-Null

# 取得結果
$result1 = Receive-Job $job1
$result2 = Receive-Job $job2

# 清理 job
Remove-Job $job1, $job2

$endTime = Get-Date
Write-Host "結束時間: $($endTime.ToString('HH:mm:ss'))" -ForegroundColor Gray
Write-Host "總耗時: $(($endTime - $startTime).TotalSeconds) 秒" -ForegroundColor Gray
Write-Host ""

# 顯示結果
Write-Host "=== 結果 ===" -ForegroundColor Green
Write-Host ""
Write-Host "請求 1 (mistral):" -ForegroundColor Cyan
Write-Host "  完成時間: $($result1.time.ToString('HH:mm:ss.fff'))"
Write-Host "  回應: $($result1.response.Substring(0, [Math]::Min(100, $result1.response.Length)))..."
Write-Host ""
Write-Host "請求 2 (llama3.2):" -ForegroundColor Cyan
Write-Host "  完成時間: $($result2.time.ToString('HH:mm:ss.fff'))"
Write-Host "  回應: $($result2.response.Substring(0, [Math]::Min(100, $result2.response.Length)))..."
Write-Host ""

Write-Host "=== 測試完成 ===" -ForegroundColor Cyan
