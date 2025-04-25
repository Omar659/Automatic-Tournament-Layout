from nicegui import ui, app

from ..backend.models import User

from ..backend.utils import get_current_user

from ..backend.apis.auth import login_with_google

# from ..backend.db import add_player_to_db, check_if_player_exists, get_players_list_from_db, remove_player_from_db

class Header():

    async def build(self):
        # del app.storage.user["user"]
        with ui.header(elevated=True).style('background-color: #3874c8').classes('items-center justify-between'):
            with ui.row(align_items="center"):
                ui.button("Automatic Tournament Layout".upper(), icon="home", on_click=lambda: ui.navigate.to("/"))
            with ui.row(align_items="center"):
                # retrieves user data
                # if "user_data" in app.storage.user:
                #     del app.storage.user["user_data"]
                # user_data = app.storage.user.get("user_data", None)
                # validate user data
                user: User = get_current_user()
                # if there is user data...
                if isinstance(user, User):
                    with ui.dropdown_button(
                        text=user.name, icon="account_circle", auto_close=True
                    ):
                        # if user.google_user_data:
                        #     if user.google_user_data.picture:
                        #         with ui.avatar():
                        #             ui.image(user.google_user_data.picture)
                        ui.item("Settings", on_click=lambda: ui.navigate.to("/settings"))
                        ui.item("Logout", on_click=self.logout)
                # if there is no user data...
                else:
                    ui.button("Login", icon="login", on_click=self.login)

    async def login(self):
        # saves current url
        app.storage.user["url_before_login"] = str(ui.context.client.request.url)
        # gets the url to do the login
        login_url = (await login_with_google())["url"]
        ui.navigate.to(login_url)

    def logout(self) -> None:
        # deletes saved data
        del app.storage.user['user']
        # navigates again to the current url
        url = str(ui.context.client.request.url)
        ui.navigate.to(url)


class Footer:

    def __init__(self):
        self.build()

    def build(self):
        with ui.footer().style("background-color: #3874c8").classes(
            "items-center justify-between"
        ):
            ui.label("footer".upper())


class PlayersListWidget:
    def __init__(self, client):
        self.client = client
        self.build()

    @ui.refreshable_method
    def build(self):
        ui.label('Players in Database').classes('text-xl font-semibold mb-4')
        players_list = get_players_list_from_db(client=self.client)
        if not players_list:
            ui.label("No players registered")
        with ui.grid(columns=2):
            for player in players_list:
                if player is None:
                    continue
                ui.label(player["name"])
                ui.button(icon='thumb_up', 
                        on_click=lambda x=player: self.delete_player_button(player=x))

    def delete_player_button(self, player):
        player_name = player["name"]
        ui.notify(f"Deleted player {player_name}")
        remove_player_from_db(client=self.client, player_name=player_name)
        self.build.refresh()


class AddPlayersWidget:
    def __init__(self, client, players_list_widget=None):
        self.client = client
        self.players_list_widget = players_list_widget
        self.build()

    @ui.refreshable_method
    def build(self):
        ui.label('Add a Player').classes('text-xl font-semibold mb-4')

        with ui.row():
            self.player_name_input = ui.input(label='Player Name').on("keydown.enter", lambda: self.add_player_button()).props('clearable').props('outlined dense')
            self.player_name_button = ui.button(text=f"Add player", 
                                        on_click=lambda: self.add_player_button()).props('clearable')

    def add_player_button(self):
        # gets player's name
        player_name = self.player_name_input.value
        if not player_name:
            ui.notify("The player must have a name")
            return
        elif len(player_name) > 32:
            ui.notify("The player name is too long (must be max. 32 characters)")
            return
        elif check_if_player_exists(client=self.client, player_name=player_name):
            ui.notify(f"A player named {player_name} already exists")
            return
        # adds the player to the db
        add_player_to_db(client=self.client, player_name=player_name)
        # resets the textbox
        self.player_name_input.set_value(None)
        # notify the browser for the success
        ui.notify(f"Added player {player_name}")
        # eventually refresh player's list
        if self.players_list_widget:
            self.players_list_widget.build.refresh()


