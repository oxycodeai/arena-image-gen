"""
CAPTCHA Handler for Arena.ai
Detects and handles CAPTCHA challenges.

Usage:
    from captcha_handler import detect_captcha, handle_captcha
    if detect_captcha(page):
        handle_captcha(page, timeout=60)
"""

import time
from pathlib import Path


# CAPTCHA detection selectors
CAPTCHA_SELECTORS = [
    # reCAPTCHA
    "iframe[src*='recaptcha']",
    "iframe[src*='google.com/recaptcha']",
    ".g-recaptcha",
    "[data-sitekey]",
    
    # hCaptcha
    "iframe[src*='hcaptcha']",
    ".h-captcha",
    
    # Cloudflare Turnstile
    "iframe[src*='challenges.cloudflare.com']",
    ".cf-turnstile",
    
    # Image CAPTCHA (like "Select all squares")
    "text=Select all squares",
    "text=Verify you are human",
    "text=I'm not a robot",
    "text=Please complete",
    "text=Select all images",
    "text=Click on",
    
    # Generic CAPTCHA
    "#captcha",
    ".captcha",
    "[data-testid='captcha']",
    
    # FunCaptcha
    "iframe[src*='funcaptcha']",
    ".funcaptcha",
    
    # GeeTest
    ".geetest_panel",
    ".geetest_widget",
]


def detect_captcha(page):
    """
    Detect if CAPTCHA is present on the page.
    
    Args:
        page: Playwright page object
    
    Returns:
        True if CAPTCHA detected, False otherwise
    """
    for selector in CAPTCHA_SELECTORS:
        try:
            element = page.query_selector(selector)
            if element:
                # Check if element is visible
                if element.is_visible():
                    print(f"  CAPTCHA detected: {selector}")
                    return True
        except Exception:
            continue
    
    # Also check for CAPTCHA text in page content
    try:
        content = page.content()
        captcha_texts = [
            "Select all squares",
            "Select all images",
            "Verify you are human",
            "I'm not a robot",
            "Please complete the captcha",
            "CAPTCHA",
            "security check",
        ]
        
        for text in captcha_texts:
            if text.lower() in content.lower():
                # Check if it's visible (not hidden)
                element = page.query_selector(f"text={text}")
                if element and element.is_visible():
                    print(f"  CAPTCHA text detected: {text}")
                    return True
    except Exception:
        pass
    
    return False


def get_captcha_type(page):
    """
    Identify the type of CAPTCHA.
    
    Args:
        page: Playwright page object
    
    Returns:
        String describing CAPTCHA type
    """
    # Check for reCAPTCHA
    if page.query_selector("iframe[src*='recaptcha']"):
        return "recaptcha"
    
    # Check for hCaptcha
    if page.query_selector("iframe[src*='hcaptcha']"):
        return "hcaptcha"
    
    # Check for Turnstile
    if page.query_selector("iframe[src*='challenges.cloudflare.com']"):
        return "turnstile"
    
    # Check for image CAPTCHA
    try:
        element = page.query_selector("text=Select all squares")
        if element:
            return "image_selection"
    except Exception:
        pass
    
    return "unknown"


def wait_for_captcha_solve(page, timeout=300, check_interval=2):
    """
    Wait for CAPTCHA to be solved (manually via VNC).
    
    Args:
        page: Playwright page object
        timeout: Maximum wait time in seconds
        check_interval: How often to check if CAPTCHA is gone
    
    Returns:
        True if CAPTCHA solved, False if timeout
    """
    print("  ⏳ Waiting for CAPTCHA to be solved...")
    print("  If VNC is active, solve it in the browser window.")
    print(f"  Timeout: {timeout} seconds")
    print("")
    
    start_time = time.time()
    last_print = 0
    
    while True:
        elapsed = time.time() - start_time
        
        # Check timeout
        if elapsed > timeout:
            print("  ❌ CAPTCHA solve timeout!")
            return False
        
        # Check if CAPTCHA is still present
        if not detect_captcha(page):
            print("  ✅ CAPTCHA solved!")
            return True
        
        # Print progress every 30 seconds
        if elapsed - last_print >= 30:
            remaining = timeout - int(elapsed)
            print(f"  ⏳ Waiting... ({remaining}s remaining)")
            last_print = elapsed
        
        time.sleep(check_interval)


def handle_captcha(page, timeout=300, vnc_available=True):
    """
    Handle CAPTCHA based on availability.
    
    Args:
        page: Playwright page object
        timeout: Maximum wait time for manual solve
        vnc_available: Whether VNC is available for manual solve
    
    Returns:
        True if CAPTCHA handled, False if failed
    """
    # Check if CAPTCHA exists
    if not detect_captcha(page):
        return True  # No CAPTCHA, continue
    
    # Get CAPTCHA type
    captcha_type = get_captcha_type(page)
    print(f"  🚨 CAPTCHA detected! Type: {captcha_type}")
    
    if vnc_available:
        # Wait for manual solve via VNC
        print("  👀 Please solve the CAPTCHA in the VNC browser window.")
        return wait_for_captcha_solve(page, timeout)
    else:
        # VNC not available - cannot solve
        print("  ❌ ERROR: CAPTCHA detected but VNC not available!")
        print("")
        print("  To solve this, you need to:")
        print("  1. Start VNC: bash start_vnc.sh")
        print("  2. Connect via SSH tunnel:")
        print("     ssh -L 6080:127.0.0.1:6080 user@VPS_IP")
        print("  3. Open noVNC: http://localhost:6080/vnc.html")
        print("  4. Solve the CAPTCHA in the browser")
        print("")
        return False


def take_screenshot_on_captcha(page, output_dir):
    """
    Take a screenshot when CAPTCHA is detected (for debugging).
    
    Args:
        page: Playwright page object
        output_dir: Directory to save screenshot
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    screenshot_path = output_dir / f"captcha_detected_{timestamp}.png"
    
    try:
        page.screenshot(path=str(screenshot_path))
        print(f"  📸 Screenshot saved: {screenshot_path}")
    except Exception as e:
        print(f"  ⚠️ Could not save screenshot: {e}")


# Example usage
if __name__ == "__main__":
    print("CAPTCHA Handler loaded!")
    print(f"Detection selectors: {len(CAPTCHA_SELECTORS)}")
    print("Use detect_captcha(page) to check for CAPTCHA")
    print("Use handle_captcha(page) to handle CAPTCHA")
