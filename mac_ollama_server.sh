#!/bin/bash
# Mac/Linux script to start Ollama server

# 檢查並終止佔用 11434 端口的進程
PORT=11434
PID=$(lsof -ti:$PORT 2>/dev/null)
if [ ! -z "$PID" ]; then
    echo -e "\033[37mChecking process on port $PORT (PID: $PID) and stopping it\033[0m"
    kill -9 $PID 2>/dev/null
    sleep 2
    echo -e "\033[37mProcess on port $PORT is stopped\033[0m"
fi

# 檢查並終止 ollama 進程
if pgrep -x "ollama" > /dev/null; then
    echo -e "\033[37mChecking existing ollama process and stopping it\033[0m"
    pkill -9 ollama
    sleep 2
    echo -e "\033[37mOllama is stopped\033[0m"
fi

# 檢查並終止 Ollama app 進程
if pgrep -x "Ollama" > /dev/null; then
    echo -e "\033[37mChecking existing Ollama app process and stopping it\033[0m"
    pkill -9 Ollama
    sleep 2
    echo -e "\033[37mOllama app is stopped\033[0m"
fi

# 設置環境變數
export OLLAMA_HOST=0.0.0.0:11434

# logs/ollama
LOG_DIR="./backend/logs/ollama"
# 如果不存在，創建目錄
if [ ! -d "$LOG_DIR" ]; then
    mkdir -p "$LOG_DIR"
fi

# log
TIMESTAMP_FILE=$(date +"%Y-%m-%d_%H-%M")
LOG_FILE="$LOG_DIR/server_$TIMESTAMP_FILE.log"

# 輸出開始訊息
echo -e "\033[37mOllama server is running...\033[0m"
echo -e "\033[37mOllama_host: $OLLAMA_HOST\033[0m"
echo -e "\033[37mAPI URL: https://api.dummyjack.com\033[0m"
echo -e "\033[37mLog file: $LOG_FILE\033[0m"
echo -e "\033[37m----------------------------------------\033[0m"

ollama serve 2>&1 | tee "$LOG_FILE"

