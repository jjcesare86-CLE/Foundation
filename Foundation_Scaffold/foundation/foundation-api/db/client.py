"""Supabase async client for foundation-api"""

import os
from supabase import create_client, Client

_client: Client | None = None

async def init_db():
    global _client
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_SERVICE_KEY"]   # Service role key (bypasses RLS)
    _client = create_client(url, key)
    print("✅ Supabase connected")

def get_db() -> Client:
    if _client is None:
        raise RuntimeError("DB not initialized — call init_db() first")
    return _client
