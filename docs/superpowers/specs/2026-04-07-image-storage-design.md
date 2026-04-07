# Fragrance Image Storage Design

**Date:** 2026-04-07

## Overview

Download the 300 Parfumo fragrance images scraped into the `fragrances` table and store them in Supabase Storage. This removes the dependency on Parfumo's CDN at runtime and gives HeavenScent reliable, self-hosted images.

---

## Database

Add `stored_image_url text` column to `fragrances` (already applied via migration):

```sql
alter table fragrances add column if not exists stored_image_url text;
```

The original `image_url` (Parfumo CDN URL) is preserved as a fallback.

---

## Supabase Storage

- Bucket: `fragrance-images` (public, no auth required)
- File path per image: `{fragrance_id}.jpg`
- Public URL format: `https://<project>.supabase.co/storage/v1/object/public/fragrance-images/{fragrance_id}.jpg`

---

## Download Script (`store_images.py`)

One-time script. Naturally resumable: skips rows where `stored_image_url` is already set.

**Steps per fragrance:**
1. Fetch all rows from `fragrances` where `stored_image_url` is null and `image_url` is not null
2. Download the image from `image_url` as-is (no query params appended)
3. Upload image bytes to Supabase Storage as `fragrance-images/{fragrance_id}.jpg`
4. Update `fragrances.stored_image_url` to the public Storage URL
5. Log progress; skip and log failures without crashing

**Execution:** Sequential (one image at a time). ~300 images, expected to complete in 1-2 minutes.

---

## App Update (`main.py`)

Add `stored_image_url` to the fields selected in `/fragrances/search`:

```python
.select("id, name, brand, gender, image_url, stored_image_url, rating, rating_count")
```

The frontend prefers `stored_image_url` when available, falls back to `image_url`.

---

## Out of Scope

- Re-downloading images already stored (script is append-only)
- Updating `collections` table image references
- Any UI changes beyond receiving the new field
