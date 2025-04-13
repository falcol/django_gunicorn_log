#!/bin/bash
#/home/falcol/django_gunicorn/deploy.sh
# Đường dẫn gốc của project
PROJECT_DIR="/home/falcol/django_gunicorn"  # Đổi nếu khác
VENV_DIR="$PROJECT_DIR/venv"
DJANGO_MODULE="django_gunicorn"  # Đổi nếu khác
GUNICORN_CONF="$PROJECT_DIR/gunicorn_conf.py"
DOMAIN="localhost"  # Đổi nếu dùng domain
USER="falcol"

echo "🔁 Updating source code..."
cd "$PROJECT_DIR" || exit
git pull

echo "🐍 Activating virtualenv..."
source "$VENV_DIR/bin/activate"

echo "📦 Installing dependencies..."
pip install -r requirements.txt

# echo "⚙️ Running migrations..."
# python manage.py migrate

echo "🧹 Removing old static files..."
rm -rf $PROJECT_DIR/staticfiles/*  # Xóa tất cả file static cũ

echo "🎨 Collecting static files..."
# python manage.py collectstatic --noinput

echo "🛠️ Creating Gunicorn systemd service..."

SERVICE_FILE="/etc/systemd/system/gunicorn.service"

sudo bash -c "cat > $SERVICE_FILE" <<EOL
[Unit]
Description=gunicorn daemon for Django project
After=network.target

[Service]
User=$USER
Group=www-data
WorkingDirectory=$PROJECT_DIR
ExecStart=$VENV_DIR/bin/gunicorn -c $GUNICORN_CONF $DJANGO_MODULE.wsgi:application

[Install]
WantedBy=multi-user.target
EOL

echo "🧹 Checking and removing old gunicorn socket if exists..."
SOCKET_FILE="$PROJECT_DIR/gunicorn.sock"
if [ -e "$SOCKET_FILE" ]; then
    echo "⚠️ Found existing socket. Removing..."
    rm "$SOCKET_FILE"
else
    echo "✅ No old socket found."
fi

echo "🔄 Restarting gunicorn service..."
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable gunicorn
sudo systemctl restart gunicorn

echo "🌐 Setting up Nginx..."

NGINX_CONF="/etc/nginx/sites-available/django_project"

sudo bash -c "cat > $NGINX_CONF" <<EOL
server {
    listen 9000;
    server_name $DOMAIN;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        alias $PROJECT_DIR/staticfiles/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:$PROJECT_DIR/gunicorn.sock;
    }
}
EOL

sudo ln -sf "$NGINX_CONF" /etc/nginx/sites-enabled/

echo "✅ Testing nginx config..."
sudo nginx -t

echo "🔁 Restarting nginx..."
sudo systemctl restart nginx

echo "🎉 Deployment complete!"
