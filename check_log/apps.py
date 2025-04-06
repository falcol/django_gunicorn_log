import logging

from django.apps import AppConfig

logger = logging.getLogger("django")


class CheckLogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'check_log'

    def ready(self):
        # from .q_cluster_starter import start_django_q_cluster
        # start_django_q_cluster()

        from .aps_runner import start_scheduler
        start_scheduler()
