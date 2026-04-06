import os
import httpx
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")


def search_cities(q: str) -> list:
    url = "http://api.openweathermap.org/geo/1.0/direct"
    response = httpx.get(url, params={"q": q, "limit": 5, "appid": API_KEY}, timeout=10)
    response.raise_for_status()
    results = response.json()
    seen = set()
    cities = []
    for r in results:
        label = f"{r['name']}, {r.get('state', r['country'])}, {r['country']}"
        if label not in seen:
            seen.add(label)
            cities.append(label)
    return cities


def get_weather(city: str) -> dict:
    url = "https://api.openweathermap.org/data/2.5/weather"
    response = httpx.get(url, params={"q": city, "appid": API_KEY, "units": "imperial"}, timeout=10)
    if response.status_code == 404:
        raise ValueError(f"City '{city}' not found.")
    response.raise_for_status()
    data = response.json()

    temp_f = round(data["main"]["temp"])
    description = data["weather"][0]["description"]
    humidity = data["main"]["humidity"]
    wind_mph = round(data["wind"]["speed"])

    summary = f"{temp_f}°F, {description}, {wind_mph}mph wind, {humidity}% humidity"

    return {"weather_summary": summary}
