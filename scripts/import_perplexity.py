"""
Foundation Import Script
Imports all Perplexity-built skills and industry agent blueprints into:
  1. Supabase foundation.skills + foundation.agents tables
  2. Supabase Storage buckets (skills/ and agent-configs/)

Usage:
  cd scripts
  pip install supabase python-dotenv
  python import_perplexity.py --skills-dir ./perplexity/skills-catalog --agents-dir ./perplexity/agent-industry-library

Or point at your desktop folders:
  python import_perplexity.py \
    --skills-dir "C:/Users/jjces/Desktop/skills-catalog" \
    --agents-dir "C:/Users/jjces/Desktop/ai-agent-industry-library"
"""

import os
import re
import json
import argparse
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv(dotenv_path=Path(__file__).parent.parent / "foundation-api" / ".env")

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_KEY"]

db: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ── CATEGORY MAPPING ─────────────────────────────────────────
CATEGORY_MAP = {
    "Voice Agent": "voice-agents",
    "Chat Agent": "chat-agents",
    "Workflow Automation": "workflow-automation",
    "Content Engine": "content-engine",
    "Marketing": "marketing",
    "Finance": "finance",
    "Analytics": "analytics",
    "HR/People": "hr-people",
    "Compliance": "compliance",
    "Widget": "widgets",
    "Document AI": "document-ai",
    "Workflow": "workflow-automation",
}

INDUSTRY_MAP = {
    "real-estate": ["real-estate"],
    "healthcare": ["healthcare", "medical", "dental"],
    "legal": ["legal"],
    "home-services": ["home-services", "hvac", "plumbing", "electrical"],
    "insurance": ["insurance"],
    "automotive": ["automotive"],
    "financial-mortgage": ["financial", "mortgage", "finance"],
    "restaurant": ["restaurant", "food-service"],
    "salon-spa": ["salon", "spa", "beauty"],
    "veterinary": ["veterinary"],
    "fitness": ["fitness", "gym"],
    "property-management": ["property-management"],
    "recruitment": ["recruitment", "staffing"],
    "construction": ["construction"],
    "ecommerce": ["ecommerce", "retail"],
    "coaching": ["coaching", "consulting"],
    "accounting": ["accounting", "bookkeeping"],
    "chiropractic": ["chiropractic", "wellness"],
    "pest-control-cleaning": ["pest-control", "cleaning"],
    "roofing-solar": ["roofing", "solar"],
    "education": ["education", "tutoring"],
    "logistics": ["logistics", "transportation"],
    "saas": ["saas", "tech"],
    "travel-hospitality": ["travel", "hospitality"],
    "funeral": ["funeral"],
}


# ── SKILL PARSER ─────────────────────────────────────────────
def parse_skills_from_batch(filepath: Path) -> list[dict]:
    """Parse a batch-N.md file into individual skill records."""
    content = filepath.read_text(encoding="utf-8")
    skills = []

    # Split on skill headers
    blocks = re.split(r'\n## (SKILL-\d{3}: .+)', content)

    i = 1
    while i < len(blocks):
        header = blocks[i].strip()
        body = blocks[i + 1] if i + 1 < len(blocks) else ""
        i += 2

        # Parse skill ID and name
        match = re.match(r'(SKILL-(\d{3})): (.+)', header)
        if not match:
            continue

        skill_id = match.group(1)
        skill_num = int(match.group(2))
        skill_name = match.group(3).strip()

        # Extract metadata fields
        category_raw = extract_field(body, "Category") or "General"
        applies_to = extract_field(body, "Applies To") or "All Industries"
        platform = extract_field(body, "Deployment Platform") or ""
        complexity = extract_field(body, "Complexity") or "Medium"
        monthly_value = extract_field(body, "Monthly Value to Client") or ""

        # Map category
        category = CATEGORY_MAP.get(category_raw, category_raw.lower().replace(" ", "-"))

        # Determine industries
        industries = []
        if "All Industries" in applies_to:
            industries = ["all"]
        else:
            for industry, tags in INDUSTRY_MAP.items():
                if any(t.lower() in applies_to.lower() for t in tags):
                    industries.extend(tags)

        # Extract sections
        what_it_does = extract_section(body, "What It Does")
        core_caps = extract_section(body, "Core Capabilities")
        system_prompt = extract_section(body, "Sample System Prompt") or \
                       extract_section(body, "System Prompt") or \
                       extract_section(body, "Voice Script") or ""

        # Build description from What It Does
        description = what_it_does[:500] if what_it_does else f"{skill_name} — {category_raw}"

        slug = f"skill-{skill_num:03d}-{slugify(skill_name)}"

        skill = {
            "name": skill_name,
            "slug": slug,
            "description": description,
            "category": category,
            "prompt_template": system_prompt or what_it_does or "",
            "config": {
                "skill_id": skill_id,
                "skill_number": skill_num,
                "applies_to": applies_to,
                "deployment_platform": platform,
                "complexity": complexity,
                "monthly_value": monthly_value,
                "core_capabilities": core_caps,
                "source_file": filepath.name,
            },
            "industries": industries,
            "platforms": ["automation-nation", "voicemio"],
            "version": "1.0.0",
            "is_active": True,
        }
        skills.append(skill)

    return skills


