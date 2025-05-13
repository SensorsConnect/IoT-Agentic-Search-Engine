#!/bin/bash
set -e

# Activate virtual environment
source /app/.venv/bin/activate

# Change to src directory
cd /app/src

# Run database migrations or other startup tasks here if needed
# For example:
# python manage.py migrate

# Execute the command passed to docker run
exec "$@" 