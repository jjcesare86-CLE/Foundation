"""
app/database.py
Supabase singleton — used by employees.py and any future router that
prefers the singleton pattern over per-call factory functions.

Wraps the existing app/db.py admin-client factory so callers get a
simple `from app.database import supabase` import.
"""

from app.db import get_admin_client

# Module-level singleton. Created at import time, reused by all callers.
supabase = get_admin_client()
