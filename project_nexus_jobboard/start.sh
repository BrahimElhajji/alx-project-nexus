#!/bin/bash
set -e

echo "Waiting for database..."
until pg_isready -h ${DB_HOST:-db} -p ${DB_PORT:-5432} -U ${DB_USER:-jobboard_user}; do
  echo "Database is unavailable - sleeping"
  sleep 1
done

echo "Database is up!"

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Starting server..."
if [ "$DEBUG" = "1" ]; then
    echo "Starting Django development server..."
    exec python manage.py runserver 0.0.0.0:8000
else
    echo "Starting Gunicorn production server..."
    exec gunicorn nexus_backend.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2
fi
