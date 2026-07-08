import asyncio
import json
import os
import threading
import webbrowser
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

from scanner.manager import run_scan

ROOT = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(ROOT, "web")
DATA_DIR = os.path.join(ROOT, "data")
CONFIG_FILE = os.path.join(ROOT, "config.json")

os.makedirs(DATA_DIR, exist_ok=True)

MARKETS = os.path.join(DATA_DIR, "markets.json")

if not os.path.exists(MARKETS):
    with open(MARKETS, "w", encoding="utf-8") as f:
        json.dump(
            {
                "updated": None,
                "status": "empty",
                "count": 0,
                "total": 0,
                "markets": []
            },
            f,
            ensure_ascii=False,
            indent=2
        )


def load_config() -> dict:
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/markets":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()

            with open(MARKETS, "rb") as f:
                self.wfile.write(f.read())

            return

        return super().do_GET()


def browser():
    webbrowser.open("http://127.0.0.1:8080")


def server():
    config = load_config()
    host = config.get("server", {}).get("host", "127.0.0.1")
    port = int(config.get("server", {}).get("port", 8080))

    httpd = ThreadingHTTPServer((host, port), Handler)

    print()
    print("=" * 60)
    print(" Algo Activity Scanner Browser V9")
    print("=" * 60)
    print(f" http://{host}:{port}")
    print("=" * 60)

    httpd.serve_forever()


async def scanner_loop():
    config = load_config()
    pause = int(config.get("scanner", {}).get("scan_pause_seconds", 15))

    while True:
        print()
        print("Starting scan...")
        await run_scan()
        await asyncio.sleep(pause)


async def main():
    threading.Timer(1, browser).start()
    threading.Thread(target=server, daemon=True).start()
    await scanner_loop()


if __name__ == "__main__":
    asyncio.run(main())
