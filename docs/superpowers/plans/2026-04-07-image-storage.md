# Fragrance Image Storage Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Download 300 Parfumo fragrance images into Supabase Storage and update the app to serve them.

**Architecture:** A one-time migration script (`store_images.py`) fetches each fragrance row, downloads the image from Parfumo, uploads it to a public Supabase Storage bucket, and writes the resulting public URL back to `fragrances.stored_image_url`. The FastAPI search endpoint is then updated to return `stored_image_url` alongside the existing `image_url`.

**Tech Stack:** Python, supabase-py (storage3), requests, python-dotenv

---

## File Map

| Action | File | Purpose |
|--------|------|---------|
| Create | `store_images.py` | One-time migration: download images, upload to Storage, update DB |
| Modify | `main.py:46` | Add `stored_image_url` to `/fragrances/search` select fields |

---

### Task 1: Write store_images.py

**Files:**
- Create: `store_images.py`

- [ ] **Step 1: Create store_images.py**

```python
"""
One-time script: downloads Parfumo fragrance images into Supabase Storage.

- Skips rows that already have stored_image_url set (safe to re-run)
- Logs failures without crashing

Run:
    python store_images.py
"""

import os
import requests
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

BUCKET = "fragrance-images"
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")


def ensure_bucket(supabase):
    existing = [b.name for b in supabase.storage.list_buckets()]
    if BUCKET not in existing:
        supabase.storage.create_bucket(BUCKET, options={"public": True})
        print(f"Created bucket '{BUCKET}'")
    else:
        print(f"Bucket '{BUCKET}' already exists")


def main():
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    ensure_bucket(supabase)

    result = (
        supabase.table("fragrances")
        .select("id, image_url")
        .is_("stored_image_url", "null")
        .not_.is_("image_url", "null")
        .execute()
    )
    fragrances = result.data
    total = len(fragrances)
    print(f"Found {total} fragrances to process")

    ok = 0
    failed = 0

    for i, row in enumerate(fragrances, 1):
        fid = row["id"]
        image_url = row["image_url"]
        filename = f"{fid}.jpg"

        try:
            resp = requests.get(image_url, timeout=15)
            resp.raise_for_status()

            supabase.storage.from_(BUCKET).upload(
                path=filename,
                file=resp.content,
                file_options={"content-type": "image/jpeg", "upsert": "true"},
            )

            public_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{filename}"

            supabase.table("fragrances").update(
                {"stored_image_url": public_url}
            ).eq("id", fid).execute()

            ok += 1
            print(f"  [{i}/{total}] OK  {row['image_url']}")

        except Exception as e:
            failed += 1
            print(f"  [{i}/{total}] FAIL {image_url} — {e}")

    print(f"\nDone. Success: {ok}, Failed: {failed}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Do a dry-run sanity check — verify the script can connect and finds rows**

Run:
```bash
python -c "
from dotenv import load_dotenv; load_dotenv()
import os
from supabase import create_client
sb = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_ROLE_KEY'))
r = sb.table('fragrances').select('id, image_url').is_('stored_image_url', 'null').not_.is_('image_url', 'null').limit(3).execute()
print(r.data)
"
```

Expected: prints 3 fragrance rows with `id` and `image_url` fields. If you see an empty list, the `stored_image_url` column may already be populated or `image_url` is null for all rows — check the DB before running the full script.

- [ ] **Step 3: Run the migration**

```bash
python store_images.py
```

Expected output (example):
```
Bucket 'fragrance-images' already exists
Found 300 fragrances to process
  [1/300] OK  https://media.parfumo.com/perfumes/...
  [2/300] OK  https://media.parfumo.com/perfumes/...
  ...
  [300/300] OK  https://media.parfumo.com/perfumes/...

Done. Success: 300, Failed: 0
```

A non-zero failure count is OK — note the failed URLs and re-run (the script skips already-stored rows). If failures persist, check whether the Parfumo URLs are valid.

- [ ] **Step 4: Spot-check a stored URL in the browser**

Run:
```bash
python -c "
from dotenv import load_dotenv; load_dotenv()
import os
from supabase import create_client
sb = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_ROLE_KEY'))
r = sb.table('fragrances').select('name, stored_image_url').not_.is_('stored_image_url', 'null').limit(3).execute()
for row in r.data: print(row['name'], '->', row['stored_image_url'])
"
```

Open one of the printed URLs in a browser — it should load the fragrance image directly.

- [ ] **Step 5: Commit**

```bash
git add store_images.py
git commit -m "feat: add store_images migration script"
```

---

### Task 2: Update /fragrances/search to return stored_image_url

**Files:**
- Modify: `main.py:46`

- [ ] **Step 1: Update the select fields in the search endpoint**

In `main.py`, find the `/fragrances/search` endpoint (around line 46). Change:

```python
.select("id, name, brand, gender, image_url, rating, rating_count")
```

to:

```python
.select("id, name, brand, gender, image_url, stored_image_url, rating, rating_count")
```

- [ ] **Step 2: Verify the endpoint returns the new field**

Start the server (`uvicorn main:app --reload`) and in a second terminal run:

```bash
curl "http://localhost:8000/fragrances/search?q=spice" | python -m json.tool
```

Expected: each result object now includes a `"stored_image_url"` key (either a Supabase Storage URL or `null` for any rows not yet migrated).

- [ ] **Step 3: Commit**

```bash
git add main.py
git commit -m "feat: include stored_image_url in fragrance search results"
```
