"""
Voting Interface Handler for Arena.ai
Handles the "A is better / B is better" voting buttons.

Usage:
    from voting_handler import detect_voting, handle_voting
    handle_voting(page, mode="skip")
"""

import time
import random


# Voting button selectors
VOTING_SELECTORS = [
    # Arena.ai specific voting buttons
    "button:has-text('A is better')",
    "button:has-text('B is better')",
    "button:has-text('Both are good')",
    "button:has-text('Both are bad')",
    "button:has-text('Tie')",
    
    # Generic vote buttons
    "[data-testid='vote-button']",
    "[data-testid='vote-a']",
    "[data-testid='vote-b']",
    
    # Alternative selectors
    "text=A is better",
    "text=B is better",
    "text=Both are good",
    "text=Both are bad",
]


def detect_voting(page):
    """
    Detect if voting interface is present.
    
    Args:
        page: Playwright page object
    
    Returns:
        True if voting interface detected, False otherwise
    """
    for selector in VOTING_SELECTORS:
        try:
            element = page.query_selector(selector)
            if element and element.is_visible():
                print(f"  🗳️ Voting interface detected!")
                return True
        except Exception:
            continue
    
    return False


def get_voting_options(page):
    """
    Get available voting options.
    
    Args:
        page: Playwright page object
    
    Returns:
        List of available voting options
    """
    options = []
    
    option_texts = [
        "A is better",
        "B is better",
        "Both are good",
        "Both are bad",
        "Tie",
    ]
    
    for text in option_texts:
        try:
            button = page.query_selector(f"button:has-text('{text}')")
            if button and button.is_visible():
                options.append(text)
        except Exception:
            continue
    
    return options


def auto_vote(page, choice="both_good"):
    """
    Automatically vote.
    
    Args:
        page: Playwright page object
        choice: Voting choice
            - "a_better": Vote A is better
            - "b_better": Vote B is better
            - "both_good": Vote Both are good
            - "both_bad": Vote Both are bad
            - "tie": Vote Tie
            - "random": Random choice
    
    Returns:
        True if vote successful, False otherwise
    """
    # Map choices to button text
    choice_map = {
        "a_better": "A is better",
        "b_better": "B is better",
        "both_good": "Both are good",
        "both_bad": "Both are bad",
        "tie": "Tie",
    }
    
    # Handle random choice
    if choice == "random":
        choice = random.choice(list(choice_map.keys()))
    
    # Get button text
    button_text = choice_map.get(choice)
    if not button_text:
        print(f"  ❌ Invalid choice: {choice}")
        return False
    
    # Find and click button
    try:
        button = page.query_selector(f"button:has-text('{button_text}')")
        if button and button.is_visible():
            # Add human-like delay
            time.sleep(random.uniform(0.2, 0.5))
            
            # Click button
            button.click()
            print(f"  ✅ Voted: {button_text}")
            
            # Wait for vote to register
            time.sleep(2)
            return True
        else:
            print(f"  ❌ Button not found: {button_text}")
            return False
    except Exception as e:
        print(f"  ❌ Vote failed: {e}")
        return False


def handle_voting(page, mode="skip", choice="both_good", wait_for_user=False):
    """
    Handle voting interface.
    
    Args:
        page: Playwright page object
        mode: Handling mode
            - "skip": Don't vote, just continue
            - "auto": Auto-vote with specified choice
            - "wait": Wait for user to vote via VNC
            - "prompt": Ask user what to do
        choice: Voting choice (for auto mode)
        wait_for_user: Whether to wait for user input
    
    Returns:
        True if voting handled, False if failed
    """
    # Check if voting interface exists
    if not detect_voting(page):
        return True  # No voting interface
    
    # Get available options
    options = get_voting_options(page)
    print(f"  📋 Available options: {', '.join(options)}")
    
    if mode == "skip":
        # Don't vote, just continue
        print("  ⏭️ Skipping vote...")
        return True
    
    elif mode == "auto":
        # Auto-vote
        return auto_vote(page, choice)
    
    elif mode == "wait":
        # Wait for user to vote via VNC
        print("  👀 Please vote in the VNC browser window.")
        print("  Press Enter here when done...")
        input()
        
        # Verify vote was made
        if not detect_voting(page):
            print("  ✅ Vote registered!")
            return True
        else:
            print("  ⚠️ Voting interface still present")
            return False
    
    elif mode == "prompt":
        # Ask user what to do
        print("")
        print("  What would you like to do?")
        print("  1. Skip (don't vote)")
        print("  2. Vote A is better")
        print("  3. Vote B is better")
        print("  4. Vote Both are good")
        print("  5. Vote Both are bad")
        print("  6. Wait for manual vote via VNC")
        print("")
        
        choice = input("  Enter choice (1-6): ").strip()
        
        if choice == "1":
            return True  # Skip
        elif choice == "2":
            return auto_vote(page, "a_better")
        elif choice == "3":
            return auto_vote(page, "b_better")
        elif choice == "4":
            return auto_vote(page, "both_good")
        elif choice == "5":
            return auto_vote(page, "both_bad")
        elif choice == "6":
            return handle_voting(page, mode="wait")
        else:
            print("  Invalid choice, skipping...")
            return True
    
    return False


def wait_for_voting_complete(page, timeout=60):
    """
    Wait for voting to complete (voting interface disappears).
    
    Args:
        page: Playwright page object
        timeout: Maximum wait time in seconds
    
    Returns:
        True if voting complete, False if timeout
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if not detect_voting(page):
            return True
        time.sleep(1)
    
    return False


# Example usage
if __name__ == "__main__":
    print("Voting Handler loaded!")
    print(f"Detection selectors: {len(VOTING_SELECTORS)}")
    print("Use detect_voting(page) to check for voting interface")
    print("Use handle_voting(page) to handle voting")
