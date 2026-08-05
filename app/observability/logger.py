import logging

logger = logging.getLogger("enterprise-ai")

logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()

    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    handler.setFormatter(formatter)

    logger.addHandler(handler)
