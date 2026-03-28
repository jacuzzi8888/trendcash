import os
import sqlite3
from datetime import datetime, timezone
from flask import Flask, jsonify, request, render_template, g

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SITE_SECRET_KEY", "change-this-in-production")

DATABASE = os.path.join(os.path.dirname(__file__), "site.db")
API_KEY = os.environ.get("SITE_API_KEY", "your-api-key-here")


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            slug TEXT NOT NULL UNIQUE,
            content TEXT NOT NULL,
            category TEXT NOT NULL,
            excerpt TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    db.commit()


@app.cli.command("init-db")
def init_db_command():
    init_db()
    print("Initialized database.")


def check_api_key():
    auth = request.headers.get("Authorization", "")
    if auth != f"Bearer {API_KEY}":
        return False
    return True


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()})


@app.route("/api/content", methods=["POST"])
def receive_content():
    if not check_api_key():
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    
    data = request.json
    
    if not data:
        return jsonify({"success": False, "error": "No data provided"}), 400
    
    required_fields = ["title", "content", "slug"]
    for field in required_fields:
        if not data.get(field):
            return jsonify({"success": False, "error": f"Missing required field: {field}"}), 400
    
    db = get_db()
    now = datetime.now(timezone.utc).isoformat()
    
    try:
        db.execute(
            """
            INSERT INTO posts (title, slug, content, category, excerpt, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["title"],
                data["slug"],
                data["content"],
                data.get("category", "general"),
                data.get("meta", {}).get("excerpt", ""),
                now,
                now
            )
        )
        db.commit()
        
        post_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
        
        return jsonify({
            "success": True,
            "post_id": post_id,
            "url": f"/post/{data['slug']}"
        })
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "error": "Slug already exists"}), 400


@app.route("/")
def index():
    db = get_db()
    posts = db.execute(
        "SELECT * FROM posts ORDER BY created_at DESC LIMIT 50"
    ).fetchall()
    return render_template("index.html", posts=posts)


@app.route("/post/<slug>")
def post(slug):
    db = get_db()
    post = db.execute(
        "SELECT * FROM posts WHERE slug = ?", (slug,)
    ).fetchone()
    if post is None:
        return "Post not found", 404
    return render_template("post.html", post=post)


if __name__ == "__main__":
    os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
    with app.app_context():
        init_db()
    app.run(debug=True, port=5001)
