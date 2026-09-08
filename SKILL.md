---
name: arena-image-gen
description: Generate images using Arena.ai's best AI models via VNC login + persistent Chrome profile. Includes stealth browser, CAPTCHA handling, and voting support.
version: 3.1.0
author: OXYCODE
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [image-generation, arena, ai-art, browser-automation, vnc, stealth, captcha]
    related_skills: []
    requires_tools: [terminal]
---

# Arena Image Generation (v3.1)

Generate high-quality AI images using Arena.ai's model router.
Uses VNC-based login with persistent Chrome profile for authentication.

## Features

- **Stealth Browser** - Avoids CAPTCHA triggers
- **CAPTCHA Detection** - Detects and handles CAPTCHA challenges
- **Voting Support** - Handles "A is better" / "B is better" voting
- **Persistent Login** - Login once, session persists forever
- **Retry Logic** - 3 attempts with verification
- **Image Filtering** - Only saves real images (>300px), skips loading indicators

## When to Use

- User asks to generate/create an image
- User asks for AI art/image generation
- User mentions "arena" with "image"
- User wants to create pictures/drawings

Don't use for: text generation, code, chat (use regular chat for those).

## Prerequisites

1. Linux VPS with SSH access
2. Python 3.11+ installed
3. First-time VNC login required (see Setup below)

## Installation

```bash
# Clone the repo
git clone https://github.com/oxycodeai/arena-image-gen.git ~/.hermes/skills/arena-image-gen

# Install VNC stack + Chrome + Playwright
bash ~/.hermes/skills/arena-image-gen/scripts/install_vnc.sh
```

## First-Time Setup (User Login via VNC)

### Step 1: Start VNC (Hermes runs)
```bash
bash ~/.hermes/skills/arena-image-gen/scripts/start_vnc.sh
```

### Step 2: User Connects via SSH Tunnel
Tell user to run from their phone/laptop:
```bash
ssh -L 6080:127.0.0.1:6080 user@YOUR_VPS_IP
```

### Step 3: User Opens noVNC
Tell user to open in browser:
```
http://localhost:6080/vnc.html
```

### Step 4: User Logs in to Arena.ai
In the Chrome window:
1. Go to: https://arena.ai
2. Click "Continue with Google"
3. Login with Google account
4. Wait for chat interface to appear

### Step 5: Stop VNC (Hermes runs)
After user confirms login:
```bash
bash ~/.hermes/skills/arena-image-gen/scripts/stop_vnc.sh
```

### Step 6: Verify Setup
```bash
python3 ~/.hermes/skills/arena-image-gen/scripts/arena_gen.py --check-auth
```
Should show: `Authentication: VALID`

---

## How to Generate Images

### User Prompt Format

When user wants to generate image, use this format:

```
use image gen skill and create [user's prompt]
```

**Example:**
```
use image gen skill and create a beautiful sunset over mountains
```

### Generation Command

```bash
cd ~/.hermes/skills/arena-image-gen/scripts
python3 arena_gen.py "user's prompt here"
```

### Options

| Flag | Description | Default |
|------|-------------|---------|
| `--output PATH` | Output directory | ~/arena-output/ |
| `--model MODEL` | Specific model | max/auto |
| `--timeout SECONDS` | Max wait time | 180 |
| `--headed` | Show browser | False |
| `--vote MODE` | Voting mode | skip |

### Voting Modes

| Mode | Description |
|------|-------------|
| `skip` | Don't vote, just download (default) |
| `auto` | Auto-click "Both are good" |
| `wait` | Wait for user to vote via VNC |

### Example Commands

```bash
# Basic generation
arena_gen.py "a cute dog image"

# With auto-voting
arena_gen.py "sunset over ocean" --vote auto

# With specific model
arena_gen.py "abstract art" --model gpt-image-1.5-high-fidelity

# Debug mode (show browser)
arena_gen.py "cat" --headed
```

---

## ⏱️ TIMING: No Fixed Time!

**IMPORTANT:** Image generation has NO fixed time limit.

| Stage | Time |
|-------|------|
| Chrome launch | 3-5 seconds |
| Page load | 3-5 seconds |
| Prompt entry | 1-2 seconds |
| **Image generation** | **30 seconds to 3+ minutes** |
| Download | 2-5 seconds |
| **Total** | **40 seconds to 5 minutes** |

**What to tell user:**
- "Image generation started, this can take 30 seconds to 3+ minutes"
- "No fixed time - depends on arena.ai server load"
- "I'll notify you when image is ready"

**Don't say:** "Image will be ready in 30 seconds" (WRONG - no guarantee)

---

## 🔍 VERIFICATION: How to Confirm Image Generated

Since image generation happens in headless mode, user can't see it. Use these methods:

### Method 1: Check Output Files
```bash
ls -la ~/arena-output/
```
Look for PNG files > 10KB (real images are 100KB-5MB)

### Method 2: Check File Size
```bash
file ~/arena-output/*.png
```
Should show: `PNG image data, 1024 1024, 8-bit/color RGBA`

### Method 3: Download and View
Tell user to download the file and open it:
```bash
# On VPS
ls -la ~/arena-output/

# Download to local machine
scp user@VPS_IP:~/arena-output/*.png ./
```

### Method 4: F12 Check (If using headed mode)
If using `--headed` flag:
1. Right-click on generated image
2. Select "Inspect" or press F12
3. Check element shows `<img>` tag with blob: URL
4. Image dimensions should be >300x300px

