#!/bin/bash
set -e

echo "=========================================="
echo "Linux Registration Client - Setup"
echo "=========================================="

if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo "ERROR: Cannot detect OS"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "Installation directory: $SCRIPT_DIR"

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo ""
echo "[1/4] Installing system dependencies..."

if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    echo "Detected: Ubuntu/Debian"
    sudo apt-get update -qq
    echo "  Installing: xvfb, fonts, build tools..."
    sudo apt-get install -y -qq \
        xvfb \
        fonts-noto-color-emoji \
        fonts-freefont-ttf \
        fonts-unifont \
        fonts-ipafont-gothic \
        fonts-wqy-zenhei \
        fonts-tlwg-loma-otf \
        build-essential \
        python3-dev \
        python3-pip \
        git \
        curl \
        wget
    echo "  OK"

elif [ "$OS" = "centos" ] || [ "$OS" = "rhel" ] || [ "$OS" = "fedora" ]; then
    echo "Detected: CentOS/RHEL/Fedora"
    sudo yum update -y -q
    sudo yum install -y -q \
        xorg-x11-server-Xvfb \
        google-noto-emoji-fonts \
        liberation-fonts \
        noto-fonts-cjk \
        noto-fonts-korean \
        texlive-fonts-all \
        gcc gcc-c++ make kernel-devel \
        python3-devel python3-pip \
        git curl wget
    echo "  OK"
else
    echo "ERROR: Unsupported OS: $OS"
    exit 1
fi

echo ""
echo "[2/4] Installing Python dependencies..."
if ! command_exists python3; then
    echo "ERROR: Python 3 not found"
    exit 1
fi
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "  Python version: $PYTHON_VERSION"
python3 -m pip install --upgrade -q pip setuptools wheel 2>/dev/null || true
echo "  Installing packages..."
pip3 install -q cloakbrowser>=0.3.0 playwright>=1.50.0 requests>=2.28.0 python-dotenv>=1.0.0 loguru>=0.7.0 urllib3
python3 -m playwright install chromium 2>&1 | grep -E "^(Installing|installing|Downloading)" || echo "  OK"
echo "  OK"

echo ""
echo "[3/4] Configuring virtual display..."
if command_exists systemctl; then
    echo "  Detected systemd"
fi
echo "  OK"

echo ""
echo "[4/4] Initializing configuration..."
CFG_FILE="$SCRIPT_DIR/cfg.txt"
if [ ! -f "$CFG_FILE" ]; then
    echo "  Creating default cfg.txt..."
    cat > "$CFG_FILE" << 'EOF'
# Configuration
# FRONT_IP=8.138.198.37
# DEBUG=false
EOF
    echo "  OK"
else
    echo "  Config already exists: $CFG_FILE"
fi

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next: cd $(dirname "$SCRIPT_DIR") && bash linux/_run.sh"
