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
