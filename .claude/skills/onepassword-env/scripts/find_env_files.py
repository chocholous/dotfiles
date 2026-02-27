#!/usr/bin/env python3
"""
Find all .env* files in a directory tree.

This script recursively searches for .env files while ignoring common
directories like .git, node_modules, and venv.

Tool Annotations:
- readOnlyHint: True (only reads directory structure, no modifications)
- destructiveHint: False (no destructive operations)
- idempotentHint: True (always returns same results for same directory)
- openWorldHint: False (only reads local filesystem)

Usage:
    python3 find_env_files.py [directory]

Arguments:
    directory: Directory to search (default: current directory)

Output:
    JSON object with list of found .env files

Example:
    python3 find_env_files.py ~/projects
"""

import json
import os
import sys
from pathlib import Path


# Directories to ignore during search
IGNORE_DIRS = {
    '.git',
    'node_modules',
    'venv',
    '.venv',
    'env',
    '.env',  # Don't search inside .env directories
    '__pycache__',
    '.pytest_cache',
    '.tox',
    'dist',
    'build',
    '.egg-info',
}


def is_env_file(filename):
    """Check if filename matches .env* pattern."""
    # Match .env, .env.local, .env.production, etc.
    # But not .env.tpl, .env.example (templates without secrets)
    if filename == '.env':
        return True
    if filename.startswith('.env.') and not filename.endswith('.tpl') and not filename.endswith('.example'):
        return True
    return False


def should_ignore_dir(dir_name):
    """Check if directory should be ignored."""
    return dir_name in IGNORE_DIRS or dir_name.startswith('.')


def find_env_files(root_path):
    """
    Recursively find all .env files in root_path.

    Args:
        root_path: Path object to search from

    Returns:
        List of absolute paths to .env files
    """
    env_files = []

    try:
        for root, dirs, files in os.walk(root_path):
            # Remove ignored directories from traversal
            dirs[:] = [d for d in dirs if not should_ignore_dir(d)]

            # Check files in current directory
            for file in files:
                if is_env_file(file):
                    full_path = os.path.join(root, file)
                    env_files.append(os.path.abspath(full_path))

    except PermissionError as e:
        print(f"⚠️  Permission denied: {e}", file=sys.stderr)
    except Exception as e:
        print(f"❌ Error during search: {e}", file=sys.stderr)
        sys.exit(1)

    return sorted(env_files)


def main():
    """Main function."""
    # Get search directory from argument or use current directory
    if len(sys.argv) > 1:
        search_path = Path(sys.argv[1])
    else:
        search_path = Path.cwd()

    # Validate path exists
    if not search_path.exists():
        print(f"❌ Error: Path does not exist: {search_path}", file=sys.stderr)
        sys.exit(1)

    if not search_path.is_dir():
        print(f"❌ Error: Path is not a directory: {search_path}", file=sys.stderr)
        sys.exit(1)

    # Find .env files
    env_files = find_env_files(search_path)

    # Output as JSON
    result = {
        "env_files": env_files
    }
    print(json.dumps(result, indent=2))

    # Exit with appropriate code
    if env_files:
        sys.exit(0)
    else:
        sys.exit(0)  # Not an error if no files found


if __name__ == "__main__":
    main()
