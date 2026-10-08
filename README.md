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
| `NYAA_FEED_URL` | `.../nyaa-rss-proxy/main/feed.json` | static file on GitHub |
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

1. Install the Android/ARM Navidrome binary, point `MusicFolder` at `~/storage/music/Japanese`.
2. After every move/delete: Web UI → Rescan.
3. Keep Android off battery optimization for Termux + Acquire Wakelock.

## Changing the music query

Change `QUERY` in `nyaa-rss-proxy/fetch_nyaa.py`, not in this repo. Here you only change `NYAA_FEED_URL` if you fork the proxy.
