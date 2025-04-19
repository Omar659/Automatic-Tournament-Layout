from nicegui import ui, app
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


@ui.page("/")
async def home():
    player_selection_widget = PlayerSelectionWidget()
    await player_selection_widget.build()
