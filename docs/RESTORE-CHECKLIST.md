# Factory-reset restore checklist

Follow in order. Each step has a verify line; do not skip it.

## 1. Termux base

Run `termux/bootstrap.sh` line by line, then verify:

```bash
which transmission-daemon python
```

```bash
crond
```

## 2. Repo + sync client

```bash
git clone https://github.com/danhnth/nyaa-rss.git $HOME/nyaa-rss
```

```bash
cp $HOME/nyaa-rss/scripts/sync_nyaa.py $HOME/scripts/sync_nyaa.py
```

```bash
python $HOME/scripts/sync_nyaa.py
```

Verify: last line prints `done: added=...`.

## 3. Navidrome (pinned 0.64.2)

```bash
bash $HOME/nyaa-rss/termux/install-navidrome.sh
```

Verify: `./navidrome --version` prints the pinned version, `VERSION` file exists.

## 4. Restore state (if you have a backup)

Music files first: copy them back to `$HOME/storage/music/Japanese` from SD/USB.

```bash
bash $HOME/nyaa-rss/scripts/restore-state.sh $HOME/storage/shared/nyaa-rss-backup/<state-DATE.tar.gz>
```

```bash
transmission-daemon
```

```bash
transmission-remote localhost:9091 -l
```

Verify: torrent list matches the old phone, no `No such torrent` errors. Fix moved data with `--find` (see README).

## 5. Navidrome first start

```bash
./navidrome --configfile $HOME/navidrome/navidrome.toml
```

Open the Web UI, log in, trigger Rescan. Verify album count looks right.

## 6. Cron + keepalive

Add the line from `termux/crontab.example` via `crontab -e`. In Android settings set Termux battery to Unrestricted and Acquire Wakelock.

Optional backup cron (weekly, cheap):

```
0 3 * * 0 bash /data/data/com.termux/files/home/nyaa-rss/scripts/backup-state.sh >> /data/data/com.termux/files/home/scripts/backup.log 2>&1
```

## What this checklist does NOT restore

Music files (too big for git), Tailscale identity (re-login in the app), and anything outside `$HOME` (needs root, out of scope).
