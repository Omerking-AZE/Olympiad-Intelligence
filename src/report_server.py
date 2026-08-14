import json
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


HOST = "127.0.0.1"
PORT = 8000

DATA_DIR = Path("data/feedback")
REQUESTS_FILE = DATA_DIR / "edit_requests.json"


def load_requests():
    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not REQUESTS_FILE.exists():
        return []

    try:
        with open(
            REQUESTS_FILE,
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        return data if isinstance(data, list) else []

    except (
        OSError,
        json.JSONDecodeError,
    ):
        return []


def save_requests(requests):
    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_file = REQUESTS_FILE.with_suffix(
        ".tmp"
    )

    with open(
        temporary_file,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            requests,
            file,
            indent=2,
            ensure_ascii=False,
        )

    temporary_file.replace(
        REQUESTS_FILE
    )


class ReportHandler(BaseHTTPRequestHandler):

    def send_json(
        self,
        status,
        payload,
    ):
        body = json.dumps(
            payload,
            ensure_ascii=False,
        ).encode("utf-8")

        self.send_response(status)

        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8",
        )

        self.send_header(
            "Content-Length",
            str(len(body)),
        )

        self.send_header(
            "Access-Control-Allow-Origin",
            "http://localhost:5173",
        )

        self.send_header(
            "Access-Control-Allow-Methods",
            "POST, OPTIONS",
        )

        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type",
        )

        self.end_headers()

        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)

        self.send_header(
            "Access-Control-Allow-Origin",
            "http://localhost:5173",
        )

        self.send_header(
            "Access-Control-Allow-Methods",
            "POST, OPTIONS",
        )

        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type",
        )

        self.end_headers()

    def do_POST(self):
        if self.path != "/api/reports":
            self.send_json(
                404,
                {
                    "ok": False,
                    "error": "Not found",
                },
            )
            return

        try:
            content_length = int(
                self.headers.get(
                    "Content-Length",
                    "0",
                )
            )

            raw_body = self.rfile.read(
                content_length
            )

            payload = json.loads(
                raw_body.decode("utf-8")
            )

        except (
            ValueError,
            json.JSONDecodeError,
        ):
            self.send_json(
                400,
                {
                    "ok": False,
                    "error": "Invalid JSON",
                },
            )
            return

        required = [
            "problem_id",
            "current_title",
            "issue_type",
            "suggested_value",
        ]

        missing = [
            field
            for field in required
            if not str(
                payload.get(field, "")
            ).strip()
        ]

        if missing:
            self.send_json(
                400,
                {
                    "ok": False,
                    "error": "Missing fields",
                    "fields": missing,
                },
            )
            return

        report = {
            "id": payload.get(
                "id"
            ),
            "problem_id": str(
                payload["problem_id"]
            ).strip(),
            "current_title": str(
                payload["current_title"]
            ).strip(),
            "issue_type": str(
                payload["issue_type"]
            ).strip(),
            "suggested_value": str(
                payload["suggested_value"]
            ).strip(),
            "description": str(
                payload.get(
                    "description",
                    "",
                )
            ).strip(),
            "created_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "status": "PENDING",
        }

        requests = load_requests()

        requests.append(
            report
        )

        save_requests(
            requests
        )

        self.send_json(
            201,
            {
                "ok": True,
                "report": report,
            },
        )

    def log_message(
        self,
        format,
        *args,
    ):
        print(
            "[REPORT SERVER]",
            format % args,
        )


def main():
    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    server = ThreadingHTTPServer(
        (HOST, PORT),
        ReportHandler,
    )

    print("=" * 60)
    print("OLYMPIAD INTELLIGENCE - REPORT SERVER")
    print("=" * 60)
    print()
    print(
        f"Listening on http://{HOST}:{PORT}"
    )
    print(
        f"Saving reports to {REQUESTS_FILE}"
    )
    print()
    print("Press Ctrl+C to stop.")
    print("=" * 60)

    try:
        server.serve_forever()

    except KeyboardInterrupt:
        print(
            "\nStopping report server..."
        )

    finally:
        server.server_close()


if __name__ == "__main__":
    main()