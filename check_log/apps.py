import logging

from django.apps import AppConfig

logger = logging.getLogger("django")


class CheckLogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'check_log'

    def ready(self):
        # from django.core.signals import request_started

        # from .q_cluster_starter import start_django_q_cluster_once

        # Gắn signal, đảm bảo không khởi chạy quá sớm
        # request_started.connect(start_django_q_cluster_once)
        # from .q_cluster_starter import start_django_q_cluster
        # start_django_q_cluster()

        from .aps_runner import start_scheduler
        start_scheduler()
