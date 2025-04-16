# gunicorn --workers 4 --access-logfile - --access-logformat="%(h)s %(l)s %(u)s %(t)s '%(r)s' %(s)s %(b)s" --error-logfile - django_gunicorn.wsgi:application
# cmd: gunicorn django_gunicorn.wsgi:application --config gunicorn_conf.py
# gunicorn  -c gunicorn_conf.py django_gunicorn.wsgi:application
import os

bind = f'unix:{os.getcwd()}/gunicorn.sock'
workers = 4
accesslog = '-'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s'
errorlog = '-'
