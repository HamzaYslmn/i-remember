from fastapi import APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from modules.Supabase import xSupabase

router = APIRouter(tags=["Root"])

@router.get("/status")
async def root():
    try:
        await xSupabase.read_sdoc("i-remember", doc_id=["141ed198-7b29-4e32-b64a-f63d5f3b9748"], select="uuid")
    except Exception as e:
        print(f"Error: {e}")
        
    return {
        "status": "online",
        "output": "Welcome to the HamzaYslmn API Service! 🏔️",
        "message": (
            "Or perhaps you're looking for the answer to the ultimate question of life, "
            "the universe, and everything? 🌌"
        ),
    }