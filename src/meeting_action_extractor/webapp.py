"""Serve the local browser demo and connect review requests to the extractors."""

import json
import mimetypes
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict
from urllib.parse import urlparse

from .openrouter import extract_with_openrouter
from .rules import extract_with_rules
from .validation import validate_evidence


STATIC_DIR = Path(__file__).with_name("web")
MAX_TRANSCRIPT_BYTES = 200_000


def extract_payload(transcript: str, method: str) -> Dict[str, Any]:
    transcript = transcript.strip()
    if not transcript:
        raise ValueError("Paste a meeting transcript before running the extractor.")
    if len(transcript.encode("utf-8")) > MAX_TRANSCRIPT_BYTES:
        raise ValueError("The transcript is too large for this demonstration.")
    if method == "rules":
        items = extract_with_rules(transcript)
        metadata: Dict[str, Any] = {"method": "rules", "version": "v1"}
    elif method == "openrouter":
        items, metadata = extract_with_openrouter(transcript)
    else:
        raise ValueError("Unknown extraction method.")

    return {
        "metadata": metadata,
        "action_items": [item.to_dict() for item in items],
        "validation": validate_evidence(items, transcript),
    }


class DemoHandler(BaseHTTPRequestHandler):
    server_version = "MeetingActionDemo/1.0"

    def _json(self, status: int, payload: Dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _static(self, relative_path: str) -> None:
        requested = (STATIC_DIR / relative_path).resolve()
        if STATIC_DIR.resolve() not in requested.parents or not requested.is_file():
            self.send_error(404)
            return
        body = requested.read_bytes()
        content_type = mimetypes.guess_type(requested.name)[0] or "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", content_type + ("; charset=utf-8" if content_type.startswith("text/") else ""))
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/health":
            self._json(200, {"status": "ok"})
            return
        files = {"/": "index.html", "/styles.css": "styles.css", "/app.js": "app.js"}
        if path in files:
            self._static(files[path])
            return
        self.send_error(404)

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/extract":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > MAX_TRANSCRIPT_BYTES + 10_000:
                raise ValueError("Invalid request size.")
            request = json.loads(self.rfile.read(length).decode("utf-8"))
            payload = extract_payload(str(request.get("transcript", "")), str(request.get("method", "openrouter")))
            self._json(200, payload)
        except (ValueError, json.JSONDecodeError) as exc:
            self._json(400, {"error": str(exc)})
        except Exception as exc:
            self._json(500, {"error": str(exc)})

    def log_message(self, format: str, *args: Any) -> None:
        print("[web] " + format % args)


def serve(host: str = "127.0.0.1", port: int = 8000, open_browser: bool = False) -> None:
    server = ThreadingHTTPServer((host, port), DemoHandler)
    url = f"http://{host}:{port}"
    print(f"Meeting Action-Item Extractor demo: {url}")
    print("Press Control-C to stop the server.")
    if open_browser:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDemo stopped.")
    finally:
        server.server_close()
