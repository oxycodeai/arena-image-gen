#!/bin/bash
# ============================================================================
# STOP VNC SERVICES
# ============================================================================
# This script stops all VNC services.
# Run this after login is complete to free resources.
#
# Usage: bash stop_vnc.sh
# ============================================================================

echo "Stopping VNC services..."

pkill -f "Xvfb :99" 2>/dev/null
pkill -f "x11vnc" 2>/dev/null
pkill -f "websockify" 2>/dev/null

sleep 1

echo "VNC services stopped."
echo "Port 6080 is now free."
