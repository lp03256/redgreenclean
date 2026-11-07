#!/usr/bin/env bash
# Symlink Red Green Clean skills into ~/.claude/skills/. Touches nothing else.
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/skills"
DEST="${CLAUDE_HOME:-$HOME/.claude}/skills"

if [[ "${1:-}" == "--remove" ]]; then
  for skill in "$SRC"/*/; do
    name="$(basename "$skill")"
    link="$DEST/$name"
    if [[ -L "$link" ]]; then
      rm "$link"
      echo "removed  $name"
    fi
  done
  echo "Red Green Clean uninstalled."
  exit 0
fi

mkdir -p "$DEST"

for skill in "$SRC"/*/; do
  name="$(basename "$skill")"
  link="$DEST/$name"

  if [[ -e "$link" && ! -L "$link" ]]; then
    echo "SKIP     $name — a real directory is already there, not overwriting" >&2
    continue
  fi

  ln -sfn "$skill" "$link"
  echo "linked   $name"
done

echo
echo "Red Green Clean installed to $DEST"
echo "Start a new Claude Code session and run /rgc"
