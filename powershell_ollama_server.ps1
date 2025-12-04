# PowerShell script to start Ollama server

# 檢查並終止佔用 11434 端口的進程
$port = 11434
$tcpConnection = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
if ($tcpConnection) {
    $processId = $tcpConnection.OwningProcess
    Write-Host "Checking process on port $port (PID: $processId) and stopping it" -ForegroundColor White
    Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    Write-Host "Process on port $port is stopped" -ForegroundColor White
}

# 檢查並終止 ollama.exe 進程
$ollamaProcess = Get-Process -Name "ollama" -ErrorAction SilentlyContinue
if ($ollamaProcess) {
    Write-Host "Checking existing ollama.exe process and stopping it" -ForegroundColor White
    Stop-Process -Name "ollama" -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    Write-Host "Ollama.exe is stopped" -ForegroundColor White
}

# 檢查並終止 ollama app.exe 進程
$ollamaAppProcess = Get-Process -Name "ollama app" -ErrorAction SilentlyContinue
if ($ollamaAppProcess) {
    Write-Host "Checking existing ollama app.exe process and stopping it" -ForegroundColor White
    Stop-Process -Name "ollama app" -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    Write-Host "Ollama app.exe is stopped" -ForegroundColor White
}

# 設置環境變數
$env:OLLAMA_HOST = "0.0.0.0:11434"

# logs/ollama
$logDir = "./backend/logs/ollama"
# 如果不存在，創建目錄
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir | Out-Null
}

# log
$timestampFile = Get-Date -Format "yyyy-MM-dd_HH-mm"
$logFile = "$logDir\server_$timestampFile.log"

# 輸出
Write-Host "Ollama server is running..."
Write-Host "API URL: https://api.dummyjack.com"
Write-Host "Log file: $logFile"
Write-Host "----------------------------------------"

ollama serve 2>&1 | Tee-Object -FilePath $logFile