"""Testy pro generate_env_template.py script."""

import subprocess
from pathlib import Path


def test_generate_simple_template(test_cases_dir, temp_work_dir, scripts_dir):
    """Test generování šablony z jednoduchého .env."""
    env_file = test_cases_dir / "case1-simple" / ".env"
    output_file = temp_work_dir / ".env.tpl"

    result = subprocess.run(
        [
            "python3", str(scripts_dir / "generate_env_template.py"),
            str(env_file), "TestVault", "TestItem",
            "--output", str(output_file)
        ],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0, f"Script failed: {result.stderr}"
    assert output_file.exists()

    content = output_file.read_text()
    assert 'op://TestVault/TestItem/db_password' in content
    assert 'op://TestVault/TestItem/api_key' in content


def test_generate_preserves_comments(test_cases_dir, temp_work_dir, scripts_dir):
    """Test, že generování zachovává komentáře."""
    env_file = test_cases_dir / "case5-comments" / ".env"
    output_file = temp_work_dir / ".env.tpl"

    result = subprocess.run(
        [
            "python3", str(scripts_dir / "generate_env_template.py"),
            str(env_file), "TestVault", "TestItem",
            "--output", str(output_file)
        ],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    content = output_file.read_text()

    # Ověř, že komentáře zůstaly
    assert "# Database Configuration" in content
    assert "# Secrets" in content
    assert "# Final comment" in content


def test_generate_mixed_secrets(test_cases_dir, temp_work_dir, scripts_dir):
    """Test detekce pouze secrets (ne všech proměnných)."""
    env_file = test_cases_dir / "case4-mixed" / ".env"
    output_file = temp_work_dir / ".env.tpl"

    result = subprocess.run(
        [
            "python3", str(scripts_dir / "generate_env_template.py"),
            str(env_file), "TestVault", "TestItem",
            "--output", str(output_file)
        ],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    content = output_file.read_text()

    # Secrets by měly mít op:// odkazy
    assert 'op://TestVault/TestItem/db_password' in content

    # Non-secrets by měly zůstat stejné (bez op:// odkazů)
    assert 'APP_NAME=MyApp' in content
    assert 'PORT=3000' in content
    assert 'ENABLE_ANALYTICS=true' in content

    # Ověř, že non-secrets NEMAJÍ op:// odkazy
    assert 'op://TestVault/TestItem/app_name' not in content
    assert 'op://TestVault/TestItem/port' not in content


def test_generate_no_secrets(test_cases_dir, temp_work_dir, scripts_dir):
    """Test když .env neobsahuje žádné secrets."""
    env_file = test_cases_dir / "case3-no-secrets" / ".env"
    output_file = temp_work_dir / ".env.tpl"

    result = subprocess.run(
        [
            "python3", str(scripts_dir / "generate_env_template.py"),
            str(env_file), "TestVault", "TestItem",
            "--output", str(output_file)
        ],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    content = output_file.read_text()

    # Neměly by být žádné op:// odkazy
    assert 'op://' not in content

    # Všechny hodnoty by měly zůstat stejné
    assert 'APP_NAME=MyApp' in content
    assert 'PORT=3000' in content
    assert 'ENVIRONMENT=development' in content


def test_generate_empty_lines_preserved(test_cases_dir, temp_work_dir, scripts_dir):
    """Test že prázdné řádky jsou zachovány."""
    env_file = test_cases_dir / "case5-comments" / ".env"
    output_file = temp_work_dir / ".env.tpl"

    result = subprocess.run(
        [
            "python3", str(scripts_dir / "generate_env_template.py"),
            str(env_file), "TestVault", "TestItem",
            "--output", str(output_file)
        ],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    content = output_file.read_text()

    # Zkontroluj že máme prázdné řádky (by měla být multi-line struktura)
    lines = content.splitlines()
    empty_lines = [i for i, line in enumerate(lines) if not line.strip()]
    assert len(empty_lines) > 0, "Měly by být zachovány prázdné řádky"
