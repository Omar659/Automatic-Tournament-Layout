import os
import re
import requests
from typing import Final, List, Optional
from uuid import uuid4
from fastapi import APIRouter, HTTPException

from ..backend_utils import generate_id
from ...main import LEGAL_CHARACTERS_RE, db
from ..models import Player

COLLECTION: Final[str] = db["players"]
router = APIRouter(prefix="/players", tags=["players"])

@router.get("/get_all")
async def get_all(owner_id: str | None = None) -> List[Player]:
    query = {}
    if owner_id:
        query["owner_id"] = owner_id
    return [Player(**x) for x in COLLECTION.find(query)]


@router.get("/get")
async def get_player(id: str | None = None, name: str | None = None) -> Optional[Player]:
    # raise an error if no parameters are provided
    if not(id or name):
        raise HTTPException(status_code=404, detail="No parameters were provided")
    query = {}
    if id:
        query["id"] = id
    if name:
        query["name"] = name
    player = COLLECTION.find_one(query)
    if player:
        player = Player(**player)
    else:
        player = None
    return player


@router.get("/add")
async def add_player(name: str, owner_id: str) -> Player:
    # checks if the new name is valid
    if not re.fullmatch(LEGAL_CHARACTERS_RE, name):
        raise HTTPException(
            status_code=404,
            detail="New name contains invalid characters, or is too short or too long",
        )
    # check if a player with that name already exists
    # if await get_player(name=name):
    #     raise HTTPException(status_code=404, detail="A player with this name already exists")
    # creates the Player object
    player_id = generate_id(key=os.environ["HASH_INIT"], init=name)
    player_obj = Player(id=player_id, name=name, owner_id=owner_id)
    # adds it to the DB
    COLLECTION.insert_one(player_obj.model_dump())
    return player_obj


@router.get("/delete")
async def delete_player(id: str | None = None, name: str | None = None):
    if not any([id, name]):
        raise HTTPException(status_code=404, detail="No parameters were given")
    query = []
    if id:
        query.append({"id": id})
    if name:
        query.append({"name": name})
    COLLECTION.delete_one({"$or": query})


@router.get("/delete_all")
async def delete_all():
    COLLECTION.drop()
