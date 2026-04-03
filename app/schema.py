"""
Shared database schema definition.
Single source of truth for all database tables and indexes.
"""

SCHEMA_SQL = """
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
"""

INDEX_SQL = """
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
"""

DEFAULT_SETTINGS = {
    "category_locked": "",
    "publish_daily_limit": "10",
    "image_policy_default": "none",
    "source_days_back": "7",
    "sources_per_trend": "3",
    "auto_fetch_sources": "true",
}