# ── AGENT PARSER ─────────────────────────────────────────────
def parse_agent_blueprint(filepath: Path) -> dict:
    """Parse an industry blueprint reference file into an agent record."""
    content = filepath.read_text(encoding="utf-8")

    # Get industry from filename
    stem = filepath.stem  # e.g. "01-real-estate"
    num_match = re.match(r'(\d+)-(.+)', stem)
    industry_slug = num_match.group(2) if num_match else stem
    industry_num = int(num_match.group(1)) if num_match else 0

    # Extract title
    title_match = re.search(r'^# (.+)', content, re.MULTILINE)
    industry_name = title_match.group(1).strip() if title_match else industry_slug.replace("-", " ").title()

    # Extract overview
    overview = extract_section(content, "Industry Overview") or ""

    # Extract sub-agents list
    sub_agents_section = extract_section(content, "Sub-Agents Breakdown") or \
                         extract_section(content, "Sub-Agents") or ""

    # Count sub-agents
    agent_count = len(re.findall(r'^### \d+\.', sub_agents_section, re.MULTILINE))

    # Extract sticky features
    sticky = extract_section(content, "Sticky Features") or \
             extract_section(content, "Stickiness Strategy") or ""

    # Extract pricing
    pricing = extract_section(content, "Revenue Model") or \
              extract_section(content, "Pricing") or ""

    industries = INDUSTRY_MAP.get(industry_slug, [industry_slug])

    # Build system prompt from the blueprint
    system_prompt = f"""You are an AI agent ecosystem architect specializing in {industry_name}.

## Industry Context
{overview[:800] if overview else ''}

## Your Capabilities
You have access to {agent_count} specialized sub-agents for this industry vertical, covering:
- Voice agents (inbound/outbound)
- Chat and SMS agents  
- Workflow automation
- Industry-specific widgets and tools
- CRM and pipeline automation
- Compliance and document management

## How to Use This Blueprint
1. Identify the client's top 3 pain points
2. Map pain points to the most relevant sub-agents
3. Build a tiered package (Starter / Professional / Enterprise)
4. Identify the stickiest 2-3 features that create deep dependency
5. Present ROI-focused value proposition

When a client asks about AI for their {industry_name.lower()} business, draw on this complete blueprint to design the optimal solution.
"""

    slug = f"agent-{industry_num:02d}-{industry_slug}-blueprint"

    return {
        "name": f"{industry_name} — AI Agent Blueprint",
        "slug": slug,
        "description": overview[:400] if overview else f"Complete AI agent ecosystem blueprint for {industry_name}",
        "agent_type": "industry-blueprint",
        "system_prompt": system_prompt,
        "tools": [],
        "model": "claude-sonnet-4-20250514",
        "temperature": 0.7,
        "max_tokens": 4096,
        "config": {
            "industry_number": industry_num,
            "industry_slug": industry_slug,
            "sub_agent_count": agent_count,
            "full_blueprint": content[:8000],  # Store full blueprint in config
            "sticky_features": sticky[:1000] if sticky else "",
            "revenue_model": pricing[:500] if pricing else "",
            "source_file": filepath.name,
        },
        "platforms": ["automation-nation", "voicemio"],
        "industries": industries,
        "version": "1.0.0",
        "is_active": True,
    }


# ── HELPERS ──────────────────────────────────────────────────
def extract_field(text: str, field: str) -> str:
    """Extract a metadata field like **Category**: Value"""
    pattern = rf'\*\*{field}\*\*:?\s*(.+?)(?:\n|$)'
    match = re.search(pattern, text)
    return match.group(1).strip() if match else ""


def extract_section(text: str, heading: str) -> str:
    """Extract content under a markdown heading."""
    pattern = rf'### {heading}\n(.*?)(?=\n### |\n## |$)'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    # Try without ###
    pattern2 = rf'## {heading}\n(.*?)(?=\n## |$)'
    match2 = re.search(pattern2, text, re.DOTALL)
    return match2.group(1).strip() if match2 else ""


def slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')[:60]


# ── SUPABASE UPSERT ──────────────────────────────────────────
def upsert_skills(skills: list[dict]) -> tuple[int, int]:
    """Upsert skills into foundation.skills — skip duplicates by slug."""
    inserted = 0
    skipped = 0
    for skill in skills:
        try:
            db.schema("foundation").table("skills").upsert(
                skill, on_conflict="slug"
            ).execute()
            inserted += 1
        except Exception as e:
            print(f"  ⚠️  Skipped {skill['slug']}: {e}")
            skipped += 1
    return inserted, skipped


