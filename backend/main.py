# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from pathlib import Path
from datetime import datetime
import openai as openai_pkg  # 只用來印出版本，方便除錯

app = FastAPI()

# 允許前端連線（例如你的本地 HTML）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 可改成 ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === 讀取外部 system prompt ===
SYSTEM_PROMPT_PATH = Path("system_prompt.txt")
if not SYSTEM_PROMPT_PATH.exists():
    raise FileNotFoundError("❌ 找不到 system_prompt.txt，請確認檔案存在於同目錄下。")

SYSTEM_PROMPT = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")


# === 前端傳入資料格式 ===
class PromptRequest(BaseModel):
    api_key: str
    prompt: str


class TestKeyRequest(BaseModel):
    api_key: str


def generate_with_compat(client: OpenAI, system_prompt: str, user_prompt: str) -> str:
    """
    SDK 相容層：
    - 若支援 Responses API (>=1.42)，走 client.responses.create(...)
    - 否則退回舊的 Chat Completions API
    """
    # 新版 (>=1.42) 會有 responses 介面
    if hasattr(client, "responses"):
        resp = client.responses.create(
            # 你原本用 gpt-4.1；這裡沿用。如果無權限，可改為 "gpt-4o-mini" / "gpt-5-mini"
            model="gpt-4.1",
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        # 新 SDK 最簡單的文字輸出
        txt = getattr(resp, "output_text", None)
        if txt:
            return txt.strip()
        # 退而求其次（不同小版序列化略有差異）
        return resp.output[0].content[0].text.strip()

    # 舊版 (1.0 ~ 1.41) 使用 chat.completions
    comp = client.chat.completions.create(
        # 若 "gpt-4.1" 不可用，改成 "gpt-4o-mini" 或你有權限的模型
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return comp.choices[0].message.content.strip()


@app.post("/generate")
def generate_text(req: PromptRequest):
    client = OpenAI(api_key=req.api_key)
    try:
        # === 顯示輸入 ===
        print("\n" + "=" * 80)
        print(f"🕒 時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("[OpenAI SDK] version:", getattr(openai_pkg, "__version__", "unknown"))
        print("🟢 使用者輸入的 prompt：")
        print(req.prompt)
        print("-" * 80)

        # === 呼叫 OpenAI（相容層）===
        output = generate_with_compat(client, SYSTEM_PROMPT, req.prompt)

        # === 顯示輸出 ===
        print("🟣 模型回應：")
        print(output)
        print("=" * 80 + "\n")

        return {"result": output}

    except Exception as e:
        print("❌ [ERROR]", e)
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/test-openai")
def test_openai(req: TestKeyRequest):
    """
    輕量驗證 OpenAI API Key：
    - 成功：回傳 {"ok": True}
    - 失敗：HTTP 400 with detail
    使用 models.list() 做 metadata 查詢，不會消耗 tokens。
    """
    try:
        client = OpenAI(api_key=req.api_key)
        # 列出模型僅為驗證金鑰有效性（不計費）
        _ = client.models.list()
        return {"ok": True, "message": "OpenAI key is valid."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
