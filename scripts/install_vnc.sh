#!/bin/bash
# ============================================================================
# ARENA.AI VNC SETUP - One-Time Installation
# ============================================================================
# This script installs everything needed for VNC-based login on a VPS.
# Run this ONCE on your VPS before first-time login.
#
# Usage: bash install_vnc.sh
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}"
    echo "============================================"
    echo "  ARENA.AI VNC SETUP - Installation"
    echo "============================================"
    echo -e "${NC}"
}

print_step() {
    echo -e "\n${GREEN}[STEP]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

# Check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "Please run as root (sudo bash install_vnc.sh)"
        exit 1
    fi
}

# Detect OS
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
        OS_VERSION=$VERSION_ID
        print_step "Detected OS: $OS $OS_VERSION"
    else
        print_error "Cannot detect OS. This script supports Ubuntu/Debian."
        exit 1
    fi
}

# Update system packages
update_system() {
    print_step "Updating system packages..."
    apt update -y
    apt upgrade -y
    print_success "System updated"
}

# Install essential tools
install_essentials() {
    print_step "Installing essential tools..."
    apt install -y \
        curl \
        wget \
        git \
        sudo \
        gnupg2 \
        software-properties-common \
        apt-transport-https \
        ca-certificates \
        lsb-release
    print_success "Essentials installed"
}

# Install Xvfb (virtual display)
install_xvfb() {
    print_step "Installing Xvfb (virtual display)..."
    apt install -y xvfb
    print_success "Xvfb installed"
}

# Install x11vnc (VNC server)
install_x11vnc() {
    print_step "Installing x11vnc (VNC server)..."
    apt install -y x11vnc
    print_success "x11vnc installed"
}

# Install noVNC (HTML5 VNC client)
install_novnc() {
    print_step "Installing noVNC (HTML5 VNC client)..."
    apt install -y novnc websockify
    print_success "noVNC installed"
}

# Install Google Chrome
install_chrome() {
    print_step "Installing Google Chrome..."
    
    # Add Google Chrome repository
    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg
    
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list
    
    apt update -y
    apt install -y google-chrome-stable
    
    # Verify installation
    if command -v google-chrome &> /dev/null; then
        CHROME_VERSION=$(google-chrome --version)
        print_success "Chrome installed: $CHROME_VERSION"
    else
        print_error "Chrome installation failed"
        exit 1
    fi
}

# Install Python 3 and pip
install_python() {
    print_step "Installing Python 3 and pip..."
    apt install -y python3 python3-pip python3-venv
    print_success "Python 3 installed"
}

# Install Playwright
install_playwright() {
    print_step "Installing Playwright..."
    
    # Install Playwright Python package
    pip3 install playwright
    
    # Install Playwright browsers
    playwright install chromium
    
    # Install system dependencies for Playwright
    playwright install-deps
    
    print_success "Playwright installed"
}

# Install project dependencies
install_project_deps() {
    print_step "Installing project dependencies..."
    
    # Create skill directory
    mkdir -p /root/.hermes/skills/arena-image-gen/auth
    mkdir -p /root/.hermes/skills/arena-image-gen/scripts
    mkdir -p /root/arena-output
    
    # Copy scripts to skill directory
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    cp "$SCRIPT_DIR"/*.py /root/.hermes/skills/arena-image-gen/scripts/ 2>/dev/null || true
    cp "$SCRIPT_DIR"/*.sh /root/.hermes/skills/arena-image-gen/scripts/ 2>/dev/null || true
    
    print_success "Project dependencies installed"
}

# Create VNC startup script
create_vnc_scripts() {
    print_step "Creating VNC management scripts..."
    
    # Start VNC script
    cat > /root/.hermes/skills/arena-image-gen/scripts/start_vnc.sh << 'EOF'
#!/bin/bash
# Start VNC services for Arena.ai login

# Kill any existing instances
pkill -f "Xvfb :99" 2>/dev/null || true
pkill -f "x11vnc" 2>/dev/null || true
pkill -f "websockify" 2>/dev/null || true

sleep 1

# Start virtual display
Xvfb :99 -screen 0 1280x800x24 -nolisten tcp &
sleep 2

# Start VNC server (LOCALHOST ONLY - no public exposure)
x11vnc -display :99 -nopw -listen 127.0.0.1 -forever -shared &
sleep 1

# Start noVNC (LOCALHOST ONLY)
websockify --web /usr/share/novnc 6080 localhost:5900 &
sleep 1

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
echo "To stop VNC: bash /root/.hermes/skills/arena-image-gen/scripts/stop_vnc.sh"
echo "============================================"
EOF
    
    # Stop VNC script
    cat > /root/.hermes/skills/arena-image-gen/scripts/stop_vnc.sh << 'EOF'
#!/bin/bash
# Stop VNC services

echo "Stopping VNC services..."

pkill -f "Xvfb :99" 2>/dev/null
pkill -f "x11vnc" 2>/dev/null
pkill -f "websockify" 2>/dev/null

sleep 1

echo "VNC services stopped."
echo "Port 6080 is now free."
EOF
    
    # Make scripts executable
    chmod +x /root/.hermes/skills/arena-image-gen/scripts/start_vnc.sh
    chmod +x /root/.hermes/skills/arena-image-gen/scripts/stop_vnc.sh
    
    print_success "VNC scripts created"
}

# Verify installation
verify_installation() {
    print_step "Verifying installation..."
    
    echo ""
    echo "============================================"
    echo "  INSTALLATION VERIFICATION"
    echo "============================================"
    
    # Check Xvfb
    if command -v Xvfb &> /dev/null; then
        print_success "Xvfb: OK"
    else
        print_error "Xvfb: NOT FOUND"
    fi
    
    # Check x11vnc
    if command -v x11vnc &> /dev/null; then
        print_success "x11vnc: OK"
    else
        print_error "x11vnc: NOT FOUND"
    fi
    
    # Check noVNC
    if [ -d "/usr/share/novnc" ]; then
        print_success "noVNC: OK"
    else
        print_warning "noVNC: Directory not found at /usr/share/novnc"
    fi
    
    # Check Chrome
    if command -v google-chrome &> /dev/null; then
        CHROME_VERSION=$(google-chrome --version)
        print_success "Chrome: OK ($CHROME_VERSION)"
    else
        print_error "Chrome: NOT FOUND"
    fi
    
    # Check Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        print_success "Python: OK ($PYTHON_VERSION)"
    else
        print_error "Python: NOT FOUND"
    fi
    
    # Check Playwright
    if python3 -c "import playwright" 2>/dev/null; then
        print_success "Playwright: OK"
    else
        print_error "Playwright: NOT FOUND"
    fi
    
    echo ""
    echo "============================================"
    echo "  INSTALLATION COMPLETE!"
    echo "============================================"
    echo ""
    echo "Next steps:"
    echo "1. Start VNC: bash /root/.hermes/skills/arena-image-gen/scripts/start_vnc.sh"
    echo "2. SSH tunnel: ssh -L 6080:127.0.0.1:6080 user@VPS_IP"
    echo "3. Open: http://localhost:6080/vnc.html"
    echo "4. Login to arena.ai via Chrome"
    echo "5. Session will be saved automatically"
    echo ""
    echo "After login, you can generate images headlessly!"
    echo "============================================"
}

# Main installation flow
main() {
    print_header
    
    check_root
    detect_os
    update_system
    install_essentials
    install_xvfb
    install_x11vnc
    install_novnc
    install_chrome
    install_python
    install_playwright
    install_project_deps
    create_vnc_scripts
    verify_installation
}

# Run main function
main "$@"
