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
