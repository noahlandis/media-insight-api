from fastapi import APIRouter

router = APIRouter(
    prefix="/auth"
)

@router.get("/google")
async def google():
    return {"message": "welcome to Google"}

@router.get("/reddit")
async def reddit():
    return {"message": "welcome to Reddit"}

@router.get("/x")
async def reddit():
    return {"message": "welcome to x"}