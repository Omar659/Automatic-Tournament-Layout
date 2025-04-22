# auth_google.py

import os
import requests
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

router = APIRouter(prefix="/auth", tags=["auth"])

# This is used to validate tokens, not for Google OAuth flow
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# Step 1: Generate Google OAuth2 login URL
@router.get("/login_with_google")
async def login_with_google():
    redirect_uri = os.environ["GOOGLE_REDIRECT_URI"]
    client_id = os.environ["GOOGLE_CLIENT_ID"]
    return {
        "url": (
            "https://accounts.google.com/o/oauth2/v2/auth"
            f"?response_type=code"
            f"&client_id={client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&scope=openid%20email%20profile"
            f"&access_type=offline"
            f"&prompt=consent"
        )
    }

# Step 2: Handle redirect from Google with ?code=
@router.get("/callback")
async def auth_google(code: str):
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": os.environ["GOOGLE_CLIENT_ID"],
        "client_secret": os.environ["GOOGLE_CLIENT_SECRET"],
        "redirect_uri": os.environ["GOOGLE_REDIRECT_URI"],
        "grant_type": "authorization_code",
    }

    token_response = requests.post(token_url, data=data)
    if token_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to get token")

    tokens = token_response.json()
    access_token = tokens["access_token"]

    # Get user info
    user_info = requests.get(
        "https://www.googleapis.com/oauth2/v1/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    if user_info.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to get user info")

    return user_info.json()  # 👈 You might want to create a local user here and return your own token

# Step 3: Optional route to decode JWT (for testing)
@router.get("/token")
async def get_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, os.environ["GOOGLE_CLIENT_SECRET"], algorithms=["HS256"])
        return payload
    except JWTError as e:
        raise HTTPException(status_code=401, detail="Invalid token")
