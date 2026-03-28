from flask import Blueprint, request, session, jsonify
from werkzeug.security import check_password_hash
from functools import wraps
from db import get_db

auth_bp = Blueprint("auth", __name__)


# ── Decorators ─────────────────────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if "user_id" not in session:
                return jsonify({"error": "Unauthorized"}), 401
            if session.get("role") not in roles:
                return jsonify({"error": "Forbidden — insufficient permissions"}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator


# ── Endpoints ──────────────────────────────────────────────────────────────

@auth_bp.route("/login", methods=["POST"])
def login():
    data     = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    conn   = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Users WHERE Username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user or not check_password_hash(user["Password"], password):
        return jsonify({"error": "Invalid username or password"}), 401

    session.permanent = True
    session["user_id"]   = user["UserID"]
    session["username"]  = user["Username"]
    session["role"]      = user["Role"]
    session["full_name"] = user["FullName"] or user["Username"]

    return jsonify({
        "success":   True,
        "user": {
            "id":        user["UserID"],
            "username":  user["Username"],
            "role":      user["Role"],
            "full_name": user["FullName"],
        },
    })


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True})


@auth_bp.route("/me")
def me():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401
    return jsonify({
        "id":        session["user_id"],
        "username":  session["username"],
        "role":      session["role"],
        "full_name": session["full_name"],
    })