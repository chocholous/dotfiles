#!/usr/bin/env python3
"""
Generate .env.tpl template from .env file with 1Password references.

This script converts a .env file to a .env.tpl template by replacing
secret values with op:// references while preserving comments and non-secrets.

Tool Annotations:
- readOnlyHint: False (reads .env, writes .env.tpl)
- destructiveHint: False (only creates new files, doesn't modify existing)
- idempotentHint: True (can run multiple times, produces same output)
- openWorldHint: False (only local filesystem operations)

Usage:
    python3 generate_env_template.py <env-file> <vault-name> <item-name> [--output <file>]

Arguments:
    env-file: Path to the .env file to convert
    vault-name: Name of 1Password vault
    item-name: Name of 1Password item
    --output: Output file path (default: same directory as input, .env.tpl)

Example:
    python3 generate_env_template.py .env Dev MyProject --output .env.tpl
"""

import argparse
import re
import sys
from pathlib import Path


# Keywords that indicate a secret value
SECRET_KEYWORDS = [
    'PASSWORD',
    'SECRET',
    'KEY',
    'TOKEN',
    'CREDENTIAL',
    'PRIVATE',
    'AUTH',
]


def is_secret_key(key):
    """
    Determine if an environment variable key represents a secret.

    Args:
        key: Environment variable name

    Returns:
        True if key likely contains a secret
    """
    key_upper = key.upper()
    return any(keyword in key_upper for keyword in SECRET_KEYWORDS)


def normalize_field_name(key):
    """
    Convert environment variable key to 1Password field name.

    Args:
        key: Environment variable key (e.g., DB_PASSWORD)

    Returns:
        Normalized field name (e.g., db_password)
    """
    return key.lower()


def parse_env_line(line):
    """
    Parse a single line from .env file.

    Args:
        line: Line from .env file

    Returns:
        Tuple of (type, key, value, original_line)
        type can be: 'empty', 'comment', 'variable'
    """
    stripped = line.strip()

    # Empty line
    if not stripped:
        return ('empty', None, None, line)

    # Comment line
    if stripped.startswith('#'):
        return ('comment', None, None, line)

    # Variable line (KEY=value or KEY="value")
    match = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)=(.*)$', stripped)
    if match:
        key = match.group(1)
        value = match.group(2)
        return ('variable', key, value, line)

    # Unknown format (preserve as-is)
    return ('unknown', None, None, line)


def generate_op_reference(vault, item, field):
    """
    Generate 1Password reference string.

    Args:
        vault: Vault name
        item: Item name
        field: Field name

    Returns:
        1Password reference string (e.g., op://Dev/MyProject/db_password)
    """
    return f'op://{vault}/{item}/{field}'


def convert_env_to_template(env_content, vault_name, item_name):
    """
    Convert .env file content to .env.tpl template.

    Args:
        env_content: Content of .env file
        vault_name: 1Password vault name
        item_name: 1Password item name

    Returns:
        Converted template content
    """
    lines = env_content.splitlines(keepends=True)
    output_lines = []

    for line in lines:
        line_type, key, value, original = parse_env_line(line)

        if line_type == 'variable':
            if is_secret_key(key):
                # Replace secret value with op:// reference
                field_name = normalize_field_name(key)
                op_ref = generate_op_reference(vault_name, item_name, field_name)
                # Preserve original line format but replace value
                new_line = f'{key}="{op_ref}"\n'
                output_lines.append(new_line)
            else:
                # Keep non-secret variables as-is
                output_lines.append(original)
        else:
            # Preserve comments, empty lines, and unknown lines
            output_lines.append(original)

    return ''.join(output_lines)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Generate .env.tpl template with 1Password references'
    )
    parser.add_argument(
        'env_file',
        help='Path to .env file'
    )
    parser.add_argument(
        'vault_name',
        help='1Password vault name'
    )
    parser.add_argument(
        'item_name',
        help='1Password item name'
    )
    parser.add_argument(
        '--output',
        help='Output file path (default: <env-file>.tpl)',
        default=None
    )

    args = parser.parse_args()

    # Validate input file
    env_path = Path(args.env_file)
    if not env_path.exists():
        print(f"❌ Error: File not found: {env_path}")
        sys.exit(1)

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        # Default: replace .env with .env.tpl
        if env_path.name == '.env':
            output_path = env_path.parent / '.env.tpl'
        else:
            output_path = env_path.parent / f'{env_path.name}.tpl'

    # Read input file
    print(f"🔍 Reading {env_path}...")
    try:
        env_content = env_path.read_text()
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        sys.exit(1)

    # Convert to template
    print(f"🔄 Converting to template...")
    template_content = convert_env_to_template(env_content, args.vault_name, args.item_name)

    # Write output file
    print(f"📝 Writing {output_path}...")
    try:
        output_path.write_text(template_content)
    except Exception as e:
        print(f"❌ Error writing file: {e}")
        sys.exit(1)

    print(f"✅ Template created successfully!")
    print(f"\nNext steps:")
    print(f"1. Review {output_path}")
    print(f"2. Create secrets in 1Password: op item create --vault {args.vault_name} --title {args.item_name}")
    print(f"3. Test: op inject -i {output_path} -o .env.test")

    sys.exit(0)


if __name__ == "__main__":
    main()
