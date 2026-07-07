import asyncio
import json
import os
import threading
import webbrowser
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

from scanner.manager import run_scan

ROOT = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(ROOT, "web")
DATA_DIR = os.path.join(ROOT, "data")

os.makedirs(DATA_DIR, exist_ok=True)

MARKETS = os.path.join(DATA_DIR, "markets.json")

if not os.path.exists(MARKETS):
    with open(MARKETS, "w", encoding="utf-8") as f:
        json.dump(
            {
                "count": 0,
                "markets": []
            },
            f,
            ensure_ascii=False,
            indent=2
        )


class Handler(SimpleHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)


def browser():

    webbrowser.open("http://127.0.0.1:8080")


def server():

    httpd = ThreadingHTTPServer(
        ("127.0.0.1", 8080),
        Handler
    )

    print()

    print("=" * 60)
    print(" Algo Activity Scanner Browser V9")
    print("=" * 60)
    print(" http://127.0.0.1:8080")
    print("=" * 60)

    httpd.serve_forever()


async def scanner_loop():

    while True:

        print()

        print("Starting scan...")

        await run_scan()

        print("Scan complete.")

        await asyncio.sleep(5)


async def main():

    threading.Timer(
        1,
        browser
    ).start()

    threading.Thread(
        target=server,
        daemon=True
    ).start()

    await scanner_loop()


if __name__ == "__main__":

    asyncio.run(main())
