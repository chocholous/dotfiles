# Troubleshooting Guide

Řešení častých problémů při práci s 1Password .env management.

## Instalace a Setup

### ❌ "op: command not found"

**Problém:** 1Password CLI není nainstalován nebo není v PATH.

**Řešení:**

**macOS:**
```bash
brew install 1password-cli
```

**Linux (Debian/Ubuntu):**
```bash
curl -sS https://downloads.1password.com/linux/debian/amd64/stable/1password-cli-latest-amd64.deb -o op.deb
sudo dpkg -i op.deb
```

**Linux (Red Hat/Fedora):**
```bash
curl -sS https://downloads.1password.com/linux/rpm/stable/x86_64/1password-cli-latest.x86_64.rpm -o op.rpm
sudo rpm -i op.rpm
```

**Windows:**
```powershell
winget install 1Password.CLI
```

**Verifikace:**
```bash
which op
op --version
```

### ❌ "You are not currently signed in"

**Problém:** Nejsi přihlášený k 1Password.

**Řešení:**

```bash
# Přihlášení
op signin

# Nebo s eval (pro nastavení session)
eval $(op signin)

# Verifikace
op whoami
```

**Tip:** Pro automatické přihlášení při otevření terminálu, přidej do `~/.zshrc` nebo `~/.bashrc`:
```bash
# Auto sign-in to 1Password
if command -v op &> /dev/null; then
  if ! op whoami &> /dev/null; then
    eval $(op signin)
  fi
fi
```

### ❌ "account not found"

**Problém:** Účet není nakonfigurovaný v 1Password CLI.

**Řešení:**

```bash
# Seznam účtů
op account list

# Přidání nového účtu
op account add --address my.1password.com --email user@example.com
```

## Práce s Items a Vaults

### ❌ "[ERROR] 2024/01/15 item \"MyProject\" isn't in vault \"Dev\""

**Problém:** Item neexistuje nebo je ve špatném vaultu.

**Řešení:**

```bash
# Seznam všech vaults
op vault list

# Seznam items v konkrétním vaultu
op item list --vault Dev

# Vytvoření nového item
op item create --category=password --title=MyProject --vault=Dev \
  db_password[password]=secret123 \
  api_key[password]=key456
```

### ❌ "vault \"VaultName\" not found"

**Problém:** Vault neexistuje nebo nemáš přístup.

**Řešení:**

```bash
# Seznam vaults, ke kterým máš přístup
op vault list

# Vytvoření nového vault
op vault create VaultName

# Nebo požádej admina o přístup k existujícímu vaultu
```

### ❌ "you do not have permission to perform that action"

**Problém:** Nemáš dostatečná oprávnění.

**Řešení:**

1. Kontaktuj admina 1Password účtu
2. Požádej o přístup k potřebnému vaultu
3. Ujisti se, že máš read/write permissions

## Práce s Templates

### ❌ "invalid secret reference"

**Problém:** Syntaxe `op://` odkazu je nesprávná.

**Správná syntaxe:**
```bash
# Formát: op://vault/item/field
op://Dev/MyProject/db_password

# ❌ Chybně:
op://Dev/MyProject/DB_PASSWORD  # Case-sensitive field name!
op://Dev MyProject/db_password  # Missing slash
op:/Dev/MyProject/db_password   # Missing slash
```

**Debugging:**
```bash
# Otestuj reference manuálně
op read "op://Dev/MyProject/db_password"

# Pokud nefunguje, zkontroluj field name:
op item get MyProject --vault Dev --fields label=db_password
```

### ❌ "Template obsahuje hodnoty místo op:// odkazů"

**Problém:** `.env.tpl` byl vytvořen nesprávně nebo jsou secrets přímo v šabloně.

**Řešení:**

```bash
# Znovu vygeneruj template
python3 scripts/generate_env_template.py .env Dev MyProject --output .env.tpl

# Zkontroluj output
cat .env.tpl | grep "op://"

# Mělo by zobrazit:
# DB_PASSWORD="op://Dev/MyProject/db_password"
```

### ❌ "`op inject` nefunguje - generuje prázdné hodnoty"

**Problém:** Field v 1Password má jiný název než v template.

**Debugging:**

```bash
# 1. Zkontroluj, jaké fieldy existují v item
op item get MyProject --vault Dev --format json | jq '.fields'

# 2. Porovnej s tím, co je v .env.tpl
grep "op://" .env.tpl

# 3. Ujisti se, že field names matchují (case-insensitive usually)
```

**Tip:** 1Password automaticky normalizuje názvy. Například:
- `DB_PASSWORD` v .env → `db_password` field v 1Password
- `API_KEY` v .env → `api_key` field v 1Password

## Migrace a Skripty

### ❌ "Permission denied" při spouštění skriptů

**Problém:** Skripty nejsou spustitelné.

