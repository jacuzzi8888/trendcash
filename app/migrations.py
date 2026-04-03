"""
Database migrations system.
Provides version-controlled schema changes.
"""

import os
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional


MIGRATIONS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "migrations")


MIGRATIONS = [
    {
        "version": 1,
        "name": "initial_schema",
        "description": "Initial database schema",
        "up": """
            CREATE TABLE IF NOT EXISTS trend_candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                category TEXT NOT NULL,
                source TEXT NOT NULL,
                velocity_score REAL NOT NULL,
                advertiser_safety_score REAL NOT NULL,
                commercial_intent_score REAL NOT NULL,
                evergreen_score REAL NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS source_packs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id INTEGER NOT NULL,
                url TEXT NOT NULL,
                publisher TEXT NOT NULL,
                published_at TEXT,
                notes TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(candidate_id) REFERENCES trend_candidates(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS drafts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                status TEXT NOT NULL,
                last_updated TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                image_policy TEXT NOT NULL DEFAULT 'none',
                image_prompt TEXT,
                target_site_id INTEGER,
                FOREIGN KEY(candidate_id) REFERENCES trend_candidates(id) ON DELETE CASCADE,
                FOREIGN KEY(target_site_id) REFERENCES sites(id) ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS qc_reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                draft_id INTEGER NOT NULL,
                source_valid INTEGER NOT NULL,
                unique_value INTEGER NOT NULL,
                advertiser_safety INTEGER NOT NULL,
                actionability INTEGER NOT NULL,
                reviewer TEXT,
                reviewed_at TEXT NOT NULL,
                FOREIGN KEY(draft_id) REFERENCES drafts(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS publish_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                draft_id INTEGER NOT NULL,
                site_id INTEGER,
                status TEXT NOT NULL,
                post_id TEXT,
                published_url TEXT,
                published_at TEXT,
                notes TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(draft_id) REFERENCES drafts(id) ON DELETE CASCADE,
                FOREIGN KEY(site_id) REFERENCES sites(id) ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                slug TEXT NOT NULL UNIQUE,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                excerpt TEXT,
                category TEXT NOT NULL,
                published_at TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_date TEXT NOT NULL,
                indexing_rate REAL,
                queries INTEGER,
                ctr REAL,
                avg_position REAL,
                notes TEXT
            );

            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS sites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                slug TEXT NOT NULL UNIQUE,
                niche TEXT NOT NULL,
                description TEXT,
                api_url TEXT NOT NULL,
                api_key TEXT,
                categories TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS publish_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                draft_id INTEGER NOT NULL,
                site_id INTEGER NOT NULL,
                status TEXT NOT NULL,
                response TEXT,
                published_url TEXT,
                published_at TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(draft_id) REFERENCES drafts(id) ON DELETE CASCADE,
                FOREIGN KEY(site_id) REFERENCES sites(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'editor',
                created_at TEXT NOT NULL,
                updated_at TEXT
            );

            CREATE TABLE IF NOT EXISTS security_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                user_id TEXT,
                ip_address TEXT,
                details TEXT,
                created_at TEXT NOT NULL
            );
        """,
        "down": """
            DROP TABLE IF EXISTS security_logs;
            DROP TABLE IF EXISTS users;
            DROP TABLE IF EXISTS publish_log;
            DROP TABLE IF EXISTS sites;
            DROP TABLE IF EXISTS settings;
            DROP TABLE IF EXISTS metrics;
            DROP TABLE IF EXISTS posts;
            DROP TABLE IF EXISTS publish_queue;
            DROP TABLE IF EXISTS qc_reviews;
            DROP TABLE IF EXISTS drafts;
            DROP TABLE IF EXISTS source_packs;
            DROP TABLE IF EXISTS trend_candidates;
        """
    },
    {
        "version": 2,
        "name": "add_indexes",
        "description": "Add performance indexes",
        "up": """
            CREATE INDEX IF NOT EXISTS idx_trend_candidates_created_at ON trend_candidates(created_at);
            CREATE INDEX IF NOT EXISTS idx_trend_candidates_category ON trend_candidates(category);
            CREATE INDEX IF NOT EXISTS idx_source_packs_candidate_id ON source_packs(candidate_id);
            CREATE INDEX IF NOT EXISTS idx_drafts_status ON drafts(status);
            CREATE INDEX IF NOT EXISTS idx_drafts_candidate_id ON drafts(candidate_id);
            CREATE INDEX IF NOT EXISTS idx_qc_reviews_draft_id ON qc_reviews(draft_id);
            CREATE INDEX IF NOT EXISTS idx_publish_queue_draft_id ON publish_queue(draft_id);
            CREATE INDEX IF NOT EXISTS idx_publish_log_created_at ON publish_log(created_at);
            CREATE INDEX IF NOT EXISTS idx_publish_log_site_id ON publish_log(site_id);
            CREATE INDEX IF NOT EXISTS idx_metrics_metric_date ON metrics(metric_date);
            CREATE INDEX IF NOT EXISTS idx_sites_slug ON sites(slug);
            CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
        """,
        "down": """
            DROP INDEX IF EXISTS idx_trend_candidates_created_at;
            DROP INDEX IF EXISTS idx_trend_candidates_category;
            DROP INDEX IF EXISTS idx_source_packs_candidate_id;
            DROP INDEX IF EXISTS idx_drafts_status;
            DROP INDEX IF EXISTS idx_drafts_candidate_id;
            DROP INDEX IF EXISTS idx_qc_reviews_draft_id;
            DROP INDEX IF EXISTS idx_publish_queue_draft_id;
            DROP INDEX IF EXISTS idx_publish_log_created_at;
            DROP INDEX IF EXISTS idx_publish_log_site_id;
            DROP INDEX IF EXISTS idx_metrics_metric_date;
            DROP INDEX IF EXISTS idx_sites_slug;
            DROP INDEX IF EXISTS idx_users_username;
        """
    },
    {
        "version": 3,
        "name": "add_migration_tracking",
        "description": "Add migrations tracking table",
        "up": """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                applied_at TEXT NOT NULL
            );
        """,
        "down": """
            DROP TABLE IF EXISTS schema_migrations;
        """
    },
]


