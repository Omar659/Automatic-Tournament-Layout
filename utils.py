from nicegui import ui, app
from pydantic import ValidationError

from .models import GoogleUserData

def get_user_data():
    user_data = app.storage.user.get("user_data", None)
    if user_data is not None and not isinstance(user_data, dict):
        try:
            user_data = GoogleUserData()
        except ValidationError as e:
            del app.storage.user["user_data"]
            return None
    return user_data