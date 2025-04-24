import json
import ast
from fastapi import Form, HTTPException
from fastapi.responses import RedirectResponse
from urllib.parse import urlparse
from urllib.parse import parse_qs
from nicegui import ui, app

from ..widgets import Header

from ..routers.auth import login_with_google
from ..routers.players import get_all, add_one, delete_one

class PlayersCard():

    all_players = []

    def __init__(self):
        pass

    @ui.refreshable_method
    async def build(self):
        self.all_players = await get_all()

        with ui.card().classes("fixed-center"):
            ui.label(f"List of players").classes("text-xl")
            ui.button(f"Create new player", on_click=self.add_player_dialog)
            if not self.all_players:
                ui.label(f"Wow, such empty")
            else:
                for player in self.all_players:
                    with ui.row():
                        ui.label(text=f"Player {player.name}")
                        ui.button(text=f"Delete", on_click=lambda p=player: self.delete_player_dialog(p))
    
    async def add_player_dialog(self):
        with ui.dialog() as dialog, ui.card():
            async def yes():
                name = name_input.value
                await add_one(name=name)
                ui.notify(f"Created {name} in the DB")
                self.build.refresh()
                dialog.close()

            with ui.row():
                name_input = ui.input(label='Name')
            with ui.row():
                ui.button('Yes', on_click=yes)
                ui.button('No', on_click=dialog.close)
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
async def home():
    header = Header()
    await header.build()

    home_card = PlayersCard()
    await home_card.build()
