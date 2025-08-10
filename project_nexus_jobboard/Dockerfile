
# Dockerfile

ckerfile
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput || true

# Create a script to run migrations and start the server
RUN echo '#!/bin/bash\n\
python manage.py migrate --noinput\n\
python manage.py collectstatic --noinput\n\
exec gunicorn nexus_backend.wsgi:application --bind 0.0.0.0:${PORT:-8000}' > /code/start.sh

RUN chmod +x /code/start.sh

CMD ["/code/start.sh"]
