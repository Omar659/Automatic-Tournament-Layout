import json
import ast
from fastapi import Form, HTTPException
from fastapi.responses import RedirectResponse
from urllib.parse import urlparse
from urllib.parse import parse_qs
from nicegui import ui, app

from ...backend.models import Player, User

from ..widgets import Header

from ...backend.apis.auth import get_user, login_with_google
from ...backend.apis.players import delete_player, get_player


class PlayerCard:

    def __init__(self, player_id):
        self.player_id: str = player_id
        self.player: Player = None
        self.owner: User = None

    @ui.refreshable_method
    async def build(self):
        # gets player's info from the db
        if not self.player:
            self.player = await get_player(self.player_id)
        # gets owner's info from the db
        if not self.owner:
            self.owner = await get_user(self.player.owner_id)

        with ui.card().classes("fixed-center"):
            ui.label(f"Name").classes("text-xl")
            ui.label(self.player.name)
            ui.label(f"ID").classes("text-xl")
            ui.label(self.player.id)
            ui.label(f"Owner").classes("text-xl")
            ui.label(self.owner.name)
            ui.label(f"Skills").classes("text-xl")
            ui.label("TODO")
            ui.button(
                "Delete player",
                icon="delete",
                color="red",
                on_click=self.delete_player_dialog,
            )

    async def delete_player_dialog(self):
        with ui.dialog() as dialog, ui.card():

            async def yes():
                try:
                    await delete_player(id=self.player.id)
                    ui.navigate.to("/players")
                except HTTPException as e:
                    ui.notify(e)

            with ui.row():
                ui.label(f"You're about to delete player {self.player.name} from the DB")
            with ui.row():
                ui.button(
                    "Delete", icon="delete", color="red", on_click=yes
                )
                ui.button("Cancel", on_click=dialog.close)
            dialog.open()


@ui.page("/players/{player_id}")
async def players(player_id):
    header = Header()
    await header.build()

    player_card = PlayerCard(player_id=player_id)
    await player_card.build()
