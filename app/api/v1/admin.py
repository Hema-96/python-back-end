from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.core.database import get_session
from app.services.admin_service import AdminService
from app.middleware.auth import get_current_user, require_admin
from app.models.user import User
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/dashboard-tiles", summary="Get admin dashboard statistics")
async def get_admin_dashboard_tiles(
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    """
    Get admin dashboard statistics including:
    - Total registered students
    - Approved colleges count
    - Total available seats from approved colleges
    - Current round number
    
    **Required Role:** Admin (Role 1)
    """
    try:
        admin_service = AdminService(session)
        return admin_service.admin_dashboard_tiles()
    except Exception as e:
        logger.error(f"Error getting admin dashboard tiles: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
