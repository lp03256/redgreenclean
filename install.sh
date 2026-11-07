#!/usr/bin/env bash
# Symlink Red Green Clean skills into ~/.claude/skills/. Touches nothing else.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST="${CLAUDE_HOME:-$HOME/.claude}/skills"
BINDEST="${RGC_BIN:-$HOME/.local/bin}"

WANT_PRO=0
REMOVE=0
for arg in "$@"; do
  case "$arg" in
    --pro)    WANT_PRO=1 ;;
    --remove) REMOVE=1 ;;
    *) echo "usage: install.sh [--pro] [--remove]" >&2; exit 2 ;;
  esac
done

link_skills() {
  for skill in "$1"/*/; do
    [ -d "$skill" ] || continue
    name="$(basename "$skill")"
    link="$DEST/$name"
    if [[ -e "$link" && ! -L "$link" ]]; then
      echo "SKIP     $name — a real directory is already there" >&2
      continue
    fi
    ln -sfn "$skill" "$link"
    echo "linked   $name"
  done
}

unlink_skills() {
  for skill in "$1"/*/; do
    [ -d "$skill" ] || continue
    name="$(basename "$skill")"
    [[ -L "$DEST/$name" ]] && rm "$DEST/$name" && echo "removed  $name"
  done
  return 0
}

if [[ $REMOVE -eq 1 ]]; then
  unlink_skills "$HERE/skills"
  [ -d "$HERE/pro/skills" ] && unlink_skills "$HERE/pro/skills"
  if [ -d "$HERE/pro/bin" ]; then
    for tool in "$HERE/pro/bin"/*; do
      name="$(basename "$tool")"
      [[ -L "$BINDEST/$name" ]] && rm "$BINDEST/$name" && echo "removed  $name"
    done
  fi
  echo "Red Green Clean uninstalled."
  exit 0
fi

mkdir -p "$DEST"
link_skills "$HERE/skills"

if [[ $WANT_PRO -eq 1 ]]; then
  if [ ! -d "$HERE/pro/skills" ]; then
    echo "No pro/ directory here — Pro is a separate purchase." >&2
    exit 1
  fi
  link_skills "$HERE/pro/skills"
  mkdir -p "$BINDEST"
  for tool in "$HERE/pro/bin"/*; do
    [ -f "$tool" ] || continue
    ln -sfn "$tool" "$BINDEST/$(basename "$tool")"
    echo "linked   $(basename "$tool") -> $BINDEST"
  done
  case ":$PATH:" in
    *":$BINDEST:"*) ;;
    *) echo
       echo "NOTE: $BINDEST is not on your PATH. Add this to your shell rc:"
       echo "      export PATH=\"\$PATH:$BINDEST\"" ;;
  esac
fi

echo
echo "Red Green Clean installed to $DEST"
[[ $WANT_PRO -eq 1 ]] && echo "Pro tools installed to $BINDEST"
echo "Start a new Claude Code session and run /rgc"
