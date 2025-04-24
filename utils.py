from nicegui import ui, app
from pydantic import ValidationError

from .models import User

def get_user() -> User | None:
    user_data = app.storage.user.get("user", None)
    if user_data is not None:
        try:
            user_data = User(**user_data)
        except ValidationError as e:
            del app.storage.user["user"]
            return None
    return user_data
