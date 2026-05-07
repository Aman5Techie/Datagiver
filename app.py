from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs

HOST = "0.0.0.0"
PORT = 8000
DATA_FILE = Path(__file__).with_name("messages.txt")
MAX_MESSAGE_LENGTH = 2000


def save_message(raw_message: str) -> None:
    message = raw_message.strip()
    if not message:
        return
    message = message[:MAX_MESSAGE_LENGTH]
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with DATA_FILE.open("a", encoding="utf-8") as file:
        file.write(f"{timestamp}\t{message}\n")


def load_messages() -> list[tuple[str, str]]:
    if not DATA_FILE.exists():
        return []

    messages: list[tuple[str, str]] = []
    for line in DATA_FILE.read_text(encoding="utf-8").splitlines():
        if "\t" not in line:
            continue
        timestamp, message = line.split("\t", 1)
        messages.append((timestamp, message))
    return messages[-100:]


def render_home_page() -> bytes:
    items = "\n".join(
        f"<li><div>{escape(message)}</div><small>{escape(timestamp)} UTC</small></li>"
        for timestamp, message in reversed(load_messages())
    )

    if not items:
        items = "<li><em>No messages yet. Be the first to post.</em></li>"

    html = f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Datagiver Wall</title>
  <style>
    body {{ font-family: Arial, sans-serif; max-width: 780px; margin: 2rem auto; padding: 0 1rem; }}
    textarea {{ width: 100%; min-height: 120px; }}
    button {{ margin-top: 0.6rem; padding: 0.6rem 1rem; cursor: pointer; }}
    ul {{ list-style: none; padding: 0; }}
    li {{ border: 1px solid #ddd; border-radius: 8px; margin: 0.75rem 0; padding: 0.75rem; }}
    small {{ color: #555; }}
  </style>
</head>
<body>
  <h1>Datagiver Wall</h1>
  <p>Write a message once. Everyone who opens this site can see it.</p>
  <form method=\"post\" action=\"/submit\">
    <textarea name=\"content\" maxlength=\"{MAX_MESSAGE_LENGTH}\" placeholder=\"Write something...\" required></textarea>
    <br />
    <button type=\"submit\">Post</button>
  </form>
  <h2>Shared messages</h2>
  <ul>
    {items}
  </ul>
</body>
</html>
"""
    return html.encode("utf-8")


class MessageBoardHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        if self.path not in {"/", "/index.html"}:
            self.send_error(HTTPStatus.NOT_FOUND, "Not Found")
            return

        body = render_home_page()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/submit":
            self.send_error(HTTPStatus.NOT_FOUND, "Not Found")
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        raw_payload = self.rfile.read(content_length).decode("utf-8", errors="ignore")
        parsed_payload = parse_qs(raw_payload)
        save_message(parsed_payload.get("content", [""])[0])

        self.send_response(HTTPStatus.SEE_OTHER)
        self.send_header("Location", "/")
        self.end_headers()

    def log_message(self, format: str, *args: object) -> None:
        return


def run() -> None:
    server = ThreadingHTTPServer((HOST, PORT), MessageBoardHandler)
    print(f"Server running at http://127.0.0.1:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    run()