class PlayerSelectionWidget:
    storage_key = "selected_players_list"  # Key for user storage
    max_players = 32  # Define the maximum number of players allowed

    def __init__(self, client, max_players=32):
        self.client = client
        assert isinstance(max_players, int) and max_players > 0, f"got {max_players=}" 
        self.max_players = max_players
        self.all_players_options = {}  # Cache for all player options {name: name}
        self.load_players_list_in_storage()
        self.build()  # Build the UI components

    def load_players_list_in_storage(self):
        """Loads the initial selection from storage, handling potential errors and limit."""
        try:
            # data is corrupted and will be erased
            if not isinstance(app.storage.user[self.storage_key], list):
                raise Exception("corrupted data found")
            # eventually truncate selection
            if len(app.storage.user[self.storage_key]) > self.max_players:
                app.storage.user[self.storage_key] = app.storage.user[self.storage_key][:self.max_players]
        except RuntimeError as e:
            app.storage.user[self.storage_key] = []

    def _get_available_players_for_add(self) -> dict:
        """Returns a dictionary of players not already selected."""
        # Return empty if limit is reached to prevent selection
        if len(self.selected_players) >= self.max_players:
            return {}
        return {
            name: name
            for name in self.all_players_options
            if name not in self.selected_players
        }

    @ui.refreshable_method
    def build(self):
        with ui.card().classes("w-full max-w-md"): 
            ui.label("Select Players").classes("text-xl")

            # fetch and prepare player data
            players_list_from_db = get_players_list_from_db(client=self.client)
            if not players_list_from_db:
                ui.label("No players available in the database.")
                return

            # --- Storage Validation (Against current DB players) ---
            # valid_player_names = set(self.all_players_options.keys())
            # validated_selection = [
            #     p for p in app.storage.user[self.storage_key] if p in valid_player_names
            # ]
            # # Also re-apply limit in case DB changed significantly
            # final_selection = validated_selection[: self.max_players]

            # if len(final_selection) != len(app.storage.user[self.storage_key]):
            #     change_occurred = True
            #     if len(validated_selection) != len(self.selected_players):
            #         ui.notify(
            #             "Some previously selected players are no longer available and were removed.",
            #             type="warning",
            #         )
            #     if len(final_selection) != len(validated_selection):
            #         ui.notify(
            #             f"Selection adjusted to maximum of {self.max_players} players.",
            #             type="info",
            #         )
            #     self._update_selection_and_storage(
            #         final_selection
            #     )  # Updates self.selected_players
            # else:
            #     self.selected_players = (
            #         final_selection  # Ensure internal state is correct
            #     )
            # --- End Storage Validation ---

            # --- Autocomplete Input for Adding Players ---
            # ui.select with with_input=True naturally hides suggestions when the input is empty.
            # It filters the provided `options` based on the text entered.
            self.add_player_input = ui.select(
                options=[p.name for p in players_list_from_db],  # Only show addable players
                label="Search and add player...",
                with_input=True,
                on_change=self.handle_add_player_selection,
            ).classes("w-full mb-2")

            # --- Disable input when limit is reached ---
            # Bind the 'disable' property to a check on the length
            # self.add_player_input.bind_enabled_from(
            #     app.storage.user,
            #     self.storage_key,
            #     backward=lambda p_list: len(p_list) < self.max_players,
            # )

            # # --- Display Selected Players ---
            ui.separator().classes("my-4")
            # # Label to show the count
            self.selected_count_label = ui.label().classes("text-lg font-medium mb-2")
            ui.label(f"{len(app.storage.user[self.storage_key])}")
            # self._update_selected_count_label()  # Set initial text

            # # Container for the dynamically updated list of selected players
            # self.selected_list_container = ui.column().classes("w-full gap-1")
            # self.build_selected_list()  # Initial rendering of the list

    # @ui.refreshable
    # def build_selected_list(self):
    #     """Builds the list of currently selected players with delete buttons."""
    #     self.selected_list_container.clear()  # Clear previous items
    #     with self.selected_list_container:
    #         if not self.selected_players:
    #             ui.label("No players selected yet.").classes("text-sm text-gray-500")
    #         else:
    #             sorted_players = sorted(self.selected_players)  # Display alphabetically
    #             for player_name in sorted_players:
    #                 with ui.row().classes("w-full items-center justify-between py-1"):
    #                     ui.label(player_name).classes("text-base")
    #                     ui.button(
    #                         icon="delete_outline",
    #                         on_click=lambda name=player_name: self.remove_player(name),
    #                         color="negative",
    #                     ).props("flat round dense")

    #     # Update the count label whenever the list is rebuilt
    #     self._update_selected_count_label()

    # def _update_selected_count_label(self):
    #     """Updates the label showing the selected player count."""
    #     if hasattr(self, "selected_count_label"):  # Ensure label exists
    #         count = len(self.selected_players)
    #         self.selected_count_label.set_text(
    #             f"Selected Players: ({count}/{self.max_players})"
    #         )
    #         # Optionally add styling if limit is reached
    #         if count >= self.max_players:
    #             self.selected_count_label.classes(
    #                 add="text-negative font-semibold", remove="text-positive"
    #             )
    #         else:
    #             self.selected_count_label.classes(
    #                 remove="text-negative font-semibold"
    #             )  # Ensure normal state if below limit

    async def handle_add_player_selection(self, event):
        selected_name = event.value  # The name selected from the dropdown

        app.storage.user[self.storage_key].append(selected_name)
        self.build.refresh()
        # --- Process Valid Selection ---
        # if (
        #     selected_name
        #     and selected_name in self.all_players_options
        #     and selected_name not in self.selected_players
        # ):
        #     # Add the player to the list
        #     new_selection = self.selected_players + [selected_name]
        #     self._update_selection_and_storage(new_selection)

        #     # Refresh the displayed list (this also updates the count label)
        #     self.build_selected_list.refresh()

        #     # Update the autocomplete options (remove added player, check limit)
        #     self.add_player_input.options = self._get_available_players_for_add()

        #     # Clear the input field
        #     await self._clear_add_input()
        #     clear_input_needed = False  # Already cleared

        #     ui.notify(f"Added player: {selected_name}", type="positive")

        # elif selected_name:
        #     # Handle case where selection was invalid or already present
        #     print(
        #         f"Debug: Could not add '{selected_name}'. Invalid selection or already selected."
        #     )
        #     # Fall through to clear input

        # # --- Clear input if not already done ---
        # if clear_input_needed and selected_name:
        #     await self._clear_add_input()

    # async def _clear_add_input(self):
    #     """Helper to clear the autocomplete input value and text."""
    #     if hasattr(self, "add_player_input"):
    #         self.add_player_input.set_value(None)
    #         # Use Quasar's reset method to clear the visible text reliably
    #         await self.add_player_input.run_method("reset")
    #         self.add_player_input.update()

    # def remove_player(self, player_name_to_remove):
    #     """Removes a player from the selection, updates state, storage, and UI."""
    #     if player_name_to_remove in self.selected_players:
    #         was_at_limit = (
    #             len(self.selected_players) >= self.max_players
    #         )  # Check limit *before* removing

    #         new_selection = [
    #             p for p in self.selected_players if p != player_name_to_remove
    #         ]
    #         self._update_selection_and_storage(new_selection)

    #         # Refresh the displayed list (this also updates the count label)
    #         self.build_selected_list.refresh()

    #         # Update the autocomplete options (add the removed player back)
    #         # Re-enable input if we just dropped below the limit
    #         if hasattr(self, "add_player_input"):
    #             self.add_player_input.options = self._get_available_players_for_add()
    #             # If it was at the limit, the input might be disabled, force update
    #             if was_at_limit:
    #                 self.add_player_input.update()  # Ensures binding re-evaluates and enables input

    #         ui.notify(f"Removed player: {player_name_to_remove}", type="info")
    #     else:
    #         print(
    #             f"Warning: Attempted to remove player '{player_name_to_remove}' not in current selection."
    #         )
