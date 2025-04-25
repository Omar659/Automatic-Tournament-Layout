from typing import Dict, List
from nicegui import ui, app
from pydantic import BaseModel, ValidationError

from ..backend.models import User, Player


def set_current_user(user: User | None):
    assert user is None or isinstance(user, User), f"got type {type(user)}"
    if user is None:
        del app.storage.user["user"]
    else:
        app.storage.user["user"] = user.model_dump()


def get_current_user() -> User | None:
    user_data = app.storage.user.get("user", None)
    if user_data is not None:
        try:
            user_data = User(**user_data)
        except ValidationError as e:
            del app.storage.user["user"]
            return None
    return user_data


def add_selected_player_to_storage(player: Player):
    # eventually creates the key
    key = "selected_players"
    if not key in app.storage.user:
        print("created key when getting")
        app.storage.user[key] = []
    # removes corrupted values
    remove_corrupted_indices_from_storage(key=key, model=Player)
    # checks if the player is already selected
    if player.id in {p_dict["id"] for p_dict in app.storage.user[key]}:
        return
    # adds the player to the storage
    app.storage.user[key].append(player.model_dump())


def get_selected_players_from_storage() -> List[Player]:
    # eventually creates the key
    key = "selected_players"
    if not key in app.storage.user:
        print("created key when getting")
        app.storage.user[key] = []
    # removes corrupted values
    remove_corrupted_indices_from_storage(key=key, model=Player)
    # gets selected players
    selected_players = []
    for i in range(len(app.storage.user[key])):
        player = Player(**app.storage.user[key][i])
        selected_players.append(player)
    return selected_players


def delete_selected_players_from_storage(player_id: str) -> Player:
    # eventually creates the key
    key = "selected_players"
    if not key in app.storage.user:
        app.storage.user[key] = []
    # removes corrupted values
    remove_corrupted_indices_from_storage(key=key, model=Player)
    # searches the index of the selected player
    found_index = None 
    for i in range(len(app.storage.user[key])):
        if app.storage.user[key][i]["id"] == player_id:
            found_index = i
            break
    if found_index is not None:
        player = Player(**app.storage.user[key].pop(found_index))
        return player


def logout():
    set_current_user(user=None)
    ui.navigate.to("/")


def remove_corrupted_indices_from_storage(key: str, model: BaseModel):
    corrupted_indices = set()
    for i, x in enumerate(app.storage.user[key]):
        try:
            model(**x)
        except:
            corrupted_indices.add(i)
    app.storage.user[key] = [
        x for i, x in enumerate(app.storage.user[key]) if i not in corrupted_indices
    ]
