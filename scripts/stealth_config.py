"""
Stealth Browser Configuration for Playwright
Makes browser appear human-like to avoid CAPTCHA triggers.

Usage:
    from stealth_config import get_stealth_context
    context = get_stealth_context(p, profile_dir, headless=True)
"""

from pathlib import Path

# Stealth initialization script
# This runs before any page JavaScript
STEALTH_INIT_SCRIPT = """
// 1. Override webdriver property
Object.defineProperty(navigator, 'webdriver', {
    get: () => undefined
});

// 2. Add chrome runtime object
window.chrome = {
    runtime: {
        onMessage: { addListener: function() {} },
        sendMessage: function() {}
    },
    loadTimes: function() { return {} },
    csi: function() { return {} },
    app: { isInstalled: false }
};

// 3. Mock navigator.plugins (headless has empty plugins)
Object.defineProperty(navigator, 'plugins', {
    get: () => {
        const plugins = [
            { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer' },
            { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai' },
            { name: 'Native Client', filename: 'internal-nacl-plugin' }
        ];
        plugins.length = 3;
        return plugins;
    }
});

// 4. Mock navigator.languages
Object.defineProperty(navigator, 'languages', {
    get: () => ['en-US', 'en']
});

// 5. Fix permissions API
const originalQuery = window.navigator.permissions.query;
window.navigator.permissions.query = (parameters) => (
    parameters.name === 'notifications' ?
    Promise.resolve({ state: Notification.permission }) :
    originalQuery(parameters)
);

// 6. Override screen dimensions (headless has 0s)
if (screen.availWidth === 0) {
    Object.defineProperty(screen, 'availWidth', { get: () => 1920 });
    Object.defineProperty(screen, 'availHeight', { get: () => 1040 });
    Object.defineProperty(screen, 'width', { get: () => 1920 });
    Object.defineProperty(screen, 'height', { get: () => 1080 });
}

// 7. Fix WebGL renderer (headless uses SwiftShader)
const getParameter = WebGLRenderingContext.prototype.getParameter;
WebGLRenderingContext.prototype.getParameter = function(parameter) {
    if (parameter === 37445) {
        return 'Intel Inc.';
    }
    if (parameter === 37446) {
        return 'Intel Iris OpenGL Engine';
    }
    return getParameter.apply(this, arguments);
};

// 8. Add missing window properties
if (!window.Notification) {
    window.Notification = { permission: 'default' };
}

// 9. Fix navigator.connection
if (!navigator.connection) {
    Object.defineProperty(navigator, 'connection', {
        get: () => ({
            effectiveType: '4g',
            rtt: 50,
            downlink: 10,
            saveData: false
        })
    });
}

// 10. Add human-like mouse movement (jitter)
const originalMouseMove = MouseEvent.prototype.initMouseEvent;
MouseEvent.prototype.initMouseEvent = function() {
    originalMouseMove.apply(this, arguments);
    // Add small random offset
    this.clientX += Math.random() * 2 - 1;
    this.clientY += Math.random() * 2 - 1;
};
"""


def get_stealth_context(playwright, profile_dir, headless=True, channel="chrome"):
    """
    Launch a browser context with stealth settings.
    
    Args:
        playwright: Playwright instance (from sync_playwright())
        profile_dir: Path to Chrome profile directory
        headless: Run in headless mode
        channel: Browser channel (chrome, chromium)
    
    Returns:
        Browser context with stealth applied
    """
    profile_dir = Path(profile_dir)
    profile_dir.mkdir(parents=True, exist_ok=True)
    
    # Browser launch arguments for stealth
    stealth_args = [
        "--disable-blink-features=AutomationControlled",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--window-size=1920,1080",
        "--start-maximized",
        "--disable-features=IsolateOrigins,site-per-process",
        "--disable-site-isolation-trials",
        "--disable-web-security",
        "--allow-running-insecure-content",
    ]
    
    # Launch persistent context
    context = playwright.chromium.launch_persistent_context(
        user_data_dir=str(profile_dir),
        headless=headless,
        channel=channel,
        args=stealth_args,
        viewport={"width": 1920, "height": 1080},
        user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        locale="en-US",
        timezone_id="America/New_York",
        color_scheme="light",
        permissions=["geolocation"],
        ignore_https_errors=True,
    )
    
    # Apply stealth script to all pages
    for page in context.pages:
        page.add_init_script(STEALTH_INIT_SCRIPT)
    
    # Apply to new pages
    context.on("page", lambda p: p.add_init_script(STEALTH_INIT_SCRIPT))
    
    return context


def add_human_delay(min_ms=100, max_ms=500):
    """
    Generate a random human-like delay.
    Use with: time.sleep(add_human_delay() / 1000)
    
    Returns:
        Delay in milliseconds
    """
    import random
    return random.randint(min_ms, max_ms)


def human_click(page, selector, delay_before=True):
    """
    Click an element with human-like behavior.
    
    Args:
        page: Playwright page
        selector: CSS selector
        delay_before: Add random delay before click
    """
    import time
    import random
    
    if delay_before:
        time.sleep(random.uniform(0.1, 0.3))
    
    element = page.query_selector(selector)
    if element:
        # Get element center
        box = element.bounding_box()
        if box:
            # Add small random offset
            x = box["x"] + box["width"] / 2 + random.uniform(-2, 2)
            y = box["y"] + box["height"] / 2 + random.uniform(-2, 2)
            page.mouse.move(x, y)
            time.sleep(random.uniform(0.05, 0.15))
            page.mouse.click(x, y)
        else:
            element.click()
    else:
        raise Exception(f"Element not found: {selector}")


def human_type(page, selector, text, char_delay=True):
    """
    Type text with human-like delays between characters.
    
    Args:
        page: Playwright page
        selector: CSS selector
        text: Text to type
        char_delay: Add delay between characters
    """
    import time
    import random
    
    element = page.query_selector(selector)
    if element:
        element.click()
        time.sleep(0.1)
        
        for char in text:
            page.keyboard.type(char)
            if char_delay:
                time.sleep(random.uniform(0.02, 0.08))
    else:
        raise Exception(f"Element not found: {selector}")


# Example usage
if __name__ == "__main__":
    print("Stealth configuration loaded!")
    print(f"Script length: {len(STEALTH_INIT_SCRIPT)} characters")
    print("Use get_stealth_context() to launch browser")
