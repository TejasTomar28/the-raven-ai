"""Application logging configuration."""

import logging


logger = logging.getLogger("raven_ai")
"""Logger shared by RAVEN AI application modules."""

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)

logger.setLevel(logging.INFO)
logger.propagate = False