**Řešení:**

```bash
chmod +x scripts/*.py

# Nebo spouštěj přes python3
python3 scripts/validate_op_cli.py
```

### ❌ "No secrets detected in .env file"

**Problém:** Script nedetekoval žádné secrets.

**Vysvětlení:**

Scripts hledají klíče obsahující:
- `PASSWORD`
- `SECRET`
- `KEY`
- `TOKEN`
- `CREDENTIAL`
- `PRIVATE`
- `AUTH`

**Řešení:**

Pokud máš secret, který nezahrnuje tato keywords:
```bash
# Manuálně přidej do 1Password
op item edit MyProject --vault Dev \
  custom_secret[password]=value

# Pak manuálně uprav .env.tpl
echo 'CUSTOM_SECRET="op://Dev/MyProject/custom_secret"' >> .env.tpl
```

### ❌ "Backup selhal - file already exists"

**Problém:** `.env.backup` už existuje.

**Řešení:**

```bash
# Zkontroluj existující backup
cat .env.backup

# Pokud je starý, smaž ho
rm .env.backup

# Spusť migraci znovu
python3 scripts/migrate_env_to_1password.py .env Dev MyProject --backup
```

## Práce s Team

### ❌ "Kolega nemůže vygenerovat .env z .env.tpl"

**Checklist:**

1. **Je 1Password CLI nainstalován?**
   ```bash
   op --version
   ```

2. **Je přihlášený?**
   ```bash
   op whoami
   ```

3. **Má přístup k vaultu?**
   ```bash
   op vault get Dev
   ```

4. **Má přístup k item?**
   ```bash
   op item get MyProject --vault Dev
   ```

5. **Je .env.tpl správná?**
   ```bash
   cat .env.tpl | grep "op://"
   ```

### ❌ "Jak rotovat secret pro celý tým?"

**Postup:**

```bash
# 1. Update hodnotu v 1Password (admin/lead)
op item edit MyProject --vault Dev \
  db_password[password]=new-password

# 2. Všichni ostatní jen regenerují .env
op inject -i .env.tpl -o .env

# 3. Nebo používají op run (žádná akce nutná)
op run --env-file=".env.tpl" -- npm start
```

**Není nutné:**
- ❌ Posílat nový .env přes Slack
- ❌ Commitovat změny do gitu
- ❌ Restartovat CI/CD

Všichni automaticky vidí novou hodnotu v 1Password!

## CI/CD Problémy

### ❌ "GitHub Actions: op command not found"

**Řešení:**

Použij oficiální 1Password GitHub Action:

```yaml
- uses: 1password/load-secrets-action@v1
  with:
    export-env: true
  env:
    OP_SERVICE_ACCOUNT_TOKEN: ${{ secrets.OP_SERVICE_ACCOUNT_TOKEN }}
```

### ❌ "Service Account token doesn't work"

**Checklist:**

1. **Je token správně nastavený jako CI secret?**
2. **Má Service Account přístup k vaultu?**
   - Jdi do 1Password → Settings → Service Accounts
   - Zkontroluj permissions

3. **Je vault name správný v .env.tpl?**
   - Case-sensitive!

## FAQ

### Jak zjistím, které secrets jsou v 1Password item?

```bash
op item get MyProject --vault Dev --format json | jq '.fields[] | {label: .label, type: .type}'
```

### Jak přidám nový secret do existujícího item?

```bash
op item edit MyProject --vault Dev \
  new_api_key[password]=abc123
```

Pak updatuj .env.tpl:
```bash
echo 'NEW_API_KEY="op://Dev/MyProject/new_api_key"' >> .env.tpl
```

### Jak smažu secret z item?

```bash
# 1Password CLI nepodporuje delete field directly
# Musíš použít web UI nebo desktop app

# Alternativa: Přejmenuj field na "deprecated_*"
op item edit MyProject --vault Dev \
  deprecated_old_key[password]=unused
```

### Můžu mít různé .env pro development/staging/production?

Ano! Vytvoř separátní templates:

```bash
# Development
.env.dev.tpl  → op://ProjectName-Dev/App/...

# Staging
.env.staging.tpl → op://ProjectName-Staging/App/...

# Production
.env.prod.tpl → op://ProjectName-Prod/App/...
```

Pak generuj podle prostředí:
```bash
op inject -i .env.dev.tpl -o .env
```

### Jak auditovat přístup k secrets?

1Password Team/Business plány mají Activity Log:

1. Jdi do 1Password web app
2. **Activity** → **All Activity**
3. Filtruj podle vault/item

Uvidíš:
- Kdo přistupoval k secrets
- Kdy
- Z jakého zařízení

## Další pomoc

- [1Password CLI Documentation](https://developer.1password.com/docs/cli/)
- [1Password Support](https://support.1password.com/)
- [Community Forum](https://1password.community/)
