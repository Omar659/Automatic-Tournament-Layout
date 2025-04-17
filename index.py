import os
from typing import Dict, List
from dotenv import load_dotenv
from nicegui import ui, app
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import ConnectionFailure, OperationFailure

from db import add_player_to_db, check_if_player_exists, get_players_list_from_db, remove_player_from_db
from widgets import AddPlayersWidget, PlayersListWidget

# --- Configuration ---
# !!! IMPORTANT: Replace with your actual MongoDB connection string !!!
load_dotenv(".env")
MONGO_URI = f"mongodb+srv://rom42pla:{os.environ['MONGODB_ATLAS_PASSWORD']}@cluster0.fg01xsr.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DATABASE_NAME = "tournament_db"
COLLECTION_NAME = "players"

# --- Database Connection ---
try:
    mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000) # 5 second timeout
    # The ismaster command is cheap and does not require auth.
    mongo_client.admin.command('ping')
    db = mongo_client[DATABASE_NAME]
    players_collection = db[COLLECTION_NAME]
    print(f"Successfully connected to MongoDB database '{DATABASE_NAME}'.")
    db_connection_ok = True
except ConnectionFailure as e:
    print(f"ERROR: Could not connect to MongoDB at {MONGO_URI}. Please check if it's running.")
    print(f"Error details: {e}")
    players_collection = None # Flag connection issue
    db_connection_ok = False
except Exception as e:
    print(f"An unexpected error occurred during MongoDB connection: {e}")
    players_collection = None
    db_connection_ok = False



@ui.page('/')
def add_player_page():
    players_list_widget = PlayersListWidget(client=mongo_client)
    add_players_widget = AddPlayersWidget(client=mongo_client, players_list_widget=players_list_widget)


# --- Run the App ---
ui.run(title="Add Player (MongoDB)", port=1337)