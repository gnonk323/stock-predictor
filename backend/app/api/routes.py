from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def read_welcome():
    return {"message": "Welcome to the backend!"}