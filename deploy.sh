#!/bin/bash
# chmod +x deploy.sh
#/home/falcol/django_gunicorn/deploy.sh
# Đường dẫn gốc của project
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"
DJANGO_MODULE="django_gunicorn"  # Đổi nếu khác
GUNICORN_CONF="$PROJECT_DIR/gunicorn_conf.py"
DOMAIN="localhost"  # Đổi nếu dùng domain
USER="falcol"

echo "🚀 Deploying project from: $PROJECT_DIR"
echo "🔁 Updating source code..."
cd "$PROJECT_DIR" || exit
git pull

if [ ! -d "$VENV_DIR" ]; then
    echo "🐍 Virtual environment not found. Creating one..."
    python3 -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment. Exiting."
        exit 1
    fi
    echo "✅ Virtual environment created successfully."
else
    echo "✅ Virtual environment already exists."
fi

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

echo "🛠️ Rendering Gunicorn systemd service..."

SERVICE_TEMPLATE="$PROJECT_DIR/template.gunicorn.service"
SERVICE_RENDERED="/tmp/gunicorn_rendered.service"
SERVICE_FILE="/etc/systemd/system/gunicorn.service"

sudo systemctl unmask gunicorn.service

sed \
    -e "s|__USER__|$USER|g" \
    -e "s|__PROJECT_DIR__|$PROJECT_DIR|g" \
    -e "s|__VENV_DIR__|$VENV_DIR|g" \
    -e "s|__GUNICORN_CONF__|$GUNICORN_CONF|g" \
    -e "s|__DJANGO_MODULE__|$DJANGO_MODULE|g" \
    "$SERVICE_TEMPLATE" > "$SERVICE_RENDERED"

sudo cp "$SERVICE_RENDERED" "$SERVICE_FILE"


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

TEMPLATE_FILE="$PROJECT_DIR/template.nginx"
TEMP_NGINX_CONF="/tmp/nginx_rendered.conf"
FINAL_NGINX_CONF="/etc/nginx/sites-available/django_project"

# Replace placeholders in the template
sed "s|__PROJECT_DIR__|$PROJECT_DIR|g; s|__DOMAIN__|$DOMAIN|g" "$TEMPLATE_FILE" > "$TEMP_NGINX_CONF"

# Copy to Nginx and create symlink
sudo cp "$TEMP_NGINX_CONF" "$FINAL_NGINX_CONF"
sudo ln -sf "$FINAL_NGINX_CONF" /etc/nginx/sites-enabled/

echo "✅ Testing nginx config..."
sudo nginx -t

echo "🔁 Restarting nginx..."
sudo systemctl restart nginx
echo "🔄 Reloading Nginx..."

echo "🎉 Deployment complete!"
