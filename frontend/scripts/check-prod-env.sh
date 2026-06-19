#!/bin/sh
# Verify .env.production contains every required key with a non-empty value.
# Runs inside the frontend Dockerfile before `next build`, so a missing
# NEXT_PUBLIC_* fails the docker build instead of silently shipping a broken
# client bundle.

set -eu

ENV_FILE="${ENV_FILE:-.env.production}"

REQUIRED="
NEXT_PUBLIC_BACKEND_URL
NEXT_PUBLIC_MAPBOX_TOKEN
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
CLERK_SECRET_KEY
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_SIGN_IN_FALLBACK_REDIRECT_URL=/chat
NEXT_PUBLIC_CLERK_SIGN_UP_FALLBACK_REDIRECT_URL=/chat
"

if [ ! -f "$ENV_FILE" ]; then
    echo "ERROR: $ENV_FILE not found. Copy .env.production.example and populate it," >&2
    echo "       or ensure the FRONTEND_ENV_PRODUCTION CI secret writes this file." >&2
    exit 1
fi

missing=""
for entry in $REQUIRED; do
    # Entries may be "KEY" or "KEY=default" — only the key matters for lookup.
    key="${entry%%=*}"
    # Find "KEY=..." in the env file, take the first match, strip everything up to and
    # including the first "=" to get the raw value. Using grep+cut (not sed) because
    # BusyBox sed (Alpine) rejects the combined substitution/quote-stripping pattern.
    line=$(grep "^${key}=" "$ENV_FILE" 2>/dev/null | head -n1 || true)
    value="${line#*=}"
    # Strip optional surrounding single or double quotes via POSIX parameter expansion.
    case "$value" in
        \"*\") value="${value#\"}"; value="${value%\"}" ;;
        \'*\') value="${value#\'}"; value="${value%\'}" ;;
    esac
    case "$value" in
        "" | *REPLACE_ME*)
            missing="${missing} ${key}"
            ;;
    esac
done

if [ -n "$missing" ]; then
    echo "ERROR: required keys missing or empty in $ENV_FILE:" >&2
    for key in $missing; do
        echo "  - $key" >&2
    done
    echo "See frontend/.env.production.example for the full list." >&2
    exit 1
fi

echo "check-prod-env: all required keys present in $ENV_FILE."
