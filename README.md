# 🎨 Arena Image Generation Skill

Generate high-quality AI images using Arena.ai's best models.
One-time VNC login → Session persists forever → Generate images anytime.

## ⚡ One-Click Setup Prompt

Copy this prompt and paste it in Hermes agent to setup everything automatically:

```
Install the arena-image-gen skill from https://github.com/oxycodeai/arena-image-gen.git

Steps:
1. Clone the repo to ~/.hermes/skills/arena-image-gen/
2. Run: bash ~/.hermes/skills/arena-image-gen/scripts/install_vnc.sh
3. Run: bash ~/.hermes/skills/arena-image-gen/scripts/start_vnc.sh
4. Tell me to login via VNC with these steps:
   - SSH tunnel: ssh -L 6080:127.0.0.1:6080 user@VPS_IP
   - Open: http://localhost:6080/vnc.html
   - Login to arena.ai with Google
5. After I confirm login, run: bash ~/.hermes/skills/arena-image-gen/scripts/stop_vnc.sh
6. Verify setup: python3 ~/.hermes/skills/arena-image-gen/scripts/arena_gen.py --check-auth

Then tell me: "Setup complete! You can now generate images. Just say: use image gen skill and create [your prompt]"
```

## 📋 Quick Start

### Option 1: One-Click Setup (Recommended)

Copy the prompt above and paste it in Hermes agent. It will:
- Install everything automatically
- Guide you through VNC login
- Verify setup is complete

### Option 2: Manual Setup

```bash
# 1. Clone the repo
git clone https://github.com/oxycodeai/arena-image-gen.git ~/.hermes/skills/arena-image-gen/

# 2. Install VNC stack
bash ~/.hermes/skills/arena-image-gen/scripts/install_vnc.sh

# 3. Start VNC and login
bash ~/.hermes/skills/arena-image-gen/scripts/start_vnc.sh
ssh -L 6080:127.0.0.1:6080 user@VPS_IP
# Open: http://localhost:6080/vnc.html
# Login to arena.ai

# 4. Stop VNC
bash ~/.hermes/skills/arena-image-gen/scripts/stop_vnc.sh

# 5. Generate images!
python3 ~/.hermes/skills/arena-image-gen/scripts/arena_gen.py "a cute dog image"
```

## 🚀 Usage Examples

```bash
# Basic image generation
python3 scripts/arena_gen.py "a cute dog image"

# With specific model
python3 scripts/arena_gen.py "sunset over ocean" --model gpt-image-1.5-high-fidelity

# Auto-vote in Battle Mode
python3 scripts/arena_gen.py "abstract art" --vote auto

# Save to custom directory
python3 scripts/arena_gen.py "cat" --output ~/my-images/
```

## 🎯 How to Use with Hermes

After setup, just tell Hermes:

```
use image gen skill and create a cute dog image
```

```
use image gen skill and create sunset over ocean with gpt-image-1.5-high-fidelity
```

```
use image gen skill and create abstract art and save to ~/my-art/
```

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

## 🏆 Best Models

| Model | Quality | Best For |
|-------|---------|----------|
| `gpt-image-1.5-high-fidelity` | 🥇 Best | Overall quality |
| `gemini-3-pro-image-preview` | 🥈 Excellent | Creative/artistic |
| `flux-2-max` | 🥉 Great | Fast generation |
| `gpt-image-1` | 4th | Balanced |
| `gemini-2.0-flash-preview` | 5th | Quick drafts |

Use `--model max` for auto-selection (default).

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

## 🛡️ Security Features

- ✅ **No public ports** - VNC binds to localhost only
- ✅ **SSH tunnel required** - Built-in encryption
- ✅ **Local storage only** - Credentials never leave VPS
- ✅ **Stealth browser** - Avoids CAPTCHA triggers
- ✅ **One-time login** - Session persists forever

## 📁 File Structure

```
arena-image-gen/
├── scripts/
│   ├── install_vnc.sh      # VNC stack installer
│   ├── start_vnc.sh        # VNC starter
│   ├── stop_vnc.sh         # VNC stopper
│   ├── arena_login.py      # Login + save profile
│   ├── arena_gen.py        # Image generation
│   ├── auth_manager.py     # Auth status check
│   ├── stealth_config.py   # Browser stealth
│   ├── captcha_handler.py  # CAPTCHA handling
│   ├── voting_handler.py   # Voting interface
│   ├── setup_guide.py      # Setup guide
│   └── requirements.txt    # Dependencies
├── SKILL.md                # Skill definition
├── README.md               # This file
└── .gitignore              # Git ignores
```

## 📝 License

MIT

## 🙏 Credits

Built by **OXYCODE** for Hermes agent platform.
Uses Arena.ai for model routing.

### Connect with us:

| Platform | Link |
|----------|------|
| Telegram | [t.me/OXYCODEAI](https://t.me/OXYCODEAI) |
| Instagram | [@oxycode.ai](https://instagram.com/oxycode.ai) |
| GitHub | [oxycodeai](https://github.com/oxycodeai) |
