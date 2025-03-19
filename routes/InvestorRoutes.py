from controllers.InvestorController import getAllInvestors, addInvestor, getInvestorById, deleteInvestor
from fastapi import APIRouter
from models.InvestorModel import Investor 


router = APIRouter()

@router.get("/users/investors/")
async def get_all_investors():
    return await getAllInvestors()

@router.post("/users/investors/")
async def add_investor(investor: Investor):
    return await addInvestor(investor)

@router.get("/users/investors/{investorId}")
async def get_investor_by_id(investorId: str):
    return await getInvestorById(investorId)

@router.delete("/users/investors/{investorId}")
async def delete_investor(investorId: str):
    return await deleteInvestor(investorId)