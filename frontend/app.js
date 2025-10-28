const API_URL = "http://127.0.0.1:8000/generate";
const HISTORY_TURNS = 8;

let apiKey = localStorage.getItem("srs_api_key") || "";
let history = JSON.parse(localStorage.getItem("srs_history") || "[]");
let greetedThisTab = sessionStorage.getItem("srs_greeted_tab") === "1";

const chat = document.getElementById("chat");
const input = document.getElementById("input");
const send = document.getElementById("send");
const clearBtn = document.getElementById("clear");
const keyInput = document.getElementById("key");
const setKeyBtn = document.getElementById("setKey");
const testKeyBtn = document.getElementById("testKey");
const keyStatus = document.getElementById("keyStatus");
const toast = document.getElementById("toast");

function addMessage(content, sender) {
  const msg = document.createElement("div");
  msg.classList.add("msg", sender);
  msg.textContent = content;
  chat.appendChild(msg);
  chat.scrollTop = chat.scrollHeight;
}
function setChatEnabled(enabled) {
  input.disabled = !enabled;
  send.disabled = !enabled;
  clearBtn.disabled = !enabled;
}
function persist() {
  localStorage.setItem("srs_history", JSON.stringify(history));
}
function showToast(title, body, type = "success", ms = 2200) {
  toast.className = type === "success" ? "success" : "error";
  toast.querySelector(".title").textContent = title;
  toast.querySelector(".body").textContent = body;
  toast.style.display = "block";
  clearTimeout(showToast._t);
  showToast._t = setTimeout(() => (toast.style.display = "none"), ms);
}

function buildPromptWithContext(latestUserText) {
  const recent = history.slice(-HISTORY_TURNS);
  const lines = [];
  lines.push("以下是最近的對話歷史（由舊到新）：");
  for (const m of recent) {
    const name = m.role === "user" ? "使用者" : "助理";
    lines.push(`${name}：${m.content}`);
  }
  lines.push("\n請在延續以上脈絡下回覆下一個問題／需求。");
  lines.push("----");
  lines.push("使用者最新輸入：");
  lines.push(latestUserText);
  return lines.join("\n");
}

async function callGenerate(prompt, signal) {
  const res = await fetch(API_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ api_key: apiKey, prompt }),
    signal,
  });
  const data = await res.json().catch(() => ({}));
  return { ok: res.ok, data };
}

async function sendMessage() {
  const text = input.value.trim();
  if (!text) return;

  addMessage(text, "user");
  history.push({ role: "user", content: text });
  persist();

  input.value = "";
  addMessage("⏳ 正在思考中...", "bot");

  try {
    const combinedPrompt = buildPromptWithContext(text);
    const { ok, data } = await callGenerate(combinedPrompt);
    chat.removeChild(chat.lastChild);

    if (ok) {
      addMessage(data.result || "(空回應)", "bot");
      history.push({ role: "assistant", content: data.result || "" });
      persist();
    } else {
      addMessage("❌ 錯誤：" + (data.detail || "未知錯誤"), "bot");
    }
  } catch (err) {
    chat.removeChild(chat.lastChild);
    addMessage("⚠️ 無法連線：" + err, "bot");
  }
}

async function testKey() {
  if (!apiKey) return showToast("測試失敗", "請先設定 Key", "error");

  try {
    const res = await fetch("http://127.0.0.1:8000/test-openai", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ api_key: apiKey }),
    });

    const data = await res.json().catch(() => ({}));
    if (res.ok && data.ok) {
      showToast("測試成功", "OpenAI Key 可正常使用");
    } else {
      showToast("測試失敗", data?.detail || "未知錯誤", "error");
    }
  } catch (e) {
    showToast("測試失敗", String(e), "error");
  }
}

input.addEventListener("keypress", (e) => {
  if (e.key === "Enter") sendMessage();
});
send.addEventListener("click", sendMessage);

clearBtn.addEventListener("click", () => {
  if (!confirm("確定要清除整段對話嗎？")) return;
  history = [];
  persist();
  chat.innerHTML = "";
  greetedThisTab = false;
  sessionStorage.removeItem("srs_greeted_tab");
  addMessage(
    "👋 想開發的系統類型與主要目標是什麼？例如：「線上訂餐系統」、「課程預約平台」、「內部報修系統」。",
    "bot"
  );
});

setKeyBtn.addEventListener("click", () => {
  const k = keyInput.value.trim();
  if (!k || k === "••••••••") {
    return showToast("設定失敗", "請輸入有效的 API Key", "error");
  }
  const firstTime = !apiKey;
  apiKey = k;
  localStorage.setItem("srs_api_key", apiKey);
  showToast("設定完成", firstTime ? "OpenAI Key 已設定" : "OpenAI Key 已更新");
  setChatEnabled(true);
});

testKeyBtn.addEventListener("click", testKey);

// 初始化：自動填入已儲存的 key，並在無歷史時顯示開場訊息
(function init() {
  if (apiKey) {
    keyInput.value = apiKey;
    setChatEnabled(true);
  } else {
    setChatEnabled(false);
  }
  for (const m of history.slice(-HISTORY_TURNS)) {
    addMessage(m.content, m.role === "user" ? "user" : "bot");
  }

  if (history.length === 0) {
    addMessage(
      "👋 想開發的系統類型與主要目標是什麼？例如：「線上訂餐系統」、「課程預約平台」、「內部報修系統」。",
      "bot"
    );
  }
})();
