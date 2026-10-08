#!/data/data/com.termux/files/usr/bin/bash
# Backup small state (history + transmission config + navidrome DB) to shared storage.
# Music files themselves are NOT included; keep them on SD/USB separately.
# Usage: backup-state.sh [backup_dir]
set -e
DEST="${1:-$HOME/storage/shared/nyaa-rss-backup}"
TS="$(date +%F_%H%M)"
OUT="$DEST/state-$TS.tar.gz"
mkdir -p "$DEST"
tar czf "$OUT" \
  -C $HOME scripts/downloaded_nyaa.txt \
  -C $HOME .config/transmission-daemon/settings.json \
  -C $HOME .config/transmission-daemon/torrents \
  -C $HOME navidrome/VERSION \
  -C $HOME navidrome/navidrome.toml \
  -C $HOME navidrome/data navidrome.db 2>/dev/null || true
ls -la "$OUT"
echo "wrote $OUT"
