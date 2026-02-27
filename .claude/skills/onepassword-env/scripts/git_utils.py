#!/usr/bin/env python3
"""
Git utilities pro detekci GitHub remote a generování 1Password názvů.

Podporuje:
- Jednoduchérepozitáře
- Git submodules
- Monorepo
- Různé GitHub URL formáty
"""

import re
import subprocess
from pathlib import Path
from typing import Tuple, Optional


class GitRemoteError(Exception):
    """Chyba při práci s Git remote."""
    pass


def find_git_root(start_path: Path) -> Optional[Path]:
    """
    Najde nejbližší .git adresář směrem nahoru od start_path.

    Podporuje submodules - každý submodule má vlastní .git.

    Args:
        start_path: Cesta, odkud začít hledání

    Returns:
        Path k git root nebo None pokud nenalezeno
    """
    current = Path(start_path).resolve()

    while current != current.parent:
        git_dir = current / '.git'
        if git_dir.exists():
            return current
        current = current.parent

    return None


def get_git_remote(repo_root: Path, remote_name: str = 'origin') -> Optional[str]:
    """
    Získá URL git remote z repozitáře.

    Args:
        repo_root: Cesta k root git repozitáře
        remote_name: Název remote (default: 'origin')

    Returns:
        URL remote nebo None pokud neexistuje
    """
    try:
        result = subprocess.run(
            ['git', 'config', '--get', f'remote.{remote_name}.url'],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            return result.stdout.strip()
        return None

    except Exception:
        return None


def parse_github_url(url: str) -> Tuple[str, str]:
    """
    Parsuje GitHub URL na (user, repo).

    Podporované formáty:
    - https://github.com/user/repo.git
    - https://github.com/user/repo
    - git@github.com:user/repo.git
    - git@github.com:user/repo

    Args:
        url: GitHub URL

    Returns:
        Tuple (user, repo)

    Raises:
        GitRemoteError: Pokud URL není validní GitHub URL
    """
    if not url:
        raise GitRemoteError("Empty URL")

    # Normalize URL
    url = url.strip()

    # HTTPS format: https://github.com/user/repo.git
    https_match = re.match(r'https?://github\.com/([^/]+)/([^/]+?)(?:\.git)?$', url)
    if https_match:
        user, repo = https_match.groups()
        return user, repo

    # SSH format: git@github.com:user/repo.git
    ssh_match = re.match(r'git@github\.com:([^/]+)/([^/]+?)(?:\.git)?$', url)
    if ssh_match:
        user, repo = ssh_match.groups()
        return user, repo

    raise GitRemoteError(f"Not a valid GitHub URL: {url}")


def relative_path_to_pattern(env_path: Path, git_root: Path) -> str:
    """
    Převede relativní cestu .env souboru na pattern pro item name.

    Pravidla:
    - /.env → "root"
    - /cli/.env → "cli__env"
    - /backend/api/.env → "backend__api__env"
    - /backend/.env.local → "backend__env.local"
    - /backend-prod/.env → "backend-prod__env"

    Args:
        env_path: Cesta k .env souboru
        git_root: Cesta k git root

    Returns:
        Pattern string pro item name
    """
    rel_path = env_path.relative_to(git_root)

    # Speciální případ: .env v root
    if str(rel_path) == '.env':
        return 'root'

    # Získej parent directory a filename
    parent = rel_path.parent
    filename = rel_path.name

    # Převeď directory path: "/" → "__"
    if str(parent) == '.':
        parent_pattern = ''
    else:
        parent_pattern = str(parent).replace('/', '__')

    # Převeď filename: .env → env, .env.local → env.local
    if filename == '.env':
        file_pattern = 'env'
    else:
        # .env.local → env.local, .env.production → env.production
        file_pattern = filename.replace('.env', 'env')

    # Složení
    if parent_pattern:
        return f"{parent_pattern}__{file_pattern}"
    else:
        return file_pattern


def get_1password_names(env_path: Path) -> Tuple[str, str]:
    """
    Automaticky odvodí 1Password vault a item name z .env souboru.

    Proces:
    1. Najde nejbližší .git (podporuje submodules)
    2. Získá GitHub remote origin URL
    3. Parsuje user/repo z URL
    4. Vytvoří vault name: "gh-projects"
    5. Vytvoří item name: "{user}__{repo}__{path_pattern}"

    Args:
        env_path: Cesta k .env souboru

    Returns:
        Tuple (vault_name, item_name)

    Raises:
        GitRemoteError: Pokud není nalezen git repo nebo GitHub remote

    Examples:
        >>> # simple-project/.env
        >>> get_1password_names(Path("/path/simple-project/.env"))
        ('gh-projects', 'testuser__simple-app__root')

        >>> # submodule-project/frontend/.env
        >>> get_1password_names(Path("/path/submodule-project/frontend/.env"))
        ('gh-projects', 'testuser__frontend-lib__root')

        >>> # monorepo/apps/web/.env
        >>> get_1password_names(Path("/path/monorepo/apps/web/.env"))
        ('gh-projects', 'testorg__monorepo__apps__web__env')
    """
    # 1. Najdi git root (nejbližší .git)
    git_root = find_git_root(env_path.parent)
    if not git_root:
        raise GitRemoteError(
            f"No git repository found for {env_path}\n"
            "Projects without git are not supported."
        )

    # 2. Získej GitHub remote
    remote_url = get_git_remote(git_root)
    if not remote_url:
        raise GitRemoteError(
            f"No git remote 'origin' found in {git_root}\n"
            "Projects without GitHub remote are not supported.\n"
            "\n"
            "To add remote:\n"
            f"  cd {git_root}\n"
            "  git remote add origin https://github.com/user/repo.git"
        )

    # 3. Ověř že je to GitHub URL
    if 'github.com' not in remote_url:
        raise GitRemoteError(
            f"Remote URL is not GitHub: {remote_url}\n"
            "Only GitHub remotes are currently supported."
        )

    # 4. Parsuj user/repo
    try:
        user, repo = parse_github_url(remote_url)
    except GitRemoteError as e:
        raise GitRemoteError(
            f"Failed to parse GitHub URL: {remote_url}\n"
            f"Error: {e}"
        )

    # 5. Vytvoř relativní cestu pattern
    path_pattern = relative_path_to_pattern(env_path, git_root)

    # 6. Vault a item name
    vault = "gh-projects"
    item = f"{user}__{repo}__{path_pattern}"

    return vault, item


if __name__ == "__main__":
    # Testovací příklady
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 git_utils.py <path-to-env-file>")
        sys.exit(1)

    env_path = Path(sys.argv[1])

    try:
        vault, item = get_1password_names(env_path)
        print(f"✅ Vault: {vault}")
        print(f"✅ Item: {item}")
    except GitRemoteError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
