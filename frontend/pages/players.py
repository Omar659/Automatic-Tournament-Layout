import json
import ast
import re
from typing import List
from fastapi import Form, HTTPException
from fastapi.responses import RedirectResponse
from urllib.parse import urlparse
from urllib.parse import parse_qs
from nicegui import ui, app

from ...main import LEGAL_CHARACTERS_RE

from ...backend.models import Player, User
from ..frontend_utils import get_current_user

from ..widgets import Header

from ...backend.apis.auth import login_with_google
from ...backend.apis.players import get_all, add_player

class PlayersCard():

    all_players = []

    def __init__(self):
        pass

    @ui.refreshable_method
    async def build(self):
        self.all_players: List[Player] = await get_all(owner_id=get_current_user().id)

        with ui.card().classes("fixed-center"):
            ui.label(f"List of players").classes("text-xl")
            ui.button(f"Create new player", on_click=self.add_player_dialog)
            if not self.all_players:
                ui.label(f"Wow, such empty")
            else:
                with ui.list().props("dense separator"):
                    for player in self.all_players:
                        ui.item(text=f"Player {player.name}", on_click=lambda: ui.navigate.to(f"/players/{player.id}"))
                        # ui.button(text=f"Delete", on_click=lambda p=player: self.delete_player_dialog(p))

    async def add_player_dialog(self):
        with ui.dialog() as dialog, ui.card():
            async def yes():
                try:
                    name = name_input.value
                    await add_player(name=name, owner_id=get_current_user().id)
                    ui.notify(f"Created player {name}")
                    self.build.refresh()
                    dialog.close()
                except Exception as e:
                    ui.notify(e)

            with ui.row():
                name_input = ui.input(
                    label="Player name",
                    validation={
                        "Too short": lambda x: len(x) >= 4,
                        "Too long": lambda x: len(x) <= 32,
                        "Invalid characters": lambda x: re.fullmatch(
                            LEGAL_CHARACTERS_RE, x
                        ),
                    },
                )
                name_input.error = "Input a name"
            with ui.row():
                ui.button("Add", on_click=yes).bind_enabled_from(
                    target_object=name_input,
                    target_name="error",
                    backward=lambda x: not x,
                )
                ui.button('Cancel', on_click=dialog.close)
            dialog.open()

    async def delete_player_dialog(self, player):
        with ui.dialog() as dialog, ui.card():
            async def yes():
                await delete_one(player_id=player.id)
                ui.notify(f"Deleted {player.name} from the DB")
                self.build.refresh()
                dialog.close()

            ui.label(f'Are you sure you want to delete {player.name}?')
            with ui.row():
                ui.button('Yes', on_click=yes)
                ui.button('No', on_click=dialog.close)
            dialog.open()


@ui.page("/players")
async def players():
    header = Header()
    await header.build()

    home_card = PlayersCard()
    await home_card.build()
