"""
Arena.ai Setup Guide - VNC-based Authentication
Interactive setup for first-time login via VNC.

Usage:
    python3 setup_guide.py
    python3 setup_guide.py --status
    python3 setup_guide.py --setup
"""

import sys
import os
from pathlib import Path

# Note: Windows encoding fix removed - not needed for Linux VPS deployment

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from auth_manager import (
    get_auth_status,
    generate_setup_guide,
    check_auth_exists,
    clear_auth
)


def print_header():
    """Print setup header."""
    print("\n" + "=" * 60)
    print("ARENA.AI IMAGE GENERATION - SETUP")
    print("=" * 60)


def print_status():
    """Print current authentication status."""
    status = get_auth_status()
    
    print("\nCURRENT STATUS")
    print("-" * 40)
    print(f"Profile exists: {status['profile']['exists']}")
    print(f"Profile valid: {status['profile']['valid']}")
    print(f"Profile size: {status['profile'].get('total_size_mb', 0)} MB")
    print(f"State exists: {status['state']['exists']}")
    print(f"State valid: {status['state']['valid']}")
    print(f"Cookies: {status['state']['cookie_count']}")
    print(f"Saved at: {status['state']['saved_at'] or 'Never'}")
    print("-" * 40)
    print(f"Status: {status['message']}")
    print("-" * 40)
    
    return status


def interactive_setup():
    """Interactive setup flow."""
    print_header()
    
    # Check current status
    status = print_status()
    
    if status['profile']['valid']:
        print("\nYou're already authenticated!")
        choice = input("\nDo you want to re-authenticate? (y/N): ").strip().lower()
        if choice != 'y':
            print("\nKeeping existing authentication.")
            return
    
    # Show setup guide
    print("\n" + "=" * 60)
    print("SETUP INSTRUCTIONS")
    print("=" * 60)
    print(generate_setup_guide())
    
    # Wait for user to complete setup
    print("\n" + "=" * 60)
    print("AFTER COMPLETING SETUP:")
    print("=" * 60)
    print("1. Make sure you've logged in via VNC")
    print("2. Session should be saved automatically")
    print("3. Run: python3 auth_manager.py --status")
    print("4. If valid, you can generate images!")
    print("")
    print("To generate an image:")
    print('  python3 arena_gen.py "a cute dog image"')
    print("=" * 60)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Arena.ai Setup Guide (VNC-based)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Interactive setup:
    python3 setup_guide.py

  Check status:
    python3 setup_guide.py --status

  Show setup guide:
    python3 setup_guide.py --setup

  Clear authentication:
    python3 setup_guide.py --clear
        """
    )
    
    parser.add_argument("--status", "-s", action="store_true",
                       help="Show current auth status")
    parser.add_argument("--setup", action="store_true",
                       help="Show setup guide")
    parser.add_argument("--clear", "-c", action="store_true",
                       help="Clear authentication")
    
    args = parser.parse_args()
    
    if args.status:
        print_header()
        print_status()
    elif args.setup:
        print_header()
        print(generate_setup_guide())
    elif args.clear:
        print_header()
        if clear_auth():
            print("\nAuthentication cleared successfully!")
        else:
            print("\nNothing to clear.")
    else:
        interactive_setup()


if __name__ == "__main__":
    main()
