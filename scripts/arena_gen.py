"""
Arena.ai Image Generation Script
Generates images using Arena.ai's model router.
Uses persistent Chrome profile for authentication.
Includes stealth browser, CAPTCHA handling, and voting support.

Usage:
    python3 arena_gen.py "a cute dog image"
    python3 arena_gen.py "sunset over ocean" --output ~/my-images/
    python3 arena_gen.py "abstract art" --model gemini-3-pro-image-preview
    python3 arena_gen.py "cat" --vote skip
    python3 arena_gen.py "dog" --vote auto
"""

import sys
import os
import json
import time
import argparse
import re
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding (for development)
if sys.platform == "win32":
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass

PLAYWRIGHT_AVAILABLE = False
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    pass

# Import stealth and handler modules
STEALTH_AVAILABLE = False
CAPTCHA_HANDLER_AVAILABLE = False
VOTING_HANDLER_AVAILABLE = False

try:
    from stealth_config import get_stealth_context
    STEALTH_AVAILABLE = True
except ImportError:
    pass

try:
    from captcha_handler import detect_captcha, handle_captcha
    CAPTCHA_HANDLER_AVAILABLE = True
except ImportError:
    pass

try:
    from voting_handler import detect_voting, handle_voting
    VOTING_HANDLER_AVAILABLE = True
except ImportError:
    pass


# Default paths
DEFAULT_PROFILE_DIR = Path.home() / ".arena-chrome-profile"
DEFAULT_OUTPUT_DIR = Path.home() / "arena-output"
DEFAULT_STATE_FILE = Path.home() / ".hermes" / "skills" / "arena-image-gen" / "auth" / "state.json"
ARENA_URL = "https://arena.ai/image/direct?model_a=max"


def print_header():
    print("""
============================================
  ARENA.AI IMAGE GENERATION
============================================
""")


def check_session_exists():
    """Check if a valid session profile exists."""
    profile_dir = Path(DEFAULT_PROFILE_DIR)
    
    # Check if profile directory exists and has data
    if profile_dir.exists():
        # Check for cookies database
        cookies_file = profile_dir / "Default" / "Cookies"
        if cookies_file.exists():
            return True
        
        # Alternative: check for any Chrome profile data
        for item in profile_dir.rglob("*"):
            if item.is_file() and item.stat().st_size > 0:
                return True
    
    return False


def handle_popups(page):
    """Handle any popups on arena.ai."""
    try:
        # Terms of Service popup
        tos_selectors = [
            "button:has-text('Accept')",
            "button:has-text('I agree')",
            "button:has-text('Continue')",
            "button:has-text('Got it')",
            "button:has-text('OK')",
        ]
        
        for selector in tos_selectors:
            try:
                button = page.query_selector(selector)
                if button and button.is_visible():
                    button.click()
                    time.sleep(1)
            except Exception:
                continue
        
        # Cookie consent popup
        cookie_selectors = [
            "button:has-text('Accept all')",
            "button:has-text('Accept cookies')",
            "button:has-text('Allow')",
        ]
        
        for selector in cookie_selectors:
            try:
                button = page.query_selector(selector)
                if button and button.is_visible():
                    button.click()
                    time.sleep(1)
            except Exception:
                continue
                
    except Exception as e:
        print(f"  Popup handling note: {e}")


def select_model(page, model="max"):
    """Ensure the correct model is selected."""
    try:
        # Check if model selector exists
        model_selectors = [
            "select[model]",
            "[data-testid='model-selector']",
            "button:has-text('Model')",
        ]
        
        for selector in model_selectors:
            try:
                element = page.query_selector(selector)
                if element:
                    # Model selector found, check current value
                    current_value = element.get_attribute('value') or ""
                    if model.lower() in current_value.lower():
                        print(f"  Model already set to: {model}")
                        return True
            except Exception:
                continue
        
        # If URL already has model parameter, it's set
        if f"model_a={model}" in page.url:
            print(f"  Model set via URL: {model}")
            return True
        
        print(f"  Using default model: {model}")
        return True
        
    except Exception as e:
        print(f"  Model selection note: {e}")
        return False


