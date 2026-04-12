import logging
import sys
from logging.config import dictConfig
from app.core.config import settings


def setup_logging() -> None:
    dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": "default",
            }
        },
        "root": {
            "level": "DEBUG" if settings.debug else "INFO",
            "handlers": ["console"],
        },
        "loggers": {
            "uvicorn.access": {"level": "WARNING"},
            "sqlalchemy.engine": {"level": "INFO" if settings.debug else "WARNING"},
        },
    })


logger = logging.getLogger("app")