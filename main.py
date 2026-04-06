from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from urllib.parse import quote_plus
from weather import get_weather, search_cities
from suggest import get_suggestion
from images import get_cologne_image

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


class SuggestRequest(BaseModel):
    city: str
    activities: str
    preferences: list[str]


@app.get("/")
def root():
    return FileResponse("static/index.html")


@app.get("/cities")
def cities(q: str):
    return search_cities(q)


@app.post("/suggest")
def suggest(request: SuggestRequest):
    try:
        weather = get_weather(request.city)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    suggestion = get_suggestion(request.city, weather["weather_summary"], request.activities, request.preferences)
    image_url = get_cologne_image(suggestion["name"]) if suggestion["name"] else None
    amazon_url = f"https://www.amazon.com/s?k={quote_plus(suggestion['name'])}&tag=levisalmon0c-20" if suggestion["name"] else None
    return {
        "city": request.city,
        "weather_summary": weather["weather_summary"],
        "activities": request.activities,
        "cologne_name": suggestion["name"],
        "suggestion": suggestion["explanation"],
        "image_url": image_url,
        "amazon_url": amazon_url,
    }
