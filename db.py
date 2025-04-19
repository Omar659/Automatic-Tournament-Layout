from nicegui import ui

from .models import Player

def add_player_to_db(client, player_name):
    db = client["Storage"]
    collection = db["Players"]
    player_obj = Player(name=player_name)
    player_obj.id = collection.insert_one(player_obj.model_dump()).inserted_id
    return player_obj

def remove_player_from_db(client, player_name):
    db = client["Storage"]
    collection = db["Players"]
    collection.delete_one({"name": player_name})

def check_if_player_exists(client, player_name):
    db = client["Storage"]
    collection = db["Players"]
    result = collection.find_one({"name": player_name})
    player = None
    if result:
        player = Player(**result)
    return player

def get_players_list_from_db(client):
    try:
        db = client["Storage"]
        collection = db["Players"]
        return [Player(**x) for x in collection.find()]
    except Exception as e:
        print(e)
