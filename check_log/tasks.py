# myapp/tasks.py
import logging

from django.utils import timezone

logger = logging.getLogger("django")

def log_time():
    logger.info(f"[log_time] Now is {timezone.now()}")



