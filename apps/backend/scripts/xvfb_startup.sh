#!/bin/bash
set -e  # Exit on error

# Set default screen resolution and color depth
WIDTH=${WIDTH:-1024}
HEIGHT=${HEIGHT:-768}
DEPTH=${DEPTH:-24}
DPI=${DPI:-96}

echo "Starting Xvfb with resolution ${WIDTH}x${HEIGHT}x${DEPTH}"

# Function to check if Xvfb is already running
check_xvfb_running() {
    if [ -e /tmp/.X${DISPLAY_NUM}-lock ]; then
        return 0  # Xvfb is already running
    else
        return 1  # Xvfb is not running
    fi
}

# Function to check if Xvfb is ready
wait_for_xvfb() {
    local timeout=10
    local start_time=$(date +%s)
    while ! xdpyinfo >/dev/null 2>&1; do
        if [ $(($(date +%s) - start_time)) -gt $timeout ]; then
            echo "Xvfb failed to start within $timeout seconds" >&2
            return 1
        fi
        sleep 0.1
    done
    return 0
}

# Check if Xvfb is already running
if check_xvfb_running; then
    echo "Xvfb is already running on display ${DISPLAY}"
    exit 0
fi

# Start Xvfb
Xvfb :${DISPLAY_NUM} -screen 0 ${WIDTH}x${HEIGHT}x${DEPTH} -ac -dpi ${DPI} &
XVFB_PID=$!

# Wait for Xvfb to start
if wait_for_xvfb; then
    echo "Xvfb started successfully on display ${DISPLAY}"
    echo "Xvfb PID: $XVFB_PID"
else
    echo "Xvfb failed to start"
    kill $XVFB_PID
    exit 1
fi
