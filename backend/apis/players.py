import requests
from typing import Final, List, Optional
from uuid import uuid4
from fastapi import APIRouter, HTTPException
from ...main import db
from ..models import Player

COLLECTION: Final[str] = "users"
router = APIRouter(prefix="/players", tags=["players"])

@router.get("/get_all")
async def get_all() -> List[Player]:
    return [Player(**x) for x in COLLECTION.find()]


@router.get("/get_one")
async def get_one(id: str | None = None, name: str | None = None) -> Optional[Player]:
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


@router.get("/add_one")
async def add_one(name: str, owner_id: str) -> Player:
    # check if a player with that name already exists
    if await get_one(name=name):
        raise HTTPException(status_code=404, detail="A player with this name already exists")
    # creates the Player object
    player_obj = Player(id=str(uuid4()), name=name, owner_id=owner_id)
    # adds it to the DB
    COLLECTION.insert_one(player_obj.model_dump())
    return player_obj


@router.get("/delete_one")
async def delete_one(player_id) -> Player:
    removed_player = COLLECTION.delete_one({"id": player_id})
    return removed_player


@router.get("/delete_all")
async def delete_all():
    COLLECTION.drop()
