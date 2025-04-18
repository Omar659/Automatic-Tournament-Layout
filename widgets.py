from nicegui import ui, app

from db import add_player_to_db, check_if_player_exists, get_players_list_from_db, remove_player_from_db

class Header:

    def __init__(self):
        self.build()

    def build(self):
        with ui.header(elevated=True).style("background-color: #3874c8").classes(
            "items-center justify-between"
        ):
            ui.label("Automatic Tournament Layout".upper())
            
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
        # notify the user for the success
        ui.notify(f"Added player {player_name}")
        # eventually refresh player's list
        if self.players_list_widget:
            self.players_list_widget.build.refresh()
