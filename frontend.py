import os
from typing import Dict, List
from dotenv import load_dotenv
from nicegui import ui, app
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import ConnectionFailure, OperationFailure

from db import add_player_to_db, check_if_player_exists, get_players_list_from_db, remove_player_from_db
from widgets import AddPlayersWidget, Footer, Header, PlayerSelectionWidget, PlayersListWidget




@ui.page("/")
def home():
    header = Header()

    PlayerSelectionWidget(client=mongo_client)

    footer = Footer()


@ui.page('/add_player')
def add_player_page():
    header = Header()

    players_list_widget = PlayersListWidget(client=mongo_client)
    add_players_widget = AddPlayersWidget(client=mongo_client, players_list_widget=players_list_widget)

    footer = Footer()
