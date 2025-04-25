import json
import ast
from fastapi import Form, HTTPException
from fastapi.responses import RedirectResponse
from urllib.parse import urlparse
from urllib.parse import parse_qs
from nicegui import ui, app

from ..backend.models import Player

from .widgets import Header
from ..backend.fastapi.auth import login_with_google
from ..backend.fastapi.players import get_all

class CreateTournamentCard():

    all_players = []

    @ui.refreshable_method
    async def build(self):
        self.all_players = await get_all()

        with ui.card().classes("fixed-center"):
            ui.label("Create tournament").classes("text-xl")

            ui.label("Name").classes("text-xl")
            ui.input(label="Name", validation={'Name is too long': lambda value: len(value) < 32})

            ui.label("Type").classes("text-xl")
            ui.select(options=["Group tournament"], value="Group tournament")

            ui.label("Players").classes("text-xl")
            with ui.row():
                ui.select(
                    options={p.id: p.name for p in self.all_players},
                    label="Search and add player...",
                    with_input=True,
                    on_change=self.add_player,
                    clearable=True,
                ).classes("mb-2")
                ui.button("Add player")
            if not "selected_players" in app.storage.user:
                ui.label("No players selected")
            else:
                for selected_player_id in app.storage.user["selected_players"]:
                    if selected_player_id not in {p.id for p in self.all_players}:
                        del app.storage.user["selected_players"][selected_player_id]
                    else:
                        with ui.row(align_items="start"):
                            player = Player(**app.storage.user["selected_players"][selected_player_id])
                            ui.label(player.name)
                            ui.button("Delete", on_click=lambda x=selected_player_id: self.delete_player(x))

    async def delete_player(self, player_id):
        if player_id in app.storage.user["selected_players"]:
            del app.storage.user["selected_players"][player_id]
            self.build.refresh()

    async def add_player(self, e):
        # creates the storage key
        if not "selected_players" in app.storage.user:
            app.storage.user["selected_players"] = {}
        # gets selected player's infos
        selected_player_id = e.value
        selected_player = [p for p in self.all_players if p.id == selected_player_id][0]
        print(selected_player, selected_player_id)
        # adds the player to the storage
        if selected_player_id not in app.storage.user["selected_players"]:
            app.storage.user["selected_players"][selected_player.id] = selected_player.model_dump()
            ui.notify(
                f"Selected: {selected_player.name}"
            )
        self.build.refresh()


class PlayerSelectionWidget():

    current_players = []

    def __init__(self):
        pass

    @ui.refreshable_method
    async def build(self):
        await self.update_current_players()


@ui.page("/tournaments/create")
async def home():
    header = Header()
    await header.build()

    create_tournament_card = CreateTournamentCard()
    await create_tournament_card.build()
