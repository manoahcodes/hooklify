#!/bin/bash
set -e

# Default to port 80 if not set
RUN_PORT="${PORT:-80}"

echo "Running Django setup..."

# Collect static files
python manage.py collectstatic --noinput

# Pull vendor files
python manage.py vendor_pull || echo "Warning: vendor_pull failed but continuing..."

# Run migrations
python manage.py migrate --noinput

# Start the server
gunicorn ${PROJ_NAME}.wsgi:application --bind "0.0.0.0:$RUN_PORT"
