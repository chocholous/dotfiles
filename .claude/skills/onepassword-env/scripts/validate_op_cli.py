#!/usr/bin/env python3
"""
Validate 1Password CLI installation and authentication status.

This script checks if the 1Password CLI (op) is installed and the user
is properly authenticated.

Tool Annotations:
- readOnlyHint: True (only reads configuration, no modifications)
- destructiveHint: False (no destructive operations)
- idempotentHint: True (always produces same result for same state)
- openWorldHint: True (checks 1Password CLI installation and auth)

Usage:
    python3 validate_op_cli.py

Exit codes:
    0: Success - op is installed and user is signed in
    1: Error - op not found or user not signed in
"""

import subprocess
import sys
import shutil


def check_op_installed():
    """Check if 1Password CLI is installed."""
    op_path = shutil.which("op")
    if not op_path:
        print("❌ 1Password CLI not found")
        print("\n📦 Installation instructions:")
        print("   macOS: brew install 1password-cli")
        print("   Linux: https://developer.1password.com/docs/cli/get-started#install")
        print("   Windows: https://developer.1password.com/docs/cli/get-started#install")
        return False

    print(f"✅ 1Password CLI found at: {op_path}")
    return True


def get_op_version():
    """Get 1Password CLI version."""
    try:
        result = subprocess.run(
            ["op", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ 1Password CLI version: {version}")
            return True
        else:
            print(f"⚠️  Could not determine version: {result.stderr}")
            return True  # CLI exists but version check failed (not critical)
    except subprocess.TimeoutExpired:
        print("⚠️  Version check timed out")
        return True
    except Exception as e:
        print(f"⚠️  Error checking version: {e}")
        return True


def check_signed_in():
    """Check if user is signed in to 1Password."""
    try:
        result = subprocess.run(
            ["op", "whoami"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            # Parse whoami output to get user email/account
            output = result.stdout.strip()
            print(f"✅ Signed in to 1Password")
            print(f"   {output}")
            return True
        else:
            print("❌ Not signed in to 1Password")
            print("\n🔐 Sign in instructions:")
            print("   Run: op signin")
            print("   Or: eval $(op signin)")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Sign-in check timed out")
        return False
    except Exception as e:
        print(f"❌ Error checking sign-in status: {e}")
        return False


def main():
    """Main validation function."""
    print("🔍 Validating 1Password CLI setup...\n")

    # Check if op is installed
    if not check_op_installed():
        sys.exit(1)

    # Get version info
    get_op_version()

    # Check if signed in
    if not check_signed_in():
        sys.exit(1)

    print("\n✅ 1Password CLI is ready to use!")
    sys.exit(0)


if __name__ == "__main__":
    main()
