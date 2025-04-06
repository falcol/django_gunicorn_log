import atexit
import logging
import os

from django.utils.timezone import now
from django_q.cluster import Cluster, Process
from django_q.models import Schedule
from django_q.tasks import schedule

from .models import Lock  # Import model Lock

logger = logging.getLogger(__name__)
LOCK_NAME = 'django_q_cluster_lock'

def remove_lock():
    try:
        lock = Lock.objects.get(lock_name=LOCK_NAME)
        lock.lock_status = False
        lock.save()
        logger.info("🧹 Removed database lock.")
    except Lock.DoesNotExist:
        logger.warning("Lock not found in database.")

def start_django_q_cluster():
    # Nếu đã khởi động rồi thì không chạy nữa
    if hasattr(start_django_q_cluster, "_started"):
        return
    start_django_q_cluster._started = True

    # Kiểm tra nếu lock đã tồn tại và đang được giữ
    lock, created = Lock.objects.get_or_create(lock_name=LOCK_NAME)
    if lock.lock_status:
        logger.info("🔁 Django Q already running (lock is active).")
        return

    # Đặt lock trong DB
    lock.lock_status = True
    lock.save()

    # Đăng ký hàm xoá lock khi process kết thúc
    atexit.register(remove_lock)

    # Start the cluster in a separate process
    p = Process(target=Cluster().start)
    p.start()

    # Schedule task if not already scheduled
    if not Schedule.objects.filter(name='log_time_task').exists():
        schedule(
            'check_log.tasks.log_time',
            name='log_time_task',
            schedule_type=Schedule.CRON,
            cron='*/1 * * * *',  # mỗi phút
            repeats=-1,
            next_run=now()
        )

    logger.info("✅ Django Q started by process PID %s", os.getpid())
