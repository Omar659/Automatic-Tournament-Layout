import json
import ast
from fastapi import Form, HTTPException
from fastapi.responses import RedirectResponse
from urllib.parse import urlparse
from urllib.parse import parse_qs
from nicegui import ui, app

from ..widgets import Header

from ..routers.auth import login_with_google
from ..routers.players import get_all

class HomeCard():

    def __init__(self):
        pass

    @ui.refreshable_method
    async def build(self):
        with ui.card().classes("fixed-center"):
            ui.button("Create tournament", on_click=lambda: ui.navigate.to("/tournaments/create")).bind_enabled(app.storage.user, "user_data")


# class PlayerSelectionWidget():

#     storage_key = "pippo"
#     current_players = []

#     def __init__(self):
#         if not self.storage_key in app.storage.user:
#             app.storage.user[self.storage_key] = []    

#     @ui.refreshable_method
#     async def build(self):
#         await self.update_current_players()

#         with ui.card().classes("w-full max-w-md"):
#             ui.label("Select Players").classes("text-xl")
#             ui.select(
#                 options={p.id: p.name for p in self.current_players},
#                 label="Search and add player...",
#                 with_input=True,
#                 on_change=self.add_player,
#                 clearable=True,
#             ).classes("w-full mb-2")

#     async def update_current_players(self):
#         self.current_players = await get_all()

#     def add_player(self, e):
#         selected_player_id = e.value
#         selected_player = [p for p in self.current_players if p.id == selected_player_id][0]
#         if selected_player_id not in app.storage.user[self.storage_key]:
#             app.storage.user[self.storage_key].append(selected_player.model_dump())
#             ui.notify(
#                 f"Selected: {app.storage.user[self.storage_key]}"
#             )

@ui.page("/")
async def home():
    header = Header()
    await header.build()

    home_card = HomeCard()
    await home_card.build()


@ui.page("/login/finalize")
async def login_finalize():
    # gets current url
    url = str(ui.context.client.request.url)
    # parses user data from current url
    user_data = parse_qs(urlparse(url).query)["data"][0]
    user_data = ast.literal_eval(user_data)
    # saves user's infos into storage
    app.storage.user["user_data"] = user_data
    ui.navigate.to(app.storage.user["url_before_login"])
