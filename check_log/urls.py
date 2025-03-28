from django.urls import path

from .views import log_message

urlpatterns = [
    path('', log_message, name='index'),
]
