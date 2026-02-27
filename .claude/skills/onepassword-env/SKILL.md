---
name: onepassword-env
description: "Secure .env file management with 1Password CLI. Migrate existing .env files to 1Password, generate templates with op:// references, and inject secrets safely. Use when users need to: (1) Migrate .env files to 1Password, (2) Create .env.tpl templates, (3) Set up 1Password for projects, (4) Handle existing .env files securely, or (5) Implement .env best practices."
---

# 1Password .env Management

## Overview

Securely manage environment variables using 1Password CLI instead of plain .env files. This skill provides tools and workflows for migrating secrets to 1Password, generating templates with secret references, and following security best practices for team collaboration.

## Quick Start

### Prerequisites

**1. 1Password CLI Required**

Verify 1Password CLI is installed and configured:

```bash
python3 scripts/validate_op_cli.py
```

If not installed, follow the installation instructions provided by the script.

**2. GitHub Remote Required**

This skill only supports projects with GitHub remotes. Projects without GitHub remote are out of scope.

Verify your project has a GitHub remote:

```bash
git remote get-url origin
# Should return: https://github.com/user/repo.git or git@github.com:user/repo.git
```

If no remote exists, add one:

```bash
git remote add origin https://github.com/user/repo.git
```

**Why GitHub remote?**
- Ensures consistent naming across team members and CI/CD
- Vault: `gh-projects` (shared across all projects)
- Item names: `{user}__{repo}__{path}` (derived from GitHub URL)
- No manual vault/item naming required

## Workflows

### Workflow 1: Migrate Existing .env Files

**When to use:** You have existing .env files containing secrets that should be moved to 1Password.

**Steps:**

1. **Find all .env files in your project:**
   ```bash
   python3 scripts/find_env_files.py
   ```

2. **Migrate each file to 1Password (auto mode - recommended):**
   ```bash
   python3 scripts/migrate_env_to_1password.py .env --auto --backup
   ```

   The `--auto` flag automatically detects vault and item names from your GitHub remote:
   - Vault: `gh-projects` (shared across all projects)
   - Item: `{user}__{repo}__{path}` (e.g., `testuser__myapp__root`)

   **Alternative - Manual mode:**
   ```bash
   python3 scripts/migrate_env_to_1password.py .env CustomVault CustomItem --backup
   ```

   Arguments:
   - `.env` - Path to your .env file
   - `--auto` - Auto-detect vault/item from GitHub remote (recommended)
   - `--backup` - Creates .env.backup before migration
   - `--dry-run` - Test without making changes

3. **Verify the template was created:**
   ```bash
   cat .env.tpl
   ```

   Should contain `op://` references like:
   ```
   DB_PASSWORD="op://gh-projects/testuser__myapp__root/db_password"
   ```

4. **Test secret injection:**
   ```bash
   op inject -i .env.tpl -o .env.test
   diff .env .env.test  # Should be identical
   ```

5. **Commit template to git:**
   ```bash
   git add .env.tpl .gitignore
   git commit -m "Add environment configuration template"
   ```

**What happens:**
- Secrets are detected and uploaded to 1Password
- Original .env is backed up to .env.backup (if --backup specified)
- .env.tpl template is generated with op:// references
- .gitignore is updated to exclude .env files

### Workflow 2: Create New .env.tpl from Scratch

**When to use:** Starting a new project and want to use 1Password from the beginning.

**Steps:**

1. **Copy example template:**
   ```bash
   cp assets/example.env.tpl .env.tpl
   ```

2. **Customize with your vault and item names:**
   ```
   DB_PASSWORD="op://YourVault/YourItem/db_password"
   API_KEY="op://YourVault/YourItem/api_key"
   ```

3. **Create secrets in 1Password manually:**
   ```bash
   op item create --category=password \
     --title=YourItem \
     --vault=YourVault \
     db_password[password]=secret123 \
     api_key[password]=key456
   ```

4. **Test template:**
   ```bash
   op inject -i .env.tpl -o .env
   ```

5. **Commit template:**
   ```bash
   git add .env.tpl
   git commit -m "Add environment template"
   ```

### Workflow 3: Team Onboarding

**When to use:** A new team member needs access to project secrets.

**Prerequisites:**
- New member has 1Password account
- New member has been granted access to the project vault

**Steps for new team member:**

1. **Install 1Password CLI:**
   ```bash
   # macOS
   brew install 1password-cli

   # See troubleshooting.md for other platforms
   ```

2. **Sign in to 1Password:**
   ```bash
   eval $(op signin)
   ```

3. **Clone repository:**
   ```bash
   git clone <repository-url>
   cd <repository>
   ```

4. **Generate .env from template:**
   ```bash
   op inject -i .env.tpl -o .env
   ```

5. **Verify application runs:**
   ```bash
   npm start  # or your project's start command
   ```

**No manual secret sharing required!** All secrets are pulled from 1Password automatically.

## Advanced Usage

### Dry-run Mode

Test migration without making changes (auto mode):

```bash
python3 scripts/migrate_env_to_1password.py .env --auto --dry-run
```

Or with manual vault/item names:

```bash
python3 scripts/migrate_env_to_1password.py .env CustomVault CustomItem --dry-run
```

Shows what would be done without:
- Creating 1Password items in production vault (templates are still generated locally)

