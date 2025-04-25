from nicegui import ui, app
from pydantic import ValidationError

from ..backend.models import User

def set_current_user(user: User | None):
    assert user is None or isinstance(user, User), f"got type {type(user)}"
    if user is None:
        del app.storage.user["user"]
    else:
        app.storage.user["user"] = user.model_dump()

def get_current_user() -> User | None:
    user_data = app.storage.user.get("user", None)
    if user_data is not None:
        try:
            user_data = User(**user_data)
        except ValidationError as e:
            del app.storage.user["user"]
            return None
    return user_data
