#!/bin/bash
set -e

# Activate virtual environment
source /app/.venv/bin/activate

# On Lambda, /app is read-only but /tmp is writable.
# Copy the pre-built milvus DB to /tmp so Milvus Lite can open it.
# vector_db_push_batch() will be a no-op since the collection is already populated.
if [ -n "$AWS_LAMBDA_FUNCTION_NAME" ]; then
    PREBUILT_DB="/app/src/vector_db/milvus_lite.db"
    TARGET_DB="${MILVUS_DB_PATH:-/tmp/milvus_lite.db}"
    if [ -f "$PREBUILT_DB" ] && [ ! -f "$TARGET_DB" ]; then
        echo "Lambda: copying pre-built milvus DB to $TARGET_DB"
        cp "$PREBUILT_DB" "$TARGET_DB"
    fi
fi

# Change to src directory
cd /app/src

# Run Alembic migrations (skip on Lambda — Neon handles schema)
if [ -z "$AWS_LAMBDA_FUNCTION_NAME" ]; then
    cd /app
    alembic upgrade head
    cd /app/src
fi

# Execute the command passed to docker run
exec "$@"