import atexit
import logging
import os
import threading

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from django.core.signals import request_started
from django.db import transaction
from django.dispatch import receiver
from django.utils.timezone import now

from .models import Lock
from .tasks import log_time

logger = logging.getLogger("django")
LOCK_NAME = "apscheduler_lock"
scheduler = BackgroundScheduler()

# Global variables to ensure the scheduler starts only once
_scheduler_started = threading.Lock()
_has_started = False

def remove_lock():
    """
    Remove the lock from the database when the process exits.
    """
    try:
        lock = Lock.objects.get(lock_name=LOCK_NAME)
        lock.is_lock = False
        lock.locked_by_pid = None
        lock.lock_at = None
        lock.save()
        logger.info("🧹 Removed APScheduler database lock.")
    except Lock.DoesNotExist:
        logger.warning("Lock not found in database.")

def update_lock(lock: Lock):
    """
    Update the lock in the database to indicate the scheduler is running.
    """
    lock.is_lock = True
    lock.lock_at = now()
    lock.locked_by_pid = os.getpid()
    lock.save()

    # Register the remove_lock function to clean up when the process exits
    atexit.register(remove_lock)

def create_lock():
    """
    Create or check the lock in the database to ensure only one instance of the scheduler runs.
    """
    try:
        with transaction.atomic():
            lock, created = Lock.objects.get_or_create(lock_name=LOCK_NAME)
            if lock.is_lock:
                logger.info("🔁 APScheduler already running (lock is active).")
                return False
            update_lock(lock)
        return True
    except Exception as e:
        logger.error(f"Error creating/updating lock: {e}")
        return False

def start_scheduler():
    """
    Start the APScheduler if the lock is successfully acquired.
    """
    if not create_lock():
        return

    scheduler.add_job(
        log_time,
        IntervalTrigger(seconds=5),
        id="log_time_job",
        name="Log time every 5 seconds",
        replace_existing=True
    )
    scheduler.start()
    logger.info(f"✅ APScheduler started by process PID {os.getpid()}")

# Use the request_started signal to trigger the scheduler startup
@receiver(request_started)
def start_scheduler_on_request(sender, **kwargs):
    """
    Start the scheduler when the first request is received.
    """
    global _has_started
    with _scheduler_started:
        if _has_started:
            # logger.info("🔁 Scheduler already started, skipping.")
            return
        _has_started = True

        logger.info("🌟 Request received, attempting to start APScheduler.")
        start_scheduler()
