# initialize MongoDB Atlas
import os
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from typing import Final

MIN_NAME_LENGTH: Final[int] = 4
MAX_NAME_LENGTH: Final[int] = 32
LEGAL_CHARACTERS_RE: Final[str] = r"^[a-zA-Z0-9 \-_@#&?!+=]+$"
NAMES_VALIDATION_RE: Final[str] = "".join([
    LEGAL_CHARACTERS_RE[:-2],
    r"{",
    f"{MIN_NAME_LENGTH},{MAX_NAME_LENGTH}",
    r"}$",
])

load_dotenv(".env")
mongo_client = MongoClient(
    f"mongodb+srv://rom42pla:{os.environ['MONGODB_ATLAS_PASSWORD']}@cluster0.fg01xsr.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
)
global db
db = mongo_client["Storage"]


# initialize FastAPI
from fastapi import FastAPI

fastapi_app = FastAPI()
from .backend.apis import players, games, tournaments, auth

for router_file in [players, games, tournaments, auth]:
    fastapi_app.include_router(router=router_file.router)

# initialize NiceGUI
from nicegui import app as nicegui_app, ui
from .frontend.pages import index, create_tournament, players, player_page, settings

ui.run_with(
    fastapi_app,
    storage_secret="pick your private secret here",  # NOTE setting a secret is optional but allows for persistent storage per user
)
