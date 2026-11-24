"""Small, configurable report intake service for local development.

For production, deploy behind a managed application server and durable database.
The JSON-file store is intended for local/demo use only.
"""
import json
import os
import re
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HOST = os.getenv("OI_REPORT_HOST", "127.0.0.1")
PORT = int(os.getenv("OI_REPORT_PORT", "8000"))
DATA_DIR = Path(os.getenv("OI_REPORT_DATA_DIR", "data/feedback"))
REQUESTS_FILE = DATA_DIR / "edit_requests.json"
ALLOWED_ORIGINS = {
    origin.strip().rstrip("/")
    for origin in os.getenv("OI_REPORT_ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
    if origin.strip()
}
MAX_BODY_BYTES = 16_384
MAX_REPORTS_IN_MEMORY = 10_000
ISSUE_TYPES = {"competition", "year", "problem_number", "wrong_problem", "other"}

def load_requests():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not REQUESTS_FILE.exists():
        return []
    try:
        with REQUESTS_FILE.open(encoding="utf-8") as file:
            data = json.load(file)
        return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        return []

def save_requests(requests):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    temporary_file = REQUESTS_FILE.with_suffix(".tmp")
    with temporary_file.open("w", encoding="utf-8") as file:
        json.dump(requests, file, indent=2, ensure_ascii=False)
    temporary_file.replace(REQUESTS_FILE)

class ReportHandler(BaseHTTPRequestHandler):
    def send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-store")
        origin = self.headers.get("Origin", "").rstrip("/")
        if origin in ALLOWED_ORIGINS:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        origin = self.headers.get("Origin", "").rstrip("/")
        if origin and origin not in ALLOWED_ORIGINS:
            self.send_json(403, {"ok": False, "error": "Origin not allowed"})
            return
        self.send_response(204)
        if origin:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Max-Age", "600")
        self.end_headers()

    def do_POST(self):
        if self.path != "/api/reports":
            self.send_json(404, {"ok": False, "error": "Not found"})
            return
        origin = self.headers.get("Origin", "").rstrip("/")
        if origin and origin not in ALLOWED_ORIGINS:
            self.send_json(403, {"ok": False, "error": "Origin not allowed"})
            return
        content_type = self.headers.get("Content-Type", "").split(";")[0].strip().lower()
        if content_type != "application/json":
            self.send_json(415, {"ok": False, "error": "Content-Type must be application/json"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = 0
        if length <= 0 or length > MAX_BODY_BYTES:
            self.send_json(413, {"ok": False, "error": "Request body is empty or too large"})
            return
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self.send_json(400, {"ok": False, "error": "Invalid JSON"})
            return
        if not isinstance(payload, dict):
            self.send_json(400, {"ok": False, "error": "Expected a JSON object"})
            return
        fields = {
            "problem_id": 120,
            "current_title": 300,
            "suggested_value": 500,
            "description": 2000,
        }
        cleaned = {}
        for field, maximum in fields.items():
            value = str(payload.get(field, "")).strip()
            if field != "description" and not value:
                self.send_json(400, {"ok": False, "error": f"{field} is required"})
                return
            if len(value) > maximum:
                self.send_json(400, {"ok": False, "error": f"{field} exceeds {maximum} characters"})
                return
            cleaned[field] = value
        issue_type = str(payload.get("issue_type", "")).strip()
        if issue_type not in ISSUE_TYPES:
            self.send_json(400, {"ok": False, "error": "Invalid issue_type"})
            return
        if not re.fullmatch(r"[A-Za-z0-9._:-]{1,120}", cleaned["problem_id"]):
            self.send_json(400, {"ok": False, "error": "Invalid problem_id"})
            return
        requests = load_requests()
        if len(requests) >= MAX_REPORTS_IN_MEMORY:
            self.send_json(503, {"ok": False, "error": "Report storage is full; try again later"})
            return
        report = {
            "id": str(payload.get("id", ""))[:100],
            **cleaned,
            "issue_type": issue_type,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "PENDING",
        }
        requests.append(report)
        try:
            save_requests(requests)
        except OSError:
            self.send_json(500, {"ok": False, "error": "Unable to save report"})
            return
        self.send_json(201, {"ok": True, "report": report})

    def log_message(self, format, *args):
        print("[REPORT SERVER]", format % args)

def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer((HOST, PORT), ReportHandler)
    print(f"Report intake listening on http://{HOST}:{PORT}")
    print(f"Allowed browser origins: {', '.join(sorted(ALLOWED_ORIGINS)) or '(none)'}")
    print(f"Local JSON store: {REQUESTS_FILE}")
    print("Note: use a managed server and durable database for production.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping report server...")
    finally:
        server.server_close()

if __name__ == "__main__":
    main()