### Method 5: Screenshot Verification
If user wants to verify visually:
```bash
# Take screenshot of arena.ai page
python3 -c "
from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://arena.ai/image/direct?model_a=max')
    time.sleep(5)
    page.screenshot(path='/tmp/arena_verify.png')
    browser.close()
    print('Screenshot saved to /tmp/arena_verify.png')
"
```

### What SUCCESS Looks Like
```
✅ File exists: ~/arena-output/20260908_123456_image_1.png
✅ File size: 245KB (real images are 100KB-5MB)
✅ Image type: PNG image data, 1024 1024, 8-bit/color RGBA
✅ No "21x21" or tiny dimensions
```

### What FAILURE Looks Like
```
❌ No files in ~/arena-output/
❌ File size < 10KB (loading indicator, not real image)
❌ Image dimensions 21x21 or 64x64 (loading indicator)
❌ Script error: "Something went wrong"
❌ Script error: "Generation timeout"
```

---

## ⚠️ ERRORS & TROUBLESHOOTING

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `No saved session found` | Login not done | Run setup steps above |
| `CAPTCHA not solved` | Anti-bot detected | Run `start_vnc.sh`, solve manually |
| `Generation timeout` | Too slow/taking long | Increase `--timeout 300` |
| `No images downloaded` | UI changed/wrong URL | Check arena.ai, selectors may need update |
| `21x21 image saved` | Loading indicator caught | Now fixed with 300px filter |
| `Something went wrong` | Arena.ai error | Retry with `--timeout 300` |
| `Image mode not activated` | Button click failed | Script continues anyway |

### If Generation Fails

1. **First attempt fails** → Script automatically retries (3 attempts)
2. **All 3 fail** → Check:
   - Is session still valid? `python3 arena_gen.py --check-auth`
   - Is arena.ai working? Open in browser manually
   - Try `--headed` mode to see what's happening
3. **Still fails** → May need to re-login:
   ```bash
   bash ~/.hermes/skills/arena-image-gen/scripts/start_vnc.sh
   # User re-login via VNC
   bash ~/.hermes/skills/arena-image-gen/scripts/stop_vnc.sh
   ```

### If Image is Small/Loading Indicator

Script now filters images >300px only. If you see:
- 21x21 pixels → Loading indicator (skipped by script)
- 64x64 pixels → Avatar/icon (skipped by script)
- 1024x1024+ → Real image ✅

---

## Procedure (What Script Does)

1. Check authentication exists
2. Launch Chrome with stealth settings (headless)
3. Navigate to `arena.ai/image/direct?model_a=max`
4. **Activate image mode** (click "Image" button)
5. Handle CAPTCHA if detected
6. Handle any popups (Terms, cookies)
7. Enter user's prompt
8. Submit and wait for generation (30s-3min)
9. **Download image only if >300px** (skip loading indicators)
10. Handle voting interface (skip/auto/wait)
11. Return file path to user

---

## Architecture

```
FIRST-TIME SETUP:
  VPS: Run Chrome on Xvfb + VNC (localhost only)
       ↓
  User: SSH tunnel from phone/laptop
       ↓
  User: Opens noVNC URL → Logs in manually
       ↓
  Script: Detects login → Saves Chrome profile
       ↓
  VNC: Shut down permanently

FUTURE USE:
  Script: Loads Chrome profile → Stealth browser
       ↓
  Navigate: /image/direct?model_a=max (correct URL!)
       ↓
  Activate: Click "Image" button
       ↓
  CAPTCHA Handler: Detects and waits for manual solve (if needed)
       ↓
  Enter Prompt → Submit → Wait (30s-3min)
       ↓
  Download: Only images >300px (skip loading indicators)
       ↓
  Voting Handler: Skips or auto-votes
       ↓
  Return: File path to user
```

---

## Components

| File | Purpose |
|------|---------|
| `stealth_config.py` | Browser stealth settings to avoid CAPTCHA |
| `captcha_handler.py` | CAPTCHA detection and handling |
| `voting_handler.py` | Voting interface handling |
| `arena_gen.py` | Main image generation script |
| `arena_login.py` | First-time login via VNC |
| `auth_manager.py` | Authentication status check |
| `install_vnc.sh` | VNC stack installer |
| `start_vnc.sh` | Start VNC services |
| `stop_vnc.sh` | Stop VNC services |

---

## Security Model

| Concern | Solution |
|---------|----------|
| Public port exposure | NEVER - VNC binds to localhost only |
| SSH tunnel security | Built-in SSH encryption |
| Chrome profile security | Stored locally, not in chat |
| Token/cookie exposure | Never printed/logged |
| Re-login after expiry | Script detects, prompts re-setup |

---

## Quick Reference

| Task | Command |
|------|---------|
| Generate image | `arena_gen.py "sunset over ocean"` |
| Check auth | `arena_gen.py --check-auth` |
| Start VNC | `bash start_vnc.sh` |
| Stop VNC | `bash stop_vnc.sh` |
| Re-login | `python3 arena_login.py` |
| List images | `ls -la ~/arena-output/` |

---

## Credits

Built by **OXYCODE** for Hermes agent platform.

| Platform | Link |
|----------|------|
| Telegram | [t.me/OXYCODEAI](https://t.me/OXYCODEAI) |
| Instagram | [@oxycode.ai](https://instagram.com/oxycode.ai) |
| GitHub | [oxycodeai](https://github.com/oxycodeai) |
