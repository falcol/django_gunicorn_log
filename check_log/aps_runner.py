import atexit
import fcntl
import logging
import os

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from .tasks import log_time

logger = logging.getLogger("django")

LOCK_FILE = "./apscheduler.lock"
LOCK_FD = None
scheduler = BackgroundScheduler()

def create_lock_file():
    global LOCK_FD
    try:
        # Mở lock file và áp dụng flock (exclusive lock)
        LOCK_FD = os.open(LOCK_FILE, os.O_CREAT | os.O_RDWR)
        fcntl.flock(LOCK_FD, fcntl.LOCK_EX | fcntl.LOCK_NB)  # Try to lock non-blocking
        return True
    except BlockingIOError:
        return False  # Lock already acquired by another process
    except Exception as e:
        logger.error(f"Error creating lock file: {e}")
        raise

def remove_lock_file():
    global LOCK_FD
    if LOCK_FD:
        fcntl.flock(LOCK_FD, fcntl.LOCK_UN)  # Unlock
        os.close(LOCK_FD)
        os.remove(LOCK_FILE)
        logger.info("🧹 Removed APScheduler lock file.")

def start_scheduler():
    if not create_lock_file():
        logger.info("🔁 APScheduler already running (flock exists).")
        return

    # Register remove_lock_file to clean up lock when the process exits
    atexit.register(remove_lock_file)

    scheduler.add_job(
        log_time,
        IntervalTrigger(seconds=5),
        id="log_time_job",
        name="Log time every 5 seconds",
        replace_existing=True
    )
    scheduler.start()
    logger.info(f"✅ APScheduler started by process PID {os.getpid()}")
