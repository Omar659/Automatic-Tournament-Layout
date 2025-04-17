from nicegui import ui

def add_player_to_db(client, player_name):
    db = client["Storage"]
    collection = db["Players"]
    mydict = { "name": player_name }
    collection.insert_one(mydict)

def remove_player_from_db(client, player_name):
    db = client["Storage"]
    collection = db["Players"]
    collection.delete_one({"name": player_name})

def check_if_player_exists(client, player_name):
    db = client["Storage"]
    collection = db["Players"]
    result = collection.find({"name": player_name})
    exists = True if len(list(result)) > 0 else False
    return exists

def get_players_list_from_db(client):
    try:
        db = client["Storage"]
        collection = db["Players"]
        return [x for x in collection.find()]
    except Exception as e:
        print(e)