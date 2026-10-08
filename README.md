# nyaa-rss — Music Home Server reproduce kit (Termux + Transmission + Navidrome)

Repo nay giup dung lai toan bo may stream nhac sau khi **doi dien thoai / reset may**.
Feed RSS duoc lay san tu repo phu: `danhnth/nyaa-rss-proxy` (GitHub Actions 12h/lan -> `feed.json`).
Termux chi keo file tinh, khong bao gio cham truc tiep `nyaa.si` (bi VN ISP chan L3 + Nyaa chan IP datacenter).

## Kien truc

```
[Nyaa.si] --(runner IP sach)--> [nyaa-rss-proxy/feed.json] --(raw.githubusercontent)--> [Termux sync_nyaa.py] -> [transmission-daemon] -> ~/storage/music/Japanese -> [Navidrome]
```

- `nyaa-rss-proxy`: `fetch_nyaa.py` stdlib-only, cron `0 */12 * * *`, ghi `feed.json` 75 items co `infoHash/size/seeders`.
- Repo nay: client Termux + doc khoi phuc. Khong trung fetch logic.

## Khoi phuc nhanh (may moi)

Chay tung dong 1 (Termux paste multi-line hay loi `\` + `~` trong quote):

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

Copy file vao may:

```bash
cp scripts/sync_nyaa.py $HOME/scripts/sync_nyaa.py
```

```bash
python $HOME/scripts/sync_nyaa.py
```

Dat cron (xem `termux/crontab.example`):

```bash
crontab -e
```

```
0 */2 * * * python /data/data/com.termux/files/home/scripts/sync_nyaa.py >> /data/data/com.termux/files/home/scripts/nyaa.log 2>&1
```

## Cau hinh

Env (co default dung duoc ngay):

| Var | Default | Y nghia |
|---|---|---|
| `NYAA_FEED_URL` | `.../nyaa-rss-proxy/main/feed.json` | file tinh github |
| `NYAA_DOWNLOAD_DIR` | `~/storage/music/Japanese` | thu muc Navidrome quet |
| `NYAA_HISTORY` | `~/scripts/downloaded_nyaa.txt` | chong tai trung |
| `NYAA_MAX_SIZE_GB` | `5.0` | block pack tram GB |
| `NYAA_ADD_PAUSED` | `1` | them o che do paused (`--start-paused`) |
| `NYAA_TR_HOST` | `localhost:9091` | transmission RPC |

Hai lop bao ve pack to: size-cap + start-paused doc lap. Muon tai tay thi Resume trong WebUI.

## Transmission remote

SSH tunnel khong can sua config:

```bash
ssh -L 9091:127.0.0.1:9091 <user>@<IP_DT> -p <PORT_SSH>
```

Mo whitelist thi xem `transmission/settings.json.example`. Nho `pkill transmission-daemon` truoc khi sua.

## Navidrome

1. Cai binary Navidrome cho Android/ARM, tro `MusicFolder` ve `~/storage/music/Japanese`.
2. Sau moi lan move/xoa folder: Web UI -> Rescan.
3. Gi Android khong toi uu pin Termux + Acquire Wakelock.

## Don dep Umamusume (1-dong paste)

Luu y: `~` trong quote khong expand, trailing `\` se nuot lenh tiep theo. Dung `$HOME`, khong `\`.

Cuu album unique:

```bash
a=$HOME/storage/music/Japanese/Umamusume/"UmaMusu discography"/"[2021-2026] WINNING LIVE"; b=$HOME/storage/music/Japanese/Umamusume/"[2021-2026] WINNING LIVE"; for d in "$a"/*; do [ -e "$b/$(basename "$d")" ] || mv "$d" "$b"/; done
```

Kiem tra truoc khi xoa:

```bash
ls -1 $HOME/storage/music/Japanese/Umamusume/"UmaMusu discography"/"[2021-2026] WINNING LIVE"
```

Xoa container:

```bash
rm -rf $HOME/storage/music/Japanese/Umamusume/"UmaMusu discography"
```

Go torrent gay data (giu file):

```bash
transmission-remote localhost:9091 -t 1 --remove
```

Verify:

```bash
ls -1 $HOME/storage/music/Japanese/Umamusume/
```

Chuyen download-dir cu sang moi (neu transmission da co data thi dung `--find`, khong `--move`):

```bash
transmission-remote localhost:9091 -t <id> --find $HOME/storage/music/Japanese
```

## Doi query nhac

Doi query thi sua `QUERY` trong `nyaa-rss-proxy/fetch_nyaa.py`, khong phai repo nay. Repo nay chi doi `NYAA_FEED_URL` neu fork proxy.
