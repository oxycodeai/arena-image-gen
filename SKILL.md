---
name: arena-image-gen
description: Generate images using Arena.ai's best AI models via VNC login + persistent Chrome profile. Includes stealth browser, CAPTCHA handling, and voting support.
version: 3.0.0
author: OXYCODE
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [image-generation, arena, ai-art, browser-automation, vnc, stealth, captcha]
    related_skills: []
    requires_tools: [terminal]
---

# Arena Image Generation (v3.0)

Generate high-quality AI images using Arena.ai's model router.
Uses VNC-based login with persistent Chrome profile for authentication.
Includes stealth browser to avoid CAPTCHA, CAPTCHA detection/handling, and voting interface support.

## Features

- **Stealth Browser** - Avoids CAPTCHA triggers
- **CAPTCHA Detection** - Detects and handles CAPTCHA challenges
- **Voting Support** - Handles "A is better" / "B is better" voting
- **Persistent Login** - Login once, session persists forever
- **No Public Ports** - VNC only accessible via SSH tunnel

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

## Setup (First Time Only)

### Automatic Setup (Hermes handles):

```bash
# Install VNC stack + Chrome + Playwright
bash ${HERMES_SKILL_DIR}/scripts/install_vnc.sh
```

### Manual Steps (User does):

#### Step 1: Start VNC
```bash
bash ${HERMES_SKILL_DIR}/scripts/start_vnc.sh
```

#### Step 2: Connect via SSH Tunnel (from phone/laptop)
```bash
ssh -L 6080:127.0.0.1:6080 user@YOUR_VPS_IP
```

#### Step 3: Open noVNC in Browser
```
http://localhost:6080/vnc.html
```

You should see a Chrome browser window.

#### Step 4: Login to Arena.ai
In the Chrome window:
1. Go to: https://arena.ai
2. Click "Continue with Google"
3. Login with your Google account
4. Wait for chat interface to appear

#### Step 5: Session Saves Automatically
Script detects login and saves session automatically.

#### Step 6: Stop VNC
```bash
bash ${HERMES_SKILL_DIR}/scripts/stop_vnc.sh
```

**DONE!** Session is now saved permanently. No more login needed.

## How to Generate Images

```bash
python3 ${HERMES_SKILL_DIR}/scripts/arena_gen.py "your prompt here"
```

Options:
- `--output PATH` - Output directory (default: ~/arena-output/)
- `--model MODEL` - Specific model (default: max/auto)
- `--timeout SECONDS` - Max wait time (default: 120)
- `--headed` - Show browser window (for debugging)
- `--vote MODE` - Voting mode: skip (default), auto, or wait

### Voting Modes

| Mode | Description |
|------|-------------|
| `skip` | Don't vote, just download images (default) |
| `auto` | Auto-click "Both are good" |
| `wait` | Wait for user to vote via VNC |

### Example Commands

```bash
# Basic generation (skip voting)
arena_gen.py "a cute dog image"

# Generate with auto-voting
arena_gen.py "sunset over ocean" --vote auto

# Generate with specific model
arena_gen.py "abstract art" --model gpt-image-1.5-high-fidelity

# Generate in headed mode (for debugging)
arena_gen.py "cat" --headed
```

## Quick Reference

| Task | Command |
|------|---------|
| Generate image | `arena_gen.py "sunset over ocean"` |
| Check auth | `auth_manager.py --status` |
| Show setup guide | `auth_manager.py --setup` |
| Clear auth | `auth_manager.py --clear` |
| Start VNC | `bash start_vnc.sh` |
| Stop VNC | `bash stop_vnc.sh` |
| Re-login | `python3 arena_login.py` |

## Procedure

1. Verify authentication exists (run setup if not)
2. Launch Chrome with stealth settings (headless)
3. Navigate to arena.ai
4. **Handle CAPTCHA if detected** (wait for VNC solve)
5. Handle any popups (Terms, cookies)
6. Ensure "Max" model is selected
7. Enter user's prompt
8. Submit and wait for generation
9. **Download generated image(s) BEFORE voting**
10. **Handle voting interface** (skip/auto/wait)
11. Return file path to user

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
  Script: Loads Chrome profile → Stealth browser → Image ready
       ↓
  CAPTCHA Handler: Detects and waits for manual solve (if needed)
       ↓
  Voting Handler: Skips or auto-votes after image download
```

## Components

| File | Purpose |
|------|---------|
| `stealth_config.py` | Browser stealth settings to avoid CAPTCHA |
| `captcha_handler.py` | CAPTCHA detection and handling |
| `voting_handler.py` | Voting interface handling |
| `arena_gen.py` | Main image generation script |
| `arena_login.py` | First-time login via VNC |
| `auth_manager.py` | Authentication status check |

## Security Model

| Concern | Solution |
|---------|----------|
| Public port exposure | NEVER - VNC binds to localhost only |
| SSH tunnel security | Built-in SSH encryption |
| Chrome profile security | Stored locally, not in chat |
| Token/cookie exposure | Never printed/logged |
| Re-login after expiry | Script detects, prompts re-setup |

## Pitfalls

- Session expires after ~2-4 weeks → re-login needed
- Arena UI may change → selectors may need updating
- Some images take 30-60 seconds to generate
- VNC must be running for first-time login only
- No public port exposure - SSH tunnel required
- Google may block headless login → Use real Chrome + automation bypass flags
- **CAPTCHA may appear** → Stealth reduces but doesn't eliminate; VNC solve required
- **Voting required** → Arena.ai Battle Mode requires voting; use `--vote skip` to bypass
- **2 images generated** → Battle Mode generates 2 images (Model A vs Model B)

## Verification

- Output file exists and is valid PNG
- File size > 10KB (not empty/broken)
- Image dimensions reasonable (>100x100)

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| VNC not visible | SSH tunnel not running | Run: `ssh -L 6080:127.0.0.1:6080 user@VPS_IP` |
| Chrome not loading | VNC services stopped | Run: `bash start_vnc.sh` |
| Login fails | Google bot detection | Use real Chrome (not bundled Chromium) |
| Session expired | Cookie TTL reached | Run: `python3 arena_login.py` |
| No images generated | UI changed | Check arena.ai selectors |
| **CAPTCHA appears** | Anti-bot detection | Stealth helps; solve via VNC if triggered |
| **Voting required** | Battle Mode default | Use `--vote skip` or `--vote auto` |
| **2 images generated** | Battle Mode behavior | Normal; both images downloaded |

## Credits

Built by **OXYCODE** for Hermes agent platform.

| Platform | Link |
|----------|------|
| Telegram | [t.me/OXYCODEAI](https://t.me/OXYCODEAI) |
| Instagram | [@oxycode.ai](https://instagram.com/oxycode.ai) |
| GitHub | [oxycodeai](https://github.com/oxycodeai) |