### Multiple .env Files

For projects with multiple .env files (e.g., `.env`, `.env.local`, `.env.production`), migrate each separately:

```bash
# Auto mode detects unique item names based on file suffix
python3 scripts/migrate_env_to_1password.py .env --auto --backup
python3 scripts/migrate_env_to_1password.py .env.production --auto --backup
```

Result:
- `.env` → `gh-projects/testuser__myapp__root`
- `.env.production` → `gh-projects/testuser__myapp__root__production`

### Generate Template Without Migration

Convert .env to .env.tpl without touching 1Password (manual mode only):

```bash
python3 scripts/generate_env_template.py .env CustomVault CustomItem
```

Useful for:
- Previewing template structure
- Creating templates for documentation
- Projects without GitHub remote (not supported by --auto mode)

### Using op run (Recommended for Production)

Instead of generating .env files, run commands with secrets in memory only:

```bash
op run --env-file=".env.tpl" -- npm start
```

**Benefits:**
- Secrets never written to disk
- Automatic rotation when secrets change in 1Password
- More secure than .env files

## Best Practices

See [references/best-practices.md](references/best-practices.md) for comprehensive guidance on:

- **Team Workflow** - How to share secrets across the team
- **CI/CD Integration** - GitHub Actions, GitLab CI setup
- **Git Hygiene** - What to commit, git history audit
- **Security Principles** - op run vs .env files, secret rotation, least privilege

## Troubleshooting

See [references/troubleshooting.md](references/troubleshooting.md) for solutions to common issues:

- Installation problems
- Authentication errors
- Template syntax issues
- CI/CD configuration
- Team access problems

## Resources

### Scripts

- **`scripts/validate_op_cli.py`** - Validate 1Password CLI installation and authentication
  ```bash
  python3 scripts/validate_op_cli.py
  ```

- **`scripts/find_env_files.py`** - Find all .env* files in project directory tree
  ```bash
  python3 scripts/find_env_files.py [directory]
  ```

- **`scripts/git_utils.py`** - GitHub remote detection and automatic naming (used internally)
  - Auto-detects vault: `gh-projects`
  - Auto-generates item: `{user}__{repo}__{path}`
  - Supports submodules and monorepos

- **`scripts/migrate_env_to_1password.py`** - Full migration workflow
  ```bash
  # Auto mode (recommended) - detects vault/item from GitHub remote
  python3 scripts/migrate_env_to_1password.py <env-file> --auto [--backup] [--dry-run]

  # Manual mode - specify vault/item explicitly
  python3 scripts/migrate_env_to_1password.py <env-file> <vault> <item> [--backup] [--dry-run]
  ```

- **`scripts/generate_env_template.py`** - Convert .env to .env.tpl template (manual mode)
  ```bash
  python3 scripts/generate_env_template.py <env-file> <vault> <item> [--output <file>]
  ```

### References

- **`references/best-practices.md`** - Team workflow, CI/CD, security guidance
- **`references/troubleshooting.md`** - Solutions to common problems and FAQ

### Assets

- **`assets/gitignore-template.txt`** - Recommended .gitignore entries for .env files
- **`assets/example.env.tpl`** - Example template showing proper op:// reference format

## Security Considerations

**What gets committed to git:**
- ✅ `.env.tpl` - Template with op:// references (no secrets)
- ✅ `.env.example` - Example values for documentation
- ✅ `.gitignore` - Excluding actual .env files

**What NEVER gets committed:**
- ❌ `.env` - Contains actual secrets
- ❌ `.env.local` - Local overrides with secrets
- ❌ `.env.backup` - Backup of secrets

**Secret detection:**

Scripts automatically identify secrets based on environment variable names containing:
- PASSWORD
- SECRET
- KEY
- TOKEN
- CREDENTIAL
- PRIVATE
- AUTH

Non-secret configuration (like `PORT`, `APP_NAME`, `DEBUG`) remains as plain text in .env.tpl.

## Example End-to-End Flow

```bash
# 1. Developer has existing .env file in a GitHub project
ls -la
# .env (contains secrets)

# 2. Validate 1Password CLI
python3 scripts/validate_op_cli.py
# ✅ 1Password CLI is ready to use!

# 3. Verify GitHub remote (required for --auto mode)
git remote get-url origin
# https://github.com/testuser/myapp.git

# 4. Migrate to 1Password (auto mode)
python3 scripts/migrate_env_to_1password.py .env --auto --backup
# 🔍 Detecting vault and item name from GitHub remote...
# ✅ Auto-detected:
#    Vault: gh-projects
#    Item:  testuser__myapp__root
# 🔐 Creating new item: testuser__myapp__root in vault gh-projects
# ✅ Secrets migrated to 1Password
# 📝 Generated .env.tpl template
# 💾 Backed up original to .env.backup

# 5. Check generated files
ls -la
# .env (original)
# .env.backup (backup)
# .env.tpl (template with op:// references)

# 5. Test template
op inject -i .env.tpl -o .env.test
diff .env .env.test
# Files are identical ✓

# 6. Commit template to git
git add .env.tpl .gitignore
git commit -m "Add environment template with 1Password references"
git push

# 7. Team member clones and generates their .env
git clone <repo>
cd <repo>
op inject -i .env.tpl -o .env
npm start  # Application runs with secrets from 1Password
```
