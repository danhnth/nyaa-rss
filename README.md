# nyaa-rss: Music Home Server reproduce kit (Termux + Transmission + Navidrome)

This repo rebuilds the music streaming box after a phone swap or factory reset.
The RSS feed is pre-fetched by the companion repo `danhnth/nyaa-rss-proxy` (GitHub Actions every 12h → `feed.json`).
Termux only pulls that static file and never touches `nyaa.si` directly (blocked by VN ISP at L3 + Nyaa blocks datacenter IPs).

## Architecture

```
[Nyaa.si] --(clean runner IP)--> [nyaa-rss-proxy/feed.json] --(raw.githubusercontent)--> [Termux sync_nyaa.py] -> [transmission-daemon] -> ~/storage/music/Japanese -> [Navidrome]
```

- `nyaa-rss-proxy`: stdlib-only `fetch_nyaa.py`, cron `0 */12 * * *`, writes `feed.json` with 75 items including `infoHash/size/seeders` (75 is Nyaa's per-feed RSS limit).
- This repo holds the Termux client and restore docs, without duplicating the fetch logic.
- Full step-by-step: `docs/RESTORE-CHECKLIST.md`.

## Quick restore (new phone)

Run line by line. Termux paste breaks on multi-line input: a trailing `\` swallows the next command, and `~` inside quotes does not expand:

```bash
pkg update -y
```

```bash
pkg install -y transmission python termux-api
```

```bash
mkdir -p $HOME/scripts $HOME/storage/music/Japanese $HOME/.config/transmission-daemon
```

```bash
termux-setup-storage
```

```bash
crond
```

```bash
termux-wake-lock
```

Copy files onto the phone:

```bash
cp scripts/sync_nyaa.py $HOME/scripts/sync_nyaa.py
```

```bash
python $HOME/scripts/sync_nyaa.py
```

Set up cron (see `termux/crontab.example`):

```bash
crontab -e
```

```
0 */2 * * * python /data/data/com.termux/files/home/scripts/sync_nyaa.py >> /data/data/com.termux/files/home/scripts/nyaa.log 2>&1
```

## Configuration

Environment variables (defaults work as is):

| Var | Default | Meaning |
|---|---|---|
| `NYAA_FEED_URLS` | `.../nyaa-rss-proxy/main/feed.json` | comma-separated feed files on GitHub (`NYAA_FEED_URL` still works for one) |
| `NYAA_DOWNLOAD_DIR` | `~/storage/music/Japanese` | directory Navidrome scans |
| `NYAA_HISTORY` | `~/scripts/downloaded_nyaa.txt` | dedup history |
| `NYAA_MAX_SIZE_GB` | `5.0` | blocks hundred-GB packs |
| `NYAA_ADD_PAUSED` | `1` | add paused (`--start-paused`) |
| `NYAA_TR_HOST` | `localhost:9091` | transmission RPC |

Two independent guards against huge packs: size cap + start-paused. Resume manually in the WebUI when you want it.

## Transmission remote access

Use an SSH tunnel, no config change needed:

```bash
ssh -L 9091:127.0.0.1:9091 <user>@<PHONE_IP> -p <SSH_PORT>
```

For whitelist mode see `transmission/settings.json.example`. Remember to `pkill transmission-daemon` before editing it.

## Moving the download directory

If you already `mv`-ed the data by hand, use `--find`, not `--move`:

```bash
transmission-remote localhost:9091 -t <id> --find $HOME/storage/music/Japanese
```

## Navidrome

1. Install the Android/ARM Navidrome binary (pinned 0.64.2, see `termux/install-navidrome.sh`), point `MusicFolder` at `~/storage/music/Japanese`.
2. After every move/delete: Web UI → Rescan.
3. Keep Android off battery optimization for Termux + Acquire Wakelock.

State backup (history + transmission config + Navidrome DB, not music files): `scripts/backup-state.sh`, restore with `scripts/restore-state.sh`.

## Changing the music query

Queries live in `nyaa-rss-proxy/queries.txt` (one per line), not in this repo.
Push a new line and the next run publishes `feed-<slug>.json`, then point the
phone at it:

```bash
export NYAA_FEED_URLS="https://raw.githubusercontent.com/danhnth/nyaa-rss-proxy/main/feed.json,https://raw.githubusercontent.com/danhnth/nyaa-rss-proxy/main/feed-umamusume.json"
```

Only change the URL host here if you fork the proxy.

## Fetching old releases (backfill)

Feeds only cover the newest 75 per query. For older releases, run the manual
`backfill-nyaa` workflow in the proxy repo (query + pages, up to 50), then add
the catalog URL to `NYAA_FEED_URLS` alongside the feeds:

```bash
export NYAA_FEED_URLS="https://raw.githubusercontent.com/danhnth/nyaa-rss-proxy/main/feed.json,https://raw.githubusercontent.com/danhnth/nyaa-rss-proxy/main/catalog-bang-dream.json"
```

Same item schema, so size cap, start-paused, and history dedup apply unchanged.
Already-downloaded items are skipped via history.
