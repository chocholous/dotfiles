"""Testy pro GitHub remote detection a naming convention."""

import pytest
from pathlib import Path
import sys

# Přidáme scripts do path
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from git_utils import (
    find_git_root,
    get_git_remote,
    parse_github_url,
    relative_path_to_pattern,
    get_1password_names,
    GitRemoteError
)


@pytest.fixture
def git_test_cases_dir():
    """Vrátí cestu k git test cases."""
    return Path("/private/tmp/claude-501/-Users-chocho/737bd6b7-084b-4352-bc37-0fe1b6b26ba2/scratchpad/onepassword-env-tests/git-test-cases")


class TestGitRootFinding:
    """Testy pro find_git_root()."""

    def test_simple_project_root(self, git_test_cases_dir):
        """Najde git root v jednoduchém projektu."""
        env_path = git_test_cases_dir / "simple-project" / ".env"
        git_root = find_git_root(env_path)

        assert git_root is not None
        assert git_root.name == "simple-project"
        assert (git_root / ".git").exists()

    def test_nested_env_finds_root(self, git_test_cases_dir):
        """Vnořený .env najde git root."""
        env_path = git_test_cases_dir / "simple-project" / "cli" / ".env"
        git_root = find_git_root(env_path)

        assert git_root is not None
        assert git_root.name == "simple-project"

    def test_submodule_finds_submodule_root(self, git_test_cases_dir):
        """Submodule .env najde submodule git root, ne parent."""
        frontend_env = git_test_cases_dir / "submodule-project" / "frontend" / ".env"
        git_root = find_git_root(frontend_env)

        assert git_root is not None
        assert git_root.name == "frontend"  # Najde frontend/.git, ne parent!
        assert (git_root / ".git").exists()

    def test_no_git_returns_none(self, tmp_path):
        """Adresář bez .git vrátí None."""
        env_file = tmp_path / ".env"
        env_file.write_text("TEST=value")

        git_root = find_git_root(env_file)
        assert git_root is None


class TestGitHubURLParsing:
    """Testy pro parse_github_url()."""

    def test_https_with_git_suffix(self):
        """HTTPS URL s .git příponou."""
        user, repo = parse_github_url("https://github.com/testuser/myproject.git")
        assert user == "testuser"
        assert repo == "myproject"

    def test_https_without_git_suffix(self):
        """HTTPS URL bez .git přípony."""
        user, repo = parse_github_url("https://github.com/testuser/myproject")
        assert user == "testuser"
        assert repo == "myproject"

    def test_ssh_with_git_suffix(self):
        """SSH URL s .git příponou."""
        user, repo = parse_github_url("git@github.com:testuser/myproject.git")
        assert user == "testuser"
        assert repo == "myproject"

    def test_ssh_without_git_suffix(self):
        """SSH URL bez .git přípony."""
        user, repo = parse_github_url("git@github.com:testuser/myproject")
        assert user == "testuser"
        assert repo == "myproject"

    def test_invalid_url_raises_error(self):
        """Nevalidní URL vyhodí chybu."""
        with pytest.raises(GitRemoteError):
            parse_github_url("not-a-valid-url")

    def test_non_github_url_raises_error(self):
        """Non-GitHub URL vyhodí chybu."""
        with pytest.raises(GitRemoteError):
            parse_github_url("https://gitlab.com/user/repo.git")


