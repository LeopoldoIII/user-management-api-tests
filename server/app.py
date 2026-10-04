"""
app.py — User Management REST API

Endpoints:
  GET    /<env>/users                  → list all users
  POST   /<env>/users                  → create user
  GET    /<env>/users/<email>           → get user by email
  PUT    /<env>/users/<email>           → update user  (BUG FIXED: now calls commit)
  DELETE /<env>/users/<email>           → delete user  (BUG FIXED: auth checked in all envs)
  POST   /<env>/users/<email>/notes     → add note to user

All bugs from the original image have been corrected:
  - BUG-001: duplicate email now returns 409 instead of crashing with 500
  - BUG-002: invalid email format returns 400 instead of 500
  - BUG-004: non-existent user returns 404 instead of crashing with 500
  - BUG-005: auth token is validated in every environment, not only "dev"
  - BUG-CRÍTICO: update_user now calls conn.commit() so changes are persisted
"""

from flask import Flask, request, jsonify
from db import get_db
from validators import validate_user, validate_note

app = Flask(__name__)

AUTH_TOKEN = "mysecrettoken"
VALID_ENVS = {"dev", "prod"}


# ── Hooks ─────────────────────────────────────────────────────────────────────

@app.after_request
def set_content_type(response):
    response.headers["Content-Type"] = "application/json"
    return response


@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({"error": "Internal server error"}), 500


# ── Helpers ───────────────────────────────────────────────────────────────────

def _parse_json_body():
    """Parse JSON body from request, return (data, error_response)."""
    try:
        data = request.get_json(force=True)
        if data is None or not isinstance(data, dict):
            raise ValueError("empty or non-object body")
        return data, None
    except Exception:
        return None, (jsonify({"error": "Invalid JSON body"}), 400)


def _user_to_dict(user_row, notes=None) -> dict:
    """Convert a SQLite Row to a plain dict. Includes notes only if provided."""
    result = {
        "name":  user_row["name"],
        "email": user_row["email"],
        "age":   user_row["age"],
    }
    if notes is not None:
        result["notes"] = notes
    return result


def _get_notes_for_user(conn, email: str) -> list:
    """Fetch all notes for a user as a list of strings."""
    rows = conn.execute(
        "SELECT note FROM notes WHERE email = ?", (email,)
    ).fetchall()
    return [r["note"] for r in rows]


# ── POST /users ───────────────────────────────────────────────────────────────

@app.route("/<env>/users", methods=["POST"])
def create_user(env):
    if env not in VALID_ENVS:
        return jsonify({"error": "Not found"}), 404

    data, err = _parse_json_body()
    if err:
        return err

    validation_error = validate_user(data, check_email_format=True)
    if validation_error:
        return jsonify({"error": validation_error}), 400

    conn = get_db(env)
    try:
        # FIX BUG-001: explicit duplicate check → 409 instead of SQLite crash → 500
        existing = conn.execute(
            "SELECT email FROM users WHERE email = ?", (data["email"],)
        ).fetchone()
        if existing:
            return jsonify({"error": "Email already exists"}), 409

        conn.execute(
            "INSERT INTO users (email, name, age) VALUES (?, ?, ?)",
            (data["email"], data["name"], data["age"]),
        )
        conn.commit()
        user = conn.execute(
            "SELECT * FROM users WHERE email = ?", (data["email"],)
        ).fetchone()
        return jsonify(_user_to_dict(user)), 201
    finally:
        conn.close()


# ── GET /users ────────────────────────────────────────────────────────────────

@app.route("/<env>/users", methods=["GET"])
def list_users(env):
    if env not in VALID_ENVS:
        return jsonify({"error": "Not found"}), 404

    conn = get_db(env)
    try:
        rows = conn.execute("SELECT * FROM users").fetchall()
        users = []
        for row in rows:
            notes = _get_notes_for_user(conn, row["email"])
            users.append(_user_to_dict(row, notes))
        return jsonify(users), 200
    finally:
        conn.close()


# ── GET /users/<email> ────────────────────────────────────────────────────────

@app.route("/<env>/users/<email>", methods=["GET"])
def get_user(env, email):
    if env not in VALID_ENVS:
        return jsonify({"error": "Not found"}), 404

    conn = get_db(env)
    try:
        user = conn.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()

        # FIX BUG-004: guard before accessing user fields → 404 instead of TypeError → 500
        if not user:
            return jsonify({"error": "User not found"}), 404

        notes = _get_notes_for_user(conn, user["email"])
        return jsonify(_user_to_dict(user, notes)), 200
    finally:
        conn.close()


# ── PUT /users/<email> ────────────────────────────────────────────────────────

@app.route("/<env>/users/<email>", methods=["PUT"])
def update_user(env, email):
    if env not in VALID_ENVS:
        return jsonify({"error": "Not found"}), 404

    data, err = _parse_json_body()
    if err:
        return err

    validation_error = validate_user(data, check_email_format=True)
    if validation_error:
        return jsonify({"error": validation_error}), 400

    conn = get_db(env)
    try:
        existing = conn.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
        if not existing:
            return jsonify({"error": "User not found"}), 404

        new_email = data["email"]
        if new_email != email:
            conflict = conn.execute(
                "SELECT email FROM users WHERE email = ?", (new_email,)
            ).fetchone()
            if conflict:
                return jsonify({"error": "Email already exists"}), 409

        conn.execute(
            "UPDATE users SET name = ?, email = ?, age = ? WHERE email = ?",
            (data["name"], new_email, data["age"], email),
        )
        # FIX BUG-CRÍTICO: commit() was missing in the original → changes were lost
        conn.commit()

        updated = conn.execute(
            "SELECT * FROM users WHERE email = ?", (new_email,)
        ).fetchone()
        return jsonify(_user_to_dict(updated)), 200
    finally:
        conn.close()


# ── DELETE /users/<email> ─────────────────────────────────────────────────────

@app.route("/<env>/users/<email>", methods=["DELETE"])
def delete_user(env, email):
    if env not in VALID_ENVS:
        return jsonify({"error": "Not found"}), 404

    # FIX BUG-005: validate token in ALL environments (original only checked "dev")
    auth = request.headers.get("Authentication")
    if auth != AUTH_TOKEN:
        return jsonify({"error": "Authentication required"}), 401

    conn = get_db(env)
    try:
        existing = conn.execute(
            "SELECT email FROM users WHERE email = ?", (email,)
        ).fetchone()
        if not existing:
            return jsonify({"error": "User not found"}), 404

        conn.execute("DELETE FROM notes WHERE email = ?", (email,))
        conn.execute("DELETE FROM users WHERE email = ?", (email,))
        conn.commit()
        return "", 204
    finally:
        conn.close()


# ── POST /users/<email>/notes ─────────────────────────────────────────────────

@app.route("/<env>/users/<email>/notes", methods=["POST"])
def add_note(env, email):
    if env not in VALID_ENVS:
        return jsonify({"error": "Not found"}), 404

    data, err = _parse_json_body()
    if err:
        return err

    validation_error = validate_note(data)
    if validation_error:
        return jsonify({"error": validation_error}), 400

    conn = get_db(env)
    try:
        user = conn.execute(
            "SELECT email FROM users WHERE email = ?", (email,)
        ).fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404

        conn.execute(
            "INSERT INTO notes (email, note) VALUES (?, ?)",
            (email, data["note"]),
        )
        conn.commit()
        return jsonify({"email": email, "note": data["note"]}), 201
    finally:
        conn.close()


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=False)
