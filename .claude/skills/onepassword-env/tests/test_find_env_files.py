"""Testy pro find_env_files.py script."""

import json
import subprocess
from pathlib import Path


def test_find_simple_env(test_cases_dir, scripts_dir):
    """Test detekce jednoduchého .env souboru."""
    case_dir = test_cases_dir / "case1-simple"
    result = subprocess.run(
        ["python3", str(scripts_dir / "find_env_files.py"), str(case_dir)],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert len(data["env_files"]) == 1
    assert data["env_files"][0].endswith(".env")


def test_find_multiple_env(test_cases_dir, scripts_dir):
    """Test detekce více .env* souborů."""
    case_dir = test_cases_dir / "case2-multiple"
    result = subprocess.run(
        ["python3", str(scripts_dir / "find_env_files.py"), str(case_dir)],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert len(data["env_files"]) == 3
    # Ověř, že obsahuje .env, .env.local, .env.production
    basenames = [Path(f).name for f in data["env_files"]]
    assert ".env" in basenames
    assert ".env.local" in basenames
    assert ".env.production" in basenames


def test_find_nested_env(test_cases_dir, scripts_dir):
    """Test detekce vnořených .env souborů."""
    case_dir = test_cases_dir / "case6-nested"
    result = subprocess.run(
        ["python3", str(scripts_dir / "find_env_files.py"), str(case_dir)],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert len(data["env_files"]) == 2


def test_find_no_env(temp_work_dir, scripts_dir):
    """Test když nejsou žádné .env soubory."""
    result = subprocess.run(
        ["python3", str(scripts_dir / "find_env_files.py"), str(temp_work_dir)],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert len(data["env_files"]) == 0


def test_find_ignores_templates(temp_work_dir, scripts_dir):
    """Test že .env.tpl a .env.example jsou ignorovány."""
    # Vytvoř .env.tpl a .env.example
    (temp_work_dir / ".env.tpl").write_text("TEMPLATE=value")
    (temp_work_dir / ".env.example").write_text("EXAMPLE=value")
    (temp_work_dir / ".env").write_text("REAL=secret")

    result = subprocess.run(
        ["python3", str(scripts_dir / "find_env_files.py"), str(temp_work_dir)],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)

    # Měl by najít pouze .env (ne .env.tpl ani .env.example)
    assert len(data["env_files"]) == 1
    assert data["env_files"][0].endswith(".env")
