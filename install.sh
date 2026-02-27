#!/usr/bin/env bash
# Dotfiles install script — spouští Coder automaticky při startu workspace
set -e

DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "→ Nastavuji dotfiles..."

# ~/.claude/ — merge, nepřepisuj existující soubory
mkdir -p "$HOME/.claude/skills"
rsync -a --ignore-existing "$DOTFILES_DIR/.claude/" "$HOME/.claude/"
echo "  ✓ ~/.claude/ (CLAUDE.md, skills, settings)"

# .gitconfig — jen pokud neexistuje
if [ ! -f "$HOME/.gitconfig" ]; then
  cp "$DOTFILES_DIR/.gitconfig" "$HOME/.gitconfig"
  echo "  ✓ .gitconfig"
fi

echo "→ Dotfiles nastaveny."
