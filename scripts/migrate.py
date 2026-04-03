"""
Migration script to transition from old modules to new refactored modules.

Usage:
    python scripts/migrate.py [--backup] [--apply]

Options:
    --backup    Create backup of old files before migration
    --apply     Apply the migration (rename files)
"""

import os
import sys
import shutil
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FILE_MAPPINGS = {
    "app/app.py": "app/app_old.py",
    "app/app_new.py": "app/app.py",
    "app/auth.py": "app/auth_old.py",
    "app/auth_new.py": "app/auth.py",
    "app/sites.py": "app/sites_old.py",
    "app/sites_new.py": "app/sites.py",
    "app/security.py": "app/security_old.py",
    "app/security_new.py": "app/security.py",
    "app/crypto.py": "app/crypto_old.py",
    "app/crypto_new.py": "app/crypto.py",
    "app/db.py": "app/db_old.py",
    "app/database.py": "app/db.py",
    "app/db_turso.py": "app/db_turso_old.py",
    "requirements.txt": "requirements_old.txt",
    "requirements_new.txt": "requirements.txt",
    "requirements-dev.txt": "requirements-dev_old.txt",
    "requirements-dev_new.txt": "requirements-dev.txt",
    "vercel.json": "vercel_old.json",
    "vercel_new.json": "vercel.json",
    "package.json": "package_old.json",
    "package_new.json": "package.json",
    "api/index.py": "api/index_old.py",
    "api/index_new.py": "api/index.py",
}

NEW_FILES = [
    "app/schema.py",
    "app/cache.py",
    "app/logging_config.py",
    "app/tasks.py",
    "app/errors.py",
    "app/migrations.py",
    "app/static/src/input.css",
    ".github/workflows/ci.yml",
    "postcss.config.js",
    "pyproject.toml",
]


def create_backup():
    """Create a backup of files to be modified."""
    backup_dir = os.path.join(BASE_DIR, "backup", datetime.now().strftime("%Y%m%d_%H%M%S"))
    os.makedirs(backup_dir, exist_ok=True)
    
    for old_path in FILE_MAPPINGS.keys():
        src = os.path.join(BASE_DIR, old_path)
        if os.path.exists(src):
            dst = os.path.join(backup_dir, old_path.replace("/", "_"))
            shutil.copy2(src, dst)
            print(f"Backed up: {old_path}")
    
    print(f"\nBackup created in: {backup_dir}")
    return backup_dir


def apply_migration():
    """Apply the migration by renaming/creating files."""
    
    for old_path, new_path in FILE_MAPPINGS.items():
        src = os.path.join(BASE_DIR, old_path)
        dst = os.path.join(BASE_DIR, new_path)
        
        if os.path.exists(src):
            dst_dir = os.path.dirname(dst)
            os.makedirs(dst_dir, exist_ok=True)
            
            if os.path.exists(dst):
                os.remove(dst)
            
            shutil.move(src, dst)
            print(f"Moved: {old_path} -> {new_path}")
        else:
            print(f"Skipped (not found): {old_path}")
    
    for new_file in NEW_FILES:
        path = os.path.join(BASE_DIR, new_file)
        if os.path.exists(path):
            print(f"Confirmed: {new_file}")
        else:
            print(f"Missing: {new_file}")
    
    css_dir = os.path.join(BASE_DIR, "app", "static", "dist")
    os.makedirs(css_dir, exist_ok=True)
    
    print("\n" + "="*50)
    print("Migration complete!")
    print("="*50)
    print("\nNext steps:")
    print("1. pip install -r requirements.txt")
    print("2. pip install -r requirements-dev.txt")
    print("3. npm install")
    print("4. npm run build:css")
    print("5. pytest tests/ -v")
    print("\nEnvironment variables needed:")
    print("- NTC_SECRET_KEY (min 32 characters)")
    print("- REDIS_URL (optional, for production)")
    print("- SENTRY_DSN (optional, for error tracking)")
    print("- TURSO_DATABASE_URL (production)")
    print("- TURSO_AUTH_TOKEN (production)")


def main():
    args = sys.argv[1:]
    
    if "--help" in args or "-h" in args:
        print(__doc__)
        return
    
    do_backup = "--backup" in args
    do_apply = "--apply" in args
    
    if not do_backup and not do_apply:
        print(__doc__)
        print("\nError: Please specify --backup and/or --apply")
        return
    
    if do_backup:
        create_backup()
    
    if do_apply:
        apply_migration()


if __name__ == "__main__":
    main()
