# gunicorn --workers 4 --access-logfile - --access-logformat="%(h)s %(l)s %(u)s %(t)s '%(r)s' %(s)s %(b)s" --error-logfile - django_gunicorn.wsgi:application
# cmd: gunicorn django_gunicorn.wsgi:application --config gunicorn_conf.py
# gunicorn  -c gunicorn_conf.py django_gunicorn.wsgi:application
# gunicorn_conf.py
# import os

# bind = f'unix:{os.getcwd()}/gunicorn.sock' # <<< DÒNG NÀY ĐÃ BỊ XÓA/COMMENT OUT
workers = 4  # Giữ lại cấu hình workers hoặc các cấu hình khác bạn muốn
accesslog = '-' # Ghi access log ra stdout để systemd/journald bắt
errorlog = '-'  # Ghi error log ra stderr để systemd/journald bắt
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s' # Định dạng log (tùy chọn)

# Bạn có thể thêm các cấu hình khác của Gunicorn tại đây nếu cần
# ví dụ: timeout = 120
