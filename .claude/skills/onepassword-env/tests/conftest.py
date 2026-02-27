"""Pytest fixtures pro onepassword-env skill testy."""

import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def test_cases_dir():
    """Vrátí cestu k testovacím případům."""
    return Path("/private/tmp/claude-501/-Users-chocho/737bd6b7-084b-4352-bc37-0fe1b6b26ba2/scratchpad/onepassword-env-tests/test-cases")


@pytest.fixture
def temp_work_dir():
    """Vytvoří dočasný pracovní adresář."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def scripts_dir():
    """Vrátí cestu ke scripts adresáři."""
    # Předpokládá, že testy jsou v tests/ a skripty v scripts/
    current_file = Path(__file__)
    skill_dir = current_file.parent.parent
    return skill_dir / "scripts"


@pytest.fixture
def git_test_cases_dir():
    """Vrátí cestu k git testovacím případům."""
    return Path("/private/tmp/claude-501/-Users-chocho/737bd6b7-084b-4352-bc37-0fe1b6b26ba2/scratchpad/onepassword-env-tests/git-test-cases")
