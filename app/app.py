import os
from datetime import datetime, timedelta, timezone
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    url_for,
    jsonify,
)

from .db import get_db, init_db, get_setting, set_setting, utc_now
from .sites import sites_bp
from .publisher import publish_to_site, log_publish, get_publish_history
from .trends_api import (
    fetch_all_trends, get_interest_over_time, get_related_queries,
    get_related_topics, get_suggestions
)
from .ai_writer import (
    generate_article, improve_content, generate_headline,
    generate_excerpt, generate_faqs, test_connection
)
from .source_fetcher import fetch_sources
from .auth import auth_bp, login_manager, init_default_user
from .security import (
    csrf, limiter, add_security_headers, get_secure_cookie_settings,
    sanitize_input, validate_id, validate_category, validate_url, validate_score,
    log_security_event, audit_log
)
from .crypto import encrypt_value, decrypt_value, mask_value
from flask_login import login_required, current_user


APP_TITLE = "Naija Trend-to-Cash"
RUBRIC_WEIGHTS = {
    "velocity": 0.30,
    "advertiser_safety": 0.30,
    "commercial_intent": 0.20,
    "evergreen": 0.20,
}


def create_app():
    static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    app = Flask(__name__, static_folder=static_folder)
    
    secret_key = os.environ.get("NTC_SECRET_KEY")
    if not secret_key:
        raise RuntimeError("NTC_SECRET_KEY environment variable must be set")
    app.config["SECRET_KEY"] = secret_key
    
    for key, value in get_secure_cookie_settings().items():
        app.config[key] = value
    
    app.config["WTF_CSRF_ENABLED"] = True
    app.config["WTF_CSRF_TIME_LIMIT"] = None
    
    csrf.init_app(app)
    limiter.init_app(app)
    login_manager.init_app(app)
    
    init_db()
    
    from .db import get_db
    conn = get_db()
    init_default_user(conn)
    conn.close()
    
    @app.after_request
    def security_headers(response):
        return add_security_headers(response)
    
    @app.template_filter('datetime')
    def format_datetime(value):
        if not value:
            return "-"
        try:
            dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
            now = datetime.now(timezone.utc)
            diff = now - dt
            
            if diff.days == 0:
                if diff.seconds < 60:
                    return "Just now"
                elif diff.seconds < 3600:
                    return f"{diff.seconds // 60} min ago"
                elif diff.seconds < 86400:
                    return f"{diff.seconds // 3600} hours ago"
            elif diff.days == 1:
                return "Yesterday"
            elif diff.days < 7:
                return f"{diff.days} days ago"
            else:
                return dt.strftime('%b %d, %Y')
        except:
            return value
    
    @app.context_processor
    def inject_csrf_token():
        from flask_wtf.csrf import generate_csrf
        return dict(csrf_token=generate_csrf)
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(sites_bp)

    @app.route("/")
    @login_required
    def index():
        conn = get_db()
        category_locked = get_setting(conn, "category_locked", "")
        counts = {
            "candidates": conn.execute(
                "SELECT COUNT(*) AS c FROM trend_candidates"
            ).fetchone()["c"],
            "drafts": conn.execute("SELECT COUNT(*) AS c FROM drafts").fetchone()["c"],
            "qc": conn.execute(
                "SELECT COUNT(*) AS c FROM drafts WHERE status = 'qc'"
            ).fetchone()["c"],
            "approved": conn.execute(
                "SELECT COUNT(*) AS c FROM drafts WHERE status = 'approved'"
            ).fetchone()["c"],
        }
        latest_metrics = conn.execute(
            "SELECT * FROM metrics ORDER BY metric_date DESC LIMIT 5"
        ).fetchall()
        conn.close()
        return render_template(
            "index.html",
            title=APP_TITLE,
            category_locked=category_locked,
            counts=counts,
            latest_metrics=latest_metrics,
        )

    @app.route("/selection", methods=["GET", "POST"])
    @login_required
    def selection():
        conn = get_db()
        if request.method == "POST":
            category = sanitize_input(request.form.get("category", ""), max_length=50)
            if category == "__unlock__":
                set_setting(conn, "category_locked", "")
                conn.commit()
                flash("Category lock cleared.", "success")
                log_security_event("category_unlock", f"User: {current_user.username}")
                conn.close()
                return redirect(url_for("selection"))
            if category:
                try:
                    category = validate_category(category)
                except ValueError as e:
                    flash(str(e), "error")
                    conn.close()
                    return redirect(url_for("selection"))
                set_setting(conn, "category_locked", category)
                conn.commit()
                flash(f"Category locked to: {category}", "success")
            conn.close()
            return redirect(url_for("selection"))

        category_locked = get_setting(conn, "category_locked", "")
        since = datetime.now(timezone.utc) - timedelta(days=14)
        rows = conn.execute(
            "SELECT * FROM trend_candidates WHERE created_at >= ?",
            (since.isoformat(),),
        ).fetchall()
        conn.close()

        scores = {}
        for row in rows:
            category = row["category"]
            score = (
                RUBRIC_WEIGHTS["velocity"] * row["velocity_score"]
                + RUBRIC_WEIGHTS["advertiser_safety"] * row["advertiser_safety_score"]
                + RUBRIC_WEIGHTS["commercial_intent"] * row["commercial_intent_score"]
                + RUBRIC_WEIGHTS["evergreen"] * row["evergreen_score"]
            )
            bucket = scores.setdefault(
                category,
                {"count": 0, "total": 0.0, "avg": 0.0},
            )
            bucket["count"] += 1
            bucket["total"] += score

        for category in scores:
            bucket = scores[category]
            bucket["avg"] = round(bucket["total"] / bucket["count"], 3)

        ranked = sorted(
            [{"category": k, **v} for k, v in scores.items()],
            key=lambda item: item["avg"],
            reverse=True,
        )

        return render_template(
            "selection.html",
            title=APP_TITLE,
            category_locked=category_locked,
            scores=ranked,
            weights=RUBRIC_WEIGHTS,
        )

    @app.route("/trends", methods=["GET", "POST"])
    @login_required
    def trends():
        conn = get_db()
        if request.method == "POST":
            try:
                topic = sanitize_input(request.form.get("topic", "").strip(), max_length=200)
                category = sanitize_input(request.form.get("category", "").strip(), max_length=50)
                source = sanitize_input(request.form.get("source", "").strip(), max_length=100)
                velocity = validate_score(request.form.get("velocity_score", "0"), name="Velocity score")
                advertiser = validate_score(request.form.get("advertiser_safety_score", "0"), name="Advertiser safety score")
                commercial = validate_score(request.form.get("commercial_intent_score", "0"), name="Commercial intent score")
                evergreen = validate_score(request.form.get("evergreen_score", "0"), name="Evergreen score")
            except ValueError as e:
                flash(str(e), "error")
                conn.close()
                return redirect(url_for("trends"))

            if not topic or not category or not source:
                flash("Topic, category, and source are required.", "error")
            else:
                conn.execute(
                    """
                    INSERT INTO trend_candidates
                    (topic, category, source, velocity_score, advertiser_safety_score,
                     commercial_intent_score, evergreen_score, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        topic,
                        category,
                        source,
                        velocity,
                        advertiser,
                        commercial,
                        evergreen,
                        utc_now(),
                    ),
                )
                conn.commit()
                flash("Trend candidate added.", "success")

            conn.close()
            return redirect(url_for("trends"))

        category_filter = request.args.get("category")
        if category_filter:
            category_filter = sanitize_input(category_filter, max_length=50)
            rows = conn.execute(
                """SELECT tc.*, 
                    (SELECT COUNT(*) FROM source_packs sp WHERE sp.candidate_id = tc.id) as source_count
                    FROM trend_candidates tc 
                    WHERE tc.category = ? ORDER BY tc.created_at DESC""",
                (category_filter,),
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT tc.*, 
                    (SELECT COUNT(*) FROM source_packs sp WHERE sp.candidate_id = tc.id) as source_count
                    FROM trend_candidates tc 
                    ORDER BY tc.created_at DESC LIMIT 200"""
            ).fetchall()
        categories = conn.execute(
            "SELECT DISTINCT category FROM trend_candidates ORDER BY category"
        ).fetchall()
        conn.close()
        return render_template(
            "trends.html",
            title=APP_TITLE,
            candidates=rows,
            categories=[row["category"] for row in categories],
            category_filter=category_filter,
        )

    @app.route("/discover", methods=["GET", "POST"])
    @login_required
    @limiter.limit("30 per hour")
    def trend_discovery():
        conn = get_db()
        keyword = sanitize_input(request.args.get("keyword", "").strip(), max_length=100)
        explore_geo = sanitize_input(request.args.get("explore_geo", "NG"), max_length=5)
        geo = "NG"
        category = "general"
        fetch_result = None
        interest_data = None
        related_queries = None
        related_topics = None
        suggestions = None

        if request.method == "POST":
            try:
                geo = sanitize_input(request.form.get("geo", "NG"), max_length=5)
                category = sanitize_input(request.form.get("category", "general").strip() or "general", max_length=50)
                custom_category = sanitize_input(request.form.get("custom_category", "").strip(), max_length=50)
                if category == "__custom__" and custom_category:
                    category = custom_category.lower()
                scores = {
                    "velocity": validate_score(request.form.get("velocity", 0.5)),
                    "advertiser_safety": validate_score(request.form.get("advertiser_safety", 0.5)),
                    "commercial_intent": validate_score(request.form.get("commercial_intent", 0.5)),
                    "evergreen": validate_score(request.form.get("evergreen", 0.5)),
                }
            except ValueError as e:
                flash(str(e), "error")
                conn.close()
                return redirect(url_for("trend_discovery"))
            
            auto_fetch = get_setting(conn, "auto_fetch_sources", "true") == "true"
            days_back = int(get_setting(conn, "source_days_back", "7"))
            sources_per_trend = int(get_setting(conn, "sources_per_trend", "3"))

            result = fetch_all_trends(geo if geo else None, category)
            if result["success"]:
                added = 0
                skipped = 0
                sources_added = 0
                for trend in result["trends"]:
                    topic = sanitize_input(trend["topic"], max_length=200)
                    source = sanitize_input(trend["source"], max_length=100)
                    existing = conn.execute(
                        "SELECT id FROM trend_candidates WHERE topic = ? AND source LIKE ?",
                        (topic, "google_autocomplete%"),
                    ).fetchone()
                    if existing:
                        skipped += 1
                        continue
                    
                    cursor = conn.execute(
                        """
                        INSERT INTO trend_candidates
                        (topic, category, source, velocity_score, advertiser_safety_score,
                         commercial_intent_score, evergreen_score, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            topic,
                            category,
                            source,
                            scores["velocity"],
                            scores["advertiser_safety"],
                            scores["commercial_intent"],
                            scores["evergreen"],
                            utc_now(),
                        ),
                    )
                    candidate_id = cursor.lastrowid
                    added += 1
                    
                    if auto_fetch and candidate_id:
                        src_result = fetch_sources(
                            topic=topic,
                            num_results=sources_per_trend,
                            days_back=days_back,
                            region=geo
                        )
                        if src_result["success"] and src_result.get("sources"):
                            for src in src_result["sources"]:
                                conn.execute(
                                    """
                                    INSERT INTO source_packs
                                    (candidate_id, url, publisher, published_at, notes, created_at)
                                    VALUES (?, ?, ?, ?, ?, ?)
                                    """,
                                    (
                                        candidate_id,
                                        sanitize_input(src["url"], max_length=2048),
                                        sanitize_input(src.get("publisher", ""), max_length=100),
                                        src.get("published_at"),
                                        sanitize_input(src.get("notes", "")[:500] if src.get("notes") else "", max_length=500),
                                        utc_now(),
                                    ),
                                )
                                sources_added += 1
                
                conn.commit()
                fetch_result = {
                    "success": True,
                    "fetched": result["count"],
                    "added": added,
                    "skipped": skipped,
                    "sources_added": sources_added,
                    "category": category,
                }
            else:
                fetch_result = {"success": False, "error": result.get("error", "Unknown error")}

        if keyword:
            interest_result = get_interest_over_time([keyword], explore_geo)
            if interest_result["success"] and interest_result["data"]:
                interest_data = interest_result["data"]

            queries_result = get_related_queries(keyword, explore_geo)
            if queries_result["success"]:
                related_queries = {"rising": queries_result["rising"], "top": queries_result["top"]}

            topics_result = get_related_topics(keyword, explore_geo)
            if topics_result["success"]:
                related_topics = {"rising": topics_result["rising"], "top": topics_result["top"]}

            suggestions_result = get_suggestions(keyword)
            if suggestions_result["success"]:
                suggestions = suggestions_result["suggestions"]

        recent_trends = conn.execute(
            "SELECT * FROM trend_candidates ORDER BY created_at DESC LIMIT 20"
        ).fetchall()
        
        custom_categories = []
        predefined = {'general', 'betting', 'crypto', 'finance', 'education', 'politics', 'sports', 'entertainment', 'travel', 'jobs', 'test', 'trending'}
        for row in recent_trends:
            try:
                cat = row.get("category", "") if hasattr(row, 'get') else (row["category"] if "category" in row.keys() else "")
            except (KeyError, TypeError):
                cat = ""
            if cat and cat not in predefined and cat not in custom_categories:
                custom_categories.append(cat)
        
        conn.close()

        return render_template(
            "trend_discovery.html",
            title=APP_TITLE,
            geo=geo,
            category=category,
            fetch_result=fetch_result,
            keyword=keyword,
            explore_geo=explore_geo,
            interest_data=interest_data,
            related_queries=related_queries,
            related_topics=related_topics,
            suggestions=suggestions,
            recent_trends=recent_trends,
            custom_categories=custom_categories,
        )

    @app.route("/sources/<int:candidate_id>", methods=["GET", "POST"])
    @login_required
    def sources(candidate_id):
        conn = get_db()
        candidate = conn.execute(
            "SELECT * FROM trend_candidates WHERE id = ?", (candidate_id,)
        ).fetchone()
        if candidate is None:
            conn.close()
            flash("Candidate not found.", "error")
            return redirect(url_for("trends"))

        if request.method == "POST":
            try:
                url = sanitize_input(request.form.get("url", "").strip(), max_length=2048)
                publisher = sanitize_input(request.form.get("publisher", "").strip(), max_length=100)
                published_at = sanitize_input(request.form.get("published_at", "").strip(), max_length=20)
                notes = sanitize_input(request.form.get("notes", "").strip(), max_length=500)
                
                validate_url(url)
            except ValueError as e:
                flash(str(e), "error")
                conn.close()
                return redirect(url_for("sources", candidate_id=candidate_id))
            
            if not url or not publisher:
                flash("URL and publisher are required.", "error")
            else:
                conn.execute(
                    """
                    INSERT INTO source_packs
                    (candidate_id, url, publisher, published_at, notes, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (candidate_id, url, publisher, published_at, notes, utc_now()),
                )
                conn.commit()
                flash("Source added.", "success")
            conn.close()
            return redirect(url_for("sources", candidate_id=candidate_id))

        sources_rows = conn.execute(
            "SELECT * FROM source_packs WHERE candidate_id = ? ORDER BY created_at DESC",
            (candidate_id,),
        ).fetchall()
        conn.close()
        return render_template(
            "sources.html",
            title=APP_TITLE,
            candidate=candidate,
            sources=sources_rows,
        )

    def _generate_draft(candidate, sources_rows, image_policy):
        now_date = datetime.now(timezone.utc).date().isoformat()
        title = f"{candidate['topic']} — What Nigerians Should Know"
        sources_list = "\n".join(
            [
                f"- {s['publisher']}: {s['url']}"
                + (f" ({s['published_at']})" if s["published_at"] else "")
                for s in sources_rows
            ]
        )
        content = (
            f"# {title}\n\n"
            "## What happened\n"
            "Summarize the key facts from the sources. Keep it factual and brief.\n\n"
            "## What it means for Nigerians\n"
            "Explain practical impact on daily life, costs, eligibility, or timelines.\n\n"
            "## What to do next\n"
            "Provide clear next steps, official links, and deadlines.\n\n"
            "## FAQs\n"
            "1. Who is affected?\n"
            "2. What are the key dates?\n"
            "3. Where is the official source?\n\n"
            "## Sources\n"
            f"{sources_list}\n"
        )
        return {
            "title": title,
            "content": content,
            "last_updated": now_date,
            "image_policy": image_policy,
        }

    @app.route("/drafts", methods=["GET"])
    @login_required
    def drafts():
        conn = get_db()
        status = sanitize_input(request.args.get("status", ""), max_length=20)
        if status:
            rows = conn.execute(
                "SELECT d.*, t.topic FROM drafts d "
                "JOIN trend_candidates t ON d.candidate_id = t.id "
                "WHERE d.status = ? ORDER BY d.updated_at DESC",
                (status,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT d.*, t.topic FROM drafts d "
                "JOIN trend_candidates t ON d.candidate_id = t.id "
                "ORDER BY d.updated_at DESC LIMIT 200"
            ).fetchall()
        conn.close()
        return render_template(
            "drafts.html",
            title=APP_TITLE,
            drafts=rows,
            status_filter=status,
        )

    @app.route("/drafts/new/<int:candidate_id>", methods=["POST"])
    @login_required
    def create_draft(candidate_id):
        conn = get_db()
        candidate = conn.execute(
            "SELECT * FROM trend_candidates WHERE id = ?", (candidate_id,)
        ).fetchone()
        if candidate is None:
            conn.close()
            flash("Candidate not found.", "error")
            return redirect(url_for("trends"))

        category_locked = get_setting(conn, "category_locked", "")
        if category_locked and candidate["category"] != category_locked:
            conn.close()
            flash("Candidate outside locked category.", "error")
            return redirect(url_for("trends"))

        sources_rows = conn.execute(
            "SELECT * FROM source_packs WHERE candidate_id = ?",
            (candidate_id,),
        ).fetchall()
        if len(sources_rows) < 2:
            conn.close()
            flash("At least 2 sources required before drafting.", "error")
            return redirect(url_for("sources", candidate_id=candidate_id))

        image_policy = get_setting(conn, "image_policy_default", "none")
        draft = _generate_draft(candidate, sources_rows, image_policy)
        now = utc_now()
        conn.execute(
            """
            INSERT INTO drafts
            (candidate_id, title, content, status, last_updated, created_at, updated_at, image_policy)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                candidate_id,
                draft["title"],
                draft["content"],
                "draft",
                draft["last_updated"],
                now,
                now,
                draft["image_policy"],
            ),
        )
        conn.commit()
        conn.close()
        flash("Draft created.", "success")
        return redirect(url_for("drafts"))

    @app.route("/drafts/<int:draft_id>", methods=["GET", "POST"])
    @login_required
    def edit_draft(draft_id):
        conn = get_db()
        draft = conn.execute(
            "SELECT * FROM drafts WHERE id = ?", (draft_id,)
        ).fetchone()
        if draft is None:
            conn.close()
            flash("Draft not found.", "error")
            return redirect(url_for("drafts"))

        if request.method == "POST":
            title = sanitize_input(request.form.get("title", "").strip(), max_length=200)
            content = request.form.get("content", "").strip()
            last_updated = sanitize_input(request.form.get("last_updated", "").strip(), max_length=20)
            image_policy = sanitize_input(request.form.get("image_policy", "none").strip(), max_length=20)
            image_prompt = sanitize_input(request.form.get("image_prompt", "").strip(), max_length=500)
            status_action = sanitize_input(request.form.get("status_action", "save"), max_length=20)
            if not title or not content or not last_updated:
                flash("Title, content, and last updated are required.", "error")
                conn.close()
                return redirect(url_for("edit_draft", draft_id=draft_id))

            new_status = draft["status"]
            if status_action == "send_qc":
                new_status = "qc"

            conn.execute(
                """
                UPDATE drafts
                SET title = ?, content = ?, last_updated = ?, updated_at = ?,
                    image_policy = ?, image_prompt = ?, status = ?
                WHERE id = ?
                """,
                (
                    title,
                    content,
                    last_updated,
                    utc_now(),
                    image_policy,
                    image_prompt,
                    new_status,
                    draft_id,
                ),
            )
            conn.commit()
            conn.close()
            flash("Draft updated.", "success")
            if status_action == "send_qc":
                return redirect(url_for("qc"))
            return redirect(url_for("edit_draft", draft_id=draft_id))

        candidate = conn.execute(
            "SELECT * FROM trend_candidates WHERE id = ?", (draft["candidate_id"],)
        ).fetchone() if draft else None
        conn.close()
        return render_template(
            "draft_edit.html",
            title=APP_TITLE,
            draft=draft,
            candidate=candidate,
        )

    @app.route("/qc", methods=["GET", "POST"])
    @login_required
    def qc():
        conn = get_db()
        if request.method == "POST":
            draft_id = request.form.get("draft_id")
            reviewer = sanitize_input(request.form.get("reviewer", "").strip(), max_length=50)
            checks = {
                "source_valid": request.form.get("source_valid") == "on",
                "unique_value": request.form.get("unique_value") == "on",
                "advertiser_safety": request.form.get("advertiser_safety") == "on",
                "actionability": request.form.get("actionability") == "on",
            }
            if not draft_id:
                conn.close()
                flash("Draft id missing.", "error")
                return redirect(url_for("qc"))
            if not all(checks.values()):
                conn.close()
                flash("All QC checks must pass to approve.", "error")
                return redirect(url_for("qc"))

            try:
                draft_id = validate_id(draft_id, "Draft ID")
            except ValueError as e:
                flash(str(e), "error")
                conn.close()
                return redirect(url_for("qc"))

            conn.execute(
                """
                INSERT INTO qc_reviews
                (draft_id, source_valid, unique_value, advertiser_safety, actionability,
                 reviewer, reviewed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    draft_id,
                    int(checks["source_valid"]),
                    int(checks["unique_value"]),
                    int(checks["advertiser_safety"]),
                    int(checks["actionability"]),
                    reviewer,
                    utc_now(),
                ),
            )
            conn.execute(
                "UPDATE drafts SET status = ?, updated_at = ? WHERE id = ?",
                ("approved", utc_now(), draft_id),
            )
            conn.commit()
            log_security_event("draft_approved", f"Draft ID: {draft_id}, Reviewer: {reviewer}", current_user.id)
            conn.close()
            flash("Draft approved.", "success")
            return redirect(url_for("qc"))

        rows = conn.execute(
            "SELECT d.*, t.topic FROM drafts d "
            "JOIN trend_candidates t ON d.candidate_id = t.id "
            "WHERE d.status = 'qc' ORDER BY d.updated_at DESC"
        ).fetchall()
        conn.close()
        return render_template(
            "qc.html",
            title=APP_TITLE,
            drafts=rows,
        )

    @app.route("/publish", methods=["GET", "POST"])
    @login_required
    def publish():
        conn = get_db()
        if request.method == "POST":
            action = sanitize_input(request.form.get("action", ""), max_length=20)
            draft_id = request.form.get("draft_id")
            site_id = request.form.get("site_id")
            
            if action == "publish" and draft_id and site_id:
                try:
                    draft_id = validate_id(draft_id, "Draft ID")
                    site_id = validate_id(site_id, "Site ID")
                except ValueError as e:
                    flash(str(e), "error")
                    conn.close()
                    return redirect(url_for("publish"))
                
                draft = conn.execute(
                    "SELECT * FROM drafts WHERE id = ?", (draft_id,)
                ).fetchone()
                if draft is None:
                    conn.close()
                    flash("Draft not found.", "error")
                    return redirect(url_for("publish"))
                
                if draft["status"] != "approved":
                    conn.close()
                    flash("Draft must be approved before publishing.", "error")
                    return redirect(url_for("publish"))
                
                site = conn.execute(
                    "SELECT * FROM sites WHERE id = ? AND is_active = 1", (site_id,)
                ).fetchone()
                if site is None:
                    conn.close()
                    flash("Site not found or inactive.", "error")
                    return redirect(url_for("publish"))
                
                limit_value = get_setting(conn, "publish_daily_limit", "10") or "10"
                try:
                    daily_limit = int(limit_value)
                except ValueError:
                    daily_limit = 10
                today_prefix = datetime.now(timezone.utc).date().isoformat()
                published_today = conn.execute(
                    "SELECT COUNT(*) AS c FROM publish_log "
                    "WHERE status = 'success' AND created_at LIKE ?",
                    (f"{today_prefix}%",),
                ).fetchone()["c"]
                if published_today >= daily_limit:
                    conn.close()
                    flash("Daily publish limit reached.", "error")
                    return redirect(url_for("publish"))
                
                result = publish_to_site(int(site_id), dict(draft))
                log_publish(int(draft_id), int(site_id), result)
                
                if result["success"]:
                    conn.execute(
                        """
                        INSERT INTO publish_queue
                        (draft_id, site_id, status, published_url, published_at, created_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (draft_id, site_id, "published", result.get("published_url"), utc_now(), utc_now()),
                    )
                    conn.execute(
                        "UPDATE drafts SET status = ?, updated_at = ? WHERE id = ?",
                        ("published", utc_now(), draft_id),
                    )
                    conn.commit()
                    log_security_event("content_published", f"Draft ID: {draft_id}, Site: {site['name']}", current_user.id)
                    flash(f"Published to {site['name']}!", "success")
                else:
                    flash(f"Publishing failed: {result.get('error')}", "error")
                conn.close()
                return redirect(url_for("publish"))
            
            conn.close()
            return redirect(url_for("publish"))
        
        approved = conn.execute(
            "SELECT d.*, t.topic, t.category FROM drafts d "
            "JOIN trend_candidates t ON d.candidate_id = t.id "
            "WHERE d.status = 'approved' ORDER BY d.updated_at DESC"
        ).fetchall()
        
        sites = conn.execute(
            "SELECT * FROM sites WHERE is_active = 1 ORDER BY name"
        ).fetchall()
        
        history = conn.execute(
            "SELECT pl.*, s.name as site_name, d.title as draft_title "
            "FROM publish_log pl "
            "JOIN sites s ON pl.site_id = s.id "
            "JOIN drafts d ON pl.draft_id = d.id "
            "ORDER BY pl.created_at DESC LIMIT 50"
        ).fetchall()
        conn.close()
        
        return render_template(
            "publish.html",
            title=APP_TITLE,
            approved=approved,
            sites=sites,
            history=history,
        )

    @app.route("/settings", methods=["GET", "POST"])
    @login_required
    def settings():
        conn = get_db()
        if request.method == "POST":
            try:
                limit_val = int(sanitize_input(request.form.get("publish_daily_limit", "10"), max_length=10))
                days_back = int(sanitize_input(request.form.get("source_days_back", "7"), max_length=10))
                sources_per = int(sanitize_input(request.form.get("sources_per_trend", "3"), max_length=10))
            except ValueError:
                flash("Numeric values must be valid integers.", "error")
                conn.close()
                return redirect(url_for("settings"))
            
            set_setting(conn, "publish_daily_limit", str(limit_val))
            set_setting(conn, "image_policy_default", sanitize_input(request.form.get("image_policy_default", "none"), max_length=20))
            
            gemini_key = request.form.get("gemini_api_key", "").strip()
            if gemini_key:
                encrypted_key = encrypt_value(gemini_key)
                set_setting(conn, "gemini_api_key", encrypted_key)
            
            set_setting(conn, "source_days_back", str(days_back))
            set_setting(conn, "sources_per_trend", str(sources_per))
            set_setting(conn, "auto_fetch_sources", "true" if request.form.get("auto_fetch_sources") else "false")
            conn.commit()
            log_security_event("settings_updated", f"User: {current_user.username}", current_user.id)
            conn.close()
            flash("Settings updated.", "success")
            return redirect(url_for("settings"))

        encrypted_key = get_setting(conn, "gemini_api_key", "")
        decrypted_key = decrypt_value(encrypted_key) if encrypted_key else ""
        masked_key = mask_value(decrypted_key, 4) if decrypted_key else ""
        
        settings_map = {
            "publish_daily_limit": get_setting(conn, "publish_daily_limit", "10"),
            "image_policy_default": get_setting(conn, "image_policy_default", "none"),
            "gemini_api_key": "",
            "gemini_api_key_masked": masked_key,
            "gemini_api_key_set": bool(encrypted_key),
            "source_days_back": get_setting(conn, "source_days_back", "7"),
            "sources_per_trend": get_setting(conn, "sources_per_trend", "3"),
            "auto_fetch_sources": get_setting(conn, "auto_fetch_sources", "true"),
        }
        conn.close()
        return render_template("settings.html", title=APP_TITLE, settings=settings_map)

    @app.route("/metrics", methods=["GET", "POST"])
    @login_required
    def metrics():
        conn = get_db()
        if request.method == "POST":
            metric_date = sanitize_input(request.form.get("metric_date", "").strip(), max_length=20)
            indexing_rate = sanitize_input(request.form.get("indexing_rate", "").strip() or None, max_length=20)
            queries = sanitize_input(request.form.get("queries", "").strip() or None, max_length=20)
            ctr = sanitize_input(request.form.get("ctr", "").strip() or None, max_length=20)
            avg_position = sanitize_input(request.form.get("avg_position", "").strip() or None, max_length=20)
            notes = sanitize_input(request.form.get("notes", "").strip(), max_length=500)
            if not metric_date:
                conn.close()
                flash("Metric date is required.", "error")
                return redirect(url_for("metrics"))

            conn.execute(
                """
                INSERT INTO metrics
                (metric_date, indexing_rate, queries, ctr, avg_position, notes)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (metric_date, indexing_rate, queries, ctr, avg_position, notes),
            )
            conn.commit()
            conn.close()
            flash("Metrics added.", "success")
            return redirect(url_for("metrics"))

        rows = conn.execute(
            "SELECT * FROM metrics ORDER BY metric_date DESC LIMIT 120"
        ).fetchall()
        conn.close()
        return render_template(
            "metrics.html",
            title=APP_TITLE,
            metrics=rows,
        )

    @app.route("/ai/generate/<int:candidate_id>", methods=["POST"])
    @login_required
    @limiter.limit("20 per hour")
    def ai_generate(candidate_id):
        conn = get_db()
        candidate = conn.execute(
            "SELECT * FROM trend_candidates WHERE id = ?", (candidate_id,)
        ).fetchone()
        if candidate is None:
            conn.close()
            return {"success": False, "error": "Candidate not found"}, 404

        sources_rows = conn.execute(
            "SELECT * FROM source_packs WHERE candidate_id = ?",
            (candidate_id,),
        ).fetchall()
        conn.close()

        sources = [
            {"publisher": s["publisher"], "url": s["url"]}
            for s in sources_rows
        ]

        style = sanitize_input(request.form.get("style", "informative"), max_length=20)
        try:
            word_count = int(request.form.get("word_count", 800))
            word_count = min(max(word_count, 200), 2000)
        except ValueError:
            word_count = 800

        encrypted_key = get_setting(get_db(), "gemini_api_key", "")
        api_key = decrypt_value(encrypted_key) if encrypted_key else None
        
        result = generate_article(
            topic=candidate["topic"],
            sources=sources,
            category=candidate["category"],
            style=style,
            word_count=word_count,
            api_key=api_key
        )

        return result

    @app.route("/ai/improve", methods=["POST"])
    @login_required
    @limiter.limit("30 per hour")
    def ai_improve():
        content = request.form.get("content", "")
        instructions = sanitize_input(request.form.get("instructions", "Improve clarity and flow"), max_length=200)
        
        if not content:
            return {"success": False, "error": "No content provided"}, 400
        
        encrypted_key = get_setting(get_db(), "gemini_api_key", "")
        api_key = decrypt_value(encrypted_key) if encrypted_key else None
        
        result = improve_content(content, instructions, api_key=api_key)
        return result

    @app.route("/ai/headlines", methods=["POST"])
    @login_required
    @limiter.limit("30 per hour")
    def ai_headlines():
        topic = sanitize_input(request.form.get("topic", ""), max_length=200)
        angle = sanitize_input(request.form.get("angle", "news"), max_length=20)
        
        if not topic:
            return {"success": False, "error": "No topic provided"}, 400
        
        encrypted_key = get_setting(get_db(), "gemini_api_key", "")
        api_key = decrypt_value(encrypted_key) if encrypted_key else None
        
        result = generate_headline(topic, angle, api_key=api_key)
        return result

    @app.route("/ai/excerpt", methods=["POST"])
    @login_required
    @limiter.limit("30 per hour")
    def ai_excerpt():
        content = request.form.get("content", "")
        try:
            max_length = int(request.form.get("max_length", 160))
            max_length = min(max(max_length, 50), 300)
        except ValueError:
            max_length = 160
        
        if not content:
            return {"success": False, "error": "No content provided"}, 400
        
        encrypted_key = get_setting(get_db(), "gemini_api_key", "")
        api_key = decrypt_value(encrypted_key) if encrypted_key else None
        
        result = generate_excerpt(content, max_length, api_key=api_key)
        return result

    @app.route("/ai/faqs", methods=["POST"])
    @login_required
    @limiter.limit("30 per hour")
    def ai_faqs():
        topic = sanitize_input(request.form.get("topic", ""), max_length=200)
        context = request.form.get("context", "")
        
        if not topic:
            return {"success": False, "error": "No topic provided"}, 400
        
        encrypted_key = get_setting(get_db(), "gemini_api_key", "")
        api_key = decrypt_value(encrypted_key) if encrypted_key else None
        
        result = generate_faqs(topic, context, api_key=api_key)
        return result

    @app.route("/ai/test", methods=["POST"])
    @login_required
    def ai_test():
        encrypted_key = get_setting(get_db(), "gemini_api_key", "")
        api_key = decrypt_value(encrypted_key) if encrypted_key else None
        result = test_connection(api_key=api_key)
        return result

    return app


if __name__ == "__main__":
    app = create_app()
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug_mode, port=5000)
