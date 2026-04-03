"""
Site management module with encrypted API keys.
"""

import json
from typing import Optional, Dict, List

from flask import Blueprint, flash, redirect, render_template, request, url_for

from .database import get_db, utc_now
from .security_new import validator, sanitize_input, validate_url
from .crypto_new import encrypt_value, decrypt_value, mask_value
from .logging_config import log_info, log_error


sites_bp = Blueprint("sites", __name__, url_prefix="/sites")


def encrypt_site_credentials(api_key: str) -> str:
    """Encrypt site API key before storage."""
    if not api_key:
        return ""
    return encrypt_value(api_key)


def decrypt_site_credentials(encrypted_key: str) -> str:
    """Decrypt site API key for use."""
    if not encrypted_key:
        return ""
    return decrypt_value(encrypted_key)


def mask_site_credentials(api_key: str) -> str:
    """Mask site API key for display."""
    if not api_key:
        return ""
    return mask_value(api_key, 4)


def prepare_site_for_display(site: dict) -> dict:
    """Prepare site dict for display, masking sensitive data."""
    site_dict = dict(site)
    
    if site_dict.get("api_key"):
        decrypted = decrypt_site_credentials(site_dict["api_key"])
        site_dict["api_key_masked"] = mask_site_credentials(decrypted)
        site_dict["api_key_set"] = True
    else:
        site_dict["api_key_masked"] = ""
        site_dict["api_key_set"] = False
    
    if site_dict.get("categories"):
        try:
            site_dict["categories_list"] = json.loads(site_dict["categories"])
        except json.JSONDecodeError:
            site_dict["categories_list"] = []
    else:
        site_dict["categories_list"] = []
    
    return site_dict


@sites_bp.route("/")
def list_sites():
    with get_db() as conn:
        sites = conn.execute(
            "SELECT * FROM sites ORDER BY created_at DESC"
        ).fetchall()
    
    sites_display = [prepare_site_for_display(site) for site in sites]
    
    return render_template("sites.html", sites=sites_display)


