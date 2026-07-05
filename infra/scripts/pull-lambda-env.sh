#!/usr/bin/env bash
# Fetches the live environment variables from the Lambda function and writes
# them to infra/.env.lambda (gitignored) as KEY=value lines.
#
# Usage: infra/scripts/pull-lambda-env.sh [--function-name NAME] [--region REGION]
set -euo pipefail

FUNCTION_NAME="localelive-backend"
REGION="us-east-1"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --function-name) FUNCTION_NAME="$2"; shift 2 ;;
    --region) REGION="$2"; shift 2 ;;
    *) echo "Unknown argument: $1" >&2; exit 1 ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT_FILE="$SCRIPT_DIR/../.env.lambda"

echo "Fetching environment variables for Lambda function '$FUNCTION_NAME' ($REGION)..."

aws lambda get-function-configuration \
  --function-name "$FUNCTION_NAME" \
  --region "$REGION" \
  --query 'Environment.Variables' \
  --output json \
| python3 -c '
import json, sys
data = json.load(sys.stdin)
for key in sorted(data):
    print(f"{key}={data[key]}")
' > "$OUT_FILE"

echo "Wrote $(wc -l < "$OUT_FILE" | tr -d " ") variables to $OUT_FILE"
echo "This file contains live secrets and is gitignored — do not commit it."
