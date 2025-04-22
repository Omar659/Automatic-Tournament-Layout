import os
import httpx
from fastapi import Form, HTTPException
from fastapi.responses import RedirectResponse
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

    @ui.refreshable_method
    async def build(self):
        user_data = app.storage.user.get('user_data', None)
        if not user_data:
            ui.add_head_html('<script src="https://accounts.google.com/gsi/client" async defer></script>')
            ui.button('Login with Google', on_click=self.login)
        else:
            ui.label(f'Welcome {user_data["name"]}!')
            ui.button('Logout', on_click=self.logout)
    
    async def logout(self) -> None:
        del app.storage.user['user_data']
        await self.build.refresh()

    async def login(self):
        
        login_url = (await login_with_google())["url"]
        ui.navigate.to(login_url)
        # async with httpx.AsyncClient() as http_client:
        #     response = await http_client.get(f'https://oauth2.googleapis.com/tokeninfo?id_token={credential}')
        # if response.status_code != 200:
        #     raise HTTPException(status_code=400, detail='Invalid token')
        # app.storage.user['user_data'] = response.json()
        # return RedirectResponse('/', status_code=303)

@ui.page("/")
async def home():
    header = Header()
    await header.build()

    player_selection_widget = PlayerSelectionWidget()
    await player_selection_widget.build()
