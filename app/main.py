from app.core.logging import setup_logging, logger
from app.core.config import settings

setup_logging()

logger.info("Starting %s", settings.app_name)

from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from app.routers.api import api_router



app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    docs_url=f"{settings.api_v1_prefix}/docs",
    openapi_url=f"{settings.api_v1_prefix}/openapi.json",
)

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=settings.cors_origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/", tags=["root"])
async def root() -> dict[str, str]:
    return {"message": f"{settings.app_name} is running"}