@sites_bp.route("/new", methods=["GET", "POST"])
def new_site():
    if request.method == "POST":
        try:
            name = sanitize_input(request.form.get("name", "").strip(), max_length=100)
            slug = sanitize_input(
                request.form.get("slug", "").strip().lower().replace(" ", "-"), max_length=50
            )
            niche = sanitize_input(request.form.get("niche", "").strip(), max_length=50)
            description = sanitize_input(request.form.get("description", "").strip(), max_length=500)
            api_url = sanitize_input(request.form.get("api_url", "").strip(), max_length=2048)
            api_key = request.form.get("api_key", "").strip()
            categories = sanitize_input(request.form.get("categories", "").strip(), max_length=500)
            is_active = 1 if request.form.get("is_active") == "on" else 0
            
            if not name:
                raise ValueError("Site name is required")
            if not slug:
                raise ValueError("Site slug is required")
            if not niche:
                raise ValueError("Site niche is required")
            if not api_url:
                raise ValueError("API URL is required")
            
            validate_url(api_url, require_https=True)
            
            if not slug.replace("-", "").replace("_", "").isalnum():
                raise ValueError("Slug can only contain letters, numbers, hyphens, and underscores")
        
        except ValueError as e:
            flash(str(e), "error")
            return redirect(url_for("sites.new_site"))
        
        categories_json = json.dumps(
            [c.strip() for c in categories.split(",") if c.strip()]
        ) if categories else "[]"
        
        encrypted_api_key = encrypt_site_credentials(api_key) if api_key else ""
        
        with get_db() as conn:
            try:
                conn.execute(
                    """INSERT INTO sites 
                    (name, slug, niche, description, api_url, api_key, categories, is_active, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (name, slug, niche, description, api_url, encrypted_api_key, 
                     categories_json, is_active, utc_now(), utc_now())
                )
                conn.commit()
                
                log_info("Site created", name=name, slug=slug)
                flash(f"Site '{name}' created successfully.", "success")
            
            except Exception as e:
                if "UNIQUE constraint" in str(e):
                    flash("A site with this slug already exists.", "error")
                else:
                    log_error("Failed to create site", exception=e)
                    flash(f"Error creating site: {e}", "error")
        
        return redirect(url_for("sites.list_sites"))
    
    return render_template("site_form.html", site=None)


@sites_bp.route("/<int:site_id>/edit", methods=["GET", "POST"])
def edit_site(site_id: int):
    with get_db() as conn:
        site = conn.execute(
            "SELECT * FROM sites WHERE id = ?", (site_id,)
        ).fetchone()
        
        if site is None:
            flash("Site not found.", "error")
            return redirect(url_for("sites.list_sites"))
        
        if request.method == "POST":
            try:
                name = sanitize_input(request.form.get("name", "").strip(), max_length=100)
                slug = sanitize_input(
                    request.form.get("slug", "").strip().lower().replace(" ", "-"), max_length=50
                )
                niche = sanitize_input(request.form.get("niche", "").strip(), max_length=50)
                description = sanitize_input(request.form.get("description", "").strip(), max_length=500)
                api_url = sanitize_input(request.form.get("api_url", "").strip(), max_length=2048)
                api_key = request.form.get("api_key", "").strip()
                categories = sanitize_input(request.form.get("categories", "").strip(), max_length=500)
                is_active = 1 if request.form.get("is_active") == "on" else 0
                
                if not name:
                    raise ValueError("Site name is required")
                if not slug:
                    raise ValueError("Site slug is required")
                if not niche:
                    raise ValueError("Site niche is required")
                if not api_url:
                    raise ValueError("API URL is required")
                
                validate_url(api_url, require_https=True)
            
            except ValueError as e:
                flash(str(e), "error")
                return redirect(url_for("sites.edit_site", site_id=site_id))
            
            categories_json = json.dumps(
                [c.strip() for c in categories.split(",") if c.strip()]
            ) if categories else "[]"
            
            if api_key:
                encrypted_api_key = encrypt_site_credentials(api_key)
            else:
                encrypted_api_key = site["api_key"]
            
            try:
                conn.execute(
                    """UPDATE sites SET 
                    name = ?, slug = ?, niche = ?, description = ?, 
                    api_url = ?, api_key = ?, categories = ?, is_active = ?, updated_at = ?
                    WHERE id = ?""",
                    (name, slug, niche, description, api_url, encrypted_api_key, 
                     categories_json, is_active, utc_now(), site_id)
                )
                conn.commit()
                
                log_info("Site updated", site_id=site_id, name=name)
                flash(f"Site '{name}' updated successfully.", "success")
            
            except Exception as e:
                if "UNIQUE constraint" in str(e):
                    flash("A site with this slug already exists.", "error")
                else:
                    log_error("Failed to update site", exception=e)
                    flash(f"Error updating site: {e}", "error")
            
            return redirect(url_for("sites.list_sites"))
        
        site_display = prepare_site_for_display(site)
    
    return render_template("site_form.html", site=site_display)


@sites_bp.route("/<int:site_id>/delete", methods=["POST"])
def delete_site(site_id: int):
    with get_db() as conn:
        site = conn.execute(
            "SELECT name FROM sites WHERE id = ?", (site_id,)
        ).fetchone()
        
        if site is None:
            flash("Site not found.", "error")
            return redirect(url_for("sites.list_sites"))
        
        conn.execute("DELETE FROM sites WHERE id = ?", (site_id,))
        conn.commit()
        
        log_info("Site deleted", site_id=site_id, name=site["name"])
        flash(f"Site '{site['name']}' deleted.", "success")
    
    return redirect(url_for("sites.list_sites"))


@sites_bp.route("/<int:site_id>/test", methods=["POST"])
def test_site(site_id: int):
    import requests
    from .tasks import ExternalAPICaller
    
    api_caller = ExternalAPICaller(max_retries=1, timeout=10)
    
    with get_db() as conn:
        site = conn.execute(
            "SELECT * FROM sites WHERE id = ?", (site_id,)
        ).fetchone()
        
        if site is None:
            flash("Site not found.", "error")
            return redirect(url_for("sites.list_sites"))
        
        api_key = decrypt_site_credentials(site["api_key"]) if site["api_key"] else ""
        
        def _test_connection():
            health_url = site["api_url"].replace("/api/content", "/api/health")
            headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
            
            response = requests.get(health_url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        
        result = api_caller.call(_test_connection)
        
        if result["success"]:
            flash(f"Connection to '{site['name']}' successful!", "success")
        else:
            flash(f"Connection failed: {result['error']}", "error")
    
    return redirect(url_for("sites.list_sites"))


def get_site_by_id(site_id: int) -> Optional[Dict]:
    """Get site by ID with decrypted credentials."""
    with get_db() as conn:
        site = conn.execute(
            "SELECT * FROM sites WHERE id = ?", (site_id,)
        ).fetchone()
        
        if site is None:
            return None
        
        site_dict = dict(site)
        if site_dict.get("api_key"):
            site_dict["api_key_decrypted"] = decrypt_site_credentials(site_dict["api_key"])
        else:
            site_dict["api_key_decrypted"] = ""
        
        return site_dict


def get_active_sites() -> List[Dict]:
    """Get all active sites."""
    with get_db() as conn:
        sites = conn.execute(
            "SELECT * FROM sites WHERE is_active = 1 ORDER BY name"
        ).fetchall()
        
        result = []
        for site in sites:
            site_dict = dict(site)
            if site_dict.get("api_key"):
                site_dict["api_key_decrypted"] = decrypt_site_credentials(site_dict["api_key"])
            else:
                site_dict["api_key_decrypted"] = ""
            result.append(site_dict)
        
        return result
