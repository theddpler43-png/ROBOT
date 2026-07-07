import json
import os
import threading
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT, "data")
WEB_DIR = os.path.join(ROOT, "web")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(WEB_DIR, exist_ok=True)

MARKETS_FILE = os.path.join(DATA_DIR, "markets.json")

if not os.path.exists(MARKETS_FILE):
    with open(MARKETS_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {
                "updated": None,
                "markets": []
            },
            f,
            indent=4,
            ensure_ascii=False
        )


class BrowserHandler(SimpleHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)


def start_server():

    server = HTTPServer(("127.0.0.1", 8080), BrowserHandler)

    print("=" * 50)
    print(" Algo Activity Scanner Browser V9")
    print("=" * 50)
    print("Server:")
    print("http://127.0.0.1:8080")
    print("=" * 50)

    server.serve_forever()


if __name__ == "__main__":

    threading.Timer(
        1.0,
        lambda: webbrowser.open("http://127.0.0.1:8080")
    ).start()

    start_server()
