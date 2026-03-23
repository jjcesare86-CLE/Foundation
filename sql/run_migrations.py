"""Run all Foundation SQL migrations against Supabase via Management API."""
import json
import os
import sys
import urllib.request
import urllib.error

PROJECT_REF = "rhtwtoinmiekttvunlzs"
ACCESS_TOKEN = os.environ.get("SUPABASE_ACCESS_TOKEN", "sbp_5fa88f3247289d2136a805a164982a8df4391c5e")
API_URL = f"https://api.supabase.com/v1/projects/{PROJECT_REF}/database/query"

MIGRATIONS = [
    "001_create_schema_and_extensions.sql",
    "002_create_skills.sql",
    "003_create_agents.sql",
    "004_create_brand_profiles.sql",
    "005_create_templates.sql",
    "006_create_client_profiles.sql",
    "007_enable_rls.sql",
    "008_semantic_search_functions.sql",
]

STORAGE_SETUP = "../supabase/storage/setup_buckets.sql"

def run_sql(sql: str, label: str) -> bool:
    data = json.dumps({"query": sql}).encode("utf-8")
    req = urllib.request.Request(
        API_URL,
        data=data,
        headers={
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "FoundationMigrations/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            result = resp.read().decode("utf-8")
            print(f"  OK: {label}")
            return True
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        print(f"  FAIL: {label}")
        print(f"    Status: {e.code}")
        print(f"    Error: {body}")
        return False

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    migrations_dir = os.path.join(script_dir, "migrations")

    print("Running Foundation database migrations...\n")

    all_ok = True
    for filename in MIGRATIONS:
        path = os.path.join(migrations_dir, filename)
        with open(path, "r") as f:
            sql = f.read()
        if not run_sql(sql, filename):
            all_ok = False
            print("  Stopping due to error.")
            break

    if all_ok:
        print("\nRunning storage bucket setup...")
        storage_path = os.path.join(script_dir, STORAGE_SETUP)
        with open(storage_path, "r") as f:
            sql = f.read()
        run_sql(sql, "setup_buckets.sql")

    print("\nDone!")

if __name__ == "__main__":
    main()
