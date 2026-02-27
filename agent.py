#!/usr/bin/env python3
"""
Coder Agent — interaktivní chat pro správu Coder workspaců přes Claude + MCP.
Použití: .venv/bin/python agent.py
"""

import asyncio
import os
import sys
from pathlib import Path

# Umožní spuštění i uvnitř Claude Code session
os.environ.pop("CLAUDECODE", None)

# ── Imports ────────────────────────────────────────────────────────────────────
try:
    from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions
    from claude_agent_sdk.types import (
        AssistantMessage,
        ResultMessage,
        TextBlock,
        ToolUseBlock,
    )
except ImportError:
    print("Chyba: claude-agent-sdk není nainstalován.")
    print("Spusť: .venv/bin/pip install claude-agent-sdk")
    sys.exit(1)

try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass  # python-dotenv je volitelný

# ── ANSI colors ────────────────────────────────────────────────────────────────
RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
DIM = "\033[2m"
RED = "\033[31m"

# ── Config (z env nebo .env souboru) ──────────────────────────────────────────
CODER_URL = os.environ.get("CODER_URL", "https://46-225-180-131.nip.io")
CODER_SESSION_TOKEN = os.environ.get("CODER_SESSION_TOKEN", "")
CODER_BINARY = os.environ.get("CODER_BINARY", "/usr/local/bin/coder")

if not CODER_SESSION_TOKEN:
    print(f"{RED}Chyba: CODER_SESSION_TOKEN není nastaveno.{RESET}")
    print("Vlož do .env:  CODER_SESSION_TOKEN=<token>")
    print("nebo:          export CODER_SESSION_TOKEN=<token>")
    sys.exit(1)

# ── System Prompt ──────────────────────────────────────────────────────────────
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
driver-builder→padak/driver_builder, driver_builder→padak/driver_builder,
driver_builder_ui→padak/driver_builder, e2b-tereza→padak/e2b-tereza,
get-started→pavel242242/osiris-get-started, get-started-x→pavel242242/osiris-get-started,
linear→padak/pizza-team, mcp-cli→chocholous/mcp-cli, mi-ui2→keboola/sales-asisstant-agent-ui,
mysql→pavel242242/mysql, mysql-p→keboola/setup-cdc-python,
ng_component→pavel242242/ng_component, ng_component_k2→pavel242242/ng_component,
osir→keboola/osiris, padak-e2b→keboola/e2b_demo,
portland-extension→pavel242242/portland-extension, pricing→keboola/pricing-agent,
rohlik_bot→padak/rohlik_bot, salescrew→pavel242242/salescrew,
setup-experiment→chocholous/budget-builder, small-data-sf-2025→dlt-hub/small-data-sf-2025,
STAGEHAND→pavel242242/bohemian-hackathon, surf→e2b-dev/surf,
testing-applicator→chocholous/applicator, testing-applicator-backup→chocholous/applicator,
thevibecoder_lovable→pavel242242/thevibecoders, thevibecoders-revamped→chocholous/thevibecoders-revamped,
ultra-apify→chocholous/apify-browser, vibecoders-react→chocholous/vibecoders-react,
vibe-coding→pavel242242/fans

## Co umíš
- Listovat, vytvářet, startovat, stopovat, mazat workspace
- Spouštět bash příkazy ve workspacích (coder_workspace_bash)
- Číst/zapisovat/editovat soubory ve workspacích
- Vytvářet AI tasky (workspace s AI Prompt → Claude autonomně pracuje)
- Spravovat templates, prohlížet logy, port forwarding

## Workflow — vytvoření AI tasku
1. coder_list_templates → zjisti template a verzi
2. coder_template_version_parameters → zjisti parametry
3. coder_create_workspace s parametry: project, AI Prompt (volitelně branch)
4. coder_get_workspace_agent_logs nebo coder_get_workspace_build_logs → sleduj průběh

## Důležité
- Workspace jméno musí být lowercase-slug (bez mezer a speciálních znaků)
- Při AI tasku vždy nastav AI Prompt parametr
- Odpovídej česky a stručně
- Používej nástroje proaktivně — seznam workspaců zobraz hned bez ptaní
"""


def fmt_tool(name: str, inp: dict) -> str:
    """Formátování tool callu pro terminál."""
    short = name.removeprefix("coder_")
    ws = inp.get("workspace_name") or inp.get("name") or ""
    if name == "coder_workspace_bash":
        cmd = inp.get("command", "")[:80]
        return f"{DIM}  ⚙ {short} [{ws}] $ {cmd}{RESET}"
    if ws:
        return f"{DIM}  ⚙ {short} {ws}{RESET}"
    return f"{DIM}  ⚙ {short}{RESET}"


async def stream_response(client: ClaudeSDKClient) -> None:
    """Stream a zobrazení odpovědi agenta."""
    in_text = False
    turns = 0
    cost = None

    async for msg in client.receive_response():
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock) and block.text:
                    if not in_text:
                        print(f"{BOLD}Claude:{RESET} ", end="", flush=True)
                        in_text = True
                    print(block.text, end="", flush=True)
                elif isinstance(block, ToolUseBlock):
                    if in_text:
                        print()
                        in_text = False
                    print(fmt_tool(block.name, block.input), flush=True)

        elif isinstance(msg, ResultMessage):
            turns = msg.num_turns
            cost = msg.total_cost_usd

    if in_text:
        print()

    cost_str = f" · ${cost:.4f}" if cost else ""
    print(f"\n{DIM}[{turns} turn(s){cost_str}]{RESET}")


async def run_repl() -> None:
    """Hlavní REPL smyčka."""
    options = ClaudeAgentOptions(
        system_prompt=SYSTEM_PROMPT,
        permission_mode="bypassPermissions",
        model="claude-sonnet-4-6",
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
        max_turns=25,
        # Nezavádět globální settings — rychlejší start, žádné cizí MCP servery
        setting_sources=[],
    )

    print(f"\n{BOLD}{CYAN}╔══════════════════════════════════╗{RESET}")
    print(f"{BOLD}{CYAN}║         Coder Agent Chat         ║{RESET}")
    print(f"{BOLD}{CYAN}╚══════════════════════════════════╝{RESET}")
    print(f"{DIM}  {CODER_URL}{RESET}")
    print(f"{DIM}  'exit' nebo Ctrl+C pro ukončení{RESET}\n")

    print(f"{DIM}  Inicializuji...{RESET}", flush=True)
    async with ClaudeSDKClient(options=options) as client:
        print(f"{DIM}  Připojeno. Coder MCP server ready.{RESET}\n", flush=True)
        loop = asyncio.get_event_loop()

        while True:
            try:
                print(f"{BOLD}{GREEN}▶{RESET} ", end="", flush=True)
                user_input = await loop.run_in_executor(None, input)
                user_input = user_input.strip()
            except (EOFError, KeyboardInterrupt):
                print(f"\n{DIM}Ukončuji...{RESET}")
                break

            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "konec", ":q"):
                print(f"{DIM}Ukončuji...{RESET}")
                break

            print()
            try:
                await client.query(user_input)
                await stream_response(client)
            except KeyboardInterrupt:
                try:
                    await client.interrupt()
                except Exception:
                    pass
                print(f"\n{YELLOW}⚡ Přerušeno{RESET}")
            except Exception as e:
                print(f"\n{RED}Chyba: {e}{RESET}")

            print()


def main() -> None:
    try:
        asyncio.run(run_repl())
    except KeyboardInterrupt:
        print(f"\n{DIM}Ukončeno.{RESET}")


if __name__ == "__main__":
    main()
