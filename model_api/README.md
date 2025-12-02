# Model API

### Run Server
```bash
python main.py
```

## 專案架構

```
model_api/
├── main.py              # 主程式入口
├── routes/              
│   ├── __init__.py
│   └── model.py         # 模型相關路由
├── swagger.yml          # API 文檔
├── logs
│   └── api.log          # API 日誌
├── requirements.txt     # 套件
├── .gitignore          
└── model_venv/          # 虛擬環境
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