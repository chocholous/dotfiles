# Coder na Hetzner — projektový přehled

Tento projekt spravuje self-hosted Coder instanci na Hetzner VPS,
která slouží jako platforma pro AI-driven development (Claude Code agenti).

---

## Infrastruktura

| Položka | Hodnota |
|---------|---------|
| Server | Hetzner cx43, IP `46.225.180.131` |
| Coder URL | `https://46-225-180-131.nip.io` |
| SSH | `ssh -i ~/.ssh/id_hetzner root@46.225.180.131` |
| Stack | Docker Compose (Coder + PostgreSQL 16 + Caddy) v `/opt/coder/` |
| Coder verze | v2.30.2 |

---

## Lokální přístup (Mac)

```bash
export CODER_URL=https://46-225-180-131.nip.io
export CODER_SESSION_TOKEN=<viz MEMORY.md>
/usr/local/bin/coder list
```

> **CODER_SESSION_TOKEN** = pro CLI (templates push, workspace management)
> **CODER_TOKEN** = pro workspace agenty (nepoužívat pro CLI)

Token platí do 2036 (vytvořen přímým INSERT do PostgreSQL).

---

## Šablona `dev-workspace`

**Lokální kopie:** `/tmp/coder-template/main.tf`
**Na serveru:** `/opt/coder-templates/dev-workspace/main.tf`

### Push šablony
```bash
CODER_URL=https://46-225-180-131.nip.io \
CODER_SESSION_TOKEN=e1d8ceca0b-XsSN6OaB0tvdRK4xsoIeUQ \
/usr/local/bin/coder templates push dev-workspace --yes -d /tmp/coder-template
```

### Update workspace
```bash
CODER_URL=... CODER_SESSION_TOKEN=... \
/usr/local/bin/coder update zdaleka --always-prompt=false
```

### Co šablona dělá
- Klonuje GitHub repo projektu do `~/project`
- Kopíruje gitignorované soubory (.env, secrets) z `/opt/projects/<projekt>/` přes rsync
- Instaluje Node.js přes nvm, Gemini CLI, GitHub CLI
- Injektuje Claude OAuth credentials z `/opt/coder-secrets/`
- Spouští agentapi (přes modul claude-code 4.7.5), který řídí Claude agenta
- Aplikuje dotfiles z `https://github.com/chocholous/dotfiles`

### Klíčové moduly
| Modul | Verze | Účel |
|-------|-------|------|
| `registry.coder.com/coder/claude-code/coder` | 4.7.5 | Claude Code + agentapi pro Tasks |
| `registry.coder.com/coder/dotfiles/coder` | 1.3.2 | Dotfiles z GitHubu |

### Parametry workspace
- **Projekt** — výběr z ~150 projektů (hodnota = název adresáře v `/opt/projects/`)
- **Branch** — git branch (prázdné = default)
- **AI Prompt** — prompt pro Claude agenta (vyplní GitHub Action nebo Coder UI)

---

## Claude Code v workspace

### Autentizace
Claude používá OAuth credentials (MAX subscription):
- **Zdroj:** `/opt/coder-secrets/claude-credentials.json` (na Hetzner serveru)
- **Cíl:** `~/.claude/.credentials.json` v home volume workspace
- Kopíruje se při prvním startu workspace (startup_script), pak zůstává v Docker volume

### Task workflow (agentapi)
Modul claude-code v4.7.5 nainstaluje agentapi, který:
1. Přijme prompt (z Coder UI nebo GitHub Action)
2. Spustí `claude --dangerously-skip-permissions -p "<prompt>"`
3. Reportuje stav zpět do Coder UI (Tasks tab)

### Přímý přístup
```bash
coder ssh zdaleka
claude --dangerously-skip-permissions
```

---

## GitHub → Coder Tasks (automatizace)

### Jak to funguje
1. Vytvoříš GitHub Issue
2. Přidáš label **`coder`**
3. GitHub Action (`coder/create-task-action@v0`) vytvoří Coder workspace s promptem z Issue
4. Agentapi spustí Claude agenta
5. Výsledky vidíš v Coder UI (Tasks tab) a jako komentář na Issue

### Nastavení (repo `chocholous/sloneek-agent`)
- Workflow: `.github/workflows/coder-task.yml`
- Secrets: `CODER_URL`, `CODER_TOKEN`
- Label: `coder`

### Přidání do nového repozitáře
```bash
gh secret set CODER_URL --body "https://46-225-180-131.nip.io" --repo chocholous/<repo>
gh secret set CODER_TOKEN --body "<CODER_SESSION_TOKEN>" --repo chocholous/<repo>
gh label create "coder" --color "0075ca" --repo chocholous/<repo>
# Zkopíruj .github/workflows/coder-task.yml z chocholous/sloneek-agent
```

---

## Projekty na serveru

- **`/opt/projects/`** — ~175 projektů, 17 GB (bez node_modules/.venv)
- **`/opt/coder-secrets/`** — credentials (claude OAuth, gh token) — read-only mounted do workspaces
- **`/opt/coder/`** — Docker Compose stack

### Přidání nového projektu
1. Na Macu: `rsync -av --exclude=node_modules --exclude=.venv /local/projekt/ root@46.225.180.131:/opt/projects/projekt/`
2. V šabloně: přidej `option { name = "projekt" value = "projekt" }` do `coder_parameter.project`
3. Push šablony

---

## Dotfiles

- Repo: `https://github.com/chocholous/dotfiles` (public)
- Lokální kopie: `/tmp/dotfiles/`
- `install.sh` musí mít `+x` (`chmod +x install.sh && git commit && git push`)

---

## PostgreSQL

```bash
# Na serveru
docker exec coder-database-1 psql -U coder
# Heslo v /opt/coder/.env (POSTGRES_PASSWORD)
```

---

## Troubleshooting

| Problém | Příčina | Fix |
|---------|---------|-----|
| `CODER_SESSION_TOKEN` nefunguje | Špatný env var nebo token | Zkontroluj v DB: `SELECT * FROM api_keys WHERE hashed_secret = encode(digest('<token>','sha256'),'hex')` |
| Workspace START_ERROR | Chyba v startup_script | `coder ssh <ws>` → `journalctl -u coder-agent` |
| `nvm` nefunguje v subshell | Pipe `\| tail` vytváří subshell | Odstraň pipe, přidej `. "$NVM_DIR/nvm.sh"` po bloku |
| `app_id must be set` | Starý modul claude-code bez task_app_id | Použij verzi 4.7.5, `count.index` pattern |
| Claude nemá credentials | Credentials file nebyl zkopírován | Zkontroluj `/opt/coder-secrets/`, startup_script |
