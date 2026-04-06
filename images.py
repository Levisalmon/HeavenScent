import os
import httpx
from dotenv import load_dotenv

load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_KEY")



def get_cologne_image(cologne_name: str) -> str | None:
    try:
        response = httpx.get(
            "https://serpapi.com/search.json",
            params={
                "engine": "google_images",
                "q": f"{cologne_name} transparent filetype:png",
                "api_key": SERPAPI_KEY,
                "tbs": "ic:trans",
                "num": 5,
            },
            timeout=10,
        )
        response.raise_for_status()
        items = response.json().get("images_results", [])
        if not items:
            return None

        for item in items:
            url = item.get("original", "")
            if url:
                return url
        return None
    except Exception:
        pass
    return None
