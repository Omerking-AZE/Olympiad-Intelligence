"""Local account, personalized rating, and problem-bank API for Olympiad Intelligence.

Development: python src/app_server.py
The Vite dev server proxies /api requests to this service.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import math
import os
import re
import secrets
import sqlite3
import time
from datetime import datetime, timezone
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from platform_store import DATA_DIR, DB_PATH, IMAGE_DIR, SKILL_KEYS, connect, ensure_session_secret, init_db

HOST = os.getenv("OI_HOST", "127.0.0.1")
PORT = int(os.getenv("OI_PORT", "8000"))
SESSION_COOKIE = "oi_session"
SESSION_SECONDS = 7 * 24 * 60 * 60
MAX_BODY_BYTES = 64 * 1024
SECRET = ensure_session_secret()
ALLOWED_ORIGINS = {
    item.strip().rstrip("/")
    for item in os.getenv(
        "OI_ALLOWED_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if item.strip()
}


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def b64url(data):
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def make_session(user_id):
    payload = json.dumps(
        {"uid": int(user_id), "exp": int(time.time()) + SESSION_SECONDS},
        separators=(",", ":"),
    ).encode("utf-8")
    body = b64url(payload)
    signature = b64url(hmac.new(SECRET, body.encode("ascii"), hashlib.sha256).digest())
    return body + "." + signature


def read_session(token):
    try:
        body, signature = token.split(".", 1)
        expected = b64url(hmac.new(SECRET, body.encode("ascii"), hashlib.sha256).digest())
        if not hmac.compare_digest(signature, expected):
            return None
        payload = json.loads(base64.urlsafe_b64decode(body + "=" * (-len(body) % 4)))
        if int(payload.get("exp", 0)) < int(time.time()):
            return None
        return int(payload["uid"])
    except (ValueError, TypeError, KeyError, json.JSONDecodeError):
        return None


def password_digest(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 310_000)


def rating_tier(rating):
    if rating >= 95:
        return "ICON"
    if rating >= 90:
        return "ELITE"
    if rating >= 85:
        return "SPECIAL"
    if rating >= 80:
        return "RARE"
    if rating >= 70:
        return "SILVER"
    return "BRONZE"


def skill_for_domain(domain, problem_type=None):
    value = str(domain or "").lower()
    if "geometry" in value:
        return "geometry"
    if "number" in value:
        return "number_theory"
    if "discrete" in value or "combinator" in value:
        return "discrete_mathematics"
    if "algebra" in value:
        return "algebra"
    if "proof" in str(problem_type or "").lower():
        return "proof"
    return "reasoning"


def safe_problem(row, user_id, db):
    try:
        topics = json.loads(row["topics_json"] or "[]")
    except (TypeError, json.JSONDecodeError):
        topics = []
    try:
        image_names = json.loads(row["images_json"] or "[]")
    except (TypeError, json.JSONDecodeError):
        image_names = []
    statement = row["problem_text_en"] or row["problem_text_original"] or ""
    statement = re.sub(r"!\\[[^\\]]*\\]\\(attached_image_\\d+\\.png\\)", "", statement).strip()
    is_english = bool(row["problem_text_en"])
    latest = db.execute(
        "SELECT result FROM attempts WHERE user_id=? AND problem_id=? ORDER BY id DESC LIMIT 1",
        (user_id, row["problem_id"]),
    ).fetchone()
    return {
        "id": row["problem_id"],
        "problem_id": row["problem_id"],
        "title": row["title"] or "Olympiad problem",
        "competition": row["competition"],
        "country": row["country"],
        "language": row["language"],
        "domain": row["domain"] or "Mathematics",
        "target_domain": row["domain"] or "Mathematics",
        "problem_type": row["problem_type"] or "Olympiad problem",
        "problem_text": statement,
        "problem_markdown": statement,
        "difficulty_score": round(float(row["difficulty_score"] or 50), 1),
        "difficulty_fit": None,
        "student_skill": None,
        "adaptive_score": None,
        "translation_status": row["translation_status"],
        "display_language": "English" if is_english else row["language"],
        "is_machine_translated": row["translation_status"] == "machine_translated_review_needed",
        "images": ["/api/images/" + name for name in image_names],
        "topics": topics,
        "last_result": latest["result"] if latest else None,
        "final_answer": row["final_answer"],
        "source": "MathNet",
        "source_booklet": row["source_booklet"],
        "booklet_source": row["booklet_source"],
    }


def profile_payload(user_id, db):
    user = db.execute(
        "SELECT id, email, display_name, created_at FROM users WHERE id=?",
        (user_id,),
    ).fetchone()
    if not user:
        return None

    ratings = {key: 55.0 for key in SKILL_KEYS}
    attempts_by_skill = {key: 0 for key in SKILL_KEYS}
    for row in db.execute(
        "SELECT skill_key, rating, attempts FROM skill_ratings WHERE user_id=?",
        (user_id,),
    ):
        if row["skill_key"] in ratings:
            ratings[row["skill_key"]] = float(row["rating"])
            attempts_by_skill[row["skill_key"]] = int(row["attempts"])

    total = db.execute(
        "SELECT COUNT(*) AS attempts, SUM(CASE WHEN result='solved' THEN 1 ELSE 0 END) AS solved "
        "FROM attempts WHERE user_id=?",
        (user_id,),
    ).fetchone()
    overall = round(sum(ratings.values()) / len(SKILL_KEYS))
    measured = [key for key in SKILL_KEYS if attempts_by_skill[key] > 0]
    strongest = sorted(measured, key=lambda key: ratings[key], reverse=True)[:3]
    weakest = sorted(measured, key=lambda key: ratings[key])[:4]
    unknown = [key for key in SKILL_KEYS if attempts_by_skill[key] == 0]

    return {
        "student_id": str(user["id"]),
        "student_name": user["display_name"],
        "email": user["email"],
        "created_at": user["created_at"],
        "is_demo": False,
        "overall_rating": overall,
        "tier": rating_tier(overall),
        "problems_attempted": int(total["attempts"] or 0),
        "problems_solved": int(total["solved"] or 0),
        "achievement": "Build your record one problem at a time",
        "strongest_skills": strongest,
        "high_priority_weaknesses": weakest[:2],
        "medium_priority_weaknesses": weakest[2:],
        "unknown_skills": unknown,
        "skill_ratings": {key: round(value) for key, value in ratings.items()},
        "skill_attempts": attempts_by_skill,
    }


class PlatformHandler(BaseHTTPRequestHandler):
    server_version = "OlympiadIntelligence/1.0"

    def send_json(self, status, payload, extra_headers=None):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Referrer-Policy", "same-origin")
        origin = self.headers.get("Origin", "").rstrip("/")
        if origin in ALLOWED_ORIGINS:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
        for key, value in (extra_headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)

    def send_cookie(self, token, clear=False):
        secure = "; Secure" if os.getenv("OI_COOKIE_SECURE", "0") == "1" else ""
        if clear:
            value = f"{SESSION_COOKIE}=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0{secure}"
        else:
            value = (
                f"{SESSION_COOKIE}={token}; Path=/; HttpOnly; SameSite=Lax; "
                f"Max-Age={SESSION_SECONDS}{secure}"
            )
        return {"Set-Cookie": value}

    def read_body(self):
        content_type = self.headers.get("Content-Type", "").split(";")[0].strip().lower()
        if content_type != "application/json":
            raise ValueError("Content-Type must be application/json")
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError as error:
            raise ValueError("Invalid content length") from error
        if length <= 0 or length > MAX_BODY_BYTES:
            raise ValueError("Request body is empty or too large")
        try:
            data = json.loads(self.rfile.read(length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise ValueError("Invalid JSON body") from error
        if not isinstance(data, dict):
            raise ValueError("Expected a JSON object")
        return data

    def user_id(self):
        cookie = SimpleCookie()
        try:
            cookie.load(self.headers.get("Cookie", ""))
            morsel = cookie.get(SESSION_COOKIE)
            return read_session(morsel.value) if morsel else None
        except Exception:
            return None

    def require_user(self):
        user_id = self.user_id()
        if not user_id:
            self.send_json(401, {"ok": False, "error": "Please sign in to continue."})
            return None
        return user_id

    def origin_allowed(self):
        origin = self.headers.get("Origin", "").rstrip("/")
        return not origin or origin in ALLOWED_ORIGINS

    def do_OPTIONS(self):
        if not self.origin_allowed():
            self.send_json(403, {"ok": False, "error": "Origin not allowed"})
            return
        self.send_response(204)
        origin = self.headers.get("Origin", "").rstrip("/")
        if origin in ALLOWED_ORIGINS:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Credentials", "true")
        self.send_header("Access-Control-Max-Age", "600")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        if path == "/api/health":
            with connect() as db:
                count = db.execute("SELECT COUNT(*) FROM problems").fetchone()[0]
            self.send_json(200, {"ok": True, "problems": count, "database": str(DB_PATH.name)})
            return

        if path.startswith("/api/images/"):
            name = unquote(path.rsplit("/", 1)[-1])
            if not re.fullmatch(r"[A-Za-z0-9_-]{1,90}\.png", name):
                self.send_json(404, {"ok": False, "error": "Image not found"})
                return
            target = (IMAGE_DIR / name).resolve()
            if target.parent != IMAGE_DIR.resolve() or not target.is_file():
                self.send_json(404, {"ok": False, "error": "Image not found"})
                return
            content = target.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "public, max-age=86400")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(content)
            return

        user_id = self.require_user()
        if user_id is None:
            return

        if path == "/api/me":
            with connect() as db:
                user = db.execute(
                    "SELECT id, email, display_name FROM users WHERE id=?",
                    (user_id,),
                ).fetchone()
            if not user:
                self.send_json(401, {"ok": False, "error": "Session expired."})
            else:
                self.send_json(200, {"id": user["id"], "email": user["email"], "display_name": user["display_name"]})
            return

        if path == "/api/profile":
            with connect() as db:
                payload = profile_payload(user_id, db)
            if payload:
                self.send_json(200, payload)
            else:
                self.send_json(404, {"ok": False, "error": "Profile not found."})
            return

        if path == "/api/progression":
            with connect() as db:
                rows = db.execute(
                    """
                    SELECT rating_after, created_at, id
                    FROM attempts WHERE user_id=?
                    ORDER BY id DESC LIMIT 25
                    """,
                    (user_id,),
                ).fetchall()
            data = [
                {
                    "id": row["id"],
                    "date": row["created_at"][:10],
                    "rating": round(row["rating_after"]),
                    "attempts": index + 1,
                }
                for index, row in enumerate(reversed(rows))
            ]
            self.send_json(200, data)
            return

        if path == "/api/problems":
            params = parse_qs(parsed.query)
            query = (params.get("search", [""])[0] or "").strip()[:160]
            domain = (params.get("domain", [""])[0] or "").strip()[:80]
            language = (params.get("language", [""])[0] or "").strip()[:40]
            try:
                limit = min(max(int(params.get("limit", ["24"])[0]), 1), 50)
                offset = min(max(int(params.get("offset", ["0"])[0]), 0), 1000000)
            except ValueError:
                self.send_json(400, {"ok": False, "error": "Invalid pagination values."})
                return
            unseen = params.get("unseen", ["1"])[0] != "0"
            clauses = []
            values = []
            if query:
                pattern = f"%{query}%"
                clauses.append(
                    "(problem_text_en LIKE ? OR problem_text_original LIKE ? OR competition LIKE ? "
                    "OR country LIKE ? OR title LIKE ?)"
                )
                values.extend([pattern] * 5)
            if domain:
                clauses.append("domain LIKE ?")
                values.append(f"%{domain}%")
            if language:
                clauses.append("language LIKE ?")
                values.append(f"%{language}%")
            if unseen:
                clauses.append(
                    "NOT EXISTS (SELECT 1 FROM attempts a WHERE a.user_id=? AND a.problem_id=problems.problem_id)"
                )
                values.append(user_id)
            where = " WHERE " + " AND ".join(clauses) if clauses else ""
            with connect() as db:
                total = db.execute("SELECT COUNT(*) FROM problems" + where, values).fetchone()[0]
                rows = db.execute(
                    """
                    SELECT * FROM problems
                    """ + where + """
                    ORDER BY abs((rowid * 1103515245 + ?) % 2147483647), rowid
                    LIMIT ? OFFSET ?
                    """,
                    [*values, int(user_id) * 12345, limit, offset],
                ).fetchall()
                results = [safe_problem(row, user_id, db) for row in rows]
            self.send_json(200, {"problems": results, "total": total, "limit": limit, "offset": offset, "unseen": unseen})
            return

        self.send_json(404, {"ok": False, "error": "Not found"})

    def do_POST(self):
        if not self.origin_allowed():
            self.send_json(403, {"ok": False, "error": "Origin not allowed"})
            return
        path = urlparse(self.path).path
        try:
            payload = self.read_body()
        except ValueError as error:
            self.send_json(400, {"ok": False, "error": str(error)})
            return

        if path == "/api/auth/signup":
            name = str(payload.get("name", "")).strip()
            email = str(payload.get("email", "")).strip().lower()
            password = str(payload.get("password", ""))
            if len(name) < 2 or len(name) > 60:
                self.send_json(400, {"ok": False, "error": "Name must be between 2 and 60 characters."})
                return
            if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email) or len(email) > 254:
                self.send_json(400, {"ok": False, "error": "Enter a valid email address."})
                return
            if len(password) < 10 or len(password) > 200:
                self.send_json(400, {"ok": False, "error": "Use a password with at least 10 characters."})
                return
            salt = secrets.token_bytes(16)
            digest = password_digest(password, salt)
            with connect() as db:
                try:
                    cursor = db.execute(
                        "INSERT INTO users(email, display_name, password_salt, password_hash, created_at) VALUES (?, ?, ?, ?, ?)",
                        (email, name, salt, digest, now_iso()),
                    )
                    user_id = cursor.lastrowid
                    db.executemany(
                        "INSERT INTO skill_ratings(user_id, skill_key, rating) VALUES (?, ?, 55)",
                        [(user_id, skill) for skill in SKILL_KEYS],
                    )
                except sqlite3.IntegrityError:
                    self.send_json(409, {"ok": False, "error": "An account with that email already exists."})
                    return
            self.send_json(
                201,
                {"ok": True, "user": {"id": user_id, "email": email, "display_name": name}},
                self.send_cookie(make_session(user_id)),
            )
            return

        if path == "/api/auth/login":
            email = str(payload.get("email", "")).strip().lower()
            password = str(payload.get("password", ""))
            with connect() as db:
                user = db.execute(
                    "SELECT id, email, display_name, password_salt, password_hash FROM users WHERE email=?",
                    (email,),
                ).fetchone()
            if not user or not hmac.compare_digest(
                password_digest(password, user["password_salt"]),
                user["password_hash"],
            ):
                self.send_json(401, {"ok": False, "error": "Email or password is incorrect."})
                return
            self.send_json(
                200,
                {"ok": True, "user": {"id": user["id"], "email": user["email"], "display_name": user["display_name"]}},
                self.send_cookie(make_session(user["id"])),
            )
            return

        if path == "/api/auth/logout":
            self.send_json(200, {"ok": True}, self.send_cookie("", clear=True))
            return

        if path == "/api/attempts":
            user_id = self.require_user()
            if user_id is None:
                return
            problem_id = str(payload.get("problem_id", "")).strip()
            result = str(payload.get("result", "")).strip().lower()
            if not problem_id or result not in {"solved", "attempted"}:
                self.send_json(400, {"ok": False, "error": "Choose a valid problem and result."})
                return
            with connect() as db:
                existing_attempt = db.execute(
                    "SELECT id FROM attempts WHERE user_id=? AND problem_id=?",
                    (user_id, problem_id),
                ).fetchone()
                if existing_attempt:
                    self.send_json(409, {"ok": False, "error": "You have already recorded this problem."})
                    return
                problem = db.execute(
                    "SELECT domain, problem_type, difficulty_score FROM problems WHERE problem_id=?",
                    (problem_id,),
                ).fetchone()
                if not problem:
                    self.send_json(404, {"ok": False, "error": "Problem not found."})
                    return
                skill = skill_for_domain(problem["domain"], problem["problem_type"])
                current = db.execute(
                    "SELECT rating, attempts FROM skill_ratings WHERE user_id=? AND skill_key=?",
                    (user_id, skill),
                ).fetchone()
                if not current:
                    current_rating, prior_attempts = 55.0, 0
                    db.execute(
                        "INSERT INTO skill_ratings(user_id, skill_key, rating, attempts, solved) VALUES (?, ?, 55, 0, 0)",
                        (user_id, skill),
                    )
                else:
                    current_rating = float(current["rating"])
                    prior_attempts = int(current["attempts"])
                difficulty = min(max(float(problem["difficulty_score"] or 50), 1), 99)
                expected = 1.0 / (1.0 + math.pow(10.0, (difficulty - current_rating) / 20.0))
                outcome = 1.0 if result == "solved" else 0.5
                k_factor = max(4.0, 14.0 / math.sqrt(prior_attempts + 1))
                updated = min(99.0, max(25.0, current_rating + k_factor * (outcome - expected)))
                db.execute(
                    """
                    UPDATE skill_ratings
                    SET rating=?, attempts=attempts+1,
                        solved=solved+?
                    WHERE user_id=? AND skill_key=?
                    """,
                    (updated, 1 if result == "solved" else 0, user_id, skill),
                )
                db.execute(
                    """
                    INSERT INTO attempts(user_id, problem_id, result, skill_key, rating_after, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (user_id, problem_id, result, skill, updated, now_iso()),
                )
                db.commit()
                profile = profile_payload(user_id, db)
            self.send_json(201, {"ok": True, "skill": skill, "rating": updated, "profile": profile})
            return

        if path == "/api/reports":
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
            if issue_type not in {"competition", "year", "problem_number", "wrong_problem", "other"}:
                self.send_json(400, {"ok": False, "error": "Invalid issue_type"})
                return
            if not re.fullmatch(r"[A-Za-z0-9._:-]{1,120}", cleaned["problem_id"]):
                self.send_json(400, {"ok": False, "error": "Invalid problem_id"})
                return
            feedback_dir = DATA_DIR / "feedback"
            feedback_dir.mkdir(parents=True, exist_ok=True)
            requests_file = feedback_dir / "edit_requests.json"
            try:
                reports = json.loads(requests_file.read_text(encoding="utf-8")) if requests_file.exists() else []
                if not isinstance(reports, list) or len(reports) >= 10000:
                    reports = []
                report = {
                    **cleaned,
                    "issue_type": issue_type,
                    "created_at": now_iso(),
                    "status": "PENDING",
                }
                reports.append(report)
                temporary = requests_file.with_suffix(".tmp")
                temporary.write_text(json.dumps(reports, ensure_ascii=False, indent=2), encoding="utf-8")
                temporary.replace(requests_file)
            except (OSError, json.JSONDecodeError):
                self.send_json(500, {"ok": False, "error": "Unable to save report"})
                return
            self.send_json(201, {"ok": True, "report": report})
            return

        self.send_json(404, {"ok": False, "error": "Not found"})

    def log_message(self, format_string, *args):
        print("[OI API]", format_string % args)


def main():
    init_db()
    server = ThreadingHTTPServer((HOST, PORT), PlatformHandler)
    print(f"Olympiad Intelligence API listening on http://{HOST}:{PORT}")
    print(f"SQLite database: {DB_PATH}")
    print("Local development only: add HTTPS, a production database, password reset, and rate limiting before public deployment.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Olympiad Intelligence API.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
