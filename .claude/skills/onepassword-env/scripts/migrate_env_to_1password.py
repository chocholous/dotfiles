#!/usr/bin/env python3
"""
Migrate .env file to 1Password with full backup and template generation.

This script performs a complete migration of secrets from a .env file to 1Password:
1. Validates 1Password CLI setup
2. Parses .env file and detects secrets
3. Creates or updates 1Password item with secrets
4. Generates .env.tpl template
5. Backs up original .env file (optional)
6. Updates .gitignore

Tool Annotations (MCP Best Practices):
- readOnlyHint: False (creates/modifies 1Password items and local files)
- destructiveHint: False in --dry-run mode, True otherwise (creates items in 1Password)
- idempotentHint: True (safe to run multiple times, updates existing items)
- openWorldHint: True (interacts with 1Password service)

Requirements:
- 1Password CLI (op) must be installed and user signed in
- GitHub remote required (use --auto mode)

Usage:
    # Auto mode (recommended) - detects vault/item from GitHub remote
    python3 migrate_env_to_1password.py <env-file> --auto [options]

    # Manual mode - specify vault and item explicitly
    python3 migrate_env_to_1password.py <env-file> <vault> <item-name> [options]

Arguments:
    env-file: Path to .env file to migrate
    vault: 1Password vault name (required if not --auto)
    item-name: 1Password item name (required if not --auto)

Options:
    --auto: Automatically detect vault/item from GitHub remote
    --backup: Create .env.backup before migration
    --dry-run: Show what would be done without making changes

Examples:
    python3 migrate_env_to_1password.py .env --auto --backup
    python3 migrate_env_to_1password.py .env Dev MyProject --backup
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

# Add scripts directory to Python path for git_utils import
_scripts_dir = Path(__file__).parent
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))

# Import git_utils for automatic GitHub-based naming
try:
    from git_utils import get_1password_names, GitRemoteError as GitUtilsError
except ImportError:
    # Allow script to work without git_utils if manual mode is used
    def get_1password_names(env_path):
        raise ImportError("git_utils module not found. Use manual mode or ensure git_utils.py is in the same directory.")

    class GitUtilsError(Exception):
        pass


# Secret detection keywords
SECRET_KEYWORDS = [
    'PASSWORD', 'SECRET', 'KEY', 'TOKEN',
    'CREDENTIAL', 'PRIVATE', 'AUTH',
]


def is_secret_key(key):
    """Check if environment variable key represents a secret."""
    key_upper = key.upper()
    return any(keyword in key_upper for keyword in SECRET_KEYWORDS)


def normalize_field_name(key):
    """Convert env var key to 1Password field name."""
    return key.lower()


def parse_env_file(env_path):
    """
    Parse .env file and extract variables.

    Args:
        env_path: Path to .env file

    Returns:
        Dict of {key: value} pairs
    """
    variables = {}
    content = env_path.read_text()

    for line in content.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue

        match = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)=(.*)$', stripped)
        if match:
            key = match.group(1)
            value = match.group(2).strip()
            # Remove quotes if present
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]
            variables[key] = value

    return variables


def detect_secrets(variables):
    """
    Separate secrets from non-secrets.

    Args:
        variables: Dict of env variables

    Returns:
        Tuple of (secrets_dict, non_secrets_dict)
    """
    secrets = {}
    non_secrets = {}

    for key, value in variables.items():
        if is_secret_key(key):
            secrets[key] = value
        else:
            non_secrets[key] = value

    return secrets, non_secrets


def validate_op_cli():
    """Validate 1Password CLI is installed and signed in."""
    # Check if op is available
    if not shutil.which("op"):
        print("❌ 1Password CLI not found. Please install it first.")
        return False

    # Check if signed in
    try:
        result = subprocess.run(
            ["op", "whoami"],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except Exception:
        return False


def create_or_update_1password_item(vault, item_name, secrets, dry_run=False):
    """
    Create or update 1Password item with secrets.

    Args:
        vault: Vault name
        item_name: Item name
        secrets: Dict of secret key-value pairs
        dry_run: If True, only print what would be done

    Returns:
        True if successful, False otherwise
    """
    if dry_run:
        print(f"🔐 [DRY-RUN] Would create/update 1Password item: {item_name} in vault {vault}")
        for key in secrets.keys():
            field = normalize_field_name(key)
            print(f"  ├─ {key} → {field}")
        return True

    # Check if item already exists
    item_exists = False
    try:
        result = subprocess.run(
            ["op", "item", "get", item_name, "--vault", vault],
            capture_output=True,
            timeout=10
        )
        item_exists = (result.returncode == 0)
    except Exception:
        pass

    if item_exists:
        print(f"📝 Updating existing item: {item_name}")
        # Update existing item
        for key, value in secrets.items():
            field = normalize_field_name(key)
            try:
                subprocess.run(
                    ["op", "item", "edit", item_name,
                     "--vault", vault,
                     f"{field}[password]={value}"],
                    check=True,
                    capture_output=True,
                    timeout=10
                )
                print(f"  ├─ {key} → Updated in 1Password")
            except subprocess.CalledProcessError as e:
                print(f"  ├─ {key} → ❌ Error: {e}")
                return False
    else:
        print(f"🔐 Creating new item: {item_name} in vault {vault}")
        # Create new item with all secrets
        fields = []
        for key, value in secrets.items():
            field = normalize_field_name(key)
            fields.append(f"{field}[password]={value}")

        try:
            cmd = ["op", "item", "create",
                   "--category", "password",
                   "--title", item_name,
                   "--vault", vault] + fields
            subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                timeout=15
            )
            for key in secrets.keys():
                print(f"  ├─ {key} → Added to 1Password")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error creating item: {e}")
            return False

    return True


def generate_template(env_path, vault, item_name):
    """
    Generate .env.tpl template file.

    Args:
        env_path: Path to original .env file
        vault: Vault name
        item_name: Item name

    Returns:
        Path to generated template
    """
    template_path = env_path.parent / ".env.tpl"

    # Use generate_env_template.py logic inline
    content = env_path.read_text()
    lines = content.splitlines(keepends=True)
    output_lines = []

    for line in lines:
        stripped = line.strip()

        # Empty or comment lines
        if not stripped or stripped.startswith('#'):
            output_lines.append(line)
            continue

        # Variable lines
        match = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)=(.*)$', stripped)
        if match:
            key = match.group(1)
            if is_secret_key(key):
                field = normalize_field_name(key)
                op_ref = f'op://{vault}/{item_name}/{field}'
                output_lines.append(f'{key}="{op_ref}"\n')
            else:
                output_lines.append(line)
        else:
            output_lines.append(line)

    template_path.write_text(''.join(output_lines))
    return template_path


def backup_env_file(env_path, dry_run=False):
    """Create backup of .env file."""
    backup_path = env_path.parent / ".env.backup"

    try:
        shutil.copy2(env_path, backup_path)
        if dry_run:
            print(f"💾 [DRY-RUN] Backed up {env_path} to {backup_path}")
        else:
            print(f"💾 Backed up original to {backup_path}")
        return True
    except Exception as e:
        print(f"❌ Error creating backup: {e}")
        return False


def update_gitignore(env_path, dry_run=False):
    """Update .gitignore to exclude .env files."""
    gitignore_path = env_path.parent / ".gitignore"

    entries_to_add = [
        "# Environment files (secrets)",
        ".env",
        ".env.local",
        ".env.*.local",
        ".env.backup",
        "",
        "# Keep templates (no secrets)",
        "!.env.tpl",
        "!.env.example",
    ]

    # Read existing gitignore or create new
    if gitignore_path.exists():
        content = gitignore_path.read_text()
    else:
        content = ""

    # Check if .env is already in gitignore
    if ".env" in content:
        if dry_run:
            print(f"📋 [DRY-RUN] .gitignore already contains .env entries")
        else:
            print(f"📋 .gitignore already contains .env entries")
        return True

    # Append our entries
    if content and not content.endswith('\n'):
        content += '\n'

    content += '\n'.join(entries_to_add) + '\n'
    gitignore_path.write_text(content)

    if dry_run:
        print(f"📋 [DRY-RUN] Updated {gitignore_path}")
    else:
        print(f"📋 Updated {gitignore_path}")
    return True


def main():
    """Main migration function."""
    parser = argparse.ArgumentParser(
        description='Migrate .env file to 1Password'
    )
    parser.add_argument('env_file', help='Path to .env file')
    parser.add_argument('vault', nargs='?', help='1Password vault name (optional with --auto)')
    parser.add_argument('item_name', nargs='?', help='1Password item name (optional with --auto)')
    parser.add_argument('--auto', action='store_true',
                        help='Automatically detect vault/item from GitHub remote')
    parser.add_argument('--backup', action='store_true',
                        help='Create .env.backup before migration')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be done without making changes')

    args = parser.parse_args()

    # Validate input
    env_path = Path(args.env_file).resolve()  # Convert to absolute path
    if not env_path.exists():
        print(f"❌ Error: File not found: {env_path}")
        sys.exit(1)

    # Determine vault and item_name
    if args.auto:
        # Auto mode: detect from GitHub remote
        print("🔍 Detecting vault and item name from GitHub remote...\n")
        try:
            vault, item_name = get_1password_names(env_path)
            print(f"✅ Auto-detected:")
            print(f"   Vault: {vault}")
            print(f"   Item:  {item_name}\n")
        except GitUtilsError as e:
            print(f"❌ Error: {e}")
            print("\nTroubleshooting:")
            print("  - Ensure you're in a git repository with a GitHub remote")
            print("  - Check: git remote get-url origin")
            print("  - Or use manual mode: <env-file> <vault> <item-name>")
            sys.exit(1)
    else:
        # Manual mode: require vault and item_name arguments
        if not args.vault or not args.item_name:
            print("❌ Error: vault and item_name are required in manual mode")
            print("\nUsage:")
            print("  Auto mode:   python3 migrate_env_to_1password.py <env-file> --auto")
            print("  Manual mode: python3 migrate_env_to_1password.py <env-file> <vault> <item-name>")
            sys.exit(1)
        vault = args.vault
        item_name = args.item_name

    print(f"🔍 Reading .env file...\n")

    # Parse .env file
    try:
        variables = parse_env_file(env_path)
    except Exception as e:
        print(f"❌ Error parsing .env file: {e}")
        sys.exit(1)

    # Detect secrets
    secrets, non_secrets = detect_secrets(variables)

    if not secrets:
        print("⚠️  No secrets detected in .env file")
        print("   (looking for keys containing: PASSWORD, SECRET, KEY, TOKEN, etc.)")
        sys.exit(0)

    print(f"Found {len(secrets)} secret(s) and {len(non_secrets)} non-secret variable(s)\n")

    # Validate 1Password CLI (skip in dry-run)
    if not args.dry_run:
        if not validate_op_cli():
            print("❌ 1Password CLI validation failed")
            print("   Run: python3 scripts/validate_op_cli.py")
            sys.exit(1)

    # Create/update 1Password item
    success = create_or_update_1password_item(
        vault,
        item_name,
        secrets,
        dry_run=args.dry_run
    )

    if not success:
        print("\n❌ Migration failed")
        sys.exit(1)

    print("\n✅ Secrets migrated to 1Password\n")

    # Generate template
    print("📝 Generating .env.tpl template...")
    template_path = generate_template(env_path, vault, item_name)
    print(f"✅ Generated {template_path}\n")

    # Backup original
    if args.backup:
        backup_env_file(env_path, dry_run=args.dry_run)
        print()

    # Update .gitignore
    update_gitignore(env_path, dry_run=args.dry_run)

    # Final instructions
    print("\n✅ Migration complete!\n")
    print("Next steps:")
    print(f"1. Review {template_path}")
    print(f"2. Test: op inject -i {template_path} -o .env.test")
    print(f"3. Verify: diff .env .env.test")
    print(f"4. Commit {template_path} to git")

    if args.dry_run:
        print("\n⚠️  This was a DRY RUN. No changes were made to 1Password.")

    sys.exit(0)


if __name__ == "__main__":
    main()
