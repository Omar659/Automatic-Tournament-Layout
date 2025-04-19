import os

from dotenv import load_dotenv
from nicegui import app as nicegui_app, ui
from pymongo.mongo_client import MongoClient

# FastAPI
from fastapi import FastAPI

# creates a connection with MongoDB Atlas
load_dotenv(".env")
mongo_client = MongoClient(
    f"mongodb+srv://rom42pla:{os.environ['MONGODB_ATLAS_PASSWORD']}@cluster0.fg01xsr.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0", 
)
global db
db = mongo_client["Storage"]


# initialize fastapi
fastapi_app = FastAPI()
from .routers import players, games, tournaments
for router_file in [players, games, tournaments]:
    fastapi_app.include_router(router=router_file.router, prefix="/api")

@ui.page("/")
def show():
    ui.label("Hello, FastAPI!")

    # NOTE dark mode will be persistent for each user across tabs and server restarts
    ui.dark_mode().bind_value(nicegui_app.storage.user, "dark_mode")
    ui.checkbox("dark mode").bind_value(nicegui_app.storage.user, "dark_mode")

ui.run_with(
    fastapi_app,
    storage_secret="pick your private secret here",  # NOTE setting a secret is optional but allows for persistent storage per user
)
