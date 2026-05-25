<p align="center">
  <img src="ghostfish_logo.png" width="200" alt="Ghostfish Logo"/>
</p>

<h1 align="center">🐡 Ghostfish — Local AI powered by Ollama</h1>

<p align="center">
  A personal AI that runs <b>completely on your own PC</b>.<br/>
  No account, no subscription, no cloud — everything stays on your computer.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue"/>
  <img src="https://img.shields.io/badge/Ollama-local-green"/>
  <img src="https://img.shields.io/badge/Windows-10%2F11-blue"/>
  <img src="https://img.shields.io/badge/License-MIT-yellow"/>
</p>

---

## ⚡ Quick Start (Windows)

1. **Download this repo** → green "Code" button → "Download ZIP"
2. Extract the ZIP
3. **Double-click `install.bat`** — that's it!

The installer sets everything up automatically:
- ✅ Python (installs if missing)
- ✅ All required packages
- ✅ Ollama (the AI engine)
- ✅ Downloads an AI model
- ✅ Creates a Desktop shortcut

---

## 🎯 Features

| Feature | Description |
|---|---|
| 💬 Chat | Natural conversations, learns your writing style |
| 🖼 Images | Send images and let the AI describe or analyze them |
| 💻 Code | Write, explain and run code directly in the chat |
| 🔍 Internet | Automatic web search for current questions |
| 🪙 Crypto | Live prices + AI analysis and buy/sell signals |
| 🤖 Bots | Create your own bots that run automatically |
| 🧠 Learning | Learns from conversations and your own files |
| 📚 GitHub | Load GitHub repos as learning material |
| 🔗 Network | Connect multiple PCs as AI agents (MoE) |
| 💾 Chat History | All conversations are saved and can be reopened |
| 🐡 Ghostfish | Animated mascot that reacts to the AI's mood |
| 🎨 Themes | 5 different color themes |

---

## 📋 Manual Installation

If `install.bat` doesn't work:

```powershell
# 1. Install Python: https://python.org/downloads
# 2. Install packages
pip install requests customtkinter pillow

# 3. Install Ollama: https://ollama.com/download

# 4. Download an AI model
ollama pull qwen2.5:latest

# 5. Start Ollama
$env:OLLAMA_ORIGINS="*"; ollama serve

# 6. Start the app (new window)
python local_ai.py
```

---

## 🤖 Recommended Models

| Model | Size | Best for |
|---|---|---|
| `qwen2.5:latest` | ~2GB | Everything general (recommended) |
| `qwen2.5-coder:latest` | ~4.7GB | Writing code |
| `qwen2.5-vl` | ~5GB | Analyzing images |
| `llava` | ~4GB | Images (alternative) |
| `llama3` | ~4GB | English, general purpose |

```powershell
ollama pull qwen2.5:latest
ollama pull qwen2.5-coder:latest
ollama pull llava
```

---

## 💬 Chat Commands

| Command | What it does |
|---|---|
| `/search anything` | Search the internet |
| `/wiki Python` | Look up Wikipedia |
| `/youtube <url>` | Analyze a YouTube video |
| `/pdf` | Analyze a PDF file |
| `/github user/repo` | Load a GitHub repo to learn from |
| `/code bubble sort` | Search learned code files |
| `/todo Task name` | Add a TODO |
| `/timer 60 Break!` | Set a timer |
| `/profile code` | Switch AI personality profile |
| `/model llava` | Switch AI model |
| `/crypto` | Open Crypto Guesser |
| `/bot News-Bot` | Run a bot |
| `/bots` | Show all bots |
| `/memory` | Show what Ghostfish remembers about you |
| `/forget` | Clear memory |
| `/theme ocean` | Switch color theme |
| `/help` | Show all commands |

---

## 🪙 Crypto Guesser

- **Live prices** for 16 coins (BTC, ETH, SOL, BNB, XRP, ADA, DOGE, AVAX, LINK, DOT, LTC, SHIB, TON, NEAR, SUI, PEPE)
- **Real-time chart** updated every 30 seconds
- **AI signal**: BUY / HOLD / SELL / WAIT
- **Risk level**: LOW / MEDIUM / HIGH / VERY HIGH
- **Entry price, Stop Loss, Take Profit**
- **Self-learning**: tracks past predictions and checks if they were correct

> ⚠️ The Crypto Guesser is AI speculation only — not financial advice!

---

## 🔧 System Requirements

- **OS:** Windows 10/11
- **RAM:** 8GB minimum (16GB recommended)
- **Storage:** 5–20GB depending on models
- **Internet:** Only needed for installation and web search

---

## 🌐 Connect Multiple PCs (optional)

You can use a second PC (Linux/Mac/Windows) as a Vision Agent for image analysis:

**On PC 2 (Linux):**
```bash
curl -fsSL https://ollama.com/install.sh | sh
OLLAMA_HOST=0.0.0.0:11434 OLLAMA_ORIGINS=* ollama serve
ollama pull llava
```

In Ghostfish → Sidebar → **🔗 Agent Network** → enter the IP of PC 2 → click Test.

---

## 📁 File Structure

Only these 4 files needed — everything else is created automatically:

```
Ghostfish/
├── local_ai.py           ← the app
├── ghostfish_logo.png    ← the mascot (put next to local_ai.py)
├── install.bat           ← one-click installer
└── README.md             ← this file
```

---

## 📄 License

MIT — free to use, modify and share.

---

<p align="center">Made with 🐡 by <a href="https://github.com/Sffff954">Sffff954</a></p>
