#!/usr/bin/env python3
"""
Coder Agent Web Chat
Spuštění: .venv/bin/python web.py
Pak otevři http://localhost:8080
"""

import asyncio
import json
import os
import sys
from pathlib import Path

os.environ.pop("CLAUDECODE", None)

try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import uvicorn

from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions
from claude_agent_sdk.types import (
    AssistantMessage,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
)

CODER_URL = os.environ.get("CODER_URL", "https://46-225-180-131.nip.io")
CODER_SESSION_TOKEN = os.environ.get("CODER_SESSION_TOKEN", "")
CODER_BINARY = os.environ.get("CODER_BINARY", "/usr/local/bin/coder")

if not CODER_SESSION_TOKEN:
    print("CHYBA: CODER_SESSION_TOKEN není nastaveno.")
    sys.exit(1)

SYSTEM_PROMPT = f"""Jsi Coder workspace management assistant s přístupem na Coder instanci přes MCP.

## Setup
- URL: {CODER_URL}
- Server: Hetzner VPS, Docker Compose (Coder + PostgreSQL + Caddy)
- Template: dev-workspace — Docker kontejnery s Claude Code, Git, Node.js, Python 3.13

## Dostupné projekty (projekt → GitHub repo)
dotfiles→chocholous/dotfiles, agentickeboola_web→pavel242242/agentic-bridge-core,
applicator→chocholous/applicator, bg→pavel242242/bg, compare→chocholous/budget-builder,
dataapps→padak/e2b-dataapps-demo, datagen→pavel242242/datagen,
datatalk-events→chocholous/datatalk-events, db-mcp→pavel242242/sql-databases-mcp,
driver-builder→padak/driver_builder, e2b-tereza→padak/e2b-tereza,
get-started→pavel242242/osiris-get-started, linear→padak/pizza-team,
mcp-cli→chocholous/mcp-cli, mi-ui2→keboola/sales-asisstant-agent-ui,
mysql→pavel242242/mysql, ng_component→pavel242242/ng_component,
osir→keboola/osiris, padak-e2b→keboola/e2b_demo,
portland-extension→pavel242242/portland-extension, pricing→keboola/pricing-agent,
rohlik_bot→padak/rohlik_bot, salescrew→pavel242242/salescrew,
STAGEHAND→pavel242242/bohemian-hackathon, surf→e2b-dev/surf,
testing-applicator→chocholous/applicator, thevibecoder_lovable→pavel242242/thevibecoders,
thevibecoders-revamped→chocholous/thevibecoders-revamped,
ultra-apify→chocholous/apify-browser, vibecoders-react→chocholous/vibecoders-react,
vibe-coding→pavel242242/fans

## Co umíš
- Listovat, vytvářet, startovat, stopovat, mazat workspace
- Spouštět bash příkazy ve workspacích (coder_workspace_bash)
- Číst/zapisovat/editovat soubory ve workspacích
- Vytvářet AI tasky (workspace s AI Prompt → Claude autonomně pracuje)
- Spravovat templates, prohlížet logy

## Workflow — vytvoření AI tasku
1. coder_list_templates → zjisti template
2. coder_template_version_parameters → zjisti parametry
3. coder_create_workspace s parametry: project, AI Prompt
4. coder_get_workspace_agent_logs → sleduj průběh

Odpovídej česky a stručně. Používej nástroje proaktivně.
"""


def make_options() -> ClaudeAgentOptions:
    return ClaudeAgentOptions(
        system_prompt=SYSTEM_PROMPT,
        max_turns=25,
        mcp_servers={
            "coder": {
                "command": CODER_BINARY,
                "args": ["exp", "mcp", "server"],
                "env": {
                    "CODER_URL": CODER_URL,
                    "CODER_SESSION_TOKEN": CODER_SESSION_TOKEN,
                    "HOME": os.environ.get("HOME", "/root"),
                    "PATH": "/usr/local/bin:/usr/bin:/bin:/usr/local/sbin",
                },
            }
        },
        allowed_tools=["mcp__coder__*"],
        permission_mode="bypassPermissions",
        setting_sources=[],
    )


