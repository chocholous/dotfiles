# Best Practices pro 1Password .env Management

Tento dokument pokrývá doporučené postupy pro bezpečnou správu environment variables pomocí 1Password CLI.

## Týmový Workflow

### Základní setup pro tým

1. **Lead vývojář vytvoří 1Password Item:**
   ```bash
   # Vytvořit vault (pokud neexistuje)
   op vault create ProjectSecrets

   # Migrovat .env do 1Password
   python3 scripts/migrate_env_to_1password.py .env ProjectSecrets MyApp --backup
   ```

2. **Sdílení přístupu:**
   - V 1Password aplikaci sdílej vault "ProjectSecrets" s týmem
   - Všichni členové musí mít přístup k tomuto vaultu

3. **Commitování do gitu:**
   ```bash
   # Commit pouze šablonu (ne secrets!)
   git add .env.tpl .gitignore
   git commit -m "Add environment configuration template"
   git push
   ```

4. **Onboarding nových členů:**
   ```bash
   # Nový člen klonuje repo
   git clone <repository>
   cd <repository>

   # Nainstaluje 1Password CLI
   brew install 1password-cli

   # Přihlásí se
   eval $(op signin)

   # Vygeneruje .env z šablony
   op inject -i .env.tpl -o .env

   # Ověří, že aplikace funguje
   npm start
   ```

## CI/CD Integrace

### GitHub Actions

Používej 1Password Service Accounts pro CI/CD:

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Load secrets from 1Password
        uses: 1password/load-secrets-action@v1
        with:
          export-env: true
        env:
          OP_SERVICE_ACCOUNT_TOKEN: ${{ secrets.OP_SERVICE_ACCOUNT_TOKEN }}

      - name: Generate .env
        run: op inject -i .env.tpl -o .env

      - name: Run tests
        run: npm test
```

### GitLab CI

```yaml
# .gitlab-ci.yml
variables:
  OP_SERVICE_ACCOUNT_TOKEN: $OP_SERVICE_ACCOUNT_TOKEN

before_script:
  - curl -sS https://downloads.1password.com/linux/debian/amd64/stable/1password-cli-latest-amd64.deb -o op.deb
  - dpkg -i op.deb
  - op inject -i .env.tpl -o .env

test:
  script:
    - npm test
```

### Vytvoření Service Account

1. V 1Password webové aplikaci: **Settings → Service Accounts**
2. Vytvoř nový Service Account s read-only přístupem k potřebnému vaultu
3. Zkopíruj token a ulož jako CI/CD secret

## Git Hygiene

### Co commitovat

✅ **Commituj:**
- `.env.tpl` - Šablona s `op://` odkazy
- `.env.example` - Příklady hodnot (bez real secrets)
- `.gitignore` - S .env exclusions

❌ **NECOMMITUJ:**
- `.env` - Obsahuje skutečné secrets
- `.env.local` - Lokální overrides
- `.env.backup` - Backup souborů
- Jakékoliv soubory s real secrets

### Audit git history

Zkontroluj, jestli .env nebyl omylem commitnutý:

```bash
# Prohledej celou historii
git log --all --full-history -- .env

# Pokud najdeš commity s .env, odstraň je:
# Varianta 1: BFG Repo-Cleaner (doporučeno)
brew install bfg
bfg --delete-files .env
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Varianta 2: git filter-branch
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all
```

⚠️ **Pozor:** Po odstranění .env z history musí všichni členové re-clone repository!

### Pre-commit Hook

Zabránění náhodnému commitu .env:

```bash
# .git/hooks/pre-commit
#!/bin/bash
if git diff --cached --name-only | grep -E "^\.env$"; then
  echo "❌ Error: Attempting to commit .env file!"
  echo "   This file contains secrets and should not be committed."
  exit 1
fi
```

Nastav jako spustitelný:
```bash
chmod +x .git/hooks/pre-commit
```

## Security Principy

### Proč používat op run místo .env souborů

**Tradiční přístup (.env soubor):**
```bash
# .env je zapsán na disku
node index.js
```

**Problémy:**
- .env soubor je na disku → risk úniku (malware, backup, atd.)
- Můžeš omylem commitnout do gitu
- Difficult rotation - musíš update .env na všech strojích

**1Password přístup (op run):**
```bash
# Secrets jsou jen v RAM, nikdy na disku
op run --env-file=".env.tpl" -- node index.js
```

**Výhody:**
- Secrets nikdy nedorazí na disk jako soubor
- Automatická rotace - update v 1Password, všichni okamžitě vidí
- Audit trail - 1Password loguje přístup k secrets
- Least privilege - granular access control per vault/item

### Secret Rotation

Jak rotovat secrets:

1. **Update v 1Password:**
   ```bash
   # Změň hodnotu v 1Password
   op item edit MyProject --vault ProjectSecrets \
     db_password[password]=new-secret-value
   ```

2. **Všichni okamžitě vidí novou hodnotu:**
   ```bash
   # Regeneruj .env
   op inject -i .env.tpl -o .env

   # Nebo použij op run (doporučeno)
   op run --env-file=".env.tpl" -- npm start
   ```

3. **Žádná synchronizace nutná** - všichni tahají z centrálního 1Password

### Least Privilege Access

Separuj secrets podle prostředí:

```
Vaults:
├── ProjectName-Dev       (development secrets)
├── ProjectName-Staging   (staging secrets)
└── ProjectName-Prod      (production secrets)
```

Pak různé .env.tpl pro každé prostředí:

**.env.dev.tpl:**
```bash
DB_PASSWORD="op://ProjectName-Dev/Database/password"
```

**.env.prod.tpl:**
```bash
DB_PASSWORD="op://ProjectName-Prod/Database/password"
```

Vývojáři mají přístup jen k Dev vaultu, DevOps k Prod vaultu.

## Troubleshooting

Pro řešení častých problémů viz [troubleshooting.md](troubleshooting.md).

## Další zdroje

- [1Password CLI Documentation](https://developer.1password.com/docs/cli/)
- [1Password GitHub Actions](https://github.com/1password/load-secrets-action)
- [Secret References Syntax](https://developer.1password.com/docs/cli/secret-references/)
