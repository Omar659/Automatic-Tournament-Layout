import hashlib
import os
import re
from typing import Final
from fastapi.responses import RedirectResponse
import requests
from fastapi import APIRouter, HTTPException

from ..models import GoogleUserData, User
from ...main import db, LEGAL_CHARACTERS_RE

COLLECTION: Final[str] = "users"
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
    name: str = None, 
    google_user_data: GoogleUserData = None
) -> User:
    if not name:
        assert isinstance(google_user_data, GoogleUserData)
        name = google_user_data.name
    # generates an id for the user which is always the same, based on Google's ID
    sha512 = hashlib.sha512(os.environ["HASH_INIT"].encode())
    sha512.update(google_user_data.id.encode())
    user_id = sha512.hexdigest()[:32].zfill(32)
    # check if a user with that id already exists
    user = await get_user(id=user_id)
    if not user:
        # creates the User object
        user = User(id=user_id, name=name, google_user_data=google_user_data)
        # adds it to the DB
        COLLECTION.insert_one(user.model_dump())
    return user


@router.get("/get")
async def get_user(id: str | None = None, name: str | None = None) -> User | None:
    if not any([id, name]):
        raise HTTPException(status_code=404, detail="No parameters were given")
    query = []
    if id:
        query.append({"id": id})
    if name:
        query.append({"name": name})
    user = COLLECTION.find_one({"$or": query})
    if user:
        user = User(**user)
    else:
        user = None
    return user


@router.get("/delete")
async def delete_user(id: str | None = None, name: str | None = None) -> User | None:
    if not any([id, name]):
        raise HTTPException(status_code=404, detail="No parameters were given")
    query = []
    if id:
        query.append({"id": id})
    if name:
        query.append({"name": name})
    COLLECTION.delete_one({"$or": query})


@router.get("/change_name")
async def change_user_name(id: str, new_name: str) -> User | None:
    # checks if the new name is valid
    if not re.fullmatch(LEGAL_CHARACTERS_RE, new_name):
        raise HTTPException(status_code=404, detail="New name contains invalid characters, or is too short or too long")
    # if the name is valid, check that there are no other users with the same name
    user_with_same_name = await get_user(name=new_name)
    if user_with_same_name:
         raise HTTPException(status_code=404, detail="There already is a user with same name")
    # if all controls have passed, proceed with name change
    COLLECTION.update_one(
        filter={"id": id},
        update={
            "$set": {
                "name": new_name,
            }
        }
    )
    return await get_user(id=id)
