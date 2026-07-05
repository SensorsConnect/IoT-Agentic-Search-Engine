#!/usr/bin/env bash
# Pushes infra/.env.lambda back up to the Lambda function's environment
# variables. Fetches the current config first and shows a diff of changed
# keys before asking for confirmation — this overwrites the live config.
#
# Usage: infra/scripts/push-lambda-env.sh [--function-name NAME] [--region REGION] [--yes]
set -euo pipefail

FUNCTION_NAME="localelive-backend"
REGION="us-east-1"
ASSUME_YES=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --function-name) FUNCTION_NAME="$2"; shift 2 ;;
    --region) REGION="$2"; shift 2 ;;
    --yes) ASSUME_YES=true; shift ;;
    *) echo "Unknown argument: $1" >&2; exit 1 ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IN_FILE="$SCRIPT_DIR/../.env.lambda"

if [[ ! -f "$IN_FILE" ]]; then
  echo "Error: $IN_FILE not found. Run pull-lambda-env.sh first to create it." >&2
  exit 1
fi

CURRENT_JSON=$(aws lambda get-function-configuration \
  --function-name "$FUNCTION_NAME" \
  --region "$REGION" \
  --query 'Environment.Variables' \
  --output json)

DIFF_OUTPUT=$(python3 -c '
import json, sys

current = json.loads(sys.argv[1])
new = {}
with open(sys.argv[2]) as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        new[key] = value

all_keys = sorted(set(current) | set(new))
changed = False
for key in all_keys:
    old_val = current.get(key)
    new_val = new.get(key)
    if key not in current:
        print(f"  + {key} (new)")
        changed = True
    elif key not in new:
        print(f"  - {key} (removed)")
        changed = True
    elif old_val != new_val:
        print(f"  ~ {key} (changed)")
        changed = True

if not changed:
    print("NO_CHANGES")

print("---JSON---")
print(json.dumps(new))
' "$CURRENT_JSON" "$IN_FILE")

DIFF_SUMMARY="${DIFF_OUTPUT%%---JSON---*}"
NEW_JSON=$(echo "$DIFF_OUTPUT" | sed -n '/---JSON---/,$p' | tail -n +2)

if echo "$DIFF_SUMMARY" | grep -q "NO_CHANGES"; then
  echo "No changes detected between $IN_FILE and the live Lambda config. Nothing to do."
  exit 0
fi

echo "The following keys will change on Lambda function '$FUNCTION_NAME' ($REGION):"
echo "$DIFF_SUMMARY"

if [[ "$ASSUME_YES" != true ]]; then
  read -r -p "Apply these changes? [y/N] " CONFIRM
  if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
  fi
fi

aws lambda update-function-configuration \
  --function-name "$FUNCTION_NAME" \
  --region "$REGION" \
  --environment "Variables=$NEW_JSON" \
  --output json > /dev/null

echo "Lambda environment variables updated."
