# auth_google.py

import os
from fastapi.responses import RedirectResponse
import requests
from fastapi import APIRouter, HTTPException
from fastapi.security import OAuth2PasswordBearer
from uuid import uuid4
from nicegui import app, ui

from ..models import GoogleUserData, User
from ...main import db

router = APIRouter(prefix="/auth", tags=["auth"])

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

    # Serialize user data and pass via query string
    import urllib.parse

    user_data = user_info.json()
    encoded_user_data = urllib.parse.quote_plus(str(user_data))

    return RedirectResponse(f"/login/finalize?data={encoded_user_data}")


@router.get("/add")
async def add_user(
    id: str, 
    name: str = None, 
    google_user_data: GoogleUserData = None
) -> User:
    if not name:
        assert isinstance(google_user_data, GoogleUserData)
        name = google_user_data.name
    collection = db["Users"]
    # check if a user with that id already exists
    user = await get_user(id=id)
    if not user:
        # creates the User object
        user = User(id=str(uuid4()), name=name, google_user_data=google_user_data)
        # adds it to the DB
        collection.insert_one(user.model_dump())
    return user


@router.get("/get")
async def get_user(id: str) -> User | None:
    collection = db["Users"]
    user = collection.find_one({"id": id})
    if user:
        user = User(**user)
    else:
        user = None
    return user
