#!/bin/bash
# chmod +x deploy.sh
#/home/falcol/django_gunicorn/deploy.sh

# --- Configuration ---
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"
DJANGO_MODULE="django_gunicorn"  # Đổi nếu tên thư mục chứa wsgi.py khác
GUNICORN_CONF="$PROJECT_DIR/gunicorn_conf.py"
LOG_DIR="$PROJECT_DIR/logs"
DOMAIN="localhost"  # <<< THAY ĐỔI DOMAIN/IP CỦA BẠN
USER="falcol" # User sở hữu project và chạy Gunicorn
SOCKET_PATH="/run/gunicorn.sock" # Đường dẫn socket chuẩn do Systemd quản lý

# --- Script Start ---
echo "🚀 Deploying project from: $PROJECT_DIR"
echo "🎯 Target Domain/IP: $DOMAIN"
echo "👤 Running as User: $USER"

echo "🔁 Updating source code..."
cd "$PROJECT_DIR" || exit 1
git pull
if [ $? -ne 0 ]; then echo "❌ Git pull failed."; exit 1; fi

# --- Virtual Environment ---
if [ ! -d "$VENV_DIR" ]; then
    echo "🐍 Virtual environment not found. Creating one..."
    python3 -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then echo "❌ Failed to create virtual environment."; exit 1; fi
    echo "✅ Virtual environment created."
else
    echo "✅ Virtual environment exists."
fi

echo "🐍 Activating virtualenv..."
source "$VENV_DIR/bin/activate"
if [ $? -ne 0 ]; then echo "❌ Failed to activate virtual environment."; exit 1; fi

# --- Dependencies & Django Setup ---
echo "📦 Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then echo "❌ Failed to install dependencies."; exit 1; fi

# echo "⚙️ Running migrations..."
# python manage.py migrate # <<< BỎ COMMENT
# if [ $? -ne 0 ]; then echo "❌ Migrations failed."; exit 1; fi

echo "🧹 Clearing old static files..."
rm -rf $PROJECT_DIR/staticfiles/*

# echo "🎨 Collecting static files..."
# python manage.py collectstatic --noinput # <<< BỎ COMMENT
# if [ $? -ne 0 ]; then echo "❌ Collectstatic failed."; exit 1; fi

# --- Systemd Gunicorn Socket Setup ---
echo "🛠️ Rendering Gunicorn systemd socket..."
SOCKET_TEMPLATE="$PROJECT_DIR/template.gunicorn.socket"
SOCKET_RENDERED="/tmp/gunicorn_rendered.socket"
SOCKET_SERVICE_FILE="/etc/systemd/system/gunicorn.socket"

# Render template (thay __PROJECT_DIR__ để description rõ hơn)
sed -e "s|__PROJECT_DIR__|${PROJECT_DIR}|g" "$SOCKET_TEMPLATE" > "$SOCKET_RENDERED"
if [ $? -ne 0 ]; then echo "❌ Failed to render socket template."; exit 1; fi

echo "🔒 Copying rendered socket file..."
sudo cp "$SOCKET_RENDERED" "$SOCKET_SERVICE_FILE"
if [ $? -ne 0 ]; then echo "❌ Failed to copy socket file."; exit 1; fi

# --- Systemd Gunicorn Service Setup ---
echo "🛠️ Rendering Gunicorn systemd service..."
SERVICE_TEMPLATE="$PROJECT_DIR/template.gunicorn.service"
SERVICE_RENDERED="/tmp/gunicorn_rendered.service"
SERVICE_FILE="/etc/systemd/system/gunicorn.service"

# Render template
sed \
    -e "s|__USER__|$USER|g" \
    -e "s|__PROJECT_DIR__|${PROJECT_DIR}|g" \
    -e "s|__VENV_DIR__|${VENV_DIR}|g" \
    -e "s|__GUNICORN_CONF__|${GUNICORN_CONF}|g" \
    -e "s|__DJANGO_MODULE__|${DJANGO_MODULE}|g" \
    -e "s|__PROJECT_DIR__|${PROJECT_DIR}|g" \
    "$SERVICE_TEMPLATE" > "$SERVICE_RENDERED"
if [ $? -ne 0 ]; then echo "❌ Failed to render service template."; exit 1; fi

echo "🔒 Copying rendered service file..."
sudo cp "$SERVICE_RENDERED" "$SERVICE_FILE"
if [ $? -ne 0 ]; then echo "❌ Failed to copy service file."; exit 1; fi

# --- Reload Systemd and Restart Gunicorn ---
# echo "🧹 Checking and removing old gunicorn socket if exists..." # <<< KHÔNG CẦN NỮA
# ... (Phần code xóa socket cũ đã được xóa) ...

echo "🔄 Reloading systemd daemon..."
sudo systemctl daemon-reload

echo "🔌 Enabling and Restarting Gunicorn socket..."
sudo systemctl enable gunicorn.socket
sudo systemctl restart gunicorn.socket # Dùng restart để đảm bảo socket mới nhất được dùng
if [ $? -ne 0 ]; then echo "❌ Failed to restart gunicorn.socket."; exit 1; fi

echo "🚀 Enabling and Restarting Gunicorn service..."
sudo systemctl enable gunicorn.service
sudo systemctl restart gunicorn.service # Dùng restart để áp dụng thay đổi
if [ $? -ne 0 ]; then echo "❌ Failed to restart gunicorn.service."; exit 1; fi

# --- Nginx Setup ---
echo "🌐 Setting up Nginx..."
NGINX_TEMPLATE_FILE="$PROJECT_DIR/template.nginx"
NGINX_TEMP_CONF="/tmp/nginx_rendered.conf"
NGINX_FINAL_CONF="/etc/nginx/sites-available/${DJANGO_MODULE}" # Đặt tên file config theo tên project

# Replace placeholders
# Sử dụng dấu phân cách khác cho sed vì PROJECT_DIR chứa dấu /
sed "s|__PROJECT_DIR__|${PROJECT_DIR}|g; s|__DOMAIN__|${DOMAIN}|g" "$NGINX_TEMPLATE_FILE" > "$NGINX_TEMP_CONF"
if [ $? -ne 0 ]; then echo "❌ Failed to render Nginx template."; exit 1; fi

echo "🔒 Copying Nginx config..."
sudo cp "$NGINX_TEMP_CONF" "$NGINX_FINAL_CONF"
if [ $? -ne 0 ]; then echo "❌ Failed to copy Nginx config."; exit 1; fi

echo "🔗 Linking Nginx config..."
sudo ln -sf "$NGINX_FINAL_CONF" "/etc/nginx/sites-enabled/"
# Cân nhắc xóa link default nếu cần: sudo rm -f /etc/nginx/sites-enabled/default

echo "✅ Testing Nginx config..."
sudo nginx -t
if [ $? -ne 0 ]; then
    echo "❌ Nginx configuration test failed. Please check logs."
    exit 1
fi

echo "🔁 Reloading Nginx..."
sudo systemctl reload nginx # Dùng reload thay vì restart nếu chỉ thay đổi config
if [ $? -ne 0 ]; then echo "❌ Failed to reload Nginx."; exit 1; fi

# --- Deactivate Virtualenv ---
deactivate
echo "🐍 Virtual environment deactivated."

echo "🎉 Deployment complete! Access at http://$DOMAIN"
