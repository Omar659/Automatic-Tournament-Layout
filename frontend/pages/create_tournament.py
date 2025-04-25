from pprint import pprint
import re
from typing import List
from nicegui import ui, app

from ..frontend_utils import (
    add_selected_player_to_storage,
    delete_selected_players_from_storage,
    get_selected_players_from_storage,
)

from ...main import LEGAL_CHARACTERS_RE, MIN_NAME_LENGTH

from ...backend.models import Player

from ..widgets import Header
from ...backend.apis.players import get_all, search_players


class SelectedPlayersList:

    selected_players: List[Player] = []

    @ui.refreshable_method
    async def build(self):
        self.selected_players = get_selected_players_from_storage()
        ui.label(f"Selected players ({len(self.selected_players)})").classes(
            "text-xl"
        )
        with ui.list().props("dense separator"):
            for player in self.selected_players:
                with ui.row():
                    ui.item(player.name)
                    ui.button(
                        "Remove",
                        icon="delete",
                        color="red",
                        on_click=lambda x=player: self.remove_player_button(
                            player=x
                        ),
                    )

    def remove_player_button(self, player: Player):
        delete_selected_players_from_storage(player_id=player.id)
        self.build.refresh()


class SearchedPlayersList:
    current_search = ""
    players_matched: List[Player] = []

    def __init__(self, selected_players_list: SelectedPlayersList):
        assert isinstance(selected_players_list, SelectedPlayersList)
        self.selected_players_list = selected_players_list

    @ui.refreshable_method
    async def build(self):
        if self.current_search:
            players_matched = await search_players(name=self.current_search)
            with ui.list().props("dense separator"):
                for player in players_matched:
                    ui.item(
                        player.name,
                        on_click=lambda x=player: self.click_on_player(x),
                    )
            if len(self.current_search) > MIN_NAME_LENGTH:
                ui.button(f"Create new player {self.current_search}")

    def click_on_player(self, player):
        add_selected_player_to_storage(player)
        self.current_search = ""
        self.selected_players_list.build.refresh()


class CreateTournamentCard:

    selected_players_list: SelectedPlayersList = SelectedPlayersList()

    def __init__(self):

        self.searched_players_list: SearchedPlayersList = SearchedPlayersList(
            self.selected_players_list
        )

    @ui.refreshable_method
    async def build(self):
        # del app.storage.user["selected_players"]
        self.all_players = await get_all()

        with ui.card().classes("fixed-center"):
            ui.label("Create tournament").classes("text-xl")

            ui.label("Name").classes("text-xl")
            ui.input(
                label="Name",
                validation={
                    "Too short": lambda x: len(x) >= 4,
                    "Too long": lambda x: len(x) <= 32,
                    "Invalid characters": lambda x: re.fullmatch(
                        LEGAL_CHARACTERS_RE, x
                    ),
                },
            )

            ui.label("Type").classes("text-xl")
            ui.select(options=["Group tournament"], value="Group tournament")

            ui.label("Players").classes("text-xl")

            ui.input(
                "Search players",
                validation={
                    "Too long": lambda x: len(x) <= 32,
                    "Invalid characters": lambda x: re.fullmatch(
                        LEGAL_CHARACTERS_RE, x
                    ),
                },
                on_change=lambda x: self.searched_players_list.build.refresh(),
            ).bind_value(self.searched_players_list, "current_search")
            await self.searched_players_list.build()
            await self.selected_players_list.build()
            
            ui.button(text="Create tournament", icon="add").bind_enabled_from(self.selected_players_list, "selected_players", lambda x: 2 <= len(x) <= 32)
            # if search_input:
            #     ui.button(f"Create new player {search_input.value}")
            # ui.select(
            #     options={p.id: p.name for p in self.all_players},
            #     label="Search and add player...",
            #     with_input=True,
            #     # on_change=self.add_player,
            #     on_change=lambda x: ui.notify("change"),
            #     clearable=True,
            # ).classes("mb-2")
            # if not "selected_players" in app.storage.user:
            #     ui.label("No players selected")
            # else:
            #     for selected_player_id in app.storage.user["selected_players"]:
            #         if selected_player_id not in {p.id for p in self.all_players}:
            #             del app.storage.user["selected_players"][selected_player_id]
            #         else:
            #             with ui.row(align_items="start"):
            #                 player = Player(**app.storage.user["selected_players"][selected_player_id])
            #                 ui.label(player.name)
            #                 ui.button("Delete", on_click=lambda x=selected_player_id: self.delete_player(x))

    # async def delete_player(self, player_id):
    #     if player_id in app.storage.user["selected_players"]:
    #         del app.storage.user["selected_players"][player_id]
    #         self.build.refresh()

    # async def add_player(self, e):
    #     # creates the storage key
    #     if not "selected_players" in app.storage.user:
    #         app.storage.user["selected_players"] = {}
    #     # gets selected player's infos
    #     selected_player_id = e.value
    #     selected_player = [p for p in self.all_players if p.id == selected_player_id][0]
    #     print(selected_player, selected_player_id)
    #     # adds the player to the storage
    #     if selected_player_id not in app.storage.user["selected_players"]:
    #         app.storage.user["selected_players"][selected_player.id] = selected_player.model_dump()
    #         ui.notify(
    #             f"Selected: {selected_player.name}"
    #         )
    #     self.build.refresh()


@ui.page("/tournaments/create")
async def home():
    header = Header()
    await header.build()

    create_tournament_card = CreateTournamentCard()
    await create_tournament_card.build()
