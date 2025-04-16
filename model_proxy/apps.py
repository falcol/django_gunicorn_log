from django.apps import AppConfig


class ModelProxyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'model_proxy'
