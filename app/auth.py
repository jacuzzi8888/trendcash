import os
import functools
from datetime import datetime, timezone
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "error"


class User(UserMixin):
    def __init__(self, user_dict):
        self.id = str(user_dict["id"])
        self.username = user_dict["username"]
        self.role = user_dict.get("role", "editor")


_user_cache = {}


def get_user_by_id(conn, user_id):
    if user_id in _user_cache:
        return _user_cache[user_id]
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if row:
        _user_cache[user_id] = User(dict(row))
        return _user_cache[user_id]
    return None


def get_user_by_username(conn, username):
    row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    if row:
        return User(dict(row))
    return None


def create_user(conn, username, password, role="editor"):
    password_hash = generate_password_hash(password)
    now = datetime.now(timezone.utc).isoformat()
    cursor = conn.execute(
        "INSERT INTO users (username, password_hash, role, created_at) VALUES (?, ?, ?, ?)",
        (username, password_hash, role, now),
    )
    return cursor.lastrowid


def update_password(conn, user_id, new_password):
    password_hash = generate_password_hash(new_password)
    conn.execute(
        "UPDATE users SET password_hash = ?, updated_at = ? WHERE id = ?",
        (password_hash, datetime.now(timezone.utc).isoformat(), user_id),
    )


def init_default_user(conn):
    default_user = os.environ.get("NTC_DEFAULT_USER", "admin")
    default_pass = os.environ.get("NTC_DEFAULT_PASSWORD")
    
    existing = conn.execute("SELECT COUNT(*) as c FROM users").fetchone()
    if existing and existing["c"] > 0:
        return
    
    if default_pass:
        create_user(conn, default_user, default_pass, role="admin")
        conn.commit()


def ensure_admin_user(conn, username="admin", password="admin123"):
    existing = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
    if existing:
        password_hash = generate_password_hash(password)
        conn.execute("UPDATE users SET password_hash = ? WHERE username = ?", (password_hash, username))
        conn.commit()
        return existing["id"]
    return create_user(conn, username, password, role="admin")


@login_manager.user_loader
def load_user(user_id):
    from .db import get_db
    conn = get_db()
    user = get_user_by_id(conn, user_id)
    conn.close()
    return user


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        remember = request.form.get("remember") == "on"
        
        from .db import get_db
        conn = get_db()
        user = get_user_by_username(conn, username)
        
        if user and check_password_hash(
            conn.execute("SELECT password_hash FROM users WHERE id = ?", (user.id,)).fetchone()["password_hash"],
            password
        ):
            login_user(user, remember=remember)
            conn.close()
            next_page = request.args.get("next")
            return redirect(next_page or url_for("index"))
        
        conn.close()
        flash("Invalid username or password.", "error")
    
    return render_template("login.html", title="Login")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))


@auth_bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        current_password = request.form.get("current_password", "")
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")
        
        if not current_password or not new_password or not confirm_password:
            flash("All fields are required.", "error")
        elif new_password != confirm_password:
            flash("New passwords do not match.", "error")
        elif len(new_password) < 8:
            flash("Password must be at least 8 characters.", "error")
        else:
            from .db import get_db
            conn = get_db()
            stored = conn.execute(
                "SELECT password_hash FROM users WHERE id = ?", (current_user.id,)
            ).fetchone()
            
            if stored and check_password_hash(stored["password_hash"], current_password):
                update_password(conn, current_user.id, new_password)
                conn.commit()
                conn.close()
                flash("Password changed successfully.", "success")
                return redirect(url_for("settings"))
            
            conn.close()
            flash("Current password is incorrect.", "error")
    
    return render_template("change_password.html", title="Change Password")


def role_required(role):
    def decorator(f):
        @functools.wraps(f)
        @login_required
        def wrapped(*args, **kwargs):
            if current_user.role != role and current_user.role != "admin":
                flash("You do not have permission to access this page.", "error")
                return redirect(url_for("index"))
            return f(*args, **kwargs)
        return wrapped
    return decorator
