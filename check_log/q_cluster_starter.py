import atexit
import logging
import os
import threading

from django.utils.timezone import now
from django_q.cluster import Cluster, Process
from django_q.models import Schedule
from django_q.tasks import schedule

from .models import Lock

logger = logging.getLogger("django")
LOCK_NAME = 'django_q_cluster_lock'
_cluster_started = threading.Lock()
_has_started = False

def remove_lock():
    try:
        lock = Lock.objects.get(lock_name=LOCK_NAME)
        lock.is_lock = False
        lock.locked_by_pid = None
        lock.lock_at = None
        lock.save()
        logger.info("🧹 Removed database lock.")
    except Lock.DoesNotExist:
        logger.warning("Lock not found in database.")

def update_lock(lock: Lock):
    lock.is_lock = True
    lock.lock_at = now()
    lock.locked_by_pid = os.getpid()
    lock.save()
    atexit.register(remove_lock)

def start_django_q_cluster_once(sender=None, **kwargs):
    global _has_started
    with _cluster_started:
        if _has_started:
            return
        _has_started = True

        # Phần còn lại giữ nguyên
        lock, _ = Lock.objects.get_or_create(lock_name=LOCK_NAME)
        if lock.is_lock:
            logger.info("🔁 Django Q already running (lock is active).")
            return

        update_lock(lock)

        p = Process(target=Cluster().start)
        p.start()

        if not Schedule.objects.filter(name='log_time_task').exists():
            schedule(
                'check_log.tasks.log_time',
                name='log_time_task',
                schedule_type=Schedule.CRON,
                cron='*/1 * * * *',
                repeats=-1,
                next_run=now()
            )

        logger.info("✅ Django Q started by process PID %s", os.getpid())
