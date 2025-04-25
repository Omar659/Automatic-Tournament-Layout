import json
import ast
import re
from fastapi import Form, HTTPException
from fastapi.responses import RedirectResponse
from urllib.parse import urlparse
from urllib.parse import parse_qs
from nicegui import ui, app

from ...main import MIN_NAME_LENGTH, MAX_NAME_LENGTH, LEGAL_CHARACTERS_RE
from ..utils import get_current_user, set_current_user

from ...backend.models import User

from ..widgets import Header

from ...backend.apis.auth import change_name, login_with_google
from ...backend.apis.players import get_one


class SettingsCard:

    @ui.refreshable_method
    async def build(self):
        # if user is logged out, then return to the home
        if not get_current_user():
            ui.navigate.to("/")
            return

        with ui.card().classes("fixed-center"):
            ui.label(f"Name").classes("text-xl")
            with ui.row():
                ui.label(get_current_user().name)
                ui.button("Edit", icon="edit", on_click=self.change_user_name_dialog)
            ui.label(f"ID").classes("text-xl")
            ui.label(get_current_user().id)
            if get_current_user().google_user_data:
                ui.label(f"Skills").classes("text-xl")
                ui.label("TODO")

    async def change_user_name_dialog(self):
        with ui.dialog() as dialog, ui.card():

            async def yes():
                name = name_input.value
                try:
                    user = await change_name(id=get_current_user().id, new_name=name)
                    set_current_user(user=user)
                    ui.notify(f"Changed name to {name} in the DB")
                    self.build.refresh()
                    dialog.close()
                except HTTPException as e:
                    ui.notify(e)

            with ui.row():
                name_input = ui.input(
                    label="New name",
                    value=get_current_user().name,
                    validation={
                        "Too short": lambda x: len(x) >= 4,
                        "Too long": lambda x: len(x) <= 32,
                        "Invalid characters": lambda x: re.fullmatch(LEGAL_CHARACTERS_RE, x)
                    },
                )
            with ui.row():
                ui.button("Done", on_click=yes).bind_enabled_from(target_object=name_input, target_name="error", backward=lambda x: not x)
                ui.button("Cancel", on_click=dialog.close)
            dialog.open()


@ui.page("/settings")
async def settings():
    header = Header()
    await header.build()

    settings_card = SettingsCard()
    await settings_card.build()
