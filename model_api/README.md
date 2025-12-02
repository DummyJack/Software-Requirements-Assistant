# Model API

## 環境設定

Step 1: 虛擬環境
```bash
# 創建
python -m venv model_venv

# 啟動
.\model_venv\Scripts\Activate.ps1
```

Step 2: 安裝套件
```bash
pip install -r requirements.txt
```

## Run Server
```bash
python main.py
```

```bash
uvicorn main:app --host 127.0.0.1 --port 6000
```

## 專案架構

```
model_api/
├── main.py              # 主程式入口
├── routes/              
│   ├── __init__.py
│   └── model.py         # 模型路由
├── swagger.yml          # API 文檔
├── logs
│   └── api.log          # API 日誌
├── requirements.txt     # 套件
├── .gitignore          
└── model_venv/          # 虛擬環境
```

## 測試

```bash
.\test_api.ps1
```

## API Doc

Step 1: 安裝

```bash
npm install -g redoc-cli
```

Step 2: 產生 html (swagger.yml --> apiDoc.html)

```
redoc-cli build -o apiDoc.html swagger.yml
```

## TODO
<!-- - [ ] or - [X] -->
- [ ] 是否加上 API key