import os
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def get_suggestion(city: str, weather_summary: str, activities: str, preferences: list) -> dict:
    pref_str = " or ".join(preferences)
    prompt = (
        f"You are a fragrance expert. The weather today in {city} is {weather_summary}. "
        f"The person's plans for the day: {activities}. "
        f"Only suggest fragrances categorized as: {pref_str}. "
        f"Suggest ONE single fragrance and briefly explain why it suits the day. "
        f"Respond with a JSON object with two fields: "
        f"\"name\" (the full cologne name including brand, e.g. \"Dior Sauvage\") and "
        f"\"explanation\" (your explanation). Return only the JSON, no markdown."
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt,
    )

    try:
        text = response.text.strip()
        # Strip markdown code fences if present
        if text.startswith("```"):
            text = text.split("\n", 1)[-1]
            text = text.rsplit("```", 1)[0].strip()
        data = json.loads(text)
        return {"name": data["name"], "explanation": data["explanation"]}
    except Exception:
        return {"name": None, "explanation": response.text}
