from fastapi import APIRouter

router = APIRouter(prefix="/tournaments", tags=["tournaments"])


@router.get("/")
async def read_users():
    return [{"username": "Rick"}, {"username": "Morty"}]
