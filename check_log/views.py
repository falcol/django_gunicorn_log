import logging

from django.http import HttpResponse
from django.utils import timezone

logger = logging.getLogger("django")

def log_message(request):
    logger.info('This is a test message.')
    localtime = timezone.localtime(timezone.now())
    return HttpResponse(f"Logged a message! Current time is: {localtime}")
# Create your views here.
