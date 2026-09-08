#!/bin/bash
# ============================================================================
# START VNC SERVICES
# ============================================================================
# This script starts VNC services for Arena.ai login.
# Run this when user needs to login for the first time.
#
# Usage: bash start_vnc.sh
# ============================================================================

echo "============================================"
echo "  Starting VNC Services..."
echo "============================================"

# Kill any existing instances
pkill -f "Xvfb :99" 2>/dev/null || true
pkill -f "x11vnc" 2>/dev/null || true
pkill -f "websockify" 2>/dev/null || true

sleep 1

# Start virtual display
echo "[1/3] Starting Xvfb (virtual display)..."
Xvfb :99 -screen 0 1280x800x24 -nolisten tcp &
sleep 2

# Start VNC server (LOCALHOST ONLY - no public exposure)
echo "[2/3] Starting x11vnc (VNC server)..."
x11vnc -display :99 -nopw -listen 127.0.0.1 -forever -shared &
sleep 1

# Start noVNC (LOCALHOST ONLY)
echo "[3/3] Starting noVNC (HTML5 VNC client)..."
websockify --web /usr/share/novnc 6080 localhost:5900 &
sleep 1

echo ""
echo "============================================"
echo "  VNC Services Started!"
echo "============================================"
echo ""
echo "Access via SSH tunnel (from your phone/laptop):"
echo "  ssh -L 6080:127.0.0.1:6080 user@YOUR_VPS_IP"
echo ""
echo "Then open in browser:"
echo "  http://localhost:6080/vnc.html"
echo ""
echo "To stop VNC: bash stop_vnc.sh"
echo "============================================"
