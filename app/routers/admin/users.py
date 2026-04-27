from fastapi import APIRouter, Depends

from app.security.dependencies import get_admin_user
router = APIRouter()


@router.get("/staff_ping")
def staff_ping():
    """Simple endpoint to verify staff router access is working."""
    return {"ok": True}

@router.get("/admin_ping")
def admin_ping(
    current_user= Depends(get_admin_user)
    ):
    """Simple endpoint to verify admin router access is working."""
    return {"ok": True}
