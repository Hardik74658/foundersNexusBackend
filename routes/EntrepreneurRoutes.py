from fastapi import APIRouter
from controllers import EntrepreneurController
from models.EntrepreneurModel import Entrepreneur


router = APIRouter()


@router.get("/users/entrepreneurs/")
async def get_all_entrepreneurs():
    await EntrepreneurController.getAllEntrepreneurs()

@router.post("/users/entrepreneurs/")
async def add_entrepreneur(entrepreneur:Entrepreneur):
    await EntrepreneurController.addEntrepreneur(entrepreneur)
