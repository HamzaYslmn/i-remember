from fastapi import APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

router = APIRouter(tags=["Root"])

@router.get("/status")
async def root():
    return {
        "status": "online",
        "output": "Welcome to the HamzaYslmn API Service! 🏔️",
        "message": (
            "Or perhaps you're looking for the answer to the ultimate question of life, "
            "the universe, and everything? 🌌"
        ),
    }