# ALWAYS:
- be aware you're running on Mac OS 26.2
- use gh to operate github
- in python use venv for everything (python3.13)
- use ripgrep instead of grep
- use parallel subagents, when faster and reliable, avoid using them only when it would endanger the code consistency (dependencies between code parts or multiple subagents might need to edit the same file(s))
- Before introducing ANY hardcoded values (magic numbers, URLs, timeouts, defaults, fallbacks), STOP and warn the user. Suggest alternatives (env vars, config files, named constants) and wait for explicit approval.
- Docker runs via OrbStack — always prepend `export PATH="$HOME/.orbstack/bin:$PATH"` before any docker/docker-compose commands, or use full path `~/.orbstack/bin/docker`


# NEVER:
- NEVER assume capabilities of CLI tools libraries and frameworks from memory. ALWAYS run the tool's help/docs command first to verify available flags and output formats before making claims about what's possible. Consult context7 for this purpose. Make sure you use the same version of docs as the one you're using.

# Session review
Po dokončení compaction a otevreni dalsi session
1. Přečti jeji transkript z `~/.claude/projects/<current-project>/` (JSONL soubory, seřazené dle data)
2. Analyzuj: co zpomalovalo, jaké chyby vznikly, co se opakovalo, co chybělo v instrukcích
3. Zapiš návrhy do `~/.claude/CLAUDE-suggestions.md` ve formátu:
   ```
   ## [datum] [projekt]
   ### Navrhovaná změna
   - **Co:** konkrétní pravidlo/instrukce
   - **Proč:** jaký problém to řeší (odkaz na session)
   - **Kam:** user CLAUDE.md / projekt CLAUDE.md / MEMORY.md
   - **Priorita:** HIGH/MEDIUM/LOW
   ```
4. Neaplikuj změny automaticky — pouze navrhni, uživatel rozhodne

# Coder — koordinace AI tasků

## Setup
Binary: `/usr/local/bin/coder` (nebo `coder` pokud je v PATH)
```bash
export CODER_URL=https://46-225-180-131.nip.io
export CODER_SESSION_TOKEN=e1d8ceca0b-XsSN6OaB0tvdRK4xsoIeUQ
```
Template: `dev-workspace` (id: f7ab77d1-f401-4a1f-b90b-5e2e0872dc0d)

## Vytvoření AI tasku (= nový workspace s Claude agentem)
```bash
coder create <nazev> \
  --template dev-workspace \
  --parameter "project=<projekt>" \
  --parameter "AI Prompt=<co má Claude udělat>" \
  --yes
```
Claude v workspace autonomně pracuje a reportuje stav do Tasks tabu v Coder UI.

## Projekty s GitHub remote (42)
agentickeboola_web, applicator, bg, cc-2, cc2-transfer, compare,
compare-second-branch, cursor-auto-rules-agile-workflow, dataapps,
datagen, datatalk-events, db-mcp, dotfiles, driver-builder,
driver_builder, driver_builder_ui, e2b-tereza, get-started,
get-started-x, linear, mcp-cli, mi-ui2, mysql, mysql-p,
ng_component, ng_component_k2, osir, padak-e2b, portland-extension,
pricing, rohlik_bot, salescrew, setup-experiment, small-data-sf-2025,
STAGEHAND, surf, testing-applicator, testing-applicator-backup,
thevibecoder_lovable, thevibecoders-revamped, ultra-apify,
vibecoders-react, vibe-coding

## Správa tasků
```bash
coder list                          # stav workspace
coder logs <workspace> -f           # logy buildu
curl -H "Coder-Session-Token: $CODER_SESSION_TOKEN" $CODER_URL/api/v2/tasks  # Tasks API
```