HTML = (
    """<!DOCTYPE html>
<html lang="cs">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Coder Agent</title>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  :root {
    --bg: #0d1117;
    --surface: #161b22;
    --border: #30363d;
    --text: #e6edf3;
    --text-dim: #7d8590;
    --accent: #58a6ff;
    --user-bg: #1f6feb;
    --tool-bg: #21262d;
    --tool-text: #79c0ff;
    --success: #3fb950;
  }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
    background: var(--bg);
    color: var(--text);
    height: 100vh;
    display: flex;
    flex-direction: column;
  }
  header {
    padding: 14px 20px;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    gap: 10px;
    background: var(--surface);
  }
  header .dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #ff453a;
  }
  header .dot.green { background: var(--success); }
  header h1 { font-size: 15px; font-weight: 600; }
  header .url { font-size: 12px; color: var(--text-dim); margin-left: auto; }
  #chat {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
  .msg {
    max-width: 80%;
    animation: fadeIn 0.15s ease;
  }
  @keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } }
  .msg.user { align-self: flex-end; }
  .msg.assistant { align-self: flex-start; }
  .msg.user .bubble {
    background: var(--user-bg);
    border-radius: 18px 18px 4px 18px;
    padding: 10px 16px;
    font-size: 14px;
  }
  .msg.assistant .bubble {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 4px 18px 18px 18px;
    padding: 12px 16px;
    font-size: 14px;
    line-height: 1.6;
  }
  .msg.assistant .bubble h1,
  .msg.assistant .bubble h2,
  .msg.assistant .bubble h3 { margin: 8px 0 4px; font-size: 1em; }
  .msg.assistant .bubble p { margin: 4px 0; }
  .msg.assistant .bubble code {
    background: var(--bg);
    border-radius: 4px;
    padding: 1px 5px;
    font-family: "SF Mono", "Fira Code", monospace;
    font-size: 12px;
    color: var(--tool-text);
  }
  .msg.assistant .bubble pre {
    background: var(--bg);
    border-radius: 6px;
    padding: 10px;
    overflow-x: auto;
    margin: 6px 0;
  }
  .msg.assistant .bubble pre code {
    background: none;
    padding: 0;
    color: var(--text);
  }
  .msg.assistant .bubble table {
    border-collapse: collapse;
    width: 100%;
    margin: 6px 0;
    font-size: 13px;
  }
  .msg.assistant .bubble th,
  .msg.assistant .bubble td {
    border: 1px solid var(--border);
    padding: 5px 10px;
    text-align: left;
  }
  .msg.assistant .bubble th { background: var(--bg); }
  .tool-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: var(--tool-bg);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 3px 8px;
    font-size: 11px;
    color: var(--tool-text);
    font-family: "SF Mono", monospace;
    margin: 2px;
  }
  .tool-badge::before { content: "⚙"; font-size: 10px; }
  .tools-row { margin-bottom: 6px; }
  .meta { font-size: 11px; color: var(--text-dim); margin-top: 4px; padding-left: 2px; }
  .cursor { display: inline-block; width: 2px; height: 14px; background: var(--accent); animation: blink 1s infinite; vertical-align: middle; }
  @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }
  #status {
    padding: 6px 20px;
    font-size: 12px;
    color: var(--text-dim);
    background: var(--surface);
    border-top: 1px solid var(--border);
    min-height: 24px;
  }
  #input-row {
    display: flex;
    gap: 10px;
    padding: 14px 20px;
    background: var(--surface);
    border-top: 1px solid var(--border);
  }
  #input {
    flex: 1;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 10px;
    color: var(--text);
    font-size: 14px;
    padding: 10px 14px;
    outline: none;
    resize: none;
    font-family: inherit;
    line-height: 1.5;
    max-height: 120px;
  }
  #input:focus { border-color: var(--accent); }
  #send {
    background: var(--accent);
    border: none;
    border-radius: 10px;
    color: #000;
    font-weight: 600;
    font-size: 14px;
    padding: 10px 18px;
    cursor: pointer;
    align-self: flex-end;
    transition: opacity 0.15s;
  }
  #send:disabled { opacity: 0.4; cursor: not-allowed; }
  #send:hover:not(:disabled) { opacity: 0.85; }
  .welcome {
    text-align: center;
    color: var(--text-dim);
    font-size: 13px;
    padding: 40px 20px;
  }
  .welcome strong { color: var(--text); display: block; font-size: 16px; margin-bottom: 8px; }
</style>
</head>
<body>
<header>
  <div class="dot" id="status-dot"></div>
  <h1>Coder Agent</h1>
  <span class="url">"""
    + CODER_URL
    + """</span>
</header>
<div id="chat">
  <div class="welcome">
    <strong>Coder Agent Chat</strong>
    Connecting to Coder MCP server…
  </div>
</div>
<div id="status">Inicializuji...</div>
<div id="input-row">
  <textarea id="input" placeholder="Napiš dotaz... (Enter = odeslat, Shift+Enter = nový řádek)" rows="1" disabled></textarea>
  <button id="send" disabled>Odeslat</button>
</div>

<script>
const chat = document.getElementById('chat');
const input = document.getElementById('input');
const sendBtn = document.getElementById('send');
const statusEl = document.getElementById('status');
const statusDot = document.getElementById('status-dot');

let ws = null;
let currentBubble = null;
let currentTools = [];
let currentText = '';
let isStreaming = false;

function setStatus(msg, ready) {
  statusEl.textContent = msg;
  statusDot.className = 'dot' + (ready ? ' green' : '');
  input.disabled = !ready;
  sendBtn.disabled = !ready;
}

function scrollBottom() {
  chat.scrollTop = chat.scrollHeight;
}

function addUserMsg(text) {
  const msg = document.createElement('div');
  msg.className = 'msg user';
  msg.innerHTML = '<div class="bubble">' + escHtml(text) + '</div>';
  chat.appendChild(msg);
  scrollBottom();
}

function escHtml(s) {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

function startAssistantMsg() {
  currentBubble = null;
  currentTools = [];
  currentText = '';
  isStreaming = true;

  const msg = document.createElement('div');
  msg.className = 'msg assistant';
  msg.id = 'streaming';
  msg.innerHTML = '<div class="tools-row" id="tools-row"></div><div class="bubble" id="stream-bubble"><span class="cursor"></span></div>';
  chat.appendChild(msg);
  currentBubble = document.getElementById('stream-bubble');
  scrollBottom();
}

function appendText(text) {
  currentText += text;
  currentBubble.innerHTML = marked.parse(currentText) + '<span class="cursor"></span>';
  scrollBottom();
}

function addTool(name) {
  currentTools.push(name);
  const row = document.getElementById('tools-row');
  row.innerHTML = currentTools.map(t => `<span class="tool-badge">${t}</span>`).join('');
  scrollBottom();
}

function finishMsg(cost, turns) {
  if (currentBubble) {
    currentBubble.innerHTML = marked.parse(currentText || '…');
    const meta = document.createElement('div');
    meta.className = 'meta';
    meta.textContent = `${turns} turn${turns !== 1 ? 's' : ''} · $${cost.toFixed(4)}`;
    document.getElementById('streaming').appendChild(meta);
    document.getElementById('streaming').removeAttribute('id');
  }
  isStreaming = false;
  setStatus('Připraven', true);
  scrollBottom();
}

function connect() {
  const proto = location.protocol === 'https:' ? 'wss' : 'ws';
  ws = new WebSocket(`${proto}://${location.host}/ws`);

  ws.onopen = () => setStatus('Inicializuji Coder MCP…', false);

  ws.onmessage = (e) => {
    const msg = JSON.parse(e.data);
    if (msg.type === 'ready') {
      chat.innerHTML = '';
      setStatus('Připraven', true);
    } else if (msg.type === 'text') {
      if (!isStreaming) startAssistantMsg();
      appendText(msg.content);
    } else if (msg.type === 'tool') {
      if (!isStreaming) startAssistantMsg();
      addTool(msg.name);
    } else if (msg.type === 'done') {
      finishMsg(msg.cost || 0, msg.turns || 1);
    } else if (msg.type === 'error') {
      if (currentBubble) currentBubble.innerHTML = '<em style="color:#f85149">Chyba: ' + escHtml(msg.message) + '</em>';
      isStreaming = false;
      setStatus('Chyba', false);
    }
  };

  ws.onclose = () => {
    setStatus('Odpojeno — obnovuji…', false);
    setTimeout(connect, 2000);
  };

  ws.onerror = () => ws.close();
}

function send() {
  const text = input.value.trim();
  if (!text || isStreaming) return;
  addUserMsg(text);
  input.value = '';
  input.style.height = 'auto';
  setStatus('Claude přemýšlí…', false);
  ws.send(JSON.stringify({ type: 'message', text }));
}

input.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    send();
  }
});
input.addEventListener('input', () => {
  input.style.height = 'auto';
  input.style.height = Math.min(input.scrollHeight, 120) + 'px';
});
sendBtn.addEventListener('click', send);

connect();
</script>
</body>
</html>
"""
)


app = FastAPI(title="Coder Agent")


@app.get("/")
async def index():
    return HTMLResponse(HTML)


@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    await websocket.accept()
    options = make_options()
    try:
        async with ClaudeSDKClient(options=options) as client:
            await websocket.send_json({"type": "ready"})
            while True:
                data = await websocket.receive_json()
                if data.get("type") != "message":
                    continue
                text = data.get("text", "").strip()
                if not text:
                    continue

                await client.query(text)

                async for msg in client.receive_response():
                    if isinstance(msg, AssistantMessage):
                        for block in msg.content:
                            if isinstance(block, TextBlock) and block.text:
                                await websocket.send_json(
                                    {"type": "text", "content": block.text}
                                )
                            elif isinstance(block, ToolUseBlock):
                                await websocket.send_json(
                                    {
                                        "type": "tool",
                                        "name": block.name.removeprefix("coder_"),
                                    }
                                )
                    elif isinstance(msg, ResultMessage):
                        await websocket.send_json(
                            {
                                "type": "done",
                                "cost": msg.total_cost_usd or 0,
                                "turns": msg.num_turns,
                            }
                        )
    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    print(f"Coder Agent Web Chat → http://localhost:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")
