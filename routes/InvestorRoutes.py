from controllers.InvestorController import getAllInvestors, addInvestor, getInvestorById, deleteInvestor, updateInvestorProfile
from fastapi import APIRouter, Body
from models.InvestorModel import Investor 


router = APIRouter()

# @router.get("/users/investors/",tags=["Investors"])
# async def get_all_investors():
#     return await getAllInvestors()

@router.post("/users/investors/",tags=["Investors"])
async def add_investor(investor: Investor):
    return await addInvestor(investor)

@router.get("/users/investors/{investorId}",tags=["Investors"])
async def get_investor_by_id(investorId: str):
    return await getInvestorById(investorId)

@router.delete("/users/investors/{investorId}",tags=["Investors"])
async def delete_investor(investorId: str):
    return await deleteInvestor(investorId)

@router.put("/users/investors/{userId}", tags=["Investors"])
async def update_investor_profile(userId: str, investor_update: dict = Body(...)):
    """
    Update investor profile by userId.
    """
    return await updateInvestorProfile(userId, investor_update)