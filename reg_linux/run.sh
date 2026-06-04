#!/bin/bash
# GitHub Actions Registration Script
# Config from config.txt

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARENT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=== Twitch CDK Registration (Actions) ==="

# Load config
set -a
source "$SCRIPT_DIR/config.txt"
set +a

export API_URL="http://${FRONT_IP}:5000"

echo "Front: $API_URL | Count: ${REGISTER_COUNT:-10} | Threads: ${REG_THREADS:-3} | Debug: ${DEBUG:-false}"

if [ "$DEBUG" = "true" ]; then
    export LOGURU_LEVEL="DEBUG"
fi

# Install Python deps
pip3 install -r "$SCRIPT_DIR/requirements.txt" --quiet --break-system-packages 2>&1 || \
pip3 install -r "$SCRIPT_DIR/requirements.txt" --quiet 2>&1

mkdir -p "$PARENT_DIR/profiles"

echo "Starting..."
cd "$PARENT_DIR"
python3 -m reg_linux.main
echo "Done."
