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

```bash
export CODER_URL=https://46-225-180-131.nip.io
export CODER_SESSION_TOKEN=<viz MEMORY.md>
```

## Vytvoření AI tasku
```bash
coder create <nazev> --template dev-workspace \
  --parameter "project=<projekt>" \
  --parameter "AI Prompt=<prompt>" --yes
```

Detailní infra dokumentace: viz `CLAUDE.md` v kořeni tohoto repozitáře.
