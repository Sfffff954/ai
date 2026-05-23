# 🤖 Geist-AI — Lokale KI mit Ollama

Eine persönliche KI die komplett **lokal auf deinem PC** läuft.  
Kein Account, kein Abo, keine Cloud — alles auf deinem Computer.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Ollama](https://img.shields.io/badge/Ollama-lokal-green)
![Windows](https://img.shields.io/badge/Windows-10%2F11-blue)

---

## ⚡ Schnellstart (Windows)

1. **Dieses Repo herunterladen** → grüner "Code" Button → "Download ZIP"
2. ZIP entpacken
3. **`install.bat` doppelklicken** — fertig!

Der Installer richtet alles automatisch ein:
- ✅ Python (falls nicht installiert)
- ✅ Alle benötigten Pakete
- ✅ Ollama (die KI-Engine)
- ✅ KI-Modell herunterladen
- ✅ Desktop-Verknüpfung erstellen

---

## 🎯 Features

| Feature | Beschreibung |
|---|---|
| 💬 Chat | Natürliche Gespräche, lernt deinen Schreibstil |
| 🖼 Bilder | Bilder analysieren und beschreiben |
| 💻 Code | Code schreiben, erklären, ausführen |
| 🔍 Internet | Automatische Websuche bei aktuellen Fragen |
| 🪙 Crypto | Live Preise + KI-Analyse und Kaufsignal |
| 🤖 Bots | Eigene Bots erstellen die automatisch laufen |
| 🧠 Lernen | Lernt aus Gesprächen und eigenen Dateien |
| 📚 GitHub | GitHub Repos als Lernmaterial laden |
| 🔗 Netzwerk | Mehrere PCs als Agenten verbinden |
| 💾 Chats | Alle Gespräche werden gespeichert |

---

## 📋 Manuelle Installation

Falls `install.bat` nicht funktioniert:

```powershell
# 1. Python installieren: https://python.org/downloads
# 2. Pakete installieren
pip install requests customtkinter pillow

# 3. Ollama installieren: https://ollama.com/download

# 4. KI-Modell laden
ollama pull qwen2.5:latest

# 5. Ollama starten
$env:OLLAMA_ORIGINS="*"; ollama serve

# 6. App starten (neues Fenster)
python local_ai.py
```

---

## 🤖 Empfohlene Modelle

| Modell | Größe | Gut für |
|---|---|---|
| `qwen2.5:latest` | ~2GB | Alles allgemein (empfohlen) |
| `qwen2.5-coder:latest` | ~4.7GB | Code schreiben |
| `llava` | ~4GB | Bilder analysieren |
| `llama3` | ~4GB | Englisch, allgemein |

```powershell
ollama pull qwen2.5:latest
ollama pull qwen2.5-coder:latest
ollama pull llava
```

---

## 💬 Befehle im Chat

| Befehl | Funktion |
|---|---|
| `/search was auch immer` | Internet durchsuchen |
| `/wiki Python` | Wikipedia |
| `/youtube <url>` | YouTube Video analysieren |
| `/pdf` | PDF Datei analysieren |
| `/github user/repo` | GitHub Repo lernen |
| `/code bubble sort` | Code in Wissensbasis suchen |
| `/todo Aufgabe` | TODO hinzufügen |
| `/timer 60 Pause!` | Timer stellen |
| `/profile code` | KI-Profil wechseln |
| `/model llava` | Modell wechseln |
| `/crypto` | Crypto-Guesser öffnen |
| `/help` | Alle Befehle |

---

## 🔧 Systemanforderungen

- **OS:** Windows 10/11
- **RAM:** min. 8GB (16GB empfohlen)
- **Speicher:** 5-20GB je nach Modell
- **Internet:** Nur für erste Installation und Websuche

---

## 🌐 Mehrere PCs verbinden (optional)

Du kannst einen zweiten PC (auch Linux/Mac) als Bild-Agent nutzen:

**Auf PC 2 (Linux):**
```bash
curl -fsSL https://ollama.com/install.sh | sh
OLLAMA_HOST=0.0.0.0:11434 OLLAMA_ORIGINS=* ollama serve
ollama pull llava
```

In Geist-AI → Sidebar → **🔗 Agent-Netzwerk** → IP von PC 2 eintragen.

---

## ⚠️ Hinweise

- Der **Crypto-Guesser** ist reine KI-Spekulation — kein Finanzratschlag!
- Die App läuft **komplett lokal** — keine Daten werden an externe Server geschickt
- Ollama muss laufen wenn die App startet (startet automatisch)

---

## 📄 Lizenz

MIT — kostenlos nutzbar, veränderbar und weitergeben erlaubt.
