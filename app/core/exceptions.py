# app/core/exceptions.py
from fastapi import Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception: {exc}")  # Full traceback in logs
    return JSONResponse(
        status_code=500,
        content={"error": "INTERNAL_ERROR", "message": "Something went wrong"}
        # Never send str(exc) or traceback to clients
    )