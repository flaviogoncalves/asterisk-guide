#!/usr/bin/env bash
# Move files to the project trashcan (.trash/<stamp>/) instead of deleting them, and
# untrack them from git. Recover with: mv .trash/<stamp>/<file> <original-path>
set -euo pipefail
stamp="$(date +%Y%m%d-%H%M%S)"
dest=".trash/$stamp"; mkdir -p "$dest"
for f in "$@"; do
  [ -e "$f" ] || { echo "skip (missing): $f"; continue; }
  mkdir -p "$dest/$(dirname "$f")"
  cp -a "$f" "$dest/$f"
  git rm -q --ignore-unmatch "$f" 2>/dev/null || rm -f "$f"
  echo "trashed: $f -> $dest/$f"
done
