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

## 🏆 Best Models

| Model | Quality | Best For |
|-------|---------|----------|
| `gpt-image-1.5-high-fidelity` | 🥇 Best | Overall quality |
| `gemini-3-pro-image-preview` | 🥈 Excellent | Creative/artistic |
| `flux-2-max` | 🥉 Great | Fast generation |
| `gpt-image-1` | 4th | Balanced |
| `gemini-2.0-flash-preview` | 5th | Quick drafts |

Use `--model max` for auto-selection (default).

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

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| CAPTCHA appears | Solve via VNC (auto-detected) |
| Voting required | Use `--vote skip` or `--vote auto` |
| Session expired | Run: `python3 arena_login.py` |
| VNC not visible | Check SSH tunnel |
| No images generated | Check auth: `arena_gen.py --check-auth` |

## 📝 License

MIT

## 🙏 Credits

Built for Hermes agent platform.
Uses Arena.ai for model routing.