def activate_image_mode(page):
    """Click the Image button to ensure image generation mode."""
    print("  Activating image mode...")
    
    image_button_selectors = [
        "button:has-text('Image')",
        "button[aria-label*='Image']",
        "[data-testid='image-button']",
        ".image-mode-button",
    ]
    
    for selector in image_button_selectors:
        try:
            button = page.query_selector(selector)
            if button and button.is_visible():
                button.click()
                time.sleep(1)
                print("  Image mode activated")
                return True
        except Exception:
            continue
    
    # Check if already in image mode (textarea exists with image-related placeholder)
    textarea = page.query_selector("textarea")
    if textarea:
        placeholder = textarea.get_attribute('placeholder') or ""
        if "image" in placeholder.lower() or "describe" in placeholder.lower():
            print("  Image mode already active")
            return True
    
    print("  Image mode button not found (continuing anyway)")
    return True


def enter_prompt(page, prompt):
    """Enter the image generation prompt."""
    print(f"  Entering prompt: {prompt[:50]}...")
    
    # Find the input field
    input_selectors = [
        "textarea[placeholder*='Ask']",
        "textarea[placeholder*='Type']",
        "textarea[placeholder*='Message']",
        "div[contenteditable='true']",
        "input[type='text']",
        "[data-testid='chat-input']",
    ]
    
    for selector in input_selectors:
        try:
            element = page.query_selector(selector)
            if element and element.is_visible():
                # Clear existing text
                element.click()
                time.sleep(0.5)
                
                # Type the prompt
                element.fill(prompt)
                time.sleep(0.5)
                
                print("  Prompt entered successfully")
                return True
        except Exception as e:
            continue
    
    print("  ERROR: Could not find input field")
    return False


def submit_prompt(page):
    """Submit the prompt for generation."""
    print("  Submitting prompt...")
    
    # Find and click submit button
    submit_selectors = [
        "button[aria-label*='Send']",
        "button[aria-label*='Submit']",
        "button[type='submit']",
        "button:has-text('Send')",
        "button:has-text('Generate')",
        "button:has(svg)",  # Many submit buttons have SVG icons
    ]
    
    for selector in submit_selectors:
        try:
            button = page.query_selector(selector)
            if button and button.is_visible():
                button.click()
                print("  Prompt submitted!")
                return True
        except Exception:
            continue
    
    # Fallback: try pressing Enter
    try:
        page.keyboard.press("Enter")
        print("  Prompt submitted via Enter key")
        return True
    except Exception:
        pass
    
    print("  ERROR: Could not find submit button")
    return False


def wait_for_generation(page, timeout_seconds=120):
    """Wait for image generation to complete."""
    print(f"  Waiting for generation (timeout: {timeout_seconds}s)...")
    
    start_time = time.time()
    
    while True:
        elapsed = time.time() - start_time
        if elapsed > timeout_seconds:
            print("  WARNING: Generation timeout reached")
            return False
        
        # Check for generated images
        image_selectors = [
            "img[src*='blob:']",
            "img[src*='data:image']",
            "img[alt*='Generated']",
            "img[alt*='image']",
            ".generated-image",
            "[data-testid='generated-image']",
            "canvas",
        ]
        
        for selector in image_selectors:
            try:
                images = page.query_selector_all(selector)
                if images:
                    # Check if any image is substantial (not just a loading indicator)
                    for img in images:
                        try:
                            width = img.get_attribute('width') or "0"
                            height = img.get_attribute('height') or "0"
                            if int(width) > 300 and int(height) > 300:
                                print(f"  Image detected! ({width}x{height})")
                                time.sleep(2)  # Wait a bit more for full load
                                return True
                        except Exception:
                            continue
            except Exception:
                continue
        
        # Check for loading indicators (to know generation is in progress)
        loading_selectors = [
            ".loading",
            "[data-testid='loading']",
            "text=Generating",
            "text=Loading",
            "text=Processing",
        ]
        
        for selector in loading_selectors:
            try:
                element = page.query_selector(selector)
                if element:
                    print(f"  Generating... ({int(elapsed)}s elapsed)")
                    time.sleep(5)
                    break
            except Exception:
                continue
        
        time.sleep(3)


