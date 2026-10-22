> **アーカイブ済み (2026-10)** — 更新は終了しました。同じことは [LocalSend](https://localsend.org) でできます。

# LocalDrop

AirDrop-like file transfer between Pixel (Android) and Mac.

## Why?
Quick Share doesn't support Mac. AirDrop doesn't support Android. LocalDrop fills that gap.

## How it works
- Same Wi-Fi network required
- Mac: Chrome extension + Python server
- Android: Native app

## Setup

### Mac
1. Run `python3 server.py`
2. Load `chrome-extension/` in Chrome (Developer mode)

### Android
1. Install the app
2. Open app → tap device → select file → send

## Requirements
- Python 3
- Chrome
- Android 7.0+
- Same Wi-Fi network
