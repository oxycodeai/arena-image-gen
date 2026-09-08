#!/bin/bash
# ============================================================================
# START VNC SERVICES + CHROME
# ============================================================================
# This script starts VNC services AND launches Chrome for Arena.ai login.
# Run this when user needs to login for the first time.
#
# Usage: bash start_vnc.sh
# ============================================================================

echo "============================================"
echo "  Starting VNC Services + Chrome..."
echo "============================================"

# Kill any existing instances
pkill -f "Xvfb :99" 2>/dev/null || true
pkill -f "x11vnc" 2>/dev/null || true
pkill -f "websockify" 2>/dev/null || true
pkill -f "chrome.*arena" 2>/dev/null || true

sleep 1

# Start virtual display
echo "[1/4] Starting Xvfb (virtual display)..."
Xvfb :99 -screen 0 1280x800x24 -nolisten tcp &
sleep 2

# Start VNC server (LOCALHOST ONLY - no public exposure)
echo "[2/4] Starting x11vnc (VNC server)..."
x11vnc -display :99 -nopw -listen 127.0.0.1 -forever -shared &
sleep 1

# Start noVNC (LOCALHOST ONLY)
echo "[3/4] Starting noVNC (HTML5 VNC client)..."
websockify --web /usr/share/novnc 6080 localhost:5900 &
sleep 1

# Launch Chrome in the virtual display
echo "[4/4] Launching Chrome..."
export DISPLAY=:99

# Find Chrome binary
CHROME_BIN=""
if [ -f "/usr/bin/google-chrome" ]; then
    CHROME_BIN="/usr/bin/google-chrome"
elif [ -f "/usr/bin/google-chrome-stable" ]; then
    CHROME_BIN="/usr/bin/google-chrome-stable"
elif [ -f "/usr/bin/chromium-browser" ]; then
    CHROME_BIN="/usr/bin/chromium-browser"
elif [ -f "/usr/bin/chromium" ]; then
    CHROME_BIN="/usr/bin/chromium"
fi

if [ -n "$CHROME_BIN" ]; then
    # Launch Chrome with arena.ai
    $CHROME_BIN \
        --no-sandbox \
        --disable-gpu \
        --disable-dev-shm-usage \
        --window-size=1280,800 \
        --disable-blink-features=AutomationControlled \
        --user-data-dir=$HOME/.arena-chrome-profile \
        "https://arena.ai" &
    
    CHROME_PID=$!
    sleep 3
    
    # Check if Chrome launched successfully
    if ps -p $CHROME_PID > /dev/null 2>&1; then
        echo "  Chrome launched successfully (PID: $CHROME_PID)"
    else
        echo "  WARNING: Chrome may have failed to launch"
        echo "  Try running manually: python3 arena_login.py"
    fi
else
    echo "  WARNING: Chrome not found!"
    echo "  Install Chrome first: bash install_vnc.sh"
    echo "  Or run manually: python3 arena_login.py"
fi

echo ""
echo "============================================"
echo "  VNC + Chrome Started!"
echo "============================================"
echo ""
echo "Access via SSH tunnel (from your phone/laptop):"
echo "  ssh -L 6080:127.0.0.1:6080 user@YOUR_VPS_IP"
echo ""
echo "Then open in browser:"
echo "  http://localhost:6080/vnc.html"
echo ""
echo "You should see Chrome with arena.ai loaded."
echo "Login with Google, then tell me to stop VNC."
echo ""
echo "To stop VNC: bash stop_vnc.sh"
echo "============================================"
