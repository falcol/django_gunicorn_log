# gunicorn --workers 4 --access-logfile - --access-logformat="%(h)s %(l)s %(u)s %(t)s '%(r)s' %(s)s %(b)s" --error-logfile - django_ginicorn.wsgi:application
# cmd: gunicorn django_ginicorn.wsgi:application --config gunicorn_conf.py

workers = 4
accesslog = '-'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s'
errorlog = '-'
