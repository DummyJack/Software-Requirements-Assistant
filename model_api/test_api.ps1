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

# 測試文本生成
Write-Host "測試生成" -ForegroundColor Yellow
$body1 = @{ 
    prompt = "用一句話解釋什麼是 API ?" 
} | ConvertTo-Json -Compress

$response1 = Invoke-RestMethod -Uri http://127.0.0.1:6000/api/v1/completion `
    -Method Post -Body $body1 -ContentType "application/json"
Write-Host "使用模型: $($response1.model)" -ForegroundColor Green
Write-Host "回應: $($response1.response)" -ForegroundColor White
Write-Host ""

Write-Host "=== 測試完成 ===" -ForegroundColor Cyan
