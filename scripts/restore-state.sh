#!/data/data/com.termux/files/usr/bin/bash
# Restore state from a backup tarball. Stops daemons first to avoid clobbering.
# Usage: restore-state.sh <state-YYYY-MM-DD_HHMM.tar.gz>
set -e
test -n "$1" || { echo "usage: restore-state.sh <backup.tar.gz>"; exit 1; }
pkill transmission-daemon 2>/dev/null || true
pkill navidrome 2>/dev/null || true
tar xzf "$1" -C $HOME
echo "restored from $1"
echo "next: start transmission-daemon, verify with transmission-remote -l, then start navidrome"
