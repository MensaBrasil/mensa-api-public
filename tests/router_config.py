from fastapi import APIRouter, Depends
from people_api.auth import permission_required
from people_api.schemas import FirebaseToken

test_router = APIRouter(tags=["Test"], prefix="/test")

@test_router.get("/auth-role-valid")
async def test_auth_role_valid(token_data: FirebaseToken = Depends(permission_required("CREATE.EVENT"))):
    return {"message": "Authenticated with CREATE.EVENT permission"}

@test_router.get("/auth-role-invalid")
async def test_auth_role_invalid(token_data: FirebaseToken = Depends(permission_required("NON_EXISTENT.PERMISSION"))):
    """This endpoint should always return a 403 because the permission does not exist."""
    return {"message": "Authenticated with NON_EXISTENT.PERMISSION"}  # Should never be reached.

@test_router.get("/auth-group-valid")
async def test_auth_group_valid(token_data: FirebaseToken = Depends(permission_required("WHATSAPP.BOT"))):
    """Tests that a user in BETA.TESTER group can authenticate based on permission."""
    return {"message": "Authenticated with WHATSAPP.BOT permission"}

@test_router.get("/auth-group-invalid")
async def test_auth_group_invalid(token_data: FirebaseToken = Depends(permission_required("EDIT.EVENT"))):
    """This should fail for our test user since they don’t have EDIT.EVENT permission."""
    return {"message": "Authenticated with EDIT.EVENT permission"}  # Should never be reached.