def get_applied_migrations(conn) -> List[int]:
    """Get list of applied migration versions."""
    try:
        result = conn.execute(
            "SELECT version FROM schema_migrations ORDER BY version"
        ).fetchall()
        return [row["version"] for row in result]
    except Exception:
        return []


def get_pending_migrations(conn) -> List[Dict[str, Any]]:
    """Get list of pending migrations."""
    applied = get_applied_migrations(conn)
    return [m for m in MIGRATIONS if m["version"] not in applied]


def apply_migration(conn, migration: Dict[str, Any]) -> bool:
    """Apply a single migration."""
    try:
        conn.executescript(migration["up"])
        
        conn.execute(
            "INSERT INTO schema_migrations (version, name, applied_at) VALUES (?, ?, ?)",
            (migration["version"], migration["name"], datetime.now(timezone.utc).isoformat())
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise RuntimeError(f"Migration {migration['version']} failed: {e}")


def rollback_migration(conn, migration: Dict[str, Any]) -> bool:
    """Rollback a single migration."""
    try:
        conn.executescript(migration["down"])
        
        conn.execute(
            "DELETE FROM schema_migrations WHERE version = ?",
            (migration["version"],)
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise RuntimeError(f"Rollback {migration['version']} failed: {e}")


def migrate_up(conn, target_version: int = None) -> List[int]:
    """Apply all pending migrations up to target version."""
    pending = get_pending_migrations(conn)
    
    if target_version:
        pending = [m for m in pending if m["version"] <= target_version]
    
    applied = []
    for migration in pending:
        apply_migration(conn, migration)
        applied.append(migration["version"])
    
    return applied


def migrate_down(conn, target_version: int = None) -> List[int]:
    """Rollback migrations down to target version."""
    applied_versions = get_applied_migrations(conn)
    
    if target_version:
        to_rollback = [v for v in applied_versions if v > target_version]
    else:
        to_rollback = [applied_versions[-1]] if applied_versions else []
    
    rolled_back = []
    for version in sorted(to_rollback, reverse=True):
        migration = next((m for m in MIGRATIONS if m["version"] == version), None)
        if migration:
            rollback_migration(conn, migration)
            rolled_back.append(version)
    
    return rolled_back


def get_migration_status(conn) -> Dict[str, Any]:
    """Get current migration status."""
    applied = get_applied_migrations(conn)
    pending = get_pending_migrations(conn)
    
    return {
        "current_version": max(applied) if applied else 0,
        "applied_count": len(applied),
        "pending_count": len(pending),
        "applied": applied,
        "pending": [m["version"] for m in pending],
    }


def create_migration(name: str, up_sql: str, down_sql: str) -> Dict[str, Any]:
    """Create a new migration."""
    max_version = max(m["version"] for m in MIGRATIONS) if MIGRATIONS else 0
    
    migration = {
        "version": max_version + 1,
        "name": name.lower().replace(" ", "_"),
        "description": name,
        "up": up_sql,
        "down": down_sql,
    }
    
    return migration
