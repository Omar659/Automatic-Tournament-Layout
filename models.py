from typing import List, Optional
from uuid import uuid4
from pydantic import BaseModel, ConfigDict, Field

from .enums import SkillLevel

class Entity(BaseModel):
    id: str
    name: str

class Game(Entity):
    pass

class GameSkill(BaseModel):
    game: Game
    level: SkillLevel

class Player(Entity):
    skills: List[GameSkill] = []

class GoogleUserData(BaseModel):
    id: str
    email: str
    name: str = None
    given_name: str = None
    family_name: str = None
    picture: str = None
