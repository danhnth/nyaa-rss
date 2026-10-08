#!/usr/bin/env python3
"""Termux client: keo feed.json tinh tu nyaa-rss-proxy -> nap magnet vao Transmission.

Chi dung stdlib + `transmission-remote`. Thiet ke de chay headless qua cron.
"""
import json
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request

FEED_URL = os.environ.get(
    "NYAA_FEED_URL",
    "https://raw.githubusercontent.com/danhnth/nyaa-rss-proxy/main/feed.json",
)
DOWNLOAD_DIR = os.environ.get(
    "NYAA_DOWNLOAD_DIR",
    os.path.join(os.path.expanduser("~"), "storage", "music", "Japanese"),
)
HISTORY_FILE = os.environ.get(
    "NYAA_HISTORY",
    os.path.join(os.path.expanduser("~"), "scripts", "downloaded_nyaa.txt"),
)
MAX_SIZE_GB = float(os.environ.get("NYAA_MAX_SIZE_GB", "5.0"))
ADD_PAUSED = os.environ.get("NYAA_ADD_PAUSED", "1") == "1"
TR_HOST = os.environ.get("NYAA_TR_HOST", "localhost:9091")

UA = "Mozilla/5.0 (Linux; Android 10; Termux) AppleWebKit/537.36"


def parse_size_gb(size_str: str) -> float:
    """Parse '715.5 MiB' / '1.2 GiB' / '800 MB' -> GB. Khong parse duoc -> 0 (cho qua)."""
    if not size_str:
        return 0.0
    m = re.match(r"\s*([\d.,]+)\s*([KMGT]?i?B)\s*", str(size_str), re.I)
    if not m:
        return 0.0
    num = float(m.group(1).replace(",", ""))
    unit = m.group(2).upper().replace("IB", "B")
    factor = {"B": 1 / 1024**3, "KB": 1 / 1024**2, "MB": 1 / 1024, "GB": 1.0, "TB": 1024.0}
    return num * factor.get(unit, 0.0)


def load_history() -> set:
    if not os.path.exists(HISTORY_FILE):
        return set()
    with open(HISTORY_FILE, encoding="utf-8", errors="ignore") as f:
        return {line.strip() for line in f if line.strip()}


def save_history(guid: str) -> None:
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(guid + "\n")


def fetch_feed() -> dict:
    req = urllib.request.Request(FEED_URL, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def add_magnet(title: str, info_hash: str) -> bool:
    magnet = f"magnet:?xt=urn:btih:{info_hash}&dn={urllib.parse.quote(title)}"
    cmd = ["transmission-remote", TR_HOST, "-w", DOWNLOAD_DIR]
    if ADD_PAUSED:
        cmd.append("--start-paused")
    cmd += ["-a", magnet]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"ADD_FAIL: {title[:80]} :: {res.stderr.strip()}", file=sys.stderr)
        return False
    return True


def main() -> int:
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    try:
        feed = fetch_feed()
    except Exception as e:
        print(f"FEED_FAIL: {e}", file=sys.stderr)
        return 1
    items = feed.get("items", [])
    seen = load_history()
    added, skipped_size, skipped_dup = 0, 0, 0
    for it in items:
        guid = it.get("guid") or it.get("link") or it.get("title")
        if not guid or guid in seen:
            skipped_dup += 1
            continue
        size_gb = parse_size_gb(it.get("size", ""))
        if MAX_SIZE_GB > 0 and size_gb > MAX_SIZE_GB:
            print(f"SKIP_SIZE {size_gb:.1f}G > {MAX_SIZE_GB}G: {it.get('title', '')[:80]}")
            save_history(guid)  # nho da thay de khong log lai lan sau
            skipped_size += 1
            continue
        info_hash = (it.get("infoHash") or "").strip()
        if not info_hash:
            print(f"SKIP_NOHASH: {it.get('title', '')[:80]}", file=sys.stderr)
            continue
        if add_magnet(it.get("title", info_hash), info_hash):
            added += 1
            save_history(guid)
    print(f"done: added={added} skip_size={skipped_size} skip_dup={skipped_dup} total={len(items)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
