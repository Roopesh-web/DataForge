import sys
from pathlib import Path

from loguru import logger

from app.core.config import BASE_DIR, settings

LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "<level>{message}</level>"
)


def setup_logging() -> None:
    logger.remove()

    logger.add(
        sys.stderr,
        level=settings.log_level,
        format=LOG_FORMAT,
        colorize=True,
        backtrace=settings.debug,
        diagnose=settings.debug,
    )

    logger.add(
        LOG_DIR / "dataforge_{time:YYYY-MM-DD}.log",
        level=settings.log_level,
        format=LOG_FORMAT,
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        enqueue=True,
        backtrace=settings.debug,
        diagnose=settings.debug,
    )

    logger.info(
        "Logging configured | env={} | level={}",
        settings.app_env,
        settings.log_level,
    )


def get_logger(name: str | None = None):
    if name:
        return logger.bind(module=name)
    return logger
