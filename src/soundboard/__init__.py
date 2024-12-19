import logging

from soundboard.constants import settings

logging.basicConfig(level=settings.log_level)

logger = logging.getLogger(__file__)
