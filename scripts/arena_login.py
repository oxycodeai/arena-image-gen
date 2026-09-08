"""
Arena.ai Login Script - First-Time Authentication
Launches Chrome in headed mode via VNC for manual login.
Saves storageState after successful login.

Usage:
    python3 arena_login.py
    
    Or with custom settings:
    python3 arena_login.py --profile-dir /path/to/profile --state-file /path/to/state.json
"""

import sys
import os
import json
import time
import argparse
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding (for development)
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("ERROR: Playwright not installed. Run:")
    print("  pip3 install playwright")
    print("  playwright install chromium")
    sys.exit(1)


# Default paths
DEFAULT_PROFILE_DIR = Path.home() / ".arena-chrome-profile"
DEFAULT_STATE_FILE = Path.home() / ".hermes" / "skills" / "arena-image-gen" / "auth" / "state.json"
ARENA_URL = "https://arena.ai"
LOGIN_TIMEOUT_MS = 300000  # 5 minutes


def print_header():
    print("""
============================================
  ARENA.AI LOGIN - First-Time Setup
============================================
This will open Chrome via VNC for you to login.

Steps:
1. Make sure VNC is running (bash start_vnc.sh)
2. Open noVNC in your browser (via SSH tunnel)
3. Login to arena.ai in the Chrome window
4. This script will detect login and save session
============================================
""")


