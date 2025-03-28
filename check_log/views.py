import logging

from django.http import HttpResponse

logger = logging.getLogger("django")

def log_message(request):
    logger.info('This is a test message.')
    return HttpResponse("Logged a message!")
# Create your views here.
