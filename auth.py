import os
import httpx
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
) -> dict:
    token = credentials.credentials
    response = httpx.get(
        f"{SUPABASE_URL}/auth/v1/user",
        headers={
            "Authorization": f"Bearer {token}",
            "apikey": SUPABASE_SERVICE_ROLE_KEY,
        },
        timeout=10,
    )
    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = response.json()
    return {"user_id": user["id"], "email": user["email"]}
