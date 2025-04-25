import json
import ast
import os
from fastapi import Form, HTTPException
from fastapi.responses import RedirectResponse
from urllib.parse import urlparse
from urllib.parse import parse_qs
import hashlib
from nicegui import ui, app

from ..frontend_utils import set_current_user

from ...backend.models import GoogleUserData

from ..widgets import Header

from ...backend.apis.auth import add_user, login_with_google
from ...backend.apis.players import get_all

class HomeCard():

    @ui.refreshable_method
    async def build(self):
        with ui.card().classes("fixed-center"):
            ui.button("Create tournament", on_click=lambda: ui.navigate.to("/tournaments/create")).bind_enabled(app.storage.user, "user_data")
            ui.button("Your players", on_click=lambda: ui.navigate.to("/players"))

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
    # for now, just the login with Google is supported
    google_user_data = GoogleUserData(**user_data)
    # eventually adds the user to the DB
    user = await add_user(google_user_data=google_user_data)
    # saves user's infos into storage
    set_current_user(user=user)
    ui.navigate.to(app.storage.user["url_before_login"])
