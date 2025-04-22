import json
import ast
from fastapi import Form, HTTPException
from fastapi.responses import RedirectResponse
from urllib.parse import urlparse
from urllib.parse import parse_qs
from nicegui import ui, app

from ..routers.auth import login_with_google
from ..routers.players import get_all


class PlayerSelectionWidget():

    storage_key = "pippo"
    current_players = []

    def __init__(self):
        if not self.storage_key in app.storage.user:
            app.storage.user[self.storage_key] = []    

    @ui.refreshable_method
    async def build(self):
        await self.update_current_players()

        with ui.card().classes("w-full max-w-md"):
            ui.label("Select Players").classes("text-xl")
            ui.select(
                options={p.id: p.name for p in self.current_players},
                label="Search and add player...",
                with_input=True,
                on_change=self.add_player,
                clearable=True,
            ).classes("w-full mb-2")

    async def update_current_players(self):
        self.current_players = await get_all()

    def add_player(self, e):
        selected_player_id = e.value
        selected_player = [p for p in self.current_players if p.id == selected_player_id][0]
        if selected_player_id not in app.storage.user[self.storage_key]:
            app.storage.user[self.storage_key].append(selected_player.model_dump())
            ui.notify(
                f"Selected: {app.storage.user[self.storage_key]}"
            )

class Header():

    async def build(self):
        with ui.header(elevated=True).style('background-color: #3874c8').classes('items-center justify-between'):
            with ui.row(align_items="center"):
                ui.label("Automatic Tournament Layout".upper())
            with ui.row(align_items="center"):
                # retrieves user data
                # if "user_data" in app.storage.user:
                #     del app.storage.user["user_data"]
                user_data = app.storage.user.get("user_data", None)
                # if there is user data...
                if user_data:
                    with ui.avatar():
                        ui.image(user_data["picture"])
                    ui.label(user_data["given_name"])
                    ui.button("Logout", on_click=self.logout)
                # if there is no user data...
                else:
                    ui.button("Login", on_click=self.login)

    async def login(self):
        # saves current url
        app.storage.user["url_before_login"] = str(ui.context.client.request.url)
        # gets the url to do the login
        login_url = (await login_with_google())["url"]
        ui.navigate.to(login_url)

    def logout(self) -> None:
        # deletes saved data
        del app.storage.user['user_data']
        # navigates again to the current url
        url = str(ui.context.client.request.url)
        ui.navigate.to(url)

@ui.page("/")
async def home():
    header = Header()
    await header.build()

    player_selection_widget = PlayerSelectionWidget()
    await player_selection_widget.build()


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
