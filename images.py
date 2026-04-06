import os
import io
import base64
import httpx
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_KEY")


def remove_background(img: Image.Image, threshold: int = 245) -> Image.Image:
    """Flood-fill from corners to remove white/near-white background."""
    img = img.convert("RGBA")
    width, height = img.size
    pixels = img.load()

    def is_bg(x, y):
        r, g, b, a = pixels[x, y]
        return r >= threshold and g >= threshold and b >= threshold

    visited = set()
    stack = [(0, 0), (width - 1, 0), (0, height - 1), (width - 1, height - 1)]

    while stack:
        x, y = stack.pop()
        if (x, y) in visited or not (0 <= x < width and 0 <= y < height):
            continue
        visited.add((x, y))
        if is_bg(x, y):
            r, g, b, a = pixels[x, y]
            pixels[x, y] = (r, g, b, 0)
            stack += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]

    return img


def trim_transparent(img: Image.Image) -> Image.Image:
    """Crop out transparent padding."""
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    bbox = img.split()[3].getbbox()
    return img.crop(bbox) if bbox else img


def get_cologne_image(cologne_name: str) -> str | None:
    try:
        response = httpx.get(
            "https://serpapi.com/search.json",
            params={
                "engine": "google_images",
                "q": f"{cologne_name} cologne bottle transparent png",
                "api_key": SERPAPI_KEY,
                "tbs": "ic:trans",
                "num": 1,
            },
            timeout=10,
        )
        response.raise_for_status()
        items = response.json().get("images_results", [])
        if not items:
            return None

        img_response = httpx.get(items[0]["original"], timeout=10, follow_redirects=True)
        img_response.raise_for_status()

        img = Image.open(io.BytesIO(img_response.content))
        img = remove_background(img)
        img = trim_transparent(img)

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        b64 = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{b64}"
    except Exception:
        pass
    return None
