"""
Stripe read access for Zacchaeus, via connection_broker.

TODO (blocked on item C, Connections Hub): connection_broker today only has
the Fernet encrypt/decrypt primitives (app/app/services/connection_broker.py)
— there is no OAuth flow, no get_valid_token(), and no live Stripe
connection has ever been created for any client. This module is a stub
that makes that gap loud rather than silent: has_stripe_connection() always
returns False right now (nothing in foundation.client_connections has
provider='stripe' yet — checked, not assumed), and fetch_transactions()
raises NotImplementedError rather than pretending to return real data.

When item C ships a real get_valid_token(client_id, "stripe"):
  1. Replace fetch_transactions() body with a real
     stripe.Charge.list()/PaymentIntent.list() call using that token.
  2. Delete the NotImplementedError branch below.
Everything else in this Zacchaeus build (categorization, deadlines, 1099
sweep) works against whatever is in foundation.zb_transactions regardless
of how it got there — real Stripe sync or the synthetic backfill seed
(scripts/zacchaeus_backfill_seed.py) used in place of it for now.
"""
from app.database import supabase


def has_stripe_connection(client_id: str) -> bool:
    result = (
        supabase.schema("foundation").table("client_connections")
        .select("id").eq("client_id", client_id).eq("provider", "stripe").eq("status", "active")
        .execute()
    )
    return bool(result.data)


def fetch_transactions(client_id: str, since_days: int = 90) -> list[dict]:
    if not has_stripe_connection(client_id):
        raise NotImplementedError(
            f"no active Stripe connection for client {client_id} — Connections Hub "
            f"(item C) hasn't shipped a real OAuth flow yet. Not returning fake data."
        )
    # TODO: real stripe.Charge.list(...) call once connection_broker.get_valid_token exists.
    raise NotImplementedError("live Stripe fetch not implemented yet — see module docstring")
