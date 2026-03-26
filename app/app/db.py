from supabase import create_client, Client
from app.config import SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY


def get_client() -> Client:
    """Read-only client using anon key."""
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


def get_admin_client() -> Client:
    """Write client using service role key (server-side only)."""
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
