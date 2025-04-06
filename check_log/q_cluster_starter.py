# myapp/q_cluster_starter.py

import atexit
import logging
import os
from multiprocessing import Process

from django.utils.timezone import now
from django_q.cluster import Cluster
from django_q.models import Schedule
from django_q.tasks import schedule

logger = logging.getLogger(__name__)
LOCK_FILE = "./django_q_cluster.lock"

def remove_lock_file():
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)
        logger.info("🧹 Removed APScheduler lock file.")


def start_django_q_cluster():
    # Nếu đã khởi động rồi thì không chạy nữa
    if hasattr(start_django_q_cluster, "_started"):
        return
    start_django_q_cluster._started = True

    if os.path.exists(LOCK_FILE):
        logger.info("🔁 Django Q already running (lock file exists).")
        return

    with open(LOCK_FILE, "w") as f:
        f.write("locked")

    # Đăng ký hàm xoá lock file khi process kết thúc
    atexit.register(remove_lock_file)


    # Start the cluster in a separate process
    p = Process(target=Cluster().start)
    p.start()

    # Schedule task if not already scheduled
    if not Schedule.objects.filter(name='log_time_task').exists():
        schedule(
            'myapp.tasks.log_time',
            name='log_time_task',
            schedule_type=Schedule.CRON,
            cron='*/1 * * * *',  # mỗi phút
            repeats=-1,
            next_run=now()
        )
    logger.info("✅ Django Q started by process PID %s", os.getpid())
