from cryptography.fernet import Fernet
import os

_ENCRYPTION_KEY = os.getenv("CONNECTION_BROKER_ENCRYPTION_KEY")
if not _ENCRYPTION_KEY:
    raise RuntimeError("CONNECTION_BROKER_ENCRYPTION_KEY not set — refusing to start")

_fernet = Fernet(_ENCRYPTION_KEY.encode())


def encrypt_token(plaintext: str) -> str:
    """Encrypt a token for storage. Returns a URL-safe base64 string."""
    return _fernet.encrypt(plaintext.encode()).decode()


def decrypt_token(ciphertext: str) -> str:
    """Decrypt a stored token. Raises InvalidToken on bad key/data."""
    return _fernet.decrypt(ciphertext.encode()).decode()


# --- Usage in the OAuth callback endpoint ---
# After exchanging the auth code for tokens:
#
#   from app.services.connection_broker import encrypt_token
#
#   encrypted_access = encrypt_token(access_token)
#   encrypted_refresh = encrypt_token(refresh_token)
#
#   # Store in client_connections:
#   await supabase.table("client_connections").upsert({
#       "client_id": client_id,
#       "provider": provider,
#       "access_token_encrypted": encrypted_access,
#       "refresh_token_encrypted": encrypted_refresh,
#       ...
#   })
#
# --- Usage when an agent needs to act ---
#
#   from app.services.connection_broker import decrypt_token
#
#   row = await supabase.table("client_connections") \
#       .select("access_token_encrypted") \
#       .eq("client_id", client_id) \
#       .eq("provider", "google") \
#       .single()
#
#   access_token = decrypt_token(row["access_token_encrypted"])
#   # Use access_token for the API call — never log it, never return it
