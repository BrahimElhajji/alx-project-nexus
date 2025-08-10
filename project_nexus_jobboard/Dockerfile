FROM python:3.10-slim

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Set environment variables for Railway
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=nexus_backend.settings

# Expose port
EXPOSE 8000

# Simple startup command
CMD python manage.py migrate && python manage.py runserver 0.0.0.0:${PORT:-8000}