def download_images(page, output_dir):
    """Download all generated images with size filtering."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    downloaded = []
    
    print("  Downloading images...")
    
    # Find all images on the page
    image_selectors = [
        "img[src*='blob:']",
        "img[src*='data:image']",
        "img[alt*='Generated']",
        "img[alt*='image']",
        ".generated-image img",
        "[data-testid='generated-image']",
    ]
    
    seen_srcs = set()  # Avoid duplicates
    
    for selector in image_selectors:
        try:
            images = page.query_selector_all(selector)
            for i, img in enumerate(images):
                try:
                    # Get image source
                    src = img.get_attribute('src')
                    if not src or src in seen_srcs:
                        continue
                    seen_srcs.add(src)
                    
                    # Check image size via JavaScript (more reliable)
                    try:
                        size = page.evaluate("""
                            (el) => ({
                                naturalWidth: el.naturalWidth || 0,
                                naturalHeight: el.naturalHeight || 0,
                                displayWidth: el.offsetWidth || 0,
                                displayHeight: el.offsetHeight || 0
                            })
                        """, img)
                        
                        real_width = max(size['naturalWidth'], size['displayWidth'])
                        real_height = max(size['naturalHeight'], size['displayHeight'])
                        
                        if real_width < 300 or real_height < 300:
                            print(f"  Skipped small image ({real_width}x{real_height})")
                            continue
                    except Exception:
                        # If can't check size, skip blob/data URLs (likely loading indicators)
                        if src.startswith('blob:') or src.startswith('data:'):
                            continue
                    
                    # Download blob images
                    if src.startswith('blob:'):
                        try:
                            img_data = page.evaluate("""
                                async (el) => {
                                    const canvas = document.createElement('canvas');
                                    canvas.width = el.naturalWidth;
                                    canvas.height = el.naturalHeight;
                                    const ctx = canvas.getContext('2d');
                                    ctx.drawImage(el, 0, 0);
                                    return canvas.toDataURL('image/png');
                                }
                            """, img)
                            
                            import base64
                            header, data = img_data.split(',', 1)
                            img_bytes = base64.b64decode(data)
                            
                            filename = f"{timestamp}_image_{len(downloaded)+1}.png"
                            filepath = output_dir / filename
                            filepath.write_bytes(img_bytes)
                            downloaded.append(filepath)
                            print(f"  Saved: {filename}")
                            
                        except Exception as e:
                            print(f"  Failed to save blob image: {e}")
                    
                    # Download data URL images
                    elif src.startswith('data:image'):
                        try:
                            import base64
                            header, data = src.split(',', 1)
                            img_bytes = base64.b64decode(data)
                            
                            filename = f"{timestamp}_image_{len(downloaded)+1}.png"
                            filepath = output_dir / filename
                            filepath.write_bytes(img_bytes)
                            downloaded.append(filepath)
                            print(f"  Saved: {filename}")
                            
                        except Exception as e:
                            print(f"  Failed to save data URL: {e}")
                    
                    # Download regular URL images
                    else:
                        try:
                            response = page.request.get(src)
                            if response.ok:
                                filename = f"{timestamp}_image_{len(downloaded)+1}.png"
                                filepath = output_dir / filename
                                filepath.write_bytes(response.body())
                                downloaded.append(filepath)
                                print(f"  Saved: {filename}")
                        except Exception as e:
                            print(f"  Failed to download URL: {e}")
                    
                except Exception as e:
                    continue
        except Exception:
            continue
    
    # Fallback: try canvas elements
    if not downloaded:
        try:
            canvases = page.query_selector_all("canvas")
            for i, canvas in enumerate(canvases):
                try:
                    size = page.evaluate("""
                        (el) => ({
                            width: el.width || 0,
                            height: el.height || 0
                        })
                    """, canvas)
                    
                    if size['width'] < 300 or size['height'] < 300:
                        continue
                    
                    img_data = page.evaluate("""
                        (el) => el.toDataURL('image/png')
                    """, canvas)
                    
                    import base64
                    header, data = img_data.split(',', 1)
                    img_bytes = base64.b64decode(data)
                    
                    filename = f"{timestamp}_canvas_{len(downloaded)+1}.png"
                    filepath = output_dir / filename
                    filepath.write_bytes(img_bytes)
                    downloaded.append(filepath)
                    print(f"  Saved canvas: {filename}")
                except Exception:
                    continue
        except Exception:
            pass
    
    return downloaded


def generate_image(prompt, output_dir=None, model="max", timeout=120, headless=True, vote_mode="skip"):
    """
    Main function to generate an image using Arena.ai.
    
    Args:
        prompt: Image generation prompt
        output_dir: Output directory for images
        model: Model to use (default: max/auto)
        timeout: Generation timeout in seconds
        headless: Run in headless mode
        vote_mode: Voting mode - "skip", "auto", or "wait"
    
    Returns:
        List of downloaded image paths
    """
    if output_dir is None:
        output_dir = DEFAULT_OUTPUT_DIR
    
    print(f"Prompt: {prompt}")
    print(f"Output: {output_dir}")
    print(f"Model: {model}")
    print(f"Mode: {'HEADLESS' if headless else 'HEADED'}")
    print(f"Vote: {vote_mode}")
    print("")
    
    # Check if session exists
    if not check_session_exists():
        print("ERROR: No saved session found!")
        print("")
        print("Please login first:")
        print("  python3 arena_login.py")
        print("")
        print("Or if VNC is not set up:")
        print("  bash install_vnc.sh")
        print("  bash start_vnc.sh")
        print("  ssh -L 6080:127.0.0.1:6080 user@VPS_IP")
        print("  http://localhost:6080/vnc.html")
        return []
    
    # Check if Playwright is available
    if not PLAYWRIGHT_AVAILABLE:
        print("ERROR: Playwright not installed. Run:")
        print("  pip3 install playwright")
        print("  playwright install chromium")
        return []
    
    with sync_playwright() as p:
        # Launch Chrome with stealth settings
        print("Launching Chrome with stealth settings...")
        
        if STEALTH_AVAILABLE:
            # Use stealth configuration
            context = get_stealth_context(p, DEFAULT_PROFILE_DIR, headless)
        else:
            # Fallback to basic configuration
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(DEFAULT_PROFILE_DIR),
                headless=headless,
                channel="chrome",
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--window-size=1920,1080"
                ],
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            # Add basic stealth script
            page = context.pages[0] if context.pages else context.new_page()
            page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)
        
        page = context.pages[0] if context.pages else context.new_page()
        
        try:
            # Navigate to arena.ai
            print("Navigating to arena.ai...")
            page.goto(ARENA_URL, wait_until="domcontentloaded")
            time.sleep(3)
            
            # Activate image mode
            activate_image_mode(page)
            
            # Handle CAPTCHA if detected
            if CAPTCHA_HANDLER_AVAILABLE:
                if not handle_captcha(page, timeout=60):
                    print("ERROR: CAPTCHA not solved")
                    return []
            
            # Handle any popups
            print("Handling popups...")
            handle_popups(page)
            
            # Select model
            print("Selecting model...")
            select_model(page, model)
            
            # Enter prompt
            print("Entering prompt...")
            if not enter_prompt(page, prompt):
                print("ERROR: Failed to enter prompt")
                return []
            
            # Submit prompt
            print("Submitting prompt...")
            if not submit_prompt(page):
                print("ERROR: Failed to submit prompt")
                return []
            
            # Wait for generation
            if not wait_for_generation(page, timeout):
                print("WARNING: Generation may not have completed")
            
            # Download images BEFORE voting
            print("Downloading images...")
            downloaded = download_images(page, output_dir)
            
            # Handle voting (after images downloaded)
            if VOTING_HANDLER_AVAILABLE:
                handle_voting(page, mode=vote_mode)
            
            if downloaded:
                print("")
                print("============================================")
                print("  IMAGE GENERATION COMPLETE!")
                print("============================================")
                print(f"  Generated: {len(downloaded)} image(s)")
                print(f"  Location: {output_dir}")
                print("")
                for img in downloaded:
                    print(f"    - {img}")
                print("============================================")
            else:
                print("")
                print("WARNING: No images were downloaded")
                print("The generation may have failed or the UI changed")
            
            return downloaded
            
        except Exception as e:
            print(f"ERROR: {e}")
            return []
        
        finally:
            context.close()


def generate_with_retry(prompt, output_dir, model="max", timeout=180, headless=True, vote_mode="skip", max_retries=3):
    """Try generation with retries and verify real images."""
    for attempt in range(max_retries):
        print(f"\n{'='*40}")
        print(f"  ATTEMPT {attempt + 1}/{max_retries}")
        print(f"{'='*40}")
        
        downloaded = generate_image(
            prompt=prompt,
            output_dir=output_dir,
            model=model,
            timeout=timeout,
            headless=headless,
            vote_mode=vote_mode
        )
        
        if downloaded:
            # Verify images are real (>300px)
            real_images = []
            for img_path in downloaded:
                try:
                    from PIL import Image
                    img = Image.open(img_path)
                    if img.width > 300 and img.height > 300:
                        real_images.append(img_path)
                        print(f"  Verified: {img_path.name} ({img.width}x{img.height})")
                except ImportError:
                    # No PIL - check file size (>10KB = likely real image)
                    if img_path.stat().st_size > 10000:
                        real_images.append(img_path)
                except Exception:
                    continue
            
            if real_images:
                print(f"\n  SUCCESS! {len(real_images)} real image(s) generated")
                return real_images
            else:
                print(f"  No real images found, retrying...")
        
        if attempt < max_retries - 1:
            wait_time = 5 * (attempt + 1)  # 5s, 10s
            print(f"  Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
    
    print(f"\n  FAILED after {max_retries} attempts")
    return []


def main():
    parser = argparse.ArgumentParser(description="Arena.ai Image Generation")
    parser.add_argument("prompt", nargs="?", help="Image generation prompt (optional with --check-auth)")
    parser.add_argument("--output", "-o", type=str, 
                       default=str(DEFAULT_OUTPUT_DIR),
                       help="Output directory (default: ~/arena-output/)")
    parser.add_argument("--model", "-m", type=str, default="max",
                       help="Model to use (default: max/auto)")
    parser.add_argument("--timeout", "-t", type=int, default=120,
                       help="Generation timeout in seconds (default: 120)")
    parser.add_argument("--headed", action="store_true",
                       help="Run in headed mode (for debugging)")
    parser.add_argument("--check-auth", action="store_true",
                       help="Check if authentication exists")
    parser.add_argument("--vote", "-v", type=str, default="skip",
                       choices=["skip", "auto", "wait"],
                       help="Voting mode: skip (default), auto, or wait")
    
    args = parser.parse_args()
    
    # Check auth only
    if args.check_auth:
        if check_session_exists():
            print("Authentication: VALID")
            print(f"Profile: {DEFAULT_PROFILE_DIR}")
        else:
            print("Authentication: NOT FOUND")
            print("Please login first: python3 arena_login.py")
        return
    
    # Prompt is required for image generation
    if not args.prompt:
        parser.error("prompt is required for image generation")
    
    print_header()
    
    # Generate image with retries
    downloaded = generate_with_retry(
        prompt=args.prompt,
        output_dir=args.output,
        model=args.model,
        timeout=args.timeout,
        headless=not args.headed,
        vote_mode=args.vote,
        max_retries=3
    )
    
    if downloaded:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
