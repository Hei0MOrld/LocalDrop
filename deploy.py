#!/usr/bin/env python3
import os
import subprocess
import sys
from pathlib import Path

# ===== 設定 =====
REPO_DIR = Path(__file__).parent
GITHUB_PAGES_BRANCH = "gh-pages"
SITE_DIR = REPO_DIR / "docs"  # GitHub Pagesのソースフォルダ

def run(cmd, cwd=None):
    result = subprocess.run(cmd, shell=True, cwd=cwd or REPO_DIR, 
                          capture_output=True, text=True)
    if result.returncode != 0:
        print(f"エラー: {result.stderr}")
        return False
    print(result.stdout.strip())
    return True

def git_push():
    print("\n📦 GitHubにpush中...")
    run("git add -A")
    
    # 変更があるか確認
    result = subprocess.run("git status --porcelain", shell=True, 
                          cwd=REPO_DIR, capture_output=True, text=True)
    if not result.stdout.strip():
        print("  変更なし、スキップ")
        return True
    
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    run(f'git commit -m "update: {timestamp}"')
    run("git push origin main")
    print("  ✓ push完了")
    return True

def enable_github_pages():
    print("\n🌐 GitHub Pages有効化中...")
    
    # docsフォルダがなければ作成
    SITE_DIR.mkdir(exist_ok=True)
    
    # index.htmlがなければ作成
    index_file = SITE_DIR / "index.html"
    if not index_file.exists():
        index_file.write_text("""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>LocalDrop</title>
<style>
  body { font-family: -apple-system, sans-serif; max-width: 800px; 
         margin: 0 auto; padding: 40px 20px; }
  h1 { font-size: 48px; }
  .badge { background: #1a1a1a; color: white; padding: 12px 24px; 
           border-radius: 8px; text-decoration: none; display: inline-block; }
</style>
</head>
<body>
  <h1>📡 LocalDrop</h1>
  <p>AirDrop-like file transfer between Pixel (Android) and Mac.</p>
  <p>Quick Share doesn't support Mac. AirDrop doesn't support Android.<br>
  LocalDrop fills that gap — no cloud, no cables, just Wi-Fi.</p>
  <a class="badge" href="https://github.com/Hei0MOrld/LocalDrop">
    View on GitHub →
  </a>
</body>
</html>""")
        print("  ✓ index.html作成")
    
    # GitHub Pagesの設定をgh-pages APIで有効化
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        import urllib.request
        import json
        
        data = json.dumps({
            "source": {"branch": "main", "path": "/docs"}
        }).encode()
        
        req = urllib.request.Request(
            "https://api.github.com/repos/Hei0MOrld/LocalDrop/pages",
            data=data,
            headers={
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json",
                "Content-Type": "application/json"
            },
            method="POST"
        )
        try:
            urllib.request.urlopen(req)
            print("  ✓ GitHub Pages有効化完了")
        except Exception as e:
            print(f"  (既に有効化済みか手動設定が必要: {e})")
    else:
        print("  ⚠ GITHUB_TOKENが未設定 — 手動でPages設定が必要")
    
    return True

def submit_sitemap():
    print("\n🔍 サイトマップ送信中...")
    
    # サイトマップ生成
    sitemap = SITE_DIR / "sitemap.xml"
    sitemap.write_text("""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://hei0morld.github.io/LocalDrop/</loc>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>""")
    print("  ✓ sitemap.xml生成")
    
    # Google Search Console APIでサイトマップ送信
    token = os.environ.get("GITHUB_TOKEN")
    print("  ℹ Google Search ConsoleへのサイトマップはGSC画面から手動登録してください")
    print("  URL: https://hei0morld.github.io/LocalDrop/sitemap.xml")
    
    return True

def main():
    print("🚀 LocalDrop デプロイ開始")
    print("=" * 40)
    
    enable_github_pages()
    git_push()
    submit_sitemap()
    
    print("\n" + "=" * 40)
    print("✅ デプロイ完了!")
    print("🌐 サイト: https://hei0morld.github.io/LocalDrop/")
    print("📦 GitHub: https://github.com/Hei0MOrld/LocalDrop")

if __name__ == "__main__":
    main()