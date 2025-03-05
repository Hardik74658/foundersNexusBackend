from fastapi import APIRouter
from controllers.RoleController import getAllRoles,addRole,deleteRole,getRoleById
from models.RoleModel import Role

router = APIRouter()


@router.get("/roles/")
async def get_roles():
    return await getAllRoles()


@router.post("/roles/")
async def add_role(role:Role):
    return await addRole(role)

@router.delete("/roles/{roleId}")
async def delete_role(roleId:str):
    return await deleteRole(roleId)

@router.get("/roles/{roleId}")
async def get_role_by_id(roleId:str):
    return await getRoleById(roleId)