# myapp/tasks.py
import logging

from django.utils import timezone

logger = logging.getLogger("django")

def log_time():
    local_time = timezone.localtime(timezone.now())
    logger.info(f"[log_time] Now is {local_time}")  # Updated to log local_time instead of timezone.now()



