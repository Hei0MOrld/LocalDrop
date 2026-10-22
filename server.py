#!/usr/bin/env python3
import os
import socket
import threading
from pathlib import Path

PORT = 39877
SAVE_DIR = Path.home() / "Downloads" / "LocalDrop-received"
SAVE_DIR.mkdir(exist_ok=True)

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()

def handle_client(conn, addr):
    try:
        # ファイル名の長さを読む（2バイト）
        name_len_bytes = conn.recv(2)
        if not name_len_bytes or len(name_len_bytes) < 2:
            return
        name_len = int.from_bytes(name_len_bytes, 'big')

        # ファイル名を読む
        filename = conn.recv(name_len).decode('utf-8')

        # ファイルサイズを読む（8バイト）
        size_bytes = b''
        while len(size_bytes) < 8:
            chunk = conn.recv(8 - len(size_bytes))
            if not chunk:
                return
            size_bytes += chunk
        file_size = int.from_bytes(size_bytes, 'big')

        # ファイルデータを読む
        data = b''
        while len(data) < file_size:
            chunk = conn.recv(min(4096, file_size - len(data)))
            if not chunk:
                break
            data += chunk

        # 送られてきた名前からフォルダ部分を捨てる(../ で保存先の外に書かれるのを防ぐ)
        filename = Path(filename.replace('\\', '/')).name
        if filename in ('', '.', '..'):
            print("  受信拒否: 不正なファイル名")
            return
        save_path = SAVE_DIR / filename
        with open(save_path, 'wb') as f:
            f.write(data)

        print(f"  受信完了: {filename} ({file_size} bytes) → {save_path}")

    except Exception as e:
        print(f"  受信エラー: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    local_ip = get_local_ip()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", PORT))
    server.listen(5)

    print(f"LocalDrop サーバー起動")
    print(f"  IP: {local_ip}")
    print(f"  ポート: {PORT}")
    print(f"  保存先: {SAVE_DIR}")
    print(f"  Ctrl+C で停止")

    try:
        while True:
            conn, addr = server.accept()
            print(f"  接続: {addr[0]}")
            t = threading.Thread(target=handle_client, args=(conn, addr))
            t.daemon = True
            t.start()
    except KeyboardInterrupt:
        print("\n停止しました")
    finally:
        server.close()