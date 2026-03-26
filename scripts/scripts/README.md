# Foundation Import Scripts

## import_perplexity.py

Imports all 165 Perplexity-built skills and 25 industry agent blueprints into:
- `foundation.skills` table in Supabase
- `foundation.agents` table in Supabase
- `skills/` and `agent-configs/` Supabase Storage buckets

### Setup (run once)
```powershell
cd scripts
pip install supabase python-dotenv
```

### Run the Import
```powershell
python import_perplexity.py `
  --skills-dir "../skills-library" `
  --agents-dir "../agents-library"
```

### Expected Output
```
📚 Importing Skills...
  batch-1-universal.md: 40 skills parsed
  batch-2-industry-a.md: 40 skills parsed
  batch-3-industry-b.md: 40 skills parsed
  batch-4-niche-advanced.md: 45 skills parsed
  ✅ Skills: 165 upserted, 0 skipped

🤖 Importing Industry Agent Blueprints...
  ✅ Agents: 25 upserted, 0 skipped

foundation.skills  → 173 total rows  (165 + 8 from seed)
foundation.agents  → 38 total rows   (25 + 13 from seed)
✅ Import complete!
```

### Skip Storage Upload (faster, DB only)
```powershell
python import_perplexity.py `
  --skills-dir "../skills-library" `
  --agents-dir "../agents-library" `
  --skip-storage
```

### Re-run Safely
The script uses `upsert` with `on_conflict="slug"` so it's safe to run
multiple times — it updates existing records rather than creating duplicates.
