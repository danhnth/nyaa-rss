# nyaa-rss — Bộ reproduce Music Home Server (Termux + Transmission + Navidrome)

Repo này giúp dựng lại toàn bộ máy stream nhạc sau khi **đổi điện thoại / reset máy**.
Feed RSS được lấy sẵn từ repo phụ: `danhnth/nyaa-rss-proxy` (GitHub Actions 12h/lần → `feed.json`).
Termux chỉ kéo file tĩnh, không bao giờ chạm trực tiếp `nyaa.si` (bị VN ISP chặn L3 + Nyaa chặn IP datacenter).

## Kiến trúc

```
[Nyaa.si] --(runner IP sạch)--> [nyaa-rss-proxy/feed.json] --(raw.githubusercontent)--> [Termux sync_nyaa.py] -> [transmission-daemon] -> ~/storage/music/Japanese -> [Navidrome]
```

- `nyaa-rss-proxy`: `fetch_nyaa.py` chỉ dùng stdlib, cron `0 */12 * * *`, ghi `feed.json` 75 items có `infoHash/size/seeders` (75 là giới hạn của Nyaa cho mỗi RSS feed).
- Repo này: client Termux + tài liệu khôi phục. Không trùng logic fetch.

## Khôi phục nhanh (máy mới)

Chạy từng dòng một (Termux hay lỗi khi paste multi-line: dấu `\` cuối dòng sẽ nuốt lệnh tiếp theo, `~` trong quote không expand):

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

Copy file vào máy:

```bash
cp scripts/sync_nyaa.py $HOME/scripts/sync_nyaa.py
```

```bash
python $HOME/scripts/sync_nyaa.py
```

Đặt cron (xem `termux/crontab.example`):

```bash
crontab -e
```

```
0 */2 * * * python /data/data/com.termux/files/home/scripts/sync_nyaa.py >> /data/data/com.termux/files/home/scripts/nyaa.log 2>&1
```

## Cấu hình

Biến môi trường (đã có default dùng được ngay):

| Var | Default | Ý nghĩa |
|---|---|---|
| `NYAA_FEED_URL` | `.../nyaa-rss-proxy/main/feed.json` | file tĩnh trên GitHub |
| `NYAA_DOWNLOAD_DIR` | `~/storage/music/Japanese` | thư mục Navidrome quét |
| `NYAA_HISTORY` | `~/scripts/downloaded_nyaa.txt` | chống tải trùng |
| `NYAA_MAX_SIZE_GB` | `5.0` | chặn pack hàng trăm GB |
| `NYAA_ADD_PAUSED` | `1` | thêm ở chế độ paused (`--start-paused`) |
| `NYAA_TR_HOST` | `localhost:9091` | transmission RPC |

Hai lớp bảo vệ pack to: size-cap + start-paused độc lập. Muốn tải bằng tay thì Resume trong WebUI.

## Transmission remote

SSH tunnel, không cần sửa config:

```bash
ssh -L 9091:127.0.0.1:9091 <user>@<IP_DT> -p <PORT_SSH>
```

Mở whitelist thì xem `transmission/settings.json.example`. Nhớ `pkill transmission-daemon` trước khi sửa.

## Chuyển thư mục tải (nếu đổi đường dẫn)

Nếu data đã tự `mv` bằng tay thì dùng `--find`, không dùng `--move`:

```bash
transmission-remote localhost:9091 -t <id> --find $HOME/storage/music/Japanese
```

## Navidrome

1. Cài binary Navidrome cho Android/ARM, trỏ `MusicFolder` về `~/storage/music/Japanese`.
2. Sau mỗi lần move/xóa folder: Web UI → Rescan.
3. Giữ Android không tối ưu pin Termux + Acquire Wakelock.

## Đổi query nhạc

Đổi query thì sửa `QUERY` trong `nyaa-rss-proxy/fetch_nyaa.py`, không phải repo này. Repo này chỉ đổi `NYAA_FEED_URL` nếu fork proxy.
