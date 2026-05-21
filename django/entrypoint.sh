#!/bin/sh
set -e

echo "Waiting for MySQL..."
# 等待数据库就绪（可根据实际配置调整 host 和 port）
while ! nc -z db 3306; do
  sleep 1
done
echo "MySQL started"

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Starting Gunicorn..."
exec gunicorn -c gunicorn.conf.py simpleserver.wsgi:application
