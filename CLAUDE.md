# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the App

```bash
# Activate virtual environment first
source venv/Scripts/activate  # Windows/Git Bash
# or
venv\Scripts\activate         # Windows CMD

# Start development server
uvicorn main:app --reload

# Start production server
uvicorn main:app
```

The app runs on `http://localhost:8000` by default.

## Architecture

This is a FastAPI application that recommends fragrances based on weather and user activities.

**Request flow:**
1. Frontend (`static/index.html`) sends `POST /suggest` with `{city, activities, preferences[]}`
2. `main.py` calls `weather.py` → OpenWeather API to get current conditions
3. `main.py` calls `suggest.py` → Google Gemini (`gemini-2.5-flash-lite`) with the weather + user inputs
4. Returns `{city, weather_summary, activities, suggestion}` JSON to the frontend

**Key files:**
- `main.py` — FastAPI app, `SuggestRequest` Pydantic model, `/suggest` endpoint, static file serving
- `weather.py` — `get_weather(city)` using httpx + OpenWeather API
- `suggest.py` — `get_suggestion(city, weather_summary, activities, preferences)` using Google Gemini
- `static/index.html` — Single-page frontend with toggle-based preference selectors

## Environment Variables

Required in `.env`:
- `GEMINI_API_KEY` — Google Gemini (used for suggestions)
- `OPENWEATHER_API_KEY` — OpenWeather API (used for weather data)
- `ANTHROPIC_API_KEY` — Present in `.env` but not currently used by the app

## Dependencies

No `requirements.txt` exists — dependencies are only in the `venv`. To export:
```bash
pip freeze > requirements.txt
```

Key packages: `fastapi`, `uvicorn`, `httpx`, `python-dotenv`, `google-genai`, `pydantic`
