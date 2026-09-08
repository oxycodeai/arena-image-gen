"""
Authentication Manager for Arena.ai Image Generation (v2.0)
Uses Playwright's persistent Chrome profile for authentication.
No manual cookie export needed - login via VNC once, session persists.

Usage:
    python3 auth_manager.py --status
    python3 auth_manager.py --check
    python3 auth_manager.py --setup
    python3 auth_manager.py --clear
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# Fix Windows console encoding (for development)
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


# Default paths
DEFAULT_PROFILE_DIR = Path.home() / ".arena-chrome-profile"
DEFAULT_AUTH_DIR = Path.home() / ".hermes" / "skills" / "arena-image-gen" / "auth"
DEFAULT_STATE_FILE = DEFAULT_AUTH_DIR / "state.json"


def get_profile_status(profile_dir: Optional[Path] = None) -> Dict[str, Any]:
    """
    Get status of Chrome profile directory.
    
    Args:
        profile_dir: Path to Chrome profile directory
        
    Returns:
        Dict with profile status information
    """
    if profile_dir is None:
        profile_dir = Path(DEFAULT_PROFILE_DIR)
    
    status = {
        "exists": profile_dir.exists(),
        "filepath": str(profile_dir),
        "valid": False,
        "has_cookies": False,
        "has_data": False,
        "message": ""
    }
    
    if not profile_dir.exists():
        status["message"] = "No Chrome profile found. Please login first."
        return status
    
    # Check for cookies database
    cookies_file = profile_dir / "Default" / "Cookies"
    if cookies_file.exists():
        status["has_cookies"] = True
    
    # Check for any substantial data
    total_size = 0
    file_count = 0
    for item in profile_dir.rglob("*"):
        if item.is_file():
            total_size += item.stat().st_size
            file_count += 1
    
    status["has_data"] = file_count > 10  # Chrome profile has many files
    status["file_count"] = file_count
    status["total_size_mb"] = round(total_size / (1024 * 1024), 2)
    
    # Determine if valid
    if status["has_cookies"] and status["has_data"]:
        status["valid"] = True
        status["message"] = f"Valid Chrome profile found ({status['total_size_mb']} MB, {file_count} files)"
    elif status["has_data"]:
        status["valid"] = False
        status["message"] = "Chrome profile exists but may not have valid cookies"
    else:
        status["message"] = "Chrome profile directory is empty or minimal"
    
    return status


def get_state_status(state_file: Optional[Path] = None) -> Dict[str, Any]:
    """
    Get status of saved state file.
    
    Args:
        state_file: Path to state.json file
        
    Returns:
        Dict with state status information
    """
    if state_file is None:
        state_file = Path(DEFAULT_STATE_FILE)
    
    status = {
        "exists": state_file.exists(),
        "filepath": str(state_file),
        "valid": False,
        "cookie_count": 0,
        "saved_at": None,
        "message": ""
    }
    
    if not state_file.exists():
        status["message"] = "No saved state found. Please login first."
        return status
    
    try:
        with open(state_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Count cookies
        cookies = data.get('cookies', [])
        if isinstance(cookies, list):
            status["cookie_count"] = len(cookies)
        elif isinstance(cookies, dict):
            status["cookie_count"] = len(cookies)
        
        # Check saved timestamp
        if 'saved_at' in data:
            status["saved_at"] = data['saved_at']
        
        # Determine if valid
        if status["cookie_count"] > 0:
            status["valid"] = True
            status["message"] = f"Valid state found ({status['cookie_count']} cookies)"
        else:
            status["message"] = "State file exists but contains no cookies"
            
    except Exception as e:
        status["message"] = f"Error reading state file: {str(e)}"
    
    return status


def get_auth_status() -> Dict[str, Any]:
    """
    Get comprehensive authentication status.
    
    Returns:
        Dict with complete auth status
    """
    profile_status = get_profile_status()
    state_status = get_state_status()
    
    return {
        "profile": profile_status,
        "state": state_status,
        "authenticated": profile_status["valid"],
        "message": _get_status_message(profile_status, state_status)
    }


def _get_status_message(profile_status: Dict, state_status: Dict) -> str:
    """Generate human-readable status message."""
    if profile_status["valid"]:
        return "Authentication: VALID - Ready to generate images!"
    elif profile_status["exists"] and not profile_status["valid"]:
        return "Authentication: PARTIAL - Profile exists but may need re-login"
    else:
        return "Authentication: NOT FOUND - Please login first"


def check_auth_exists() -> bool:
    """
    Check if authentication exists and is valid.
    
    Returns:
        True if valid auth exists
    """
    profile_status = get_profile_status()
    return profile_status["valid"]


def clear_auth(profile_dir: Optional[Path] = None, state_file: Optional[Path] = None) -> bool:
    """
    Clear authentication data.
    
    Args:
        profile_dir: Path to Chrome profile directory
        state_file: Path to state.json file
        
    Returns:
        True if cleared successfully
    """
    cleared = False
    
    # Clear state file
    if state_file is None:
        state_file = Path(DEFAULT_STATE_FILE)
    
    if state_file.exists():
        try:
            state_file.unlink()
            cleared = True
        except Exception as e:
            print(f"Error clearing state file: {e}")
    
    # Note: We don't delete Chrome profile by default
    # User can do that manually if needed
    
    return cleared


def generate_setup_guide() -> str:
    """
    Generate setup guide for first-time login.
    
    Returns:
        Formatted guide string
    """
    guide = """
