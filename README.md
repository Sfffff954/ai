# 🤖 Ghostfish — Local AI powered by Ollama

A personal AI that runs **completely on your own PC**.  
No account, no subscription, no cloud — everything stays on your computer.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Ollama](https://img.shields.io/badge/Ollama-local-green)
![Windows](https://img.shields.io/badge/Windows-10%2F11-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

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
| 🔗 Network | Connect multiple PCs as AI agents |
| 💾 Chat History | All conversations are saved and can be reopened |
| 👻 Ghost Character | Animated ghost that reacts to the AI's mood |
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

**On PC 2 (Windows):**
```powershell
$env:OLLAMA_HOST="0.0.0.0:11434"
$env:OLLAMA_ORIGINS="*"
ollama serve
```

In Ghostfish → Sidebar → **🔗 Agent Network** → enter the IP of PC 2 → click Test.

Ghostfish automatically routes image requests to the Vision Agent!

---

## 🧠 How the Self-Learning Works

- Ghostfish remembers facts you tell it (your name, job, interests)
- It learns your writing style from the chat automatically
- You can feed it text files, code files, or entire GitHub repos
- The Crypto Guesser tracks prediction accuracy and improves over time
- Everything is stored locally in JSON files — nothing leaves your PC

---

## ⚠️ Notes

- Runs **100% locally** — no data is sent to external servers
- Ollama must be running when the app starts (auto-starts via the bat file)
- Optional APIs (ElevenLabs, Claude, Gemini, OpenAI) can be added in Settings → APIs

---

## 📁 File Structure

Only these 3 files are needed — everything else is created automatically:

```
Ghostfish/
├── local_ai.py       ← the app
├── install.bat       ← one-click installer
└── README.md         ← this file

Auto-created on first start:
├── lern_daten/           ← learned text files
├── lern_code/            ← learned code files
├── gespeicherte_chats/   ← saved chats
├── erstellte_dateien/    ← files created by AI
├── obsidian_export/      ← Obsidian exports
└── *.json                ← memory, settings, bots
```

---

## 📄 License

MIT — free to use, modify and share.

---

Made with 👻 by [Sffff954](https://github.com/Sffff954)
