from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.db.session import init_db
from app.routers.api import api_router


from app.core.exceptions import global_exception_handler

setup_logging()

logger.info("Starting %s", settings.app_name)

# FastAPI application with lifespan event to initialize the database connection
@asynccontextmanager #   
async def lifespan(_: FastAPI): 
    init_db(create_tables=False) 
    yield

# FastAPI application instance with metadata and lifespan configuration
app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    docs_url=f"{settings.api_v1_prefix}/docs",
    openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    lifespan=lifespan,

)

# CORS middleware configuration
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins, # Allow origins from settings
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

# Global exception handler for all unhandled exceptions
app.add_exception_handler(Exception, global_exception_handler) 

# Include API router with versioned prefix
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/", tags=["root"])
def root() -> dict[str, str]:
    """Return a basic message confirming the API process is running."""
    return {"message": f"{settings.app_name} is running"}
