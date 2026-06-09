#!/bin/bash
set -e

echo "=== Runner Init ==="

export DISPLAY=:99
export XAUTHORITY=/tmp/.Xauthority

if ! pgrep -x Xvfb > /dev/null; then
    echo "Starting Xvfb..."
    Xvfb :99 -screen 0 1920x1080x24 > /dev/null 2>&1 &
    XVFB_PID=$!
    sleep 2
    echo "Xvfb PID: $XVFB_PID"
fi

if [ -f "linux/cfg.txt" ]; then
    echo "Loading config..."
    set -a
    source <(grep -v '^#' linux/cfg.txt | grep -v '^$')
    set +a
    echo "  FRONT_IP: ${FRONT_IP:-not set}"
    echo "  REG_THREADS: ${REG_THREADS:-1}"
    echo "  REGISTER_COUNT: ${REGISTER_COUNT:-10}"
    echo "  PREFIX: ${PREFIX:-default}"
else
    echo "WARN: cfg.txt not found"
fi

export TWITCH_CTF=1
export LOGURU_LEVEL=INFO

cd linux

if ! python3 -c "import playwright" 2>/dev/null; then
    echo "Installing deps..."
    pip install -r req.txt
fi

echo "Starting with WORKER_ID: ${WORKER_ID:-reg_worker}"
python3 -m linux

echo "Done."
