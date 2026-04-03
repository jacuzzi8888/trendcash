"""
Authentication module with proper caching and security.
"""

import os
import functools
from datetime import datetime, timezone
from typing import Optional

from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

from .database import get_db, utc_now
from .cache import UserCache
from .security_new import validator, log_security_event
from .logging_config import log_info, log_error


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "error"


class User(UserMixin):
    def __init__(self, user_dict: dict):
        self.id = str(user_dict["id"])
        self.username = user_dict["username"]
        self.role = user_dict.get("role", "editor")
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role,
        }


def get_user_by_id(conn, user_id: str) -> Optional[User]:
    cached = UserCache.get(user_id)
    if cached:
        return User(cached)
    
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if row:
        user_dict = dict(row)
        UserCache.set(user_id, user_dict)
        return User(user_dict)
    return None


def get_user_by_username(conn, username: str) -> Optional[User]:
    row = conn.execute(
        "SELECT * FROM users WHERE username = ?", (username.lower(),)
    ).fetchone()
    if row:
        return User(dict(row))
    return None


def create_user(conn, username: str, password: str, role: str = "editor") -> int:
    username = validator.validate_username(username)
    password = validator.validate_password(password)
    
    password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
    now = utc_now()
    
    cursor = conn.execute(
        "INSERT INTO users (username, password_hash, role, created_at) VALUES (?, ?, ?, ?)",
        (username.lower(), password_hash, role, now),
    )
    
    log_info("User created", username=username, role=role)
    return cursor.lastrowid


def update_password(conn, user_id: str, new_password: str) -> bool:
    new_password = validator.validate_password(new_password)
    
    password_hash = generate_password_hash(new_password, method='pbkdf2:sha256', salt_length=16)
    conn.execute(
        "UPDATE users SET password_hash = ?, updated_at = ? WHERE id = ?",
        (password_hash, utc_now(), user_id),
    )
    
    UserCache.delete(user_id)
    
    log_info("Password updated", user_id=user_id)
    return True


def init_default_user(conn):
    default_user = os.environ.get("NTC_DEFAULT_USER", "admin")
    default_pass = os.environ.get("NTC_DEFAULT_PASSWORD")
    
    existing = conn.execute("SELECT COUNT(*) as c FROM users").fetchone()
    if existing and existing["c"] > 0:
        return
    
    if default_pass:
        if len(default_pass) < 12:
            log_error("Default password too short, must be at least 12 characters")
            return
        
        create_user(conn, default_user, default_pass, role="admin")
        conn.commit()
        log_info("Default admin user created", username=default_user)


def clear_user_cache(user_id: str):
    UserCache.delete(user_id)


@login_manager.user_loader
def load_user(user_id: str) -> Optional[User]:
    with get_db() as conn:
        return get_user_by_id(conn, user_id)


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")
        remember = request.form.get("remember") == "on"
        
        if not username or not password:
            flash("Username and password are required.", "error")
            return render_template("login.html", title="Login")
        
        with get_db() as conn:
            user = get_user_by_username(conn, username)
            
            if user:
                stored = conn.execute(
                    "SELECT password_hash FROM users WHERE id = ?", (user.id,)
                ).fetchone()
                
                if stored and check_password_hash(stored["password_hash"], password):
                    login_user(user, remember=remember)
                    
                    session.permanent = remember
                    
                    log_security_event(
                        "login_success",
                        f"User: {user.username}",
                        user_id=user.id,
                        ip_address=request.remote_addr,
                    )
                    
                    next_page = request.args.get("next")
                    return redirect(next_page or url_for("index"))
        
        log_security_event(
            "login_failed",
            f"Username: {username}",
            ip_address=request.remote_addr,
        )
        
        flash("Invalid username or password.", "error")
    
    return render_template("login.html", title="Login")


@auth_bp.route("/logout")
@login_required
def logout():
    username = current_user.username
    user_id = current_user.id
    
    logout_user()
    
    UserCache.delete(user_id)
    
    log_security_event(
        "logout",
        f"User: {username}",
        user_id=user_id,
    )
    
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
            with get_db() as conn:
                stored = conn.execute(
                    "SELECT password_hash FROM users WHERE id = ?", (current_user.id,)
                ).fetchone()
                
                if stored and check_password_hash(stored["password_hash"], current_password):
                    update_password(conn, current_user.id, new_password)
                    conn.commit()
                    
                    log_security_event(
                        "password_changed",
                        f"User: {current_user.username}",
                        user_id=current_user.id,
                    )
                    
                    flash("Password changed successfully.", "success")
                    return redirect(url_for("settings"))
                
                flash("Current password is incorrect.", "error")
    
    return render_template("change_password.html", title="Change Password")


def role_required(role: str):
    """Decorator to require a specific role."""
    def decorator(f):
        @functools.wraps(f)
        @login_required
        def wrapped(*args, **kwargs):
            if current_user.role != role and current_user.role != "admin":
                log_security_event(
                    "unauthorized_access",
                    f"User {current_user.username} attempted to access {role}-only endpoint",
                    user_id=current_user.id,
                )
                flash("You do not have permission to access this page.", "error")
                return redirect(url_for("index"))
            return f(*args, **kwargs)
        return wrapped
    return decorator


def admin_required(f):
    """Decorator to require admin role."""
    return role_required("admin")(f)


from flask_limiter import Limiter
limiter = Limiter()


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def login_with_limit():
    return login()
