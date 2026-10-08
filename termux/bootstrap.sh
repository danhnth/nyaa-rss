#!/data/data/com.termux/files/usr/bin/bash
# Bootstrap may moi / reset may: chay tung dong (khong paste multi-line 1 cuc).
set -e
pkg update -y
pkg install -y transmission python termux-api
mkdir -p $HOME/scripts $HOME/storage/music/Japanese $HOME/.config/transmission-daemon
termux-setup-storage
crond || true
termux-wake-lock || true
echo "OK. Tiep theo: copy scripts/sync_nyaa.py vao \$HOME/scripts/ roi chay: python \$HOME/scripts/sync_nyaa.py"
