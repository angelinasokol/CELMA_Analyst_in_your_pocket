from fastapi import APIRouter

router = APIRouter()  # ← обязательно такое имя

@router.get("/test")
def test():
    return {"status": "ok"}