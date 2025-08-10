FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Set Django settings
ENV DJANGO_SETTINGS_MODULE=nexus_backend.settings

# Create staticfiles directory
RUN mkdir -p /app/staticfiles

# Create startup script with proper line endings
RUN echo '#!/bin/bash' > /app/start.sh && \
    echo 'set -e' >> /app/start.sh && \
    echo 'echo "Waiting for database..."' >> /app/start.sh && \
    echo 'until pg_isready -h ${DB_HOST:-db} -p ${DB_PORT:-5432} -U ${DB_USER:-jobboard_user}; do' >> /app/start.sh && \
    echo '  echo "Database is unavailable - sleeping"' >> /app/start.sh && \
    echo '  sleep 1' >> /app/start.sh && \
    echo 'done' >> /app/start.sh && \
    echo 'echo "Database is up!"' >> /app/start.sh && \
    echo 'echo "Running migrations..."' >> /app/start.sh && \
    echo 'python manage.py migrate --noinput' >> /app/start.sh && \
    echo 'echo "Collecting static files..."' >> /app/start.sh && \
    echo 'python manage.py collectstatic --noinput --clear' >> /app/start.sh && \
    echo 'echo "Starting server..."' >> /app/start.sh && \
    echo 'if [ "$DEBUG" = "1" ]; then' >> /app/start.sh && \
    echo '  exec python manage.py runserver 0.0.0.0:8000' >> /app/start.sh && \
    echo 'else' >> /app/start.sh && \
    echo '  exec gunicorn nexus_backend.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2' >> /app/start.sh && \
    echo 'fi' >> /app/start.sh

# Make script executable
RUN chmod +x /app/start.sh

EXPOSE 8000

CMD ["/app/start.sh"]

