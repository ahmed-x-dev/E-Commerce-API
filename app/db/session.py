from collections.abc import Iterator

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.core.logging import logger
from app.db.base import Base

# Define engine arguments based on the database URL and application settings
engine_kwargs: dict[str, object] = {
    "echo": settings.debug,
    "pool_pre_ping": True,
}

# sqlite does not support pooling arguments like pool_size/max_overflow.
if not settings.database_url.startswith("sqlite"):
    engine_kwargs.update(
        {
            "pool_size": 5,
            "max_overflow": 10,
            "pool_recycle": 1800,
        }
    )

# Create the SQLAlchemy engine using the database URL from settings and the defined engine arguments
engine = create_engine(settings.database_url, **engine_kwargs)

# Create a configured "Session" class and a session factory
SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    autocommit=False,
    autoflush=False,
)

# Dependency function to check the database connection by executing a simple query
def check_db_connection() -> bool:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except SQLAlchemyError:
        logger.exception("Database connection check failed.")
        return False

# Function to initialize the database, optionally creating tables based on the defined models
def init_db(create_tables: bool = False) -> None:
    if create_tables:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created.")

    if check_db_connection():
        logger.info("Database connection is healthy.")
    else:
        logger.warning("Database connection is not healthy.")


# Dependency function to get a database session for use in FastAPI endpoints
def get_db() -> Iterator[Session]:
    session = SessionLocal()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
