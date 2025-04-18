from typing import List, Optional
from pydantic import BaseModel, ConfigDict

from enums import SkillLevel

class Entity(BaseModel):
    id: Optional[int] = None
    name: str
    
class Game(Entity):
    pass

class GameSkill(BaseModel):
    game: Game
    level: SkillLevel
    
class Player(Entity):
    skills: List[GameSkill] = []




    