def upsert_agents(agents: list[dict]) -> tuple[int, int]:
    """Upsert agents into foundation.agents."""
    inserted = 0
    skipped = 0
    for agent in agents:
        try:
            db.schema("foundation").table("agents").upsert(
                agent, on_conflict="slug"
            ).execute()
            inserted += 1
        except Exception as e:
            print(f"  ⚠️  Skipped {agent['slug']}: {e}")
            skipped += 1
    return inserted, skipped


def upload_to_storage(filepath: Path, bucket: str, dest_name: str):
    """Upload a file to Supabase Storage."""
    try:
        content = filepath.read_bytes()
        db.storage.from_(bucket).upload(
            dest_name,
            content,
            {"content-type": "text/markdown", "upsert": "true"}
        )
    except Exception as e:
        print(f"  ⚠️  Storage upload failed for {dest_name}: {e}")


# ── MAIN ─────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Import Perplexity skills + agents into Foundation")
    parser.add_argument("--skills-dir", required=True, help="Path to skills-catalog folder")
    parser.add_argument("--agents-dir", required=True, help="Path to ai-agent-industry-library folder")
    parser.add_argument("--skip-storage", action="store_true", help="Skip Supabase Storage upload")
    args = parser.parse_args()

    skills_dir = Path(args.skills_dir)
    agents_dir = Path(args.agents_dir)

    print("\n🚀 Foundation Import Script")
    print("=" * 50)

    # ── IMPORT SKILLS ────────────────────────────────────────
    print("\n📚 Importing Skills...")
    batch_files = sorted(skills_dir.glob("batch-*.md"))
    if not batch_files:
        print(f"  ❌ No batch-*.md files found in {skills_dir}")
    else:
        all_skills = []
        for bf in batch_files:
            print(f"  Parsing {bf.name}...")
            skills = parse_skills_from_batch(bf)
            print(f"    Found {len(skills)} skills")
            all_skills.extend(skills)

            if not args.skip_storage:
                upload_to_storage(bf, "skills", bf.name)
                print(f"    ✅ Uploaded to skills/ bucket")

        print(f"\n  Upserting {len(all_skills)} skills to Supabase...")
        ins, skip = upsert_skills(all_skills)
        print(f"  ✅ Skills: {ins} upserted, {skip} skipped")

        # Upload master catalog
        master = skills_dir / "00-MASTER-CATALOG.md"
        if master.exists() and not args.skip_storage:
            upload_to_storage(master, "skills", "00-MASTER-CATALOG.md")
            print(f"  ✅ Master catalog uploaded")

    # ── IMPORT AGENT BLUEPRINTS ──────────────────────────────
    print("\n🤖 Importing Industry Agent Blueprints...")
    refs_dir = agents_dir / "references"
    if not refs_dir.exists():
        refs_dir = agents_dir  # fallback if no references subfolder

    ref_files = sorted(refs_dir.glob("*.md"))
    if not ref_files:
        print(f"  ❌ No .md files found in {refs_dir}")
    else:
        all_agents = []
        for rf in ref_files:
            print(f"  Parsing {rf.name}...")
            agent = parse_agent_blueprint(rf)
            all_agents.append(agent)

            if not args.skip_storage:
                upload_to_storage(rf, "agent-configs", rf.name)
                print(f"    ✅ Uploaded to agent-configs/ bucket")

        # Upload SKILL.md master index
        skill_md = agents_dir / "SKILL.md"
        if skill_md.exists() and not args.skip_storage:
            upload_to_storage(skill_md, "agent-configs", "SKILL.md")

        print(f"\n  Upserting {len(all_agents)} blueprints to Supabase...")
        ins, skip = upsert_agents(all_agents)
        print(f"  ✅ Agents: {ins} upserted, {skip} skipped")

    # ── FINAL SUMMARY ────────────────────────────────────────
    print("\n" + "=" * 50)
    print("📊 Verifying counts in Supabase...")
    skills_count = db.schema("foundation").table("skills").select("id", count="exact").execute()
    agents_count = db.schema("foundation").table("agents").select("id", count="exact").execute()
    print(f"  foundation.skills  → {skills_count.count} total rows")
    print(f"  foundation.agents  → {agents_count.count} total rows")
    print("\n✅ Import complete! Foundation library is loaded.")
    print(f"   Test it: GET https://your-foundation-api.onrender.com/skills")
    print(f"            GET https://your-foundation-api.onrender.com/agents?agent_type=industry-blueprint")


if __name__ == "__main__":
    main()
