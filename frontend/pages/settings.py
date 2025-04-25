import json
import ast
from fastapi import Form, HTTPException
from fastapi.responses import RedirectResponse
from urllib.parse import urlparse
from urllib.parse import parse_qs
from nicegui import ui, app

from ...backend.utils import get_current_user

from ...backend.models import User

from ..widgets import Header

from ...backend.apis.auth import login_with_google
from ...backend.apis.players import get_one


class SettingsCard:

    @ui.refreshable_method
    async def build(self):

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
                # await add_one(name=name, owner_id=self.user.id)
                ui.notify(f"Changed name to {name} in the DB")
                self.build.refresh()
                dialog.close()

            with ui.row():
                name_input = ui.input(
                    label="New name", value=get_current_user().name
                )
            with ui.row():
                ui.button("Done", on_click=yes)
                ui.button("Cancel", on_click=dialog.close)
            dialog.open()


@ui.page("/settings")
async def settings():
    header = Header()
    await header.build()

    settings_card = SettingsCard()
    await settings_card.build()
