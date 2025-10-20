#!/bin/bash
set -e

# Setup Python environment
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PYENV_ROOT/shims:$HOME/.local/bin:$PATH"
eval "$(pyenv init -)"

# Set default display number if not set
export DISPLAY_NUM=${DISPLAY_NUM:-1}
export DISPLAY=:${DISPLAY_NUM}
./scripts/xvfb_startup.sh
./scripts/tint2_startup.sh
./scripts/mutter_startup.sh
./scripts/x11vnc_startup.sh
./scripts/novnc_startup.sh

# Start FastAPI application
echo "starting FastAPI app..."
uvicorn main:app --host 0.0.0.0 --port 8000 &

echo "✨ Ready! ✨ "
echo "computer-use-v2-api is running at http://localhost:8000"

# Keep the container running
tail -f /dev/null
