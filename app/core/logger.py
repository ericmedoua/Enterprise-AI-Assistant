import sys

from loguru import logger  # type: ignore[import]

logger.remove()

logger.add(
    sys.stdout,
    level="INFO",
    format="<green>{time}</green> | <level>{level}</level> | {message}",
)

app_logger = logger