def check_vnc_running():
    """Check if VNC services are running."""
    import subprocess
    
    try:
        # Check if Xvfb is running
        result = subprocess.run(['pgrep', '-f', 'Xvfb :99'], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            return False
        
        # Check if x11vnc is running
        result = subprocess.run(['pgrep', '-f', 'x11vnc'], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            return False
        
        # Check if websockify is running
        result = subprocess.run(['pgrep', '-f', 'websockify'], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            return False
        
        return True
    except FileNotFoundError:
        # pgrep not available (Windows), skip check
        return True


def wait_for_login(page, timeout_ms=LOGIN_TIMEOUT_MS):
    """
    Wait for user to login manually via VNC.
    Detects login by waiting for chat interface elements.
    """
    print("Waiting for login... (user karega login VNC se)")
    print(f"Timeout: {timeout_ms // 1000} seconds")
    print("")
    
    # Arena.ai chat interface selectors (multiple options)
    selectors = [
        "textarea[placeholder*='Ask']",
        "textarea[placeholder*='Type']",
        "textarea[placeholder*='Message']",
        "div[contenteditable='true']",
        "[data-testid='chat-input']",
        "input[type='text'][placeholder*='Ask']",
    ]
    
    start_time = time.time()
    
    while True:
        elapsed = time.time() - start_time
        if elapsed * 1000 > timeout_ms:
            raise TimeoutError("Login timeout reached")
        
        for selector in selectors:
            try:
                element = page.query_selector(selector)
                if element:
                    # Verify it's actually the arena.ai chat interface
                    # by checking the URL or page content
                    current_url = page.url
                    if "arena.ai" in current_url:
                        print(f"\nLogin detected! (found: {selector})")
                        return True
            except Exception:
                continue
        
        # Check if we're on the right page
        try:
            current_url = page.url
            if "arena.ai" in current_url:
                # Check for any interactive element that indicates logged-in state
                logged_in_selectors = [
                    "textarea",
                    "[contenteditable='true']",
                    "button[aria-label*='Send']",
                    "button[aria-label*='Submit']",
                ]
                for sel in logged_in_selectors:
                    element = page.query_selector(sel)
                    if element:
                        print(f"\nLogin detected! (found: {sel})")
                        return True
        except Exception:
            pass
        
        # Print progress every 30 seconds
        if int(elapsed) % 30 == 0 and int(elapsed) > 0:
            print(f"  Still waiting... ({int(elapsed)}s elapsed)")
        
        time.sleep(2)


def save_storage_state(context, state_file):
    """Save browser storage state (cookies + localStorage + IndexedDB)."""
    state_file = Path(state_file)
    state_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Save storage state
    context.storage_state(path=str(state_file))
    
    # Also save metadata
    metadata = {
        "saved_at": datetime.now().isoformat(),
        "state_file": str(state_file),
        "version": "2.0"
    }
    
    metadata_file = state_file.parent / "state_metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"Session saved to: {state_file}")
    return state_file


def launch_chrome_for_login(profile_dir, headless=False):
    """
    Launch Chrome for manual login via VNC.
    Uses real Chrome with automation bypass flags.
    """
    profile_dir = Path(profile_dir)
    profile_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Profile directory: {profile_dir}")
    print(f"Mode: {'HEADLESS' if headless else 'HEADED (via VNC)'}")
    print("")
    
    with sync_playwright() as p:
        # Launch Chrome with persistent profile
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=headless,
            channel="chrome",
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--window-size=1280,800"
            ],
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        # Remove webdriver flag
        page = context.pages[0] if context.pages else context.new_page()
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        # Navigate to arena.ai
        print("Navigating to arena.ai...")
        page.goto(ARENA_URL, wait_until="domcontentloaded")
        
        print("")
        print("============================================")
        print("  BROWSER IS OPEN!")
        print("============================================")
        print("")
        print("If you don't see Chrome, make sure:")
        print("1. VNC is running: bash start_vnc.sh")
        print("2. You're connected via SSH tunnel")
        print("3. You opened: http://localhost:6080/vnc.html")
        print("")
        print("Login to arena.ai in the Chrome window.")
        print("This script will detect when you're logged in.")
        print("============================================")
        print("")
        
        # Wait for login
        try:
            wait_for_login(page)
            
            # Wait a bit more for all cookies to set
            print("Waiting for session to fully establish...")
            time.sleep(5)
            
            # Save storage state
            state_file = save_storage_state(context, DEFAULT_STATE_FILE)
            
            print("")
            print("============================================")
            print("  LOGIN SUCCESSFUL!")
            print("============================================")
            print("")
            print("Session saved permanently!")
            print("Ab se login ki zaroorat nahi.")
            print("")
            print("You can now:")
            print("1. Stop VNC: bash stop_vnc.sh")
            print("2. Generate images: python3 arena_gen.py 'prompt'")
            print("============================================")
            
            return True
            
        except TimeoutError:
            print("")
            print("ERROR: Login timeout!")
            print("Please try again.")
            return False
        
        except KeyboardInterrupt:
            print("")
            print("Login cancelled by user.")
            return False
        
        finally:
            context.close()


def check_existing_session():
    """Check if a valid session already exists."""
    if DEFAULT_STATE_FILE.exists():
        try:
            with open(DEFAULT_STATE_FILE, 'r') as f:
                state = json.load(f)
            
            if 'cookies' in state and len(state['cookies']) > 0:
                return True
        except Exception:
            pass
    
    return False


def main():
    parser = argparse.ArgumentParser(description="Arena.ai Login Script")
    parser.add_argument("--profile-dir", type=str, 
                       default=str(DEFAULT_PROFILE_DIR),
                       help="Chrome profile directory")
    parser.add_argument("--state-file", type=str,
                       default=str(DEFAULT_STATE_FILE),
                       help="Output state file path")
    parser.add_argument("--headless", action="store_true",
                       help="Run in headless mode (for testing)")
    parser.add_argument("--force", action="store_true",
                       help="Force new login even if session exists")
    
    args = parser.parse_args()
    
    print_header()
    
    # Check for existing session
    if not args.force and check_existing_session():
        print("Valid session already exists!")
        print(f"State file: {DEFAULT_STATE_FILE}")
        print("")
        choice = input("Do you want to login again? (y/N): ").strip().lower()
        if choice != 'y':
            print("Keeping existing session.")
            return
    
    # Check if VNC is running (skip on Windows)
    if sys.platform != "win32" and not args.headless:
        if not check_vnc_running():
            print("ERROR: VNC services not running!")
            print("")
            print("Please start VNC first:")
            print("  bash start_vnc.sh")
            print("")
            print("Then connect via SSH tunnel and try again.")
            return
    
    # Launch Chrome for login
    success = launch_chrome_for_login(
        profile_dir=args.profile_dir,
        headless=args.headless
    )
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