class TestRelativePathPattern:
    """Testy pro relative_path_to_pattern()."""

    def test_root_env(self, tmp_path):
        """/.env → 'root'"""
        git_root = tmp_path
        env_path = git_root / ".env"

        pattern = relative_path_to_pattern(env_path, git_root)
        assert pattern == "root"

    def test_nested_env(self, tmp_path):
        """/cli/.env → 'cli__env'"""
        git_root = tmp_path
        env_path = git_root / "cli" / ".env"

        pattern = relative_path_to_pattern(env_path, git_root)
        assert pattern == "cli__env"

    def test_deeply_nested_env(self, tmp_path):
        """/backend/api/.env → 'backend__api__env'"""
        git_root = tmp_path
        env_path = git_root / "backend" / "api" / ".env"

        pattern = relative_path_to_pattern(env_path, git_root)
        assert pattern == "backend__api__env"

    def test_env_with_suffix(self, tmp_path):
        """/backend/.env.local → 'backend__env.local'"""
        git_root = tmp_path
        env_path = git_root / "backend" / ".env.local"

        pattern = relative_path_to_pattern(env_path, git_root)
        assert pattern == "backend__env.local"

    def test_collision_cases(self, tmp_path):
        """Ověř že různé cesty mají různé patterns."""
        git_root = tmp_path

        # backend-prod/.env vs backend/prod/.env
        path1 = git_root / "backend-prod" / ".env"
        path2 = git_root / "backend" / "prod" / ".env"

        pattern1 = relative_path_to_pattern(path1, git_root)
        pattern2 = relative_path_to_pattern(path2, git_root)

        assert pattern1 == "backend-prod__env"
        assert pattern2 == "backend__prod__env"
        assert pattern1 != pattern2  # Žádná kolize!


class TestGet1PasswordNames:
    """Testy pro get_1password_names() - end-to-end."""

    def test_simple_project_root_env(self, git_test_cases_dir):
        """Jednoduchý projekt - root .env"""
        env_path = git_test_cases_dir / "simple-project" / ".env"

        vault, item = get_1password_names(env_path)

        assert vault == "gh-projects"
        assert item == "testuser__simple-app__root"

    def test_simple_project_nested_env(self, git_test_cases_dir):
        """Jednoduchý projekt - vnořený .env"""
        env_path = git_test_cases_dir / "simple-project" / "cli" / ".env"

        vault, item = get_1password_names(env_path)

        assert vault == "gh-projects"
        assert item == "testuser__simple-app__cli__env"

    def test_submodule_frontend(self, git_test_cases_dir):
        """Submodule - použije submodule remote, ne parent!"""
        env_path = git_test_cases_dir / "submodule-project" / "frontend" / ".env"

        vault, item = get_1password_names(env_path)

        assert vault == "gh-projects"
        assert item == "testuser__frontend-lib__root"  # frontend-lib, NE main-app!

    def test_submodule_backend(self, git_test_cases_dir):
        """Submodule - backend má vlastní remote."""
        env_path = git_test_cases_dir / "submodule-project" / "backend" / ".env"

        vault, item = get_1password_names(env_path)

        assert vault == "gh-projects"
        assert item == "testuser__backend-api__root"  # backend-api, NE main-app!

    def test_submodule_parent(self, git_test_cases_dir):
        """Submodule project - parent .env používá parent remote."""
        env_path = git_test_cases_dir / "submodule-project" / ".env"

        vault, item = get_1password_names(env_path)

        assert vault == "gh-projects"
        assert item == "testuser__main-app__root"  # main-app

    def test_monorepo_root(self, git_test_cases_dir):
        """Monorepo - root .env."""
        env_path = git_test_cases_dir / "monorepo-project" / ".env"

        vault, item = get_1password_names(env_path)

        assert vault == "gh-projects"
        assert item == "testorg__monorepo__root"

    def test_monorepo_nested(self, git_test_cases_dir):
        """Monorepo - vnořený .env sdílí stejný prefix."""
        env_path = git_test_cases_dir / "monorepo-project" / "apps" / "web" / ".env"

        vault, item = get_1password_names(env_path)

        assert vault == "gh-projects"
        assert item == "testorg__monorepo__apps__web__env"

    def test_no_remote_raises_error(self, git_test_cases_dir):
        """Projekt bez remote vyhodí jasnou chybu."""
        env_path = git_test_cases_dir / "no-remote-project" / ".env"

        with pytest.raises(GitRemoteError) as exc_info:
            get_1password_names(env_path)

        error_msg = str(exc_info.value)
        assert "No git remote" in error_msg
        assert "not supported" in error_msg
        assert "git remote add origin" in error_msg  # Návod jak opravit

    def test_no_git_raises_error(self, tmp_path):
        """Projekt bez .git vyhodí jasnou chybu."""
        env_path = tmp_path / ".env"
        env_path.write_text("TEST=value")

        with pytest.raises(GitRemoteError) as exc_info:
            get_1password_names(env_path)

        error_msg = str(exc_info.value)
        assert "No git repository" in error_msg
        assert "not supported" in error_msg
