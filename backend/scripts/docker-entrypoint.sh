#!/bin/bash
set -e

# Activate virtual environment
source /app/.venv/bin/activate

# Change to src directory
cd /app/src

# Run Alembic migrations
cd /app
alembic upgrade head
cd /app/src

# Execute the command passed to docker run
exec "$@" 