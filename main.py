from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from urllib.parse import quote_plus
from weather import get_weather, search_cities
from suggest import get_suggestion
from images import get_cologne_image
from auth import get_current_user
from database import supabase

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


class SuggestRequest(BaseModel):
    city: str
    activities: str
    preferences: list[str]


class CollectionItemCreate(BaseModel):
    cologne_name: str
    brand: str | None = None
    notes: str | None = None
    image_url: str | None = None
    amazon_url: str | None = None


@app.get("/")
def root():
    return FileResponse("static/index.html")


@app.get("/cities")
def cities(q: str):
    return search_cities(q)


@app.get("/collection")
def get_collection(user: dict = Depends(get_current_user)):
    result = (
        supabase.table("collections")
        .select("*")
        .eq("user_id", user["user_id"])
        .order("added_at", desc=True)
        .execute()
    )
    return result.data


@app.post("/collection", status_code=201)
def add_to_collection(item: CollectionItemCreate, user: dict = Depends(get_current_user)):
    existing = (
        supabase.table("collections")
        .select("id")
        .eq("user_id", user["user_id"])
        .eq("cologne_name", item.cologne_name)
        .execute()
    )
    if existing.data:
        raise HTTPException(status_code=409, detail="Fragrance already in collection")

    result = (
        supabase.table("collections")
        .insert({
            "user_id": user["user_id"],
            "cologne_name": item.cologne_name,
            "brand": item.brand,
            "notes": item.notes,
            "image_url": item.image_url,
            "amazon_url": item.amazon_url,
        })
        .execute()
    )
    return result.data[0]


@app.delete("/collection/{item_id}")
def delete_from_collection(item_id: str, user: dict = Depends(get_current_user)):
    result = (
        supabase.table("collections")
        .delete()
        .eq("id", item_id)
        .eq("user_id", user["user_id"])
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"ok": True}


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
