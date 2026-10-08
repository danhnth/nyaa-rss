#!/data/data/com.termux/files/usr/bin/bash
# Install Navidrome pinned version on Termux. Run line by line, one block at a time.
# Pinned: 0.64.2 (2026-09-24). Override with NAVIDROME_VERSION=x.y.z env.
set -e
: "${NAVIDROME_VERSION:=0.64.2}"
: "${NAVIDROME_PORT:=4533}"
ARCH="$(uname -m)"
case "$ARCH" in
  aarch64) NDARCH="arm64" ;;
  armv7l|armv8l) NDARCH="armv7" ;;
  *) echo "unsupported arch: $ARCH (need aarch64 or armv7)"; exit 1 ;;
esac
mkdir -p $HOME/navidrome $HOME/storage/music/Japanese
cd $HOME/navidrome
curl -fL -o navidrome.tar.gz "https://github.com/navidrome/navidrome/releases/download/v${NAVIDROME_VERSION}/navidrome_${NAVIDROME_VERSION}_linux_${NDARCH}.tar.gz"
tar xzf navidrome.tar.gz navidrome
chmod +x navidrome
./navidrome --version
echo "$NAVIDROME_VERSION $NDARCH" > VERSION
test -f navidrome.toml || cp $HOME/nyaa-rss/navidrome/navidrome.toml.example navidrome.toml
echo "OK $NAVIDROME_VERSION ($NDARCH). Start with: ./navidrome --configfile $HOME/navidrome/navidrome.toml"
