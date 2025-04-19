from fastapi import APIRouter

router = APIRouter(prefix="/games", tags=["games"])


@router.get("/")
async def read_users():
    return [{"username": "Rick"}, {"username": "Morty"}]
