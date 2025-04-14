from fastapi import APIRouter
from controllers.EntrepreneurController import getAllEntrepreneurs, addEntrepreneur, deleteEntrepreneur, getEnterpreneurByUserId, updateEntrepreneur
from models.EntrepreneurModel import Entrepreneur, EntrepreneurUpdate

router = APIRouter()

# @router.get("/users/entrepreneurs/",tags=["Entrepreneurs"])
# async def get_all_entrepreneurs():
#     return await getAllEntrepreneurs()

@router.post("/users/entrepreneurs/",tags=["Entrepreneurs"])
async def add_entrepreneur(entrepreneur: Entrepreneur):
    return await addEntrepreneur(entrepreneur)

@router.delete("/users/entrepreneurs/{entrepreneurId}",tags=["Entrepreneurs"])
async def delete_entrepreneur(entrepreneurId: str):
    return await deleteEntrepreneur(entrepreneurId)

@router.get("/users/entrepreneurs/{userId}",tags=["Entrepreneurs"])
async def get_entrepreneur_by_userid(userId: str):
    return await getEnterpreneurByUserId(userId)

@router.put("/users/entrepreneurs/{userId}", tags=["Entrepreneurs"])
async def update_entrepreneur(userId: str, entrepreneur: EntrepreneurUpdate):
    return await updateEntrepreneur(userId, entrepreneur)
