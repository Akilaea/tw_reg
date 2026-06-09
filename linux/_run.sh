#!/bin/sh
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PARENT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PARENT_DIR"

echo "=== Linux Registration Client ==="

if command -v python3 >/dev/null 2>&1; then
    PYTHON=python3
elif command -v python >/dev/null 2>&1; then
    PYTHON=python
else
    echo "ERROR: Python not found"
    exit 1
fi
echo "Python: $($PYTHON --version)"

if command -v pip3 >/dev/null 2>&1; then
    PIP=pip3
elif command -v pip >/dev/null 2>&1; then
    PIP=pip
else
    echo "ERROR: pip not found"
    exit 1
fi

CFG_FILE="$SCRIPT_DIR/cfg.txt"
if [ ! -f "$CFG_FILE" ]; then
    cat > "$CFG_FILE" << 'EOF'
# Configuration  
# FRONT_IP=8.138.198.37
# DEBUG=false
EOF
    echo "Config created: $CFG_FILE, please edit and re-run"
    exit 0
fi

set -a
. "$CFG_FILE"
set +a

if [ -n "$FRONT_IP" ]; then
    export API_URL="http://${FRONT_IP}:5000"
    export FRONT_IP
fi

if [ "$DEBUG" = "true" ]; then
    export LOGURU_LEVEL="DEBUG"
fi

if [ -n "$REGISTER_COUNT" ]; then
    export REGISTER_COUNT
fi
if [ -n "$REG_THREADS" ]; then
    export REG_THREADS
fi

echo "Front: ${API_URL:-default} | Count: ${REGISTER_COUNT:-10} | Threads: ${REG_THREADS:-1} | Debug: ${DEBUG:-false}"

if ! $PYTHON -c "import loguru" 2>/dev/null; then
    echo "Installing Python deps..."
    if $PIP install --help 2>&1 | grep -q break-system-packages; then
        $PIP install -r "$SCRIPT_DIR/req.txt" --quiet --break-system-packages 2>&1
    else
        $PIP install -r "$SCRIPT_DIR/req.txt" --quiet 2>&1 || \
        $PIP install -r "$SCRIPT_DIR/req.txt" --user --quiet 2>&1 || \
        sudo $PIP install -r "$SCRIPT_DIR/req.txt" --quiet 2>&1
    fi
fi

echo "Installing browser + system dependencies..."
if command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update -qq 2>/dev/null
    sudo apt-get install -y -qq \
        libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 \
        libdbus-1-3 libxkbcommon0 libxcomposite1 libxdamage1 \
        libxfixes3 libxrandr2 libgbm1 libpango-1.0-0 libcairo2 \
        libnss3 libnspr4 libx11-xcb1 libxcb1 libasound2t64 \
        xvfb \
        2>/dev/null || true
fi
$PYTHON -c "from cloakbrowser import ensure_binary; ensure_binary()" 2>/dev/null || true
echo "Browser ready"

mkdir -p "$PARENT_DIR/profiles"

echo "Starting..."
$PYTHON -m linux
echo "Done."