ARENA.AI LOGIN SETUP
====================

This is a ONE-TIME setup. After login, session persists forever.

PREREQUISITES:
  - VPS with SSH access
  - VNC stack installed (run: bash install_vnc.sh)

STEP 1: START VNC
  Run on VPS:
    bash /root/.hermes/skills/arena-image-gen/scripts/start_vnc.sh

STEP 2: CONNECT VIA SSH TUNNEL
  Run on your phone/laptop:
    ssh -L 6080:127.0.0.1:6080 user@YOUR_VPS_IP

STEP 3: OPEN NOVNC
  Open in browser:
    http://localhost:6080/vnc.html

  You should see a Chrome browser window.

STEP 4: LOGIN TO ARENA.AI
  In the Chrome window:
    1. Go to: https://arena.ai
    2. Click "Continue with Google"
    3. Login with your Google account
    4. Wait for chat interface to appear

STEP 5: SESSION SAVES AUTOMATICALLY
  The script will detect login and save session.
  You'll see: "LOGIN SUCCESSFUL!"

STEP 6: STOP VNC
  Run on VPS:
    bash /root/.hermes/skills/arena-image-gen/scripts/stop_vnc.sh

DONE! Session is now saved permanently.
No more login needed for future image generation.

TROUBLESHOOTING:
  - If VNC not visible: Check SSH tunnel is running
  - If Chrome not loading: Restart VNC
  - If login fails: Try again (bash start_vnc.sh)
"""
    return guide


def print_status():
    """Print current authentication status."""
    status = get_auth_status()
    
    print("\n[ARENA.AI AUTH STATUS]")
    print("=" * 40)
    print(f"Profile exists: {status['profile']['exists']}")
    print(f"Profile valid: {status['profile']['valid']}")
    print(f"Profile size: {status['profile'].get('total_size_mb', 0)} MB")
    print(f"State exists: {status['state']['exists']}")
    print(f"State valid: {status['state']['valid']}")
    print(f"Cookies: {status['state']['cookie_count']}")
    print(f"Saved at: {status['state']['saved_at'] or 'Never'}")
    print("-" * 40)
    print(f"Status: {status['message']}")
    print("=" * 40)


# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Arena.ai Authentication Manager (v2.0)")
    parser.add_argument("--status", action="store_true", help="Show auth status")
    parser.add_argument("--check", action="store_true", help="Check if auth exists")
    parser.add_argument("--setup", action="store_true", help="Show setup guide")
    parser.add_argument("--clear", action="store_true", help="Clear authentication")
    parser.add_argument("--profile-dir", type=str, help="Custom profile directory")
    
    args = parser.parse_args()
    
    profile_dir = Path(args.profile_dir) if args.profile_dir else None
    
    if args.status:
        print_status()
        
    elif args.check:
        if check_auth_exists():
            print("Authentication: VALID")
            sys.exit(0)
        else:
            print("Authentication: NOT FOUND")
            sys.exit(1)
            
    elif args.setup:
        print(generate_setup_guide())
        
    elif args.clear:
        if clear_auth(profile_dir):
            print("Authentication cleared successfully")
        else:
            print("Nothing to clear")
            
    else:
        parser.print_help()
