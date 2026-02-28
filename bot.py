#!/usr/bin/env python3
"""
Coder Agent Telegram Bot
Spuštění: .venv/bin/python bot.py
Prereq:   TELEGRAM_BOT_TOKEN v .env (získáš od @BotFather na Telegramu)
"""

import asyncio
import os
import sys
from pathlib import Path

os.environ.pop("CLAUDECODE", None)

try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ChatAction, ParseMode

from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions
from claude_agent_sdk.types import (
    AssistantMessage,
    ResultMessage,
    SystemMessage,
    TextBlock,
    ToolUseBlock,
)

# ── Config ─────────────────────────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CODER_URL = os.environ.get("CODER_URL", "https://46-225-180-131.nip.io")
CODER_SESSION_TOKEN = os.environ.get("CODER_SESSION_TOKEN", "")
CODER_BINARY = os.environ.get("CODER_BINARY", "/usr/local/bin/coder")

if not TELEGRAM_BOT_TOKEN:
    print("CHYBA: TELEGRAM_BOT_TOKEN není nastaveno.")
    print("1. Otevři Telegram, najdi @BotFather")
    print("2. Pošli /newbot a postupuj podle instrukcí")
    print("3. Token vlož do .env: TELEGRAM_BOT_TOKEN=123456:ABC...")
    sys.exit(1)

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

Odpovídej česky a stručně. Markdown formátování pro Telegram (tučné **text**, kód `code`).
Pokud odpověď bude delší, rozděl na více zpráv (max 4096 znaků každá).
"""

# ── Session management ──────────────────────────────────────────────────────────
# chat_id → session_id (pro obnovení konverzace bez udržování procesu)
sessions: dict[int, str] = {}


def make_options(resume_id: str | None = None) -> ClaudeAgentOptions:
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
        resume=resume_id,
    )


def truncate(text: str, limit: int = 4000) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "…"


def split_message(text: str, limit: int = 4000) -> list[str]:
    """Rozdělí dlouhý text na bloky max. limit znaků."""
    if len(text) <= limit:
        return [text]
    parts = []
    while text:
        if len(text) <= limit:
            parts.append(text)
            break
        # Hledej vhodné místo pro rozdělení (odstavec, řádek)
        cut = text.rfind("\n\n", 0, limit)
        if cut == -1:
            cut = text.rfind("\n", 0, limit)
        if cut == -1:
            cut = limit
        parts.append(text[:cut])
        text = text[cut:].lstrip("\n")
    return parts


# ── Bot setup ───────────────────────────────────────────────────────────────────
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: Message):
    chat_id = message.chat.id
    sessions.pop(chat_id, None)
    await message.reply(
        "👋 *Coder Agent* je připraven\\!\n\n"
        "Piš přímo — ptej se na workspace, vytváření úloh, logy atd\\.\n"
        "Příkazy: /reset \\(nová konverzace\\) /help",
        parse_mode=ParseMode.MARKDOWN_V2,
    )


@dp.message(Command("reset"))
async def cmd_reset(message: Message):
    sessions.pop(message.chat.id, None)
    await message.reply("✅ Konverzace resetována. Začni psát!")


@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.reply(
        "*Coder Agent* — správa Coder workspaců\n\n"
        "*Co umím:*\n"
        "• Listovat a spravovat workspacy\n"
        "• Spouštět bash příkazy ve workspace\n"
        "• Vytvářet AI tasky (Claude agent pracuje autonomně)\n"
        "• Číst a editovat soubory ve workspaci\n"
        "• Prohlížet logy a stav build procesu\n\n"
        "*Příkazy:*\n"
        "/start nebo /reset — nová konverzace\n"
        "/help — tato nápověda\n\n"
        f"*Server:* `{CODER_URL}`",
        parse_mode=ParseMode.MARKDOWN,
    )


@dp.message(F.text)
async def handle_message(message: Message):
    chat_id = message.chat.id
    user_text = message.text

    # Typing indicator
    await bot.send_chat_action(chat_id, ChatAction.TYPING)

    # Status message
    status_msg = await message.reply("⏳ Pracuji…")

    resume_id = sessions.get(chat_id)
    options = make_options(resume_id)

    full_text = ""
    tools_used: list[str] = []
    new_session_id: str | None = None

    try:
        async with ClaudeSDKClient(options=options) as client:
            await client.query(user_text)

            async for msg in client.receive_response():
                if isinstance(msg, SystemMessage):
                    # Zachyť session_id z init zprávy
                    if hasattr(msg, "data") and isinstance(msg.data, dict):
                        new_session_id = msg.data.get("session_id")
                    elif hasattr(msg, "session_id"):
                        new_session_id = msg.session_id

                elif isinstance(msg, AssistantMessage):
                    for block in msg.content:
                        if isinstance(block, TextBlock) and block.text:
                            full_text += block.text
                            # Průběžná aktualizace (každých ~200 znaků)
                            if len(full_text) % 200 < 20:
                                preview = truncate(full_text)
                                if tools_used:
                                    preview = (
                                        "⚙ `"
                                        + "` `".join(tools_used)
                                        + "`\n\n"
                                        + preview
                                    )
                                try:
                                    await status_msg.edit_text(
                                        preview, parse_mode=ParseMode.MARKDOWN
                                    )
                                except Exception:
                                    pass

                        elif isinstance(block, ToolUseBlock):
                            tool_short = block.name.removeprefix("coder_")
                            tools_used.append(tool_short)
                            preview = "⚙ `" + "` `".join(tools_used) + "`"
                            if full_text:
                                preview += "\n\n" + truncate(full_text)
                            try:
                                await status_msg.edit_text(
                                    preview, parse_mode=ParseMode.MARKDOWN
                                )
                            except Exception:
                                pass

                elif isinstance(msg, ResultMessage):
                    cost = msg.total_cost_usd or 0
                    if new_session_id is None:
                        new_session_id = msg.session_id
                    footer = f"\n\n_{msg.num_turns} turns · ${cost:.4f}_"
                    final = full_text or "_(bez odpovědi)_"

                    # Odešli finální odpověď (rozdělena pokud příliš dlouhá)
                    parts = split_message(final)
                    if tools_used:
                        header = "⚙ `" + "` `".join(tools_used) + "`\n\n"
                        parts[0] = header + parts[0]
                    parts[-1] += footer

                    # První part edituje status_msg, zbytek posílá nové zprávy
                    await status_msg.edit_text(
                        truncate(parts[0]), parse_mode=ParseMode.MARKDOWN
                    )
                    for part in parts[1:]:
                        await message.reply(
                            truncate(part), parse_mode=ParseMode.MARKDOWN
                        )

        # Uložení session_id pro pokračování konverzace
        if new_session_id:
            sessions[chat_id] = new_session_id

    except Exception as e:
        err = str(e)[:200]
        try:
            await status_msg.edit_text(
                f"❌ Chyba: `{err}`", parse_mode=ParseMode.MARKDOWN
            )
        except Exception:
            await message.reply(f"❌ Chyba: {err}")


async def main():
    print(f"Coder Telegram Bot spuštěn (server: {CODER_URL})")
    print("Ctrl+C pro zastavení")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
