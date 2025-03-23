from fastapi import APIRouter
from controllers.EntrepreneurController import getAllEntrepreneurs, addEntrepreneur, deleteEntrepreneur
from models.EntrepreneurModel import Entrepreneur

router = APIRouter()

@router.get("/users/entrepreneurs/",tags=["Entrepreneurs"])
async def get_all_entrepreneurs():
    return await getAllEntrepreneurs()

@router.post("/users/entrepreneurs/",tags=["Entrepreneurs"])
async def add_entrepreneur(entrepreneur: Entrepreneur):
    return await addEntrepreneur(entrepreneur)

@router.delete("/users/entrepreneurs/{entrepreneurId}",tags=["Entrepreneurs"])
async def delete_entrepreneur(entrepreneurId: str):
    return await deleteEntrepreneur(entrepreneurId)
