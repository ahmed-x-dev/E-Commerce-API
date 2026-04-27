from fastapi import APIRouter, Response, status

from app.db.session import check_db_connection


router = APIRouter(tags=["health"])


@router.get("/health", summary="Health check")
def health_check(response: Response) -> dict[str, str]:
    """Report API and database availability for liveness monitoring."""
    db_ok = check_db_connection()
    if not db_ok:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "degraded", "database": "unavailable"}

    return {"status": "ok", "database": "connected"}
