#!/bin/bash
# Twitch CDK Registration Client - Linux
# Config: 同级目录 config.txt
# Usage: bash start.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARENT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PARENT_DIR"

echo "=== Twitch CDK Registration Client (Linux) ==="

# Python check
if command -v python3 &>/dev/null; then
    PYTHON=python3
elif command -v python &>/dev/null; then
    PYTHON=python
else
    echo "ERROR: Python not found"
    exit 1
fi
echo "Python: $($PYTHON --version)"

# pip check
if ! command -v pip3 &>/dev/null && ! command -v pip &>/dev/null; then
    echo "ERROR: pip not found. apt install -y python3-pip"
    exit 1
fi
if command -v pip3 &>/dev/null; then PIP=pip3; else PIP=pip; fi

# Load config
CONFIG_FILE="$SCRIPT_DIR/config.txt"
if [ ! -f "$CONFIG_FILE" ]; then
    cat > "$CONFIG_FILE" << 'EOF'
FRONT_IP=8.138.198.37
API_TOKEN=twitch-cdk-api-token-2024
MAIL_API_URL=https://mailapi.izlvxhe.cn
MAIL_ADMIN_AUTH=Aalcsttkx1!
REGISTER_COUNT=10
PREFIX=blue_ctf
PASSWORD=BlueCtf2026!Secure
DEBUG=false
EOF
    echo "默认配置文件已生成: $CONFIG_FILE"
    echo "请编辑后重新运行"
    exit 0
fi

# Parse config.txt and export as env vars
set -a
source "$CONFIG_FILE"
set +a

export API_URL="http://${FRONT_IP}:5000"
export REGISTER_COUNT
export PREFIX
export PASSWORD
export MAIL_API_URL
export MAIL_ADMIN_AUTH
export API_TOKEN
export DEBUG

# Set log level
if [ "$DEBUG" = "true" ]; then
    export LOGURU_LEVEL="DEBUG"
else
    export LOGURU_LEVEL="INFO"
fi

echo "Config loaded: $CONFIG_FILE"
echo "Front: $API_URL | Count: $REGISTER_COUNT | Debug: ${DEBUG:-false}"

# Install deps
if ! $PYTHON -c "import loguru" 2>/dev/null; then
    echo "Installing Python deps..."
    if $PIP install --help 2>&1 | grep -q break-system-packages; then
        $PIP install -r "$SCRIPT_DIR/requirements.txt" --quiet --break-system-packages 2>&1
    else
        $PIP install -r "$SCRIPT_DIR/requirements.txt" --quiet 2>&1 || \
        $PIP install -r "$SCRIPT_DIR/requirements.txt" --user --quiet 2>&1 || \
        sudo $PIP install -r "$SCRIPT_DIR/requirements.txt" --quiet 2>&1
    fi
fi

mkdir -p "$PARENT_DIR/profiles"

echo "Starting..."
$PYTHON -m reg_linux.main
echo "Done."
