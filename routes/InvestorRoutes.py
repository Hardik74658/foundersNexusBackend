from controllers import InvestorController
from fastapi import APIRouter
from models.InvestorModel import Investor 


router = APIRouter()

@router.get("/users/investors/")
async def get_all_investors():
    return await InvestorController.getAllInvestors()

@router.post("/users/investors/")
async def add_investor(investor: Investor):
    return await InvestorController.addInvestor(investor)

@router.get("/users/investors/{investorId}")
async def get_investor_by_id(investorId: str):
    return await InvestorController.getInvestorById(investorId)