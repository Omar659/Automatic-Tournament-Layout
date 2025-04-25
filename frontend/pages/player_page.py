import json
import ast
from fastapi import Form, HTTPException
from fastapi.responses import RedirectResponse
from urllib.parse import urlparse
from urllib.parse import parse_qs
from nicegui import ui, app

from ...backend.models import Player

from ..widgets import Header

from ...backend.apis.auth import login_with_google
from ...backend.apis.players import get_one


class PlayerCard:

    def __init__(self, player_id):
        self.player_id: str = player_id
        self.player: Player = None

    @ui.refreshable_method
    async def build(self):
        # gets player's info from the db
        if not self.player:
            self.player = await get_one(self.player_id)

        with ui.card().classes("fixed-center"):
            ui.label(f"Name").classes("text-xl")
            ui.label(self.player.name)
            ui.label(f"Owner").classes("text-xl")
            ui.label(self.player.owner_id)
            ui.label(f"Skills").classes("text-xl")
            ui.label("TODO")

@ui.page("/players/{player_id}")
async def players(player_id):
    header = Header()
    await header.build()

    player_card = PlayerCard(player_id=player_id)
    await player_card.build()
