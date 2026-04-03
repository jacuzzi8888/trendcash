import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from .db import get_db, utc_now

sites_bp = Blueprint("sites", __name__, url_prefix="/sites")


@sites_bp.route("/")
def list_sites():
    conn = get_db()
    sites = conn.execute(
        "SELECT * FROM sites ORDER BY created_at DESC"
    ).fetchall()
    
    for site in sites:
        site_dict = dict(site)
        if site["categories"]:
            try:
                site_dict["categories_list"] = json.loads(site["categories"])
            except json.JSONDecodeError:
                site_dict["categories_list"] = []
        else:
            site_dict["categories_list"] = []
    
    conn.close()
    return render_template("sites.html", sites=sites)


@sites_bp.route("/new", methods=["GET", "POST"])
def new_site():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        slug = request.form.get("slug", "").strip().lower().replace(" ", "-")
        niche = request.form.get("niche", "").strip()
        description = request.form.get("description", "").strip()
        api_url = request.form.get("api_url", "").strip()
        api_key = request.form.get("api_key", "").strip()
        categories = request.form.get("categories", "").strip()
        is_active = 1 if request.form.get("is_active") == "on" else 0
        
        if not name or not slug or not niche or not api_url:
            flash("Name, slug, niche, and API URL are required.", "error")
            return redirect(url_for("sites.new_site"))
        
        categories_json = json.dumps([c.strip() for c in categories.split(",") if c.strip()]) if categories else "[]"
        
        conn = get_db()
        try:
            conn.execute(
                """
                INSERT INTO sites (name, slug, niche, description, api_url, api_key, categories, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (name, slug, niche, description, api_url, api_key, categories_json, is_active, utc_now(), utc_now())
            )
            conn.commit()
            flash(f"Site '{name}' created successfully.", "success")
        except Exception as e:
            if "UNIQUE constraint" in str(e):
                flash("A site with this slug already exists.", "error")
            else:
                flash(f"Error creating site: {e}", "error")
        finally:
            conn.close()
        
        return redirect(url_for("sites.list_sites"))
    
    return render_template("site_form.html", site=None)


@sites_bp.route("/<int:site_id>/edit", methods=["GET", "POST"])
def edit_site(site_id):
    conn = get_db()
    site = conn.execute("SELECT * FROM sites WHERE id = ?", (site_id,)).fetchone()
    
    if site is None:
        conn.close()
        flash("Site not found.", "error")
        return redirect(url_for("sites.list_sites"))
    
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        slug = request.form.get("slug", "").strip().lower().replace(" ", "-")
        niche = request.form.get("niche", "").strip()
        description = request.form.get("description", "").strip()
        api_url = request.form.get("api_url", "").strip()
        api_key = request.form.get("api_key", "").strip()
        categories = request.form.get("categories", "").strip()
        is_active = 1 if request.form.get("is_active") == "on" else 0
        
        if not name or not slug or not niche or not api_url:
            flash("Name, slug, niche, and API URL are required.", "error")
            conn.close()
            return redirect(url_for("sites.edit_site", site_id=site_id))
        
        categories_json = json.dumps([c.strip() for c in categories.split(",") if c.strip()]) if categories else "[]"
        
        try:
            conn.execute(
                """
                UPDATE sites SET name = ?, slug = ?, niche = ?, description = ?, 
                api_url = ?, api_key = ?, categories = ?, is_active = ?, updated_at = ?
                WHERE id = ?
                """,
                (name, slug, niche, description, api_url, api_key, categories_json, is_active, utc_now(), site_id)
            )
            conn.commit()
            flash(f"Site '{name}' updated successfully.", "success")
        except Exception as e:
            if "UNIQUE constraint" in str(e):
                flash("A site with this slug already exists.", "error")
            else:
                flash(f"Error updating site: {e}", "error")
        finally:
            conn.close()
        
        return redirect(url_for("sites.list_sites"))
    
    site_dict = dict(site)
    if site["categories"]:
        try:
            site_dict["categories_list"] = json.loads(site["categories"])
        except json.JSONDecodeError:
            site_dict["categories_list"] = []
    else:
        site_dict["categories_list"] = []
    
    conn.close()
    return render_template("site_form.html", site=site_dict)


@sites_bp.route("/<int:site_id>/delete", methods=["POST"])
def delete_site(site_id):
    conn = get_db()
    site = conn.execute("SELECT name FROM sites WHERE id = ?", (site_id,)).fetchone()
    
    if site is None:
        conn.close()
        flash("Site not found.", "error")
        return redirect(url_for("sites.list_sites"))
    
    conn.execute("DELETE FROM sites WHERE id = ?", (site_id,))
    conn.commit()
    conn.close()
    
    flash(f"Site '{site['name']}' deleted.", "success")
    return redirect(url_for("sites.list_sites"))


@sites_bp.route("/<int:site_id>/test", methods=["POST"])
def test_site(site_id):
    conn = get_db()
    site = conn.execute("SELECT * FROM sites WHERE id = ?", (site_id,)).fetchone()
    conn.close()
    
    if site is None:
        flash("Site not found.", "error")
        return redirect(url_for("sites.list_sites"))
    
    import requests
    try:
        response = requests.get(
            site["api_url"].replace("/api/content", "/api/health"),
            timeout=10
        )
        if response.status_code == 200:
            flash(f"Connection to '{site['name']}' successful!", "success")
        else:
            flash(f"Connection failed: HTTP {response.status_code}", "error")
    except Exception as e:
        flash(f"Connection failed: {e}", "error")
    
    return redirect(url_for("sites.list_sites"))
