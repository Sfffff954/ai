"""
╔══════════════════════════════════════════════════════╗
║  Ghostfish  —  Local AI powered by Ollama                  ║
║  + Bots  + Auto-Suche  + Crypto-Guesser             ║
║  + Selbstlernen  + Streaming  + Gedächtnis           ║
╚══════════════════════════════════════════════════════╝
pip install requests customtkinter pillow
python local_ai.py
"""

import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk
import requests, threading, os, re, glob
import math, base64, datetime, random, json
import subprocess, sys, tempfile, io, urllib.parse, html, time
from pathlib import Path
from PIL import Image, ImageTk

# ── Farben & Konfiguration ────────────────────────────────────────────────────
OLLAMA_URL      = "http://127.0.0.1:11434"
LEARN_FOLDER    = "lern_daten"
CODE_FOLDER     = "lern_code"
OBSIDIAN_FOLDER = "obsidian_export"
FILES_FOLDER    = "erstellte_dateien"
CHATS_FOLDER    = "gespeicherte_chats"
MEMORY_FILE     = "geist_gedaechtnis.json"
APIS_FILE       = "geist_apis.json"
PROFILES_FILE   = "geist_profile.json"
TODOS_FILE      = "geist_todos.json"
BOTS_FILE       = "geist_bots.json"

# ── Mixture of Experts — Agent-Netzwerk ──────────────────────────────────────
# PC 2 für Bilder (llava) — passe die IP an
AGENT_NODES = {
    "local": {
        "url":   "http://127.0.0.1:11434",
        "name":  "Lokaler PC",
        "icon":  "🖥",
        "role":  ["chat","code","general"],
        "online": False,
    },
    "vision": {
        "url":   "http://192.168.1.101:11434",   # ← PC 2 IP hier
        "name":  "PC 2 (Vision)",
        "icon":  "👁",
        "role":  ["vision","image","describe"],
        "online": False,
    },
}

# Expert-Routing: welche Aufgabe → welcher Agent + Modell
EXPERT_ROUTES = {
    # (task_type, preferred_node, preferred_model)
    "vision":   ("vision",  "llava"),
    "code":     ("local",   "qwen2.5-coder:latest"),
    "chat":     ("local",   "qwen2.5:latest"),
    "analysis": ("local",   "qwen2.5:latest"),
    "crypto":   ("local",   "qwen2.5:latest"),
    "search":   ("local",   "qwen2.5:latest"),
}

CODE_EXTENSIONS = {
    ".py":"Python",".c":"C",".cpp":"C++",".cs":"C#",".java":"Java",
    ".js":"JavaScript",".ts":"TypeScript",".go":"Go",".rs":"Rust",
    ".html":"HTML",".css":"CSS",".sql":"SQL",".sh":"Bash",
    ".php":"PHP",".rb":"Ruby",".swift":"Swift",".kt":"Kotlin",
    ".lua":"Lua",".r":"R",".m":"MATLAB",".asm":"Assembly"
}
AI_NAME         = "Ghostfish"

ACCENT   = "#a78bfa"
ACCENT2  = "#7c3aed"
BG_DARK  = "#0d0d14"
BG_MID   = "#13131f"
BG_CARD  = "#1a1a2e"
BG_INPUT = "#1e1e30"
BG_SEL   = "#2a1f4a"
TEXT_DIM = "#6b6b8a"
GREEN    = "#4ade80"
RED      = "#f87171"
BLUE     = "#60a5fa"

THEMES = {
    "🌙 Lila Nacht": {
        "ACCENT":"#a78bfa","ACCENT2":"#7c3aed","BG_DARK":"#0d0d14",
        "BG_MID":"#13131f","BG_CARD":"#1a1a2e","BG_INPUT":"#1e1e30",
        "BG_SEL":"#2a1f4a","TEXT_DIM":"#6b6b8a","GREEN":"#4ade80","RED":"#f87171","BLUE":"#60a5fa"
    },
    "🌊 Ocean": {
        "ACCENT":"#67e8f9","ACCENT2":"#0891b2","BG_DARK":"#042330",
        "BG_MID":"#0a2d3d","BG_CARD":"#0f3d52","BG_INPUT":"#143d52",
        "BG_SEL":"#1a5068","TEXT_DIM":"#4a8fa8","GREEN":"#4ade80","RED":"#f87171","BLUE":"#93c5fd"
    },
    "🌲 Forest": {
        "ACCENT":"#86efac","ACCENT2":"#16a34a","BG_DARK":"#0a1a0f",
        "BG_MID":"#0f2318","BG_CARD":"#142e1e","BG_INPUT":"#183625",
        "BG_SEL":"#1f4a2f","TEXT_DIM":"#4a7a5a","GREEN":"#4ade80","RED":"#f87171","BLUE":"#60a5fa"
    },
    "🔥 Ember": {
        "ACCENT":"#fca5a5","ACCENT2":"#dc2626","BG_DARK":"#1a0a0a",
        "BG_MID":"#220f0f","BG_CARD":"#2d1515","BG_INPUT":"#321818",
        "BG_SEL":"#4a1f1f","TEXT_DIM":"#7a4a4a","GREEN":"#4ade80","RED":"#f87171","BLUE":"#60a5fa"
    },
    "⚪ Hell": {
        "ACCENT":"#7c3aed","ACCENT2":"#5b21b6","BG_DARK":"#f8f8ff",
        "BG_MID":"#efeffa","BG_CARD":"#e8e8f5","BG_INPUT":"#e0e0f0",
        "BG_SEL":"#d0d0ee","TEXT_DIM":"#8888aa","GREEN":"#16a34a","RED":"#dc2626","BLUE":"#2563eb"
    },
}

# Syntax-Highlighting Farben
SYNTAX = {
    "keyword":  "#c084fc",  # lila
    "string":   "#86efac",  # grün
    "comment":  "#4a5568",  # grau
    "number":   "#fbbf24",  # gelb
    "function": "#60a5fa",  # blau
    "builtin":  "#f87171",  # rot
}

# Keywords pro Sprache
KEYWORDS = {
    "python": {"keyword": ["def","class","if","else","elif","for","while","import","from",
                           "return","try","except","with","as","in","not","and","or","is",
                           "None","True","False","pass","break","continue","raise","yield",
                           "async","await","lambda","del","global","nonlocal"],
               "builtin": ["print","len","range","list","dict","set","tuple","str","int",
                           "float","bool","open","type","isinstance","super","self"]},
    "javascript": {"keyword": ["const","let","var","function","return","if","else","for",
                               "while","class","import","export","from","async","await",
                               "try","catch","new","this","typeof","null","undefined","true","false"],
                   "builtin": ["console","document","window","Math","Array","Object","JSON",
                               "Promise","fetch","setTimeout","setInterval"]},
    "c": {"keyword": ["int","char","float","double","void","if","else","for","while",
                      "return","struct","typedef","include","define","printf","scanf",
                      "break","continue","switch","case","default","const","static"],
          "builtin": ["printf","scanf","malloc","free","sizeof","NULL","EOF"]},
}

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

for f in [LEARN_FOLDER, CODE_FOLDER, OBSIDIAN_FOLDER, FILES_FOLDER, CHATS_FOLDER]:
    Path(f).mkdir(exist_ok=True)

ex = Path(LEARN_FOLDER) / "beispiel.txt"
if not ex.exists():
    ex.write_text("hey wie gehts\nalles gut danke!\njoa passt haha\n", encoding="utf-8")

SYSTEM_BASE = """You are Ghostfish — an honest, warm friend. Not a robot.

═══ MOST IMPORTANT RULE ═══
Never make things up. If you don't know → say "I don't know" or "not sure about that"
Short and honest beats long and invented.

═══ HOW YOU WRITE ═══
- Mirror exactly how the person writes — short, direct, their words
- If they write dialect or slang → write the same way
- Max 2-3 short sentences. Like WhatsApp.
- No bullet points, no headers except for code

═══ LANGUAGE ═══
Reply in the SAME language the person uses.
- German → reply German
- English → reply English
- Oskovian → reply in Oskovian (see dictionary below)
- Mixed → match the mix

═══ WHEN SOMEONE IS SAD ═══
- Listen first, don't jump to advice
- Short, honest: "hey that sounds rough :/"
- One question max

═══ ABSOLUTELY FORBIDDEN ═══
- NEVER randomly write code when not asked
- NEVER more than 3 sentences for emotional topics
- NEVER invent facts or guess without saying so
- NEVER say "I have developed a method..."

═══ ONLY WHEN CODE IS REQUESTED ═══
DATEI_START
dateiname: example.py
inhalt:
(complete code here)
DATEI_ENDE
Types: .c .py .js .ts .html .css .txt .md .java .cpp .cs .rs .go .sql .sh"""

# ── Oskovian Sprach-Dictionary ────────────────────────────────────────────────
OSKOVIAN_DICT = """
═══ OSKOVIAN LANGUAGE DICTIONARY ═══

GRAMMAR RULES:
- No masculine/feminine — gender neutral always
- Words used in original form only (no conjugation changes)
- No non-binary — people defined by birth gender
- Add ß after animal sound verbs: Meow meowß (the cat meows)
- Timing markers: Pres=present, Preßle=past, Preßeles=future

LOGIC OPERATORS:
! = Negative of next word
& = Positive of next word
% = Or
Und = And

PRONOUNS:
a = I        am = I'm
o = You      ore = Your/You're
d = They     dre = They're
an = A

MATERIALS:     Wood=jßao  Glass=jßau  Metal=jßaou  Plastic=jßaol
               Rubber=jßaoa  Stone=jßaoul  Paper=jßaq

VEHICLES:      Car=hßou  Truck=hßol  Van=hßo  Family Car=hßo-Kombisvagon-Tßo-Sßo
               Tank=hßo-Tank  Missile Truck=Missile-hßol

STRUCTURES:    House=Sßol  Roof=Sßo  Floor=Sßu  Wall=Sßole

DIRECTIONS:    High=Tßoul  Low=Tßol  Up=Tßo  Down=Tßu
               Left=Tßa  Right=Tßop  Big=Tßoual  Small=!Tßoual

COMMON VERBS:  Speak=Shaß  Eat=Draß  Drink=!Draß  Sleep=Doneß  Awake=!Doneß
               Play=Play  Work=!Play  Need=Slauß  Want=Slauße  Have=Haß
               Do=Doß  Will=Will

BASIC WORDS:   Hello=Hello  Good=Gooß  Name=Name  Very=Vehr
               Something=Sloßel  Someone=Sloßeleß  Anything=Aße  Anyone=Aßeleß
               If=Ife  Else=Elße  Then=Thene  Because=Predre  So=So  Done=Donß

TIME:          Morning=Morgen  Night=!Morgen  Evening=Evening
               Sunrise=Sunrise  Sunset=!Sunrise

ANIMALS (sound+ß):  Cat=Meow meowß  Dog=Woof woofß  Horse=Neigh neighß  Mouse=Squeak squeakß

EXAMPLE SENTENCES:
  "Hello! am Gooß" = Hello! I'm good
  "o Haß Sloßel Gooß?" = You have something good?
  "a Slauß Draß" = I need to eat
  "Meow meowß Pres" = The cat meows (present)
  "am !Doneß Preßle" = I was awake (past)
"""




# ══════════════════════════════════════════════════════════════════════════════
#  Ghostfish Canvas  — animierter Pufferfisch
# ══════════════════════════════════════════════════════════════════════════════
class GhostCanvas(tk.Canvas):
    IDLE="idle"; THINK="think"; HAPPY="happy"; TALK="talk"

    def __init__(self, master, size=110, **kw):
        super().__init__(master, width=size, height=size,
                         bg=BG_MID, highlightthickness=0, **kw)
        self.size       = size
        self.state      = self.IDLE
        self._t         = 0.0
        self._blink     = 0
        self._running   = True
        self._particles = []
        self._animate()

    def set_state(self, s):
        self.state = s
        if s == self.HAPPY:
            self._spawn()

    def _spawn(self):
        import math as m
        cx,cy = self.size/2, self.size/2
        for _ in range(16):
            a  = random.uniform(0, 2*m.pi)
            sp = random.uniform(1.5, 3.5)
            self._particles.append([cx,cy,m.cos(a)*sp,m.sin(a)*sp-1.5,0,random.randint(18,30)])

    def _animate(self):
        if not self._running: return
        self._t    += 0.05
        self._blink = (self._blink+1) % 90
        self.delete("all")
        self._draw()
        self.after(40, self._animate)

    def _draw(self):
        import math as m
        s,cx,t = self.size, self.size/2, self._t

        if   self.state==self.HAPPY: bob=m.sin(t*4)*6;  scale=1+m.sin(t*4)*0.05
        elif self.state==self.THINK: bob=m.sin(t*1.5)*3; scale=1.0
        elif self.state==self.TALK:  bob=m.sin(t*7)*2;  scale=1.0
        else:                        bob=m.sin(t)*4;    scale=1.0

        cy = s/2 + bob
        R  = int(s*0.30 * scale)   # body radius

        # Shadow
        self.create_oval(cx-R*0.7,cy+R-2,cx+R*0.7,cy+R+5,fill="#0a0a1a",outline="")

        # ── Grey fins (behind body) ──
        # Left fin - big oval
        self.create_oval(cx-R*2.1, cy-R*0.55,
                         cx-R*0.4, cy+R*0.55,
                         fill="#777777", outline="#111111", width=1.5)
        # Right fin
        self.create_oval(cx+R*0.4,  cy-R*0.55,
                         cx+R*2.1,  cy+R*0.55,
                         fill="#777777", outline="#111111", width=1.5)

        # ── Spikes all around ──
        spike_angles = [i*22.5 for i in range(16)]
        inner = R + 1
        outer = R + int(R*0.32)
        for angle_deg in spike_angles:
            ang = m.radians(angle_deg)
            # spike base: two points slightly offset
            off = m.radians(7)
            x1 = cx + inner*m.cos(ang-off);  y1 = cy + inner*m.sin(ang-off)
            x2 = cx + outer*m.cos(ang);      y2 = cy + outer*m.sin(ang)
            x3 = cx + inner*m.cos(ang+off);  y3 = cy + inner*m.sin(ang+off)
            self.create_polygon(x1,y1,x2,y2,x3,y3,
                               fill="#ffffff",outline="#111111",width=1.5)

        # ── Main body circle ──
        self.create_oval(cx-R,cy-R,cx+R,cy+R,
                        fill="#ffffff",outline="#111111",width=2)

        # ── Belly lines (short vertical ticks) ──
        tick_y = cy + R*0.52
        for i in range(-3,4):
            tx = cx + i*(R*0.18)
            self.create_line(tx, tick_y, tx, tick_y+R*0.2,
                           fill="#cccccc",width=1.5,capstyle="round")
        for i in range(-2,3):
            tx = cx + i*(R*0.2)
            self.create_line(tx, tick_y+R*0.22, tx, tick_y+R*0.4,
                           fill="#cccccc",width=1.5,capstyle="round")

        # ── Eyes ──
        blink = self._blink not in range(2,5)
        er    = int(R*0.38)   # eye radius
        ex_off= int(R*0.44)   # eye x offset

        for sign in [-1,1]:
            ex = int(cx + sign*ex_off)
            ey = int(cy - R*0.08)
            # white
            self.create_oval(ex-er,ey-er,ex+er,ey+er,fill="#ffffff",outline="#111111",width=1.5)
            if blink:
                # pupil
                self.create_oval(ex-int(er*0.7),ey-int(er*0.6)+3,
                                ex+int(er*0.7),ey+int(er*0.8)+3,
                                fill="#111111",outline="")
                # shine
                self.create_oval(ex-int(er*0.38),ey-int(er*0.42),
                                ex+int(er*0.1), ey+int(er*0.1),
                                fill="#ffffff",outline="")
            else:
                # closed eye line
                self.create_line(ex-er+3,ey,ex+er-3,ey,fill="#111111",width=2,capstyle="round")

        # ── Smile ──
        smile_r = int(R*0.5)
        if self.state==self.HAPPY:
            self.create_arc(cx-smile_r,cy+R*0.18,cx+smile_r,cy+R*0.62,
                           start=200,extent=140,style="arc",outline="#111111",width=2)
        elif self.state==self.TALK:
            oh = int(abs(m.sin(t*6))*R*0.15+3)
            self.create_oval(cx-oh,cy+R*0.28-oh//2,cx+oh,cy+R*0.28+oh,
                           fill="#111111",outline="#111111")
        else:
            self.create_arc(cx-smile_r,cy+R*0.2,cx+smile_r,cy+R*0.58,
                           start=205,extent=130,style="arc",outline="#111111",width=2)

        # ── Think bubbles ──
        if self.state==self.THINK:
            for br,bx,by in [(3,18,-38),(5,26,-50),(7,32,-62)]:
                self.create_oval(cx+bx-br,cy+by-br,cx+bx+br,cy+by+br,
                               fill=ACCENT2,outline=ACCENT,width=1)

        # ── Happy glow ring ──
        if self.state==self.HAPPY:
            gr = 4+m.sin(t*4)*2
            self.create_oval(cx-gr,cy-gr,cx+gr,cy+gr,
                           fill="",outline="#4ade80",width=gr)

        # ── Particles ──
        alive=[]
        for p in self._particles:
            p[0]+=p[2];p[1]+=p[3];p[3]+=0.18;p[4]+=1
            if p[4]<p[5]:
                pr=max(1,int(5*(1-p[4]/p[5])))
                col=["#4ade80","#a78bfa","#60a5fa","#fbbf24"][int(p[4])%4]
                self.create_oval(p[0]-pr,p[1]-pr,p[0]+pr,p[1]+pr,fill=col,outline="")
                alive.append(p)
        self._particles=alive

    def destroy(self):
        self._running=False
        super().destroy()

class ChatEntry:
    def __init__(self, title, history, created=None, path=None):
        self.title   = title
        self.history = history  # list of {"role":..., "content":...}
        self.created = created or datetime.datetime.now()
        self.path    = path     # JSON-Datei Pfad

    def save(self):
        if not self.path:
            safe = re.sub(r'[^\w\- ]', '', self.title)[:40].strip()
            ts   = self.created.strftime("%Y%m%d_%H%M%S")
            self.path = str(Path(CHATS_FOLDER) / f"{ts}_{safe}.json")
        data = {
            "title":   self.title,
            "created": self.created.isoformat(),
            "history": self.history
        }
        Path(self.path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    @staticmethod
    def load(path):
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return ChatEntry(
            title   = data["title"],
            history = data["history"],
            created = datetime.datetime.fromisoformat(data["created"]),
            path    = path
        )



# ══════════════════════════════════════════════════════════════════════════════
#  API-Manager  (alle optionalen Keys)
# ══════════════════════════════════════════════════════════════════════════════
class ApiManager:
    SERVICES = {
        "elevenlabs": {
            "name": "ElevenLabs",
            "desc": "Text-to-Speech — Ghostfish can speak",
            "url":  "https://elevenlabs.io",
            "icon": "🔊"
        },
        "anthropic": {
            "name": "Anthropic (Claude)",
            "desc": "Claude als zusätzliches KI-Modell",
            "url":  "https://console.anthropic.com",
            "icon": "🤖"
        },
        "gemini": {
            "name": "Google Gemini",
            "desc": "Gemini als zusätzliches KI-Modell",
            "url":  "https://aistudio.google.com",
            "icon": "✨"
        },
        "openai": {
            "name": "OpenAI (ChatGPT)",
            "desc": "GPT-4 als zusätzliches KI-Modell",
            "url":  "https://platform.openai.com",
            "icon": "🟢"
        },
        "youtube": {
            "name": "YouTube Data API",
            "desc": "Video-Infos & Transkripte laden",
            "url":  "https://console.cloud.google.com",
            "icon": "▶️"
        },
        "wikipedia": {
            "name": "Wikipedia",
            "desc": "Kein Key nötig — immer verfügbar",
            "url":  "https://wikipedia.org",
            "icon": "📖",
            "no_key": True
        },
    }

    def __init__(self):
        self.path = Path(APIS_FILE)
        self.keys = self._load()

    def _load(self):
        if self.path.exists():
            try:
                return json.loads(self.path.read_text(encoding="utf-8"))
            except: pass
        return {}

    def save(self):
        self.path.write_text(
            json.dumps(self.keys, ensure_ascii=False, indent=2), encoding="utf-8")

    def get(self, service):
        return self.keys.get(service, "").strip()

    def set(self, service, key):
        self.keys[service] = key.strip()
        self.save()

    def has(self, service):
        info = self.SERVICES.get(service, {})
        if info.get("no_key"): return True
        return bool(self.get(service))


# ══════════════════════════════════════════════════════════════════════════════
#  Profile-System
# ══════════════════════════════════════════════════════════════════════════════
class ProfileManager:
    DEFAULT_PROFILES = {
        "🤝 Freund": {
            "system": "You are Ghostfish — ein warmer, empathischer Freund. Kurz, direkt, aufmunternd.",
            "temp": 0.88, "model_hint": ""
        },
        "💻 Code-Experte": {
            "system": ("Du bist ein erfahrener Software-Entwickler. "
                       "Schreibe sauberen, kommentierten, professionellen Code. "
                       "Erkläre technische Konzepte präzise. Nutze Best Practices."),
            "temp": 0.3, "model_hint": "codellama"
        },
        "📚 Lehrer": {
            "system": ("Du bist ein geduldiger, freundlicher Lehrer. "
                       "Erkläre Konzepte Schritt für Schritt, nutze Beispiele und Analogien. "
                       "Stelle sicher dass alles verstanden wird."),
            "temp": 0.7, "model_hint": ""
        },
        "🎨 Kreativ": {
            "system": ("Du bist ein kreativer Autor und Ideengeber. "
                       "Denke außerhalb der Box, schlage ungewöhnliche Ideen vor, "
                       "sei inspirierend und fantasievoll."),
            "temp": 0.95, "model_hint": ""
        },
        "🔬 Analyst": {
            "system": ("Du bist ein präziser Analyst. Antworte sachlich, strukturiert, "
                       "mit Fakten und Quellen. Keine Meinungen ohne Belege. "
                       "Nutze Listen und klare Strukturen."),
            "temp": 0.2, "model_hint": ""
        },
    }

    def __init__(self):
        self.path = Path(PROFILES_FILE)
        self.profiles = self._load()
        self.active = "🤝 Freund"

    def _load(self):
        if self.path.exists():
            try:
                return json.loads(self.path.read_text(encoding="utf-8"))
            except: pass
        return dict(self.DEFAULT_PROFILES)

    def save(self):
        self.path.write_text(
            json.dumps(self.profiles, ensure_ascii=False, indent=2), encoding="utf-8")

    def get_system(self):
        return self.profiles.get(self.active, {}).get("system", "")

    def get_temp(self):
        return self.profiles.get(self.active, {}).get("temp", 0.88)


# ══════════════════════════════════════════════════════════════════════════════
#  TODO-System
# ══════════════════════════════════════════════════════════════════════════════
class TodoManager:
    def __init__(self):
        self.path = Path(TODOS_FILE)
        self.todos = self._load()

    def _load(self):
        if self.path.exists():
            try:
                return json.loads(self.path.read_text(encoding="utf-8"))
            except: pass
        return []

    def save(self):
        self.path.write_text(
            json.dumps(self.todos, ensure_ascii=False, indent=2), encoding="utf-8")

    def add(self, text, due=None):
        self.todos.append({
            "id": len(self.todos)+1, "text": text,
            "done": False, "created": datetime.datetime.now().isoformat(),
            "due": due
        })
        self.save()

    def done(self, idx):
        if 0 <= idx < len(self.todos):
            self.todos[idx]["done"] = True
            self.save()
            return True
        return False

    def delete(self, idx):
        if 0 <= idx < len(self.todos):
            self.todos.pop(idx)
            self.save()
            return True
        return False

    def pending(self):
        return [t for t in self.todos if not t["done"]]

    def format_list(self):
        if not self.todos:
            return "Keine TODOs. Hinzufügen mit /todo <aufgabe>"
        lines = []
        for i, t in enumerate(self.todos):
            check = "✅" if t["done"] else "⬜"
            due   = f"  📅 {t['due']}" if t.get("due") else ""
            lines.append(f"  {check}  [{i+1}]  {t['text']}{due}")
        return "\n".join(lines)


class Memory:
    """Persistentes Gedächtnis zwischen Sitzungen."""
    def __init__(self):
        self.path = Path(MEMORY_FILE)
        self.data = self._load()

    def _load(self):
        if self.path.exists():
            try:
                return json.loads(self.path.read_text(encoding="utf-8"))
            except: pass
        return {"name":"","facts":[],"preferences":{},"topics":[],"session_count":0}

    def save(self):
        self.path.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8")

    def remember(self, key, value):
        self.data["preferences"][key] = value
        self.save()

    def add_fact(self, fact):
        if fact not in self.data["facts"]:
            self.data["facts"].append(fact)
            if len(self.data["facts"]) > 50:
                self.data["facts"] = self.data["facts"][-50:]
            self.save()

    def extract_facts(self, text):
        """Extrahiert Fakten aus Nutzernachrichten automatisch."""
        patterns = [
            (r"ich hei[ßs]e\s+(\w+)", "name"),
            (r"mein name ist\s+(\w+)", "name"),
            (r"ich bin\s+(\d+)\s*jahre?", "age"),
            (r"ich arbeite\s+(?:als|bei)\s+(.+?)(?:\.|$)", "job"),
            (r"ich mag\s+(.+?)(?:\.|$)", "likes"),
            (r"ich lerne?\s+(.+?)(?:\.|$)", "learning"),
            (r"mein lieblings\w+\s+ist\s+(.+?)(?:\.|$)", "favorite"),
            (r"ich wohne\s+(?:in|bei)\s+(.+?)(?:\.|$)", "location"),
        ]
        for pattern, key in patterns:
            m = re.search(pattern, text.lower())
            if m:
                val = m.group(1).strip()
                if key == "name":
                    self.data["name"] = val.capitalize()
                self.add_fact(f"{key}: {val}")

    def to_prompt(self):
        """Gedächtnis als System-Prompt-Zusatz."""
        if not any([self.data["name"], self.data["facts"]]):
            return ""
        lines = ["\n═══ DEIN GEDÄCHTNIS ÜBER DIESEN NUTZER ═══"]
        if self.data["name"]:
            lines.append(f"Name: {self.data['name']}")
        if self.data["facts"]:
            lines.append("Bekannte Fakten:")
            for f in self.data["facts"][-15:]:
                lines.append(f"  • {f}")
        lines.append(f"Sitzungen bisher: {self.data['session_count']}")
        lines.append("Nutze dieses Wissen natürlich in der Unterhaltung.")
        return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════════════
#  Mixture of Experts — Agent Router
# ══════════════════════════════════════════════════════════════════════════════
class MoERouter:
    """Leitet Anfragen automatisch an den besten Agent + Modell weiter."""

    # Keywords → Aufgaben-Typ erkennen
    TASK_KEYWORDS = {
        "vision":   ["bild","foto","image","picture","screenshot","siehst","beschreib das","was ist auf"],
        "code":     ["code","programm","skript","script","funktion","klasse","python","javascript",
                     "def ","class ","bug","error","fehler im code","schreib mir ein"],
        "analysis": ["analysiere","zusammenfassung","erkläre","vergleich","research"],
        "search":   ["such","news","aktuell","heute","preis","wetter","current","latest"],
        "crypto":   ["bitcoin","ethereum","crypto","btc","eth","sol","kurs","coin"],
    }

    def __init__(self):
        self.nodes   = {k: dict(v) for k, v in AGENT_NODES.items()}
        self.routes  = dict(EXPERT_ROUTES)
        self._status_callbacks = []
        self._check_all()

    # ── Node-Status ───────────────────────────────────────────────────────────
    def _check_all(self):
        for node_id in self.nodes:
            threading.Thread(target=self._check_node,
                             args=(node_id,), daemon=True).start()

    def _check_node(self, node_id):
        node = self.nodes[node_id]
        try:
            r = requests.get(f"{node['url']}/api/tags", timeout=4)
            models = [m["name"] for m in r.json().get("models", [])]
            node["online"]  = True
            node["models"]  = models
        except Exception:
            node["online"] = False
            node["models"] = []
        for cb in self._status_callbacks:
            try: cb()
            except: pass

    def check_all_async(self):
        self._check_all()

    def on_status_change(self, cb):
        self._status_callbacks.append(cb)

    # ── Aufgabe erkennen ──────────────────────────────────────────────────────
    def detect_task(self, text: str, has_image: bool) -> str:
        if has_image:
            return "vision"
        text_low = text.lower()
        for task, keywords in self.TASK_KEYWORDS.items():
            if any(kw in text_low for kw in keywords):
                return task
        return "chat"

    # ── Besten Agent + Modell wählen ──────────────────────────────────────────
    def route(self, task: str, force_node: str = None, force_model: str = None):
        """
        Gibt (url, model, node_name, node_icon) zurück.
        Fallback auf lokalen Node wenn bevorzugter offline.
        """
        preferred_node, preferred_model = self.routes.get(task, ("local", "qwen2.5:latest"))

        if force_node and force_node in self.nodes:
            preferred_node = force_node
        if force_model:
            preferred_model = force_model

        node = self.nodes.get(preferred_node, self.nodes["local"])

        # Fallback: wenn bevorzugter Node offline → lokalen nehmen
        if not node["online"]:
            node = self.nodes["local"]
            preferred_node = "local"

        # Modell-Fallback: wenn Modell nicht installiert → erstes verfügbares
        models = node.get("models", [])
        if preferred_model not in models and models:
            # Versuche ähnliches Modell zu finden
            similar = next(
                (m for m in models if preferred_model.split(":")[0] in m),
                models[0])
            preferred_model = similar

        return (node["url"], preferred_model,
                node["name"], node["icon"], preferred_node)

    # ── Netzwerk-Status als String ────────────────────────────────────────────
    def status_summary(self) -> str:
        parts = []
        for nid, node in self.nodes.items():
            icon   = node["icon"]
            name   = node["name"]
            status = "●" if node["online"] else "○"
            col    = "online" if node["online"] else "offline"
            models = len(node.get("models", []))
            parts.append(f"{status} {icon} {name}  ({models} Modelle)")
        return "\n".join(parts)

    # ── Einstellungen ändern ──────────────────────────────────────────────────
    def set_node_url(self, node_id: str, url: str):
        if node_id in self.nodes:
            self.nodes[node_id]["url"] = url.strip().rstrip("/")
            threading.Thread(target=self._check_node,
                             args=(node_id,), daemon=True).start()

    def set_route(self, task: str, node_id: str, model: str):
        self.routes[task] = (node_id, model)


# ══════════════════════════════════════════════════════════════════════════════
#  Bot-Manager
# ══════════════════════════════════════════════════════════════════════════════
class BotManager:
    def __init__(self):
        self.path = Path(BOTS_FILE)
        self.bots = self._load()
        self._timers = {}

    def _load(self):
        if self.path.exists():
            try: return json.loads(self.path.read_text(encoding="utf-8"))
            except: pass
        return []

    def save(self):
        self.path.write_text(
            json.dumps(self.bots, ensure_ascii=False, indent=2), encoding="utf-8")

    def add(self, name, desc, system, search_kw="", interval=0):
        bot = {"id": int(time.time()*1000), "name": name, "desc": desc,
               "system": system, "search_kw": search_kw,
               "interval": interval, "running": False, "created": datetime.datetime.now().isoformat()}
        self.bots.append(bot)
        self.save()
        return bot

    def delete(self, bot_id):
        self.stop_timer(bot_id)
        self.bots = [b for b in self.bots if b["id"] != bot_id]
        self.save()

    def stop_timer(self, bot_id):
        t = self._timers.pop(bot_id, None)
        if t: t.cancel()

    def start_timer(self, bot_id, callback, interval_min):
        self.stop_timer(bot_id)
        def _tick():
            callback(bot_id)
            t = threading.Timer(interval_min * 60, _tick)
            t.daemon = True
            self._timers[bot_id] = t
            t.start()
        t = threading.Timer(interval_min * 60, _tick)
        t.daemon = True
        self._timers[bot_id] = t
        t.start()


# ══════════════════════════════════════════════════════════════════════════════
#  Crypto-Guesser  (holt echte Preise + KI-Analyse)
# ══════════════════════════════════════════════════════════════════════════════

class CryptoWindow(ctk.CTkToplevel):
    """Professional Crypto Dashboard — Live Preise, Chart, KI-Signal, Selbstlernen."""

    COINS = [
        ("Bitcoin",    "bitcoin",          "BTC",  "₿",  "#f7931a"),
        ("Ethereum",   "ethereum",         "ETH",  "Ξ",  "#627eea"),
        ("Solana",     "solana",           "SOL",  "◎",  "#9945ff"),
        ("BNB",        "binancecoin",      "BNB",  "B",  "#f3ba2f"),
        ("XRP",        "ripple",           "XRP",  "✕",  "#00aae4"),
        ("Cardano",    "cardano",          "ADA",  "₳",  "#0033ad"),
        ("Dogecoin",   "dogecoin",         "DOGE", "Ð",  "#c2a633"),
        ("Avalanche",  "avalanche-2",      "AVAX", "A",  "#e84142"),
        ("Chainlink",  "chainlink",        "LINK", "⬡",  "#375bd2"),
        ("Polkadot",   "polkadot",         "DOT",  "●",  "#e6007a"),
        ("Litecoin",   "litecoin",         "LTC",  "Ł",  "#bfbbbb"),
        ("Shiba Inu",  "shiba-inu",        "SHIB", "🐕", "#ffa409"),
        ("Toncoin",    "the-open-network", "TON",  "💎", "#0088cc"),
        ("Near",       "near",             "NEAR", "N",  "#00c1de"),
        ("Sui",        "sui",              "SUI",  "S",  "#4da2ff"),
        ("Pepe",       "pepe",             "PEPE", "🐸", "#00b300"),
    ]
    LEARN_FILE = Path("geist_crypto_learn.json")

    # Risiko-Level Farben
    RISK_COLORS = {"LOW": "#4ade80", "MEDIUM": "#f59e0b", "HIGH": "#f87171", "VERY HIGH": "#ef4444"}
    SIGNAL_COLORS = {"BUY": "#4ade80", "HOLD": "#f59e0b", "SELL": "#f87171",
                     "WAIT": "#a78bfa", "...": "#6b6b8a"}

    def __init__(self, master, model_var, system_fn):
        super().__init__(master)
        self.title("🪙  Ghostfish Crypto")
        self.geometry("1280x800")
        self.minsize(1000, 640)
        self.configure(fg_color=BG_DARK)
        self.model_var    = model_var
        self.build_system = system_fn
        self._prices      = {}
        self._prev_prices = {}   # für Richtungspfeil
        self._history     = {}   # cid -> [(ts, price)]
        self._news_cache  = {}
        self._learned     = self._load_learned()
        self._auto_id     = None
        self._sel_coin    = None
        self._analysis_running = False
        self._build()
        self._fetch_prices()
        self._start_auto()

    # ══ Persistentes Lernen ══════════════════════════════════════════════════
    def _load_learned(self):
        if self.LEARN_FILE.exists():
            try: return json.loads(self.LEARN_FILE.read_text(encoding="utf-8"))
            except: pass
        return {"predictions": [], "accuracy_history": [], "error_patterns": [],
                "session_stats": {"correct": 0, "wrong": 0, "total": 0}}

    def _save_learned(self):
        self.LEARN_FILE.write_text(
            json.dumps(self._learned, ensure_ascii=False, indent=2), encoding="utf-8")

    def _record_prediction(self, sym, price, signal, direction, confidence, reasoning):
        self._learned["predictions"].append({
            "sym": sym, "price_at": price, "signal": signal,
            "direction": direction, "confidence": confidence,
            "reasoning": reasoning[:200], "date": datetime.datetime.now().isoformat(),
            "checked": False, "correct": None, "price_after": None
        })
        self._learned["predictions"] = self._learned["predictions"][-500:]
        self._save_learned()

    def _verify_predictions(self):
        """Vergleicht vergangene Vorhersagen — lernt aus Fehlern."""
        changed = False
        for p in self._learned["predictions"]:
            if p.get("checked"): continue
            cid = next((c[1] for c in self.COINS if c[2]==p["sym"]), None)
            if not cid: continue
            cur = self._prices.get(cid, {}).get("usd", 0)
            if not cur: continue

            old_price = p["price_at"]
            pred_up   = p["direction"] == "UP"
            actual_up = cur > old_price
            correct   = pred_up == actual_up
            pct_change = (cur - old_price) / old_price * 100

            p["checked"]    = True
            p["correct"]    = correct
            p["price_after"]= cur
            p["pct_change"] = round(pct_change, 2)

            s = self._learned["session_stats"]
            s["total"] += 1
            if correct: s["correct"] += 1
            else:
                s["wrong"] += 1
                # Fehler-Muster speichern zum Lernen
                self._learned["error_patterns"].append({
                    "sym": p["sym"], "signal": p["signal"],
                    "date": p["date"], "pct_change": pct_change,
                    "was_wrong_about": "UP" if not correct else "DOWN"
                })
                self._learned["error_patterns"] = self._learned["error_patterns"][-50:]

            changed = True

        if changed:
            s = self._learned["session_stats"]
            if s["total"] > 0:
                acc = round(s["correct"] / s["total"] * 100, 1)
                self._learned["accuracy_history"].append({
                    "date": datetime.datetime.now().isoformat(),
                    "accuracy": acc, "total": s["total"]
                })
            self._save_learned()
            return True
        return False

    def _get_accuracy_str(self):
        s = self._learned["session_stats"]
        if s["total"] == 0: return "Noch keine Vorhersagen gecheckt"
        acc = round(s["correct"] / s["total"] * 100, 1)
        return f"Genauigkeit: {acc}%  ({s['correct']}✓/{s['wrong']}✗ von {s['total']})"

    def _get_error_context(self):
        """Gibt Fehler-Muster als Kontext für KI zurück."""
        errs = self._learned.get("error_patterns", [])
        if not errs: return ""
        recent = errs[-5:]
        lines = ["Meine letzten Fehler (lerne davon!):"]
        for e in recent:
            lines.append(f"  - {e['sym']}: Signal '{e['signal']}' war falsch, "
                        f"Preis ging {e['pct_change']:+.1f}%")
        return "\n".join(lines)

    # ══ UI ══════════════════════════════════════════════════════════════════
    def _build(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ── Topbar ──────────────────────────────────────────────────────────
        top = ctk.CTkFrame(self, fg_color=BG_MID, corner_radius=0, height=52)
        top.grid(row=0, column=0, columnspan=2, sticky="ew")
        top.grid_propagate(False)
        top.grid_columnconfigure(2, weight=1)

        ctk.CTkLabel(top, text="🪙  CRYPTO PRO",
                     font=ctk.CTkFont("Helvetica",16,"bold"),
                     text_color=ACCENT).grid(row=0,column=0,padx=14,sticky="w")

        self.status_lbl = ctk.CTkLabel(top, text="Verbinde...",
                                        font=ctk.CTkFont(size=10), text_color=TEXT_DIM)
        self.status_lbl.grid(row=0,column=1,padx=8,sticky="w")

        self.acc_lbl = ctk.CTkLabel(top, text="",
                                     font=ctk.CTkFont(size=10), text_color=GREEN)
        self.acc_lbl.grid(row=0,column=2,padx=4,sticky="w")

        self.auto_var = ctk.BooleanVar(value=True)
        ctk.CTkSwitch(top, text="Auto", variable=self.auto_var,
                      font=ctk.CTkFont(size=10), width=80,
                      fg_color=BG_CARD, progress_color=ACCENT2
                      ).grid(row=0,column=3,padx=6)

        self.interval_var = ctk.StringVar(value="30s")
        ctk.CTkOptionMenu(top, variable=self.interval_var,
                          values=["10s","30s","60s","5m"],
                          width=70, height=28,
                          fg_color=BG_CARD, button_color=ACCENT2,
                          button_hover_color=ACCENT,
                          font=ctk.CTkFont(size=10)
                          ).grid(row=0,column=4,padx=2)

        for txt, cmd, col in [
            ("🔄 Refresh", self._fetch_prices,  ACCENT2),
            ("📊 Alle analysieren", self._analyze_all, "transparent"),
            ("🧠 Gelernt", self._show_learned,  "transparent"),
        ]:
            ctk.CTkButton(top, text=txt, width=130 if "Alle" in txt else 90,
                          height=30, fg_color=col,
                          border_width=1 if col=="transparent" else 0,
                          border_color=ACCENT2, text_color="white" if col==ACCENT2 else ACCENT,
                          hover_color=ACCENT, command=cmd, font=ctk.CTkFont(size=11)
                          ).grid(row=0,column=5+[0,1,2][["🔄 Refresh","📊 Alle analysieren","🧠 Gelernt"].index(txt)],
                                 padx=3)
        ctk.CTkFrame(top,width=10,fg_color="transparent").grid(row=0,column=8)

        # ── Coin-Tabelle (links) ─────────────────────────────────────────────
        left = ctk.CTkFrame(self, width=340, fg_color=BG_MID, corner_radius=0)
        left.grid(row=1,column=0,sticky="nsew")
        left.grid_propagate(False)
        left.grid_rowconfigure(1,weight=1)
        left.grid_columnconfigure(0,weight=1)

        # Tabellen-Header
        hdr = ctk.CTkFrame(left, fg_color=BG_CARD, corner_radius=0, height=28)
        hdr.grid(row=0,column=0,sticky="ew")
        hdr.grid_propagate(False)
        for col_txt, x in [("Coin",10),("Preis",130),("24h",220),("Signal",270)]:
            tk.Label(hdr, text=col_txt, fg=TEXT_DIM, bg=BG_CARD,
                     font=("Helvetica",9,"bold")).place(x=x, y=4)

        self._coin_scroll = ctk.CTkScrollableFrame(
            left, fg_color="transparent", corner_radius=0)
        self._coin_scroll.grid(row=1,column=0,sticky="nsew")
        self._coin_scroll.grid_columnconfigure(0,weight=1)

        # ── Rechts: Detail ───────────────────────────────────────────────────
        right = ctk.CTkFrame(self, fg_color="transparent")
        right.grid(row=1,column=1,sticky="nsew",padx=10,pady=10)
        right.grid_rowconfigure(2,weight=1)
        right.grid_columnconfigure(0,weight=1)

        # Coin-Info Banner
        self._info_frame = ctk.CTkFrame(right, fg_color=BG_CARD,
                                         corner_radius=12, height=90)
        self._info_frame.grid(row=0,column=0,sticky="ew",pady=(0,8))
        self._info_frame.grid_propagate(False)
        self._info_frame.grid_columnconfigure(3,weight=1)
        self._price_big  = ctk.CTkLabel(self._info_frame, text="$—",
                                         font=ctk.CTkFont("Helvetica",28,"bold"),
                                         text_color="#e2e8f0")
        self._price_big.grid(row=0,column=0,rowspan=2,padx=20,pady=10)
        self._change_lbl = ctk.CTkLabel(self._info_frame, text="",
                                         font=ctk.CTkFont("Helvetica",16,"bold"),
                                         text_color=GREEN)
        self._change_lbl.grid(row=0,column=1,padx=8,sticky="sw")
        self._stats_lbl  = ctk.CTkLabel(self._info_frame, text="",
                                         font=ctk.CTkFont(size=11), text_color=TEXT_DIM,
                                         justify="left")
        self._stats_lbl.grid(row=1,column=1,padx=8,sticky="nw")
        self._signal_box = ctk.CTkFrame(self._info_frame, fg_color=BG_INPUT,
                                         corner_radius=10, width=160, height=70)
        self._signal_box.grid(row=0,column=2,rowspan=2,padx=12,pady=10)
        self._signal_box.grid_propagate(False)
        self._signal_lbl = ctk.CTkLabel(self._signal_box, text="—",
                                         font=ctk.CTkFont("Helvetica",15,"bold"),
                                         text_color=TEXT_DIM)
        self._signal_lbl.place(relx=0.5,rely=0.35,anchor="center")
        self._risk_lbl   = ctk.CTkLabel(self._signal_box, text="",
                                         font=ctk.CTkFont(size=10), text_color=TEXT_DIM)
        self._risk_lbl.place(relx=0.5,rely=0.72,anchor="center")

        # Chart Canvas
        self._chart_frame = ctk.CTkFrame(right, fg_color=BG_CARD,
                                          corner_radius=12, height=180)
        self._chart_frame.grid(row=1,column=0,sticky="ew",pady=(0,8))
        self._chart_frame.grid_propagate(False)
        self._chart_cv = tk.Canvas(self._chart_frame, bg=BG_CARD,
                                    highlightthickness=0, height=180)
        self._chart_cv.pack(fill="both",expand=True,padx=12,pady=8)

        # Tabs: Analyse / News / Gelernt / Portfolio
        self._tabs = ctk.CTkTabview(right, fg_color=BG_MID,
                                     segmented_button_fg_color=BG_CARD,
                                     segmented_button_selected_color=ACCENT2,
                                     segmented_button_selected_hover_color=ACCENT)
        self._tabs.grid(row=2,column=0,sticky="nsew")
        for t in ["🐟 Analyse","📰 News","🧠 Gelernt"]:
            self._tabs.add(t)

        def _tb(parent, font_size=12):
            tb = ctk.CTkTextbox(parent, font=ctk.CTkFont("Helvetica",font_size),
                                fg_color=BG_CARD, corner_radius=8,
                                wrap="word", state="disabled")
            tb.pack(fill="both",expand=True)
            return tb

        self.analysis_box = _tb(self._tabs.tab("🐟 Analyse"))
        self.news_box     = _tb(self._tabs.tab("📰 News"))
        self.learn_box    = _tb(self._tabs.tab("🧠 Gelernt"))
        self._write(self.analysis_box, "← Coin auswählen um KI-Signal + Kaufempfehlung zu sehen")
        self._refresh_learn_box()

    # ══ Preise laden ════════════════════════════════════════════════════════
    def _fetch_prices(self):
        self.status_lbl.configure(text="⏳ Lade...")
        threading.Thread(target=self._do_fetch, daemon=True).start()

    def _do_fetch(self):
        try:
            ids = ",".join(c[1] for c in self.COINS)
            r = requests.get(
                f"https://api.coingecko.com/api/v3/simple/price"
                f"?ids={ids}&vs_currencies=usd,eur,btc"
                f"&include_24hr_change=true&include_market_cap=true"
                f"&include_24hr_vol=true&include_7d_change=true"
                f"&include_last_updated_at=true",
                timeout=15, headers={"User-Agent":"Ghostfish/1.0"})
            r.raise_for_status()
            self._prev_prices = {k: v.get("usd",0) for k,v in self._prices.items()}
            self._prices = r.json()

            ts = time.time()
            for _,cid,sym,_,_ in self.COINS:
                p = self._prices.get(cid,{}).get("usd",0)
                if p:
                    self._history.setdefault(cid,[]).append((ts,p))
                    self._history[cid] = self._history[cid][-120:]

            changed = self._verify_predictions()
            self.after(0, self._render_coins)
            if self._sel_coin:
                self.after(0, lambda: self._update_info_banner(self._sel_coin))
                self.after(0, lambda: self._draw_chart(self._sel_coin))
            acc = self._get_accuracy_str()
            self.after(0, lambda: self.acc_lbl.configure(text=acc))
            self.after(0, lambda: self.status_lbl.configure(
                text=f"✓ {datetime.datetime.now().strftime('%H:%M:%S')}"))
            if changed: self.after(0, self._refresh_learn_box)
        except Exception as e:
            self.after(0, lambda: self.status_lbl.configure(text=f"❌ {e}"))

    def _start_auto(self):
        def tick():
            if not self.winfo_exists(): return
            if self.auto_var.get():
                iv = self.interval_var.get()
                delay = {"10s":10,"30s":30,"60s":60,"5m":300}.get(iv,30)
                self._fetch_prices()
            self._auto_id = self.after(
                {"10s":10_000,"30s":30_000,"60s":60_000,"5m":300_000}.get(
                    self.interval_var.get(),30_000), tick)
        self._auto_id = self.after(30_000, tick)

    # ══ Coin-Liste rendern ═══════════════════════════════════════════════════
    def _render_coins(self):
        for w in self._coin_scroll.winfo_children(): w.destroy()

        ranked = []
        for name,cid,sym,icon,color in self.COINS:
            d = self._prices.get(cid,{})
            ranked.append((d.get("usd_24h_change",0) or 0, name,cid,sym,icon,color,d))
        ranked.sort(key=lambda x:-x[0])

        for i,(change,name,cid,sym,icon,color,d) in enumerate(ranked):
            p    = d.get("usd",0)
            c7   = d.get("usd_7d_change",0) or 0
            col  = GREEN if change >= 0 else RED
            arr  = "▲" if change >= 0 else "▼"
            prev = self._prev_prices.get(cid,p)
            dir_arrow = " ↑" if p > prev else (" ↓" if p < prev else "")
            sel  = (self._sel_coin == cid)

            # Letztes Signal für diesen Coin
            last_sig = next((x["signal"] for x in reversed(self._learned["predictions"])
                             if x["sym"]==sym), "")
            sig_color = self.SIGNAL_COLORS.get(last_sig, TEXT_DIM)

            card = ctk.CTkFrame(self._coin_scroll,
                fg_color=BG_SEL if sel else BG_CARD,
                corner_radius=6, border_width=1,
                border_color=ACCENT if sel else BG_INPUT)
            card.grid(row=i,column=0,sticky="ew",padx=4,pady=2)
            card.grid_columnconfigure(1,weight=1)

            # Symbol mit Farbe
            sym_lbl = ctk.CTkLabel(card,
                text=f"{icon}\n{sym}",
                font=ctk.CTkFont("Helvetica",10,"bold"),
                text_color=color, width=38, justify="center")
            sym_lbl.grid(row=0,column=0,rowspan=2,padx=(6,4),pady=5)

            # Name
            ctk.CTkLabel(card, text=name,
                font=ctk.CTkFont("Helvetica",9), text_color=TEXT_DIM, anchor="w"
                ).grid(row=0,column=1,sticky="w",pady=(5,0))

            # Preis mit Richtung
            p_fmt = (f"${p:,.6f}" if p<0.001 else
                     f"${p:,.4f}" if p<0.1 else
                     f"${p:,.2f}")
            dir_col = GREEN if p>prev else (RED if p<prev else TEXT_DIM)
            ctk.CTkLabel(card, text=p_fmt+dir_arrow,
                font=ctk.CTkFont("Helvetica",12,"bold"),
                text_color=dir_col, anchor="w"
                ).grid(row=1,column=1,sticky="w",pady=(0,5))

            # 24h
            ctk.CTkLabel(card, text=f"{arr}{change:+.2f}%",
                font=ctk.CTkFont("Helvetica",10,"bold"), text_color=col
                ).grid(row=0,column=2,padx=(0,4))

            # Signal Badge
            if last_sig:
                ctk.CTkLabel(card, text=last_sig,
                    font=ctk.CTkFont("Helvetica",8,"bold"),
                    text_color=sig_color, width=60
                    ).grid(row=1,column=2,padx=(0,4))

            # Klick
            for w in [card,sym_lbl]:
                w.bind("<Button-1>",
                    lambda e,n=name,c=cid,s=sym,ic=icon,co=color:
                    self._select(n,c,s,ic,co))

            ctk.CTkButton(card, text="🤖", width=24, height=24,
                fg_color="transparent", hover_color=BG_MID,
                text_color=ACCENT, font=ctk.CTkFont(size=11),
                command=lambda n=name,c=cid,s=sym,ic=icon,co=color:
                    self._select(n,c,s,ic,co)
                ).grid(row=0,column=3,rowspan=2,padx=(0,4))

    # ══ Coin auswählen ═══════════════════════════════════════════════════════
    def _select(self, name, cid, sym, icon, color):
        self._sel_coin = cid
        self._render_coins()
        self._update_info_banner(cid)
        self._draw_chart(cid)
        self._tabs.set("🐟 Analyse")
        self._analyze_coin(name, cid, sym, icon, color)
        self._fetch_news(name, sym)

    # ══ Info-Banner ══════════════════════════════════════════════════════════
    def _update_info_banner(self, cid):
        d   = self._prices.get(cid, {})
        p   = d.get("usd", 0)
        eur = d.get("eur", 0)
        c24 = d.get("usd_24h_change", 0) or 0
        c7  = d.get("usd_7d_change", 0) or 0
        mc  = d.get("usd_market_cap", 0) or 0
        vol = d.get("usd_24h_vol", 0) or 0

        p_fmt = (f"${p:,.6f}" if p<0.001 else
                 f"${p:,.4f}" if p<0.1 else
                 f"${p:,.2f}")
        self._price_big.configure(text=p_fmt)
        col = GREEN if c24>=0 else RED
        arr = "▲" if c24>=0 else "▼"
        self._change_lbl.configure(text=f"{arr} {c24:+.2f}%", text_color=col)
        mc_str  = f"${mc/1e9:.2f}B" if mc>1e9 else f"${mc/1e6:.0f}M"
        vol_str = f"${vol/1e9:.2f}B" if vol>1e9 else f"${vol/1e6:.0f}M"
        self._stats_lbl.configure(
            text=f"€{eur:,.2f}  |  MCap: {mc_str}  |  Vol: {vol_str}  |  7d: {c7:+.1f}%")

    def _update_signal_box(self, signal, risk):
        sig_col  = self.SIGNAL_COLORS.get(signal, TEXT_DIM)
        risk_col = self.RISK_COLORS.get(risk, TEXT_DIM)
        self._signal_lbl.configure(text=signal, text_color=sig_col)
        self._risk_lbl.configure(text=f"Risiko: {risk}", text_color=risk_col)
        # Hintergrund leicht einfärben
        bg = {"KAUFEN":"#0a2a0a","HALTEN":"#2a1a00","VERKAUFEN":"#2a0a0a",
               "ABWARTEN":"#1a0a2a"}.get(signal, BG_INPUT)
        self._signal_box.configure(fg_color=bg)

    # ══ Chart ════════════════════════════════════════════════════════════════
    def _draw_chart(self, cid):
        cv  = self._chart_cv
        cv.delete("all")
        pts = self._history.get(cid, [])
        cv.update_idletasks()
        W = cv.winfo_width() or 800
        H = cv.winfo_height() or 160
        pad_l, pad_r, pad_t, pad_b = 60, 20, 16, 24

        if len(pts) < 2:
            cv.create_text(W//2, H//2, text="Sammle Daten... (alle 30s)",
                           fill=TEXT_DIM, font=("Helvetica",11))
            return

        prices = [p for _,p in pts]
        times  = [t for t,_ in pts]
        mn, mx = min(prices), max(prices)
        rng    = mx - mn or mx * 0.001 or 1
        is_up  = prices[-1] >= prices[0]
        lc     = "#4ade80" if is_up else "#f87171"

        def px(p): return pad_l + (W-pad_l-pad_r) * (p-times[0]) / (times[-1]-times[0]+1)
        def py(v): return pad_t + (H-pad_t-pad_b) * (1-(v-mn)/rng)

        # Grid
        for i in range(1,5):
            gy = pad_t + (H-pad_t-pad_b)*i/4
            pv = mn + rng*(1-i/4)
            cv.create_line(pad_l, gy, W-pad_r, gy, fill="#222240", dash=(2,4))
            p_lbl = (f"${pv:.6f}" if pv<0.001 else
                     f"${pv:.4f}" if pv<0.1 else f"${pv:,.2f}")
            cv.create_text(pad_l-4, gy, text=p_lbl, fill=TEXT_DIM,
                           font=("Helvetica",7), anchor="e")

        # Linie + Fill
        coords = []
        for t,p in pts:
            coords.extend([px(t), py(p)])
        fill_pts = [pad_l, H-pad_b] + coords + [W-pad_r, H-pad_b]
        cv.create_polygon(fill_pts,
                          fill="#1a3020" if is_up else "#2a1515",
                          outline="", smooth=True)
        cv.create_line(*coords, fill=lc, width=2.5, smooth=True)

        # Letzter Punkt
        lx, ly = coords[-2], coords[-1]
        cv.create_oval(lx-5,ly-5,lx+5,ly+5, fill=lc, outline=BG_DARK, width=2)

        # Aktueller Preis als gestrichelte Linie
        cv.create_line(pad_l, ly, W-pad_r, ly, fill=lc, dash=(4,4), width=1)

        # Zeitstempel unten
        for i in [0, len(pts)//2, len(pts)-1]:
            if i < len(pts):
                t = pts[i][0]
                tx = px(t)
                cv.create_text(tx, H-4,
                               text=datetime.datetime.fromtimestamp(t).strftime("%H:%M"),
                               fill=TEXT_DIM, font=("Helvetica",7))

        # Preis oben rechts
        p_fmt = (f"${prices[-1]:,.6f}" if prices[-1]<0.001 else
                 f"${prices[-1]:,.4f}" if prices[-1]<0.1 else
                 f"${prices[-1]:,.2f}")
        cv.create_text(W-pad_r, pad_t, text=p_fmt, fill="#e2e8f0",
                       font=("Helvetica",10,"bold"), anchor="ne")

        # Pct change
        pct = (prices[-1]/prices[0]-1)*100
        cv.create_text(pad_l+10, pad_t, text=f"{'▲' if pct>=0 else '▼'}{pct:+.2f}%",
                       fill=lc, font=("Helvetica",9,"bold"), anchor="nw")

    # ══ News ════════════════════════════════════════════════════════════════
    def _fetch_news(self, name, sym):
        if sym in self._news_cache:
            self._write(self.news_box, self._news_cache[sym]); return
        self._write(self.news_box, f"📰 Suche News für {name}...")
        threading.Thread(target=self._do_news, args=(name,sym), daemon=True).start()

    def _do_news(self, name, sym):
        try:
            q = urllib.parse.quote(f"{name} crypto price news today")
            r = requests.get(
                f"https://api.duckduckgo.com/?q={q}&format=json&no_html=1",
                timeout=10, headers={"User-Agent":"Ghostfish/1.0"})
            d   = r.json()
            out = []
            if d.get("AbstractText"): out.append(f"📖 {d['AbstractText'][:500]}")
            for t in (d.get("RelatedTopics") or [])[:8]:
                if isinstance(t,dict) and t.get("Text"):
                    out.append(f"• {t['Text'][:180]}")
            txt = "\n\n".join(out) if out else f"Keine News für {name}."
            self._news_cache[sym] = txt
            self.after(0, lambda: self._write(self.news_box, txt))
        except Exception as e:
            self.after(0, lambda: self._write(self.news_box, f"❌ {e}"))

    # ══ KI-Analyse + Kaufempfehlung ══════════════════════════════════════════
    def _analyze_coin(self, name, cid, sym, icon, color):
        if self._analysis_running: return
        self._analysis_running = True
        d   = self._prices.get(cid, {})
        p   = d.get("usd", 0)
        c24 = d.get("usd_24h_change", 0) or 0
        c7  = d.get("usd_7d_change", 0) or 0
        mc  = d.get("usd_market_cap", 0) or 0
        vol = d.get("usd_24h_vol", 0) or 0
        news    = self._news_cache.get(sym, "")
        err_ctx = self._get_error_context()

        past = [x for x in self._learned["predictions"] if x["sym"]==sym][-5:]
        past_txt = ""
        if past:
            past_txt = f"My past signals for {sym}:\n"
            for x in past:
                s   = "CORRECT" if x.get("correct") else ("WRONG" if x.get("checked") else "PENDING")
                pct = f" ({x['pct_change']:+.1f}%)" if x.get("pct_change") else ""
                past_txt += f"  {s}: {x['date'][:10]} — {x['signal']} @ ${x['price_at']:,.4f}{pct}\n"

        self._write(self.analysis_box, f"Analyzing {icon} {name}...")
        self._update_signal_box("...", "")

        def _run():
            try:
                p_fmt    = (f"${p:,.6f}" if p<0.001 else f"${p:,.4f}" if p<0.1 else f"${p:,.2f}")
                mc_str   = f"${mc/1e9:.2f}B" if mc>1e9 else f"${mc/1e6:.0f}M"
                vol_str  = f"${vol/1e9:.2f}B" if vol>1e9 else f"${vol/1e6:.0f}M"
                vol_mcap = f"{vol/mc*100:.1f}" if mc else "0"

                msg = (
                    f"=== CRYPTO ANALYSIS REQUEST ===\n\n"
                    f"COIN:       {icon} {name} ({sym})\n"
                    f"PRICE:      {p_fmt}\n"
                    f"24h CHANGE: {c24:+.2f}%\n"
                    f"7d CHANGE:  {c7:+.2f}%\n"
                    f"MARKET CAP: {mc_str}\n"
                    f"24h VOLUME: {vol_str}\n"
                    f"VOL/MCAP:   {vol_mcap}%\n"
                    + (f"\nRECENT NEWS:\n{news[:400]}\n" if news else "")
                    + (f"\n{past_txt}" if past_txt else "")
                    + (f"\nLEARNED MISTAKES (avoid repeating):\n{err_ctx}\n" if err_ctx else "")
                    + "\n=== RESPOND EXACTLY IN THIS FORMAT ===\n\n"
                    "SIGNAL: BUY\n"
                    "(or HOLD, SELL, WAIT)\n\n"
                    "RISK: LOW\n"
                    "(or MEDIUM, HIGH, VERY HIGH)\n\n"
                    "DIRECTION: UP\n"
                    "(or DOWN, SIDEWAYS)\n\n"
                    "CONFIDENCE: 75%\n\n"
                    "ANALYSIS:\n"
                    "2-3 sentences of technical analysis based on the data above.\n\n"
                    "SHOULD YOU BUY?\n"
                    "Clear explanation of whether to enter now or wait.\n\n"
                    f"ENTRY: {p_fmt} or specify a better entry price\n"
                    "STOP LOSS: price to exit to limit losses\n"
                    "TAKE PROFIT: target price\n\n"
                    "SUMMARY: One sentence clear recommendation.\n\n"
                    "DISCLAIMER: This is AI speculation, not financial advice."
                )

                r = requests.post(
                    f"{OLLAMA_URL}/api/chat",
                    json={"model": self.model_var.get(),
                          "messages": [
                              {"role": "system", "content":
                               "You are an expert crypto trader and technical analyst. "
                               "Always respond in English. Be precise and data-driven. "
                               "Always give a CLEAR signal. Learn from past mistakes. "
                               "Never be vague — give a definitive recommendation."},
                              {"role": "user", "content": msg}],
                          "stream": True,
                          "options": {"temperature": 0.3}},
                    timeout=120, stream=True)

                full = ""
                for line in r.iter_lines():
                    if not line: continue
                    try:
                        chunk = json.loads(line.decode("utf-8"))
                        tok   = chunk.get("message", {}).get("content", "")
                        if tok:
                            full += tok
                            self.after(0, lambda t=full: self._write(self.analysis_box, t))
                        if chunk.get("done"): break
                    except: continue

                # Extract signal — support both German and English
                sig_m  = re.search(
                    r'SIGNAL:\s*(BUY|SELL|HOLD|WAIT|KAUFEN|HALTEN|VERKAUFEN|ABWARTEN)',
                    full, re.I)
                risk_m = re.search(
                    r'RISK:\s*(LOW|MEDIUM|HIGH|VERY HIGH)|RISIKO:\s*(LOW|MEDIUM|HIGH|VERY HIGH)',
                    full, re.I)
                dir_m  = re.search(
                    r'DIRECTION:\s*(UP|DOWN|SIDEWAYS)|RICHTUNG:\s*(UP|DOWN|SIDEWAYS)',
                    full, re.I)
                conf_m = re.search(r'CONFIDENCE:\s*(\d+)|KONFIDENZ:\s*(\d+)', full)

                # Normalize German → English signals
                raw_sig = (sig_m.group(1) or "").upper() if sig_m else "WAIT"
                sig_map = {"KAUFEN":"BUY","HALTEN":"HOLD","VERKAUFEN":"SELL","ABWARTEN":"WAIT"}
                signal  = sig_map.get(raw_sig, raw_sig) or "WAIT"

                raw_risk = ""
                if risk_m:
                    raw_risk = (risk_m.group(1) or risk_m.group(2) or "").upper()
                risk = raw_risk or "HIGH"

                raw_dir = ""
                if dir_m:
                    raw_dir = (dir_m.group(1) or dir_m.group(2) or "").upper()
                direction  = raw_dir or "SIDEWAYS"
                confidence = int(conf_m.group(1) or conf_m.group(2)) if conf_m else 50

                self.after(0, lambda: self._update_signal_box(signal, risk))
                self._record_prediction(sym, p, signal, direction, confidence, full)

            except Exception as e:
                self.after(0, lambda: self._write(self.analysis_box, f"Error: {e}"))
            finally:
                self._analysis_running = False

        threading.Thread(target=_run, daemon=True).start()

    def _analyze_all(self):
        if not self._prices: return
        self._tabs.set("🐟 Analyse")
        self._write(self.analysis_box, "Analyzing gesamten Markt...")

        def _run():
            try:
                rows = []
                for name,cid,sym,icon,_ in self.COINS:
                    d = self._prices.get(cid,{})
                    p = d.get("usd",0)
                    c = d.get("usd_24h_change",0) or 0
                    c7= d.get("usd_7d_change",0) or 0
                    pf = (f"${p:.6f}" if p<0.001 else
                          f"${p:.4f}" if p<0.1 else f"${p:,.2f}")
                    arr= "▲" if c>=0 else "▼"
                    rows.append(f"  {icon}{sym:5} {pf:>14} {arr}{c:+.2f}%  7d:{c7:+.1f}%")

                acc = self._get_accuracy_str()
                err = self._get_error_context()
                msg = (
                    f"=== CRYPTO MARKET SNAPSHOT ===\n" + "\n".join(rows) +
                    f"\n\nMy prediction accuracy: {acc}\n"
                    + (f"\n{err}\n" if err else "") +
                    "\nProvide a CLEAR market analysis in English:\n"
                    "1. Overall market sentiment (BULLISH / BEARISH / NEUTRAL)\n"
                    "2. TOP 3 coins to BUY right now (with reason)\n"
                    "3. TOP 3 coins to AVOID right now (with reason)\n"
                    "4. Biggest risk in the market right now\n"
                    "5. Market direction 24-48h: UP / DOWN / SIDEWAYS\n"
                    "6. One concrete strategy for today\n\n"
                    "DISCLAIMER: AI speculation only — not financial advice!"
                )
                r = requests.post(f"{OLLAMA_URL}/api/chat",
                    json={"model": self.model_var.get(),
                          "messages":[
                              {"role":"system","content":
                               "Expert crypto market analyst. Always respond in English. Be precise and actionable."},
                              {"role":"user","content":msg}],
                          "stream":True,"options":{"temperature":0.3}},
                    timeout=180, stream=True)
                full=""
                for line in r.iter_lines():
                    if not line: continue
                    try:
                        chunk=json.loads(line.decode("utf-8"))
                        tok=chunk.get("message",{}).get("content","")
                        if tok:
                            full+=tok
                            self.after(0,lambda t=full:self._write(self.analysis_box,t))
                        if chunk.get("done"): break
                    except: continue
            except Exception as e:
                self.after(0,lambda:self._write(self.analysis_box,f"Error: {e}"))
        threading.Thread(target=_run,daemon=True).start()

    # ══ Gelernt Tab ══════════════════════════════════════════════════════════
    def _show_learned(self):
        self._tabs.set("🧠 Gelernt")
        self._refresh_learn_box()

    def _refresh_learn_box(self):
        s = self._learned["session_stats"]
        acc = round(s["correct"]/s["total"]*100,1) if s["total"] else 0
        lines = [
            "=== AI LEARNING STATUS ===\n",
            f"Accuracy:  {acc}%",
            f"Correct:   {s['correct']}",
            f"Wrong:     {s['wrong']}",
            f"Total:     {s['total']} verified predictions\n",
        ]
        errs = self._learned.get("error_patterns",[])
        if errs:
            lines.append("Learned mistakes (avoiding these):")
            for e in errs[-5:]:
                lines.append(f"  - {e['sym']}: signal '{e['signal']}' was wrong ({e['pct_change']:+.1f}%)")
            lines.append("")

        preds = self._learned.get("predictions",[])
        if preds:
            lines.append(f"Last predictions ({len(preds)} total):")
            for x in reversed(preds[-20:]):
                s_icon = "✓" if x.get("correct") else ("✗" if x.get("checked") else "⏳")
                pct    = f" -> {x['pct_change']:+.1f}%" if x.get("pct_change") else ""
                lines.append(f"  {s_icon} [{x['date'][:10]}] {x['sym']:5} "
                             f"{x['signal']:6} conf:{x.get('confidence',0)}%{pct}")
        else:
            lines.append("No data yet.\nAnalyze coins and come back — Ghostfish learns over time!")

        self._write(self.learn_box, "\n".join(lines))

    # ══ Hilfsfunktionen ══════════════════════════════════════════════════════
    def _write(self, box, text):
        box.configure(state="normal")
        box.delete("1.0","end")
        box.insert("end", text)
        box.configure(state="disabled")
        box.see("end")

    def destroy(self):
        if self._auto_id:
            try: self.after_cancel(self._auto_id)
            except: pass
        super().destroy()


class GhostfishApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Ghostfish — Your Local AI")
        self.geometry("1180x740")
        self.minsize(900, 560)
        self.configure(fg_color=BG_DARK)

        self.chat_history   = []
        self.learned_texts  = []
        self.learned_code   = []
        self.learned_repos  = []
        self.selected_model = ctk.StringVar(value="qwen2.5:latest")
        self.is_typing      = False
        self.word_count     = 0
        self.pending_image  = None
        self._thumb_refs    = []
        self.current_entry  = None
        self.chat_entries   = []
        self._chat_buttons  = []
        self.current_theme  = "🌙 Lila Nacht"
        self._stream_msg_start = None  # Marker für Streaming-Position

        # Gedächtnis
        self.memory = Memory()
        self.memory.data["session_count"] += 1
        self.memory.save()

        # Neue Manager
        self.apis        = ApiManager()
        self.profiles    = ProfileManager()
        self.todos       = TodoManager()
        self.bot_manager = BotManager()
        self.moe         = MoERouter()
        self._timers     = []
        self._tts_playing = False
        self._crypto_win  = None

        # MoE Status-Callback → Sidebar updaten
        self.moe.on_status_change(lambda: self.after(0, self._update_moe_status))

        # Diese müssen VOR _build_ui da sein — sidebar braucht sie
        self.tts_var    = ctk.BooleanVar(value=False)
        self._mic_active = False
        self._lang_var  = ctk.StringVar(value="Auto")

        self._build_ui()
        self._load_learn_folder()
        self._load_all_chats()
        self._check_ollama()

    # ── Layout: 3 Spalten ─────────────────────────────────────────────────────
    def _build_ui(self):
        self.grid_columnconfigure(0, weight=0, minsize=175)  # KI-Sidebar
        self.grid_columnconfigure(1, weight=0, minsize=210)  # Chat-Verlauf
        self.grid_columnconfigure(2, weight=1)               # Haupt-Chat
        self.grid_rowconfigure(0, weight=1)
        self._build_ai_sidebar()
        self._build_history_panel()
        self._build_main()

    # ── Linke Sidebar: Geist + Buttons ────────────────────────────────────────
    def _build_ai_sidebar(self):
        sb = ctk.CTkFrame(self, width=175, corner_radius=0, fg_color=BG_MID)
        sb.grid(row=0, column=0, sticky="nsew")
        sb.grid_propagate(False)
        sb.grid_rowconfigure(99, weight=1)

        self.ghost = GhostCanvas(sb, size=100)
        self.ghost.grid(row=0, column=0, pady=(14,2))

        ctk.CTkLabel(sb, text=AI_NAME,
                     font=ctk.CTkFont("Helvetica", 17, "bold"),
                     text_color=ACCENT).grid(row=1, column=0, pady=(0,2))

        self.status_dot = ctk.CTkLabel(sb, text="● offline",
                                       font=ctk.CTkFont(size=10),
                                       text_color=TEXT_DIM)
        self.status_dot.grid(row=2, column=0, pady=(0,8))

        ctk.CTkLabel(sb, text="Modell", font=ctk.CTkFont(size=10),
                     text_color=TEXT_DIM).grid(row=3, column=0, padx=12, sticky="w")
        self.model_menu = ctk.CTkOptionMenu(
            sb, variable=self.selected_model,
            values=["qwen2.5:latest","qwen2.5-coder:latest","qwen2.5:7b",
                    "qwen2.5-vl","llava","llama3","mistral","codellama","phi3"], width=161,
            fg_color=BG_CARD, button_color=ACCENT2,
            button_hover_color=ACCENT, dropdown_fg_color=BG_CARD,
            font=ctk.CTkFont(size=11),
            command=lambda v: self.selected_model.set(v))
        self.model_menu.grid(row=4, column=0, padx=12, pady=(2,8))

        def sbtn(row, text, cmd):
            ctk.CTkButton(sb, text=text, command=cmd, width=151, height=26,
                          fg_color="transparent", border_width=1,
                          border_color=ACCENT2, hover_color=BG_CARD,
                          text_color=ACCENT, font=ctk.CTkFont(size=10)
                          ).grid(row=row, column=0, padx=12, pady=2)

        sbtn(5,  "🔄  Verbinden",         self._check_ollama)
        sbtn(6,  "📂  Lernordner",        self._open_learn_folder)
        sbtn(7,  "🔃  Neu laden",          self._reload_learn)
        sbtn(8,  "📁  Dateien öffnen",    self._open_files_folder)
        sbtn(9,  "💾  Obsidian Export",   self._save_to_obsidian)
        sbtn(10, "🤖  Bot erstellen",     self._open_bot_dialog)
        sbtn(11, "🪙  Crypto-Guesser",    self._open_crypto)
        sbtn(12, "🔗  Agent-Netzwerk",    self._open_moe_panel)

        sep2 = ctk.CTkFrame(sb, height=1, fg_color="#2a2a4a")
        sep2.grid(row=13, column=0, sticky="ew", padx=12, pady=4)
        ctk.CTkLabel(sb, text="Agent-Status",
                     font=ctk.CTkFont(size=9, weight="bold"),
                     text_color=TEXT_DIM).grid(row=14, column=0, padx=12, sticky="w")
        self.moe_status_lbl = ctk.CTkLabel(
            sb, text="Prüfe...", font=ctk.CTkFont(size=9),
            text_color=TEXT_DIM, wraplength=161, justify="left")
        self.moe_status_lbl.grid(row=15, column=0, padx=12, pady=(0,4), sticky="w")

        self.learn_info = ctk.CTkLabel(
            sb, text="0 Texte", font=ctk.CTkFont(size=9),
            text_color=TEXT_DIM, wraplength=151, justify="center")
        self.learn_info.grid(row=99, column=0, padx=12, pady=8, sticky="s")

    # ── Mittlere Spalte: Chat-Verlauf ─────────────────────────────────────────
    def _build_history_panel(self):
        panel = ctk.CTkFrame(self, width=210, corner_radius=0, fg_color=BG_DARK)
        panel.grid(row=0, column=1, sticky="nsew")
        panel.grid_propagate(False)
        panel.grid_rowconfigure(1, weight=1)
        panel.grid_columnconfigure(0, weight=1)
        self.history_panel = panel

        # Header
        hdr = ctk.CTkFrame(panel, fg_color=BG_MID, corner_radius=0, height=44)
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.grid_propagate(False)
        hdr.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(hdr, text="💬  Chats",
                     font=ctk.CTkFont("Helvetica", 13, "bold"),
                     text_color=ACCENT).grid(row=0, column=0, padx=12, pady=10, sticky="w")

        ctk.CTkButton(hdr, text="＋", width=30, height=30, corner_radius=8,
                      fg_color=ACCENT2, hover_color=ACCENT,
                      font=ctk.CTkFont(size=16),
                      command=self._new_chat
                      ).grid(row=0, column=1, padx=8, pady=7)

        # Scrollbarer Bereich für Chat-Liste
        self.history_scroll = ctk.CTkScrollableFrame(
            panel, fg_color=BG_DARK, corner_radius=0,
            scrollbar_button_color=ACCENT2,
            scrollbar_button_hover_color=ACCENT)
        self.history_scroll.grid(row=1, column=0, sticky="nsew")
        self.history_scroll.grid_columnconfigure(0, weight=1)

        # Trennlinie rechts
        sep = tk.Frame(panel, bg="#222233", width=1)
        sep.place(relx=1.0, rely=0, relheight=1.0, anchor="ne")

    def _render_history(self):
        """Alle Chat-Buttons neu zeichnen."""
        for btn in self._chat_buttons:
            btn.destroy()
        self._chat_buttons = []

        for entry in reversed(self.chat_entries):
            e = entry  # closure fix
            is_active = (self.current_entry is e)

            frame = ctk.CTkFrame(
                self.history_scroll,
                fg_color=BG_SEL if is_active else BG_CARD,
                corner_radius=8,
                border_width=1 if is_active else 0,
                border_color=ACCENT2)
            frame.grid(sticky="ew", padx=8, pady=3)
            frame.grid_columnconfigure(0, weight=1)
            self._chat_buttons.append(frame)

            # Titel + Datum
            title_lbl = ctk.CTkLabel(
                frame, text=e.title[:28],
                font=ctk.CTkFont("Helvetica", 12, "bold" if is_active else "normal"),
                text_color=ACCENT if is_active else "#ccccdd",
                anchor="w", cursor="hand2")
            title_lbl.grid(row=0, column=0, padx=10, pady=(8,2), sticky="w")
            title_lbl.bind("<Button-1>", lambda ev, en=e: self._load_chat(en))

            date_lbl = ctk.CTkLabel(
                frame, text=e.created.strftime("%d.%m.%Y  %H:%M"),
                font=ctk.CTkFont(size=10),
                text_color=TEXT_DIM, anchor="w", cursor="hand2")
            date_lbl.grid(row=1, column=0, padx=10, pady=(0,4), sticky="w")
            date_lbl.bind("<Button-1>", lambda ev, en=e: self._load_chat(en))

            preview = ""
            for m in reversed(e.history):
                if m["role"] == "assistant":
                    preview = m["content"][:50].replace("\n"," ")
                    break
            if preview:
                prev_lbl = ctk.CTkLabel(
                    frame, text=preview + "…",
                    font=ctk.CTkFont(size=10), text_color=TEXT_DIM,
                    anchor="w", wraplength=160, justify="left", cursor="hand2")
                prev_lbl.grid(row=2, column=0, padx=10, pady=(0,6), sticky="w")
                prev_lbl.bind("<Button-1>", lambda ev, en=e: self._load_chat(en))

            # Löschen-Button
            del_btn = ctk.CTkButton(
                frame, text="🗑", width=24, height=24,
                fg_color="transparent", hover_color=BG_INPUT,
                text_color=TEXT_DIM, font=ctk.CTkFont(size=12),
                command=lambda en=e: self._delete_chat(en))
            del_btn.grid(row=0, column=1, padx=(0,6), pady=(6,0))

    # ── Chat laden / erstellen / löschen ─────────────────────────────────────
    def _new_chat(self):
        """Aktuellen Chat speichern und neuen starten."""
        self._autosave_current()
        self.chat_history = []
        self.current_entry = None
        self._clear_chatbox()
        self._sys_msg("Neuer Chat gestartet ✨")
        self._render_history()

    def _load_chat(self, entry):
        """Einen gespeicherten Chat öffnen."""
        self._autosave_current()
        self.current_entry = entry
        self.chat_history  = list(entry.history)
        self._clear_chatbox()
        self._sys_msg(f"Chat opened: {entry.title}")

        # Nachrichten anzeigen
        for msg in entry.history:
            is_user = msg["role"] == "user"
            sender  = "Du" if is_user else AI_NAME
            self._print_msg(sender, msg["content"], is_user=is_user)

        self._render_history()
        self.ghost.set_state(GhostCanvas.HAPPY)
        self.after(2000, lambda: self.ghost.set_state(GhostCanvas.IDLE))

    def _delete_chat(self, entry):
        if entry.path and Path(entry.path).exists():
            Path(entry.path).unlink()
        if entry in self.chat_entries:
            self.chat_entries.remove(entry)
        if self.current_entry is entry:
            self.current_entry = None
            self.chat_history  = []
            self._clear_chatbox()
            self._sys_msg("Chat gelöscht.")
        self._render_history()

    def _autosave_current(self):
        """Speichert den aktuellen Chat automatisch."""
        if not self.chat_history:
            return
        if self.current_entry is None:
            # Titel aus erster Nachricht
            first = next((m["content"] for m in self.chat_history if m["role"]=="user"), "Chat")
            title = first[:35].strip()
            self.current_entry = ChatEntry(title, self.chat_history)
            self.chat_entries.append(self.current_entry)
        else:
            self.current_entry.history = list(self.chat_history)
        self.current_entry.save()

    def _load_all_chats(self):
        """Alle gespeicherten Chats beim Start laden."""
        self.chat_entries = []
        files = sorted(glob.glob(f"{CHATS_FOLDER}/*.json"))
        for f in files:
            try:
                entry = ChatEntry.load(f)
                self.chat_entries.append(entry)
            except Exception:
                pass
        self._render_history()

    # ── Rechte Spalte: Haupt-Chat ─────────────────────────────────────────────
    def _build_main(self):
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.grid(row=0, column=2, sticky="nsew")
        main.grid_rowconfigure(0, weight=1)
        main.grid_columnconfigure(0, weight=1)

        tabs = ctk.CTkTabview(main, fg_color=BG_MID,
                              segmented_button_fg_color=BG_CARD,
                              segmented_button_selected_color=ACCENT2,
                              segmented_button_selected_hover_color=ACCENT)
        tabs.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        self.tabs = tabs
        tabs.add("💬  Chat")
        tabs.add("🧠  Lernen")
        tabs.add("✅  TODOs")
        tabs.add("🔑  APIs")
        tabs.add("⚙️  Einstellungen")

        self._build_chat_tab()
        self._build_learn_tab()
        self._build_todos_tab()
        self._build_apis_tab()
        self._build_settings_tab()

    # ── Chat Tab ──────────────────────────────────────────────────────────────
    def _build_chat_tab(self):
        tab = self.tabs.tab("💬  Chat")
        tab.grid_rowconfigure(0, weight=1)
        tab.grid_columnconfigure(0, weight=1)

        self.chat_box = ctk.CTkTextbox(
            tab, state="disabled",
            font=ctk.CTkFont("Helvetica", 13),
            wrap="word", corner_radius=12, fg_color=BG_CARD,
            scrollbar_button_color=ACCENT2,
            scrollbar_button_hover_color=ACCENT)
        self.chat_box.grid(row=0, column=0, sticky="nsew", pady=(0,6))

        tb = self.chat_box._textbox
        tb.tag_configure("user_name", foreground=GREEN,    font=("Helvetica",12,"bold"))
        tb.tag_configure("user_msg",  foreground="#d4fae4", font=("Helvetica",13))
        tb.tag_configure("ai_name",   foreground=ACCENT,   font=("Helvetica",12,"bold"))
        tb.tag_configure("ai_msg",    foreground="#e8e0ff", font=("Helvetica",13))
        tb.tag_configure("sys_msg",   foreground=TEXT_DIM,  font=("Helvetica",11,"italic"))
        tb.tag_configure("err_msg",   foreground=RED,       font=("Helvetica",12))
        tb.tag_configure("file_msg",  foreground=BLUE,      font=("Helvetica",12,"bold"))
        tb.tag_configure("img_msg",   foreground="#fbbf24", font=("Helvetica",11,"italic"))

        # Bild-Vorschau
        self.img_preview_frame = ctk.CTkFrame(tab, fg_color=BG_CARD,
                                              corner_radius=8, height=58)
        self.img_preview_frame.grid(row=1, column=0, sticky="ew", pady=(0,4))
        self.img_preview_frame.grid_propagate(False)
        self.img_preview_frame.grid_columnconfigure(1, weight=1)
        self.img_preview_frame.grid_remove()

        self.img_thumb_label = ctk.CTkLabel(self.img_preview_frame, text="")
        self.img_thumb_label.grid(row=0, column=0, padx=8, pady=4)

        self.img_name_label = ctk.CTkLabel(
            self.img_preview_frame, text="", text_color="#fbbf24",
            font=ctk.CTkFont(size=11), wraplength=300, justify="left")
        self.img_name_label.grid(row=0, column=1, sticky="w")

        ctk.CTkButton(self.img_preview_frame, text="✕", width=26, height=26,
                      fg_color="transparent", text_color=RED,
                      hover_color=BG_INPUT, command=self._clear_image
                      ).grid(row=0, column=2, padx=8)

        # Sprach-Leiste
        lang_bar = ctk.CTkFrame(tab, fg_color="transparent")
        lang_bar.grid(row=2, column=0, sticky="ew", pady=(0,4))
        ctk.CTkLabel(lang_bar, text="🌐",
                     font=ctk.CTkFont(size=12), text_color=TEXT_DIM
                     ).pack(side="left", padx=(0,4))
        self._lang_btns = {}
        for lang_opt in ["Auto","Deutsch","English","Oskovian"]:
            btn = ctk.CTkButton(
                lang_bar, text=lang_opt, width=70, height=24,
                corner_radius=8, font=ctk.CTkFont(size=11),
                fg_color=ACCENT2 if lang_opt=="Auto" else "transparent",
                hover_color=ACCENT2,
                border_width=1, border_color=ACCENT2,
                text_color=ACCENT,
                command=lambda l=lang_opt: self._set_lang(l))
            btn.pack(side="left", padx=2)
            self._lang_btns[lang_opt] = btn

        # Eingabe
        inp = ctk.CTkFrame(tab, fg_color="transparent")
        inp.grid(row=3, column=0, sticky="ew")
        inp.grid_columnconfigure(1, weight=1)

        self.img_btn = ctk.CTkButton(
            inp, text="🖼", width=50, height=50, corner_radius=12,
            fg_color=BG_INPUT, hover_color=BG_CARD,
            border_width=1, border_color=ACCENT2,
            font=ctk.CTkFont(size=19),
            command=self._pick_image)
        self.img_btn.grid(row=0, column=0, padx=(0,6))

        self.input_box = ctk.CTkTextbox(
            inp, height=50, font=ctk.CTkFont("Helvetica", 13),
            wrap="word", corner_radius=12, fg_color=BG_INPUT,
            border_color=ACCENT2, border_width=1)
        self.input_box.grid(row=0, column=1, sticky="ew", padx=(0,6))
        self.input_box.bind("<Return>",       self._on_enter)
        self.input_box.bind("<Shift-Return>", lambda e: None)
        self.input_box.bind("<KeyRelease>",   self._on_key_input)

        # Autocomplete-Popup
        self.cmd_popup = tk.Listbox(
            self, bg=BG_CARD, fg=ACCENT,
            selectbackground=ACCENT2, selectforeground="white",
            font=("Courier", 11), borderwidth=0, highlightthickness=1,
            highlightcolor=ACCENT2, relief="flat", height=4)
        self.cmd_popup.bind("<ButtonRelease-1>", self._autocomplete_select)
        self.cmd_popup.bind("<Return>",           self._autocomplete_select)
        self._popup_visible = False

        self.send_btn = ctk.CTkButton(
            inp, text="➤", width=50, height=50, corner_radius=12,
            fg_color=ACCENT2, hover_color=ACCENT,
            font=ctk.CTkFont(size=19),
            command=self._send_message)
        self.send_btn.grid(row=0, column=2, padx=(0,4))

        # Mikrofon-Button
        self.mic_btn = ctk.CTkButton(
            inp, text="🎙", width=50, height=50, corner_radius=12,
            fg_color=BG_INPUT, hover_color=BG_CARD,
            border_width=1, border_color=ACCENT2,
            font=ctk.CTkFont(size=19),
            command=self._toggle_mic)
        self.mic_btn.grid(row=0, column=3)

        self._sys_msg("Ghostfish is ready ✨  Neuen Chat starten oder alten Chat öffnen!")

    def _on_enter(self, event):
        if not (event.state & 0x1):
            self._hide_popup()
            self._send_message()
            return "break"

    def _on_key_input(self, event):
        text = self.input_box.get("1.0","end").strip()
        if text.startswith("/"):
            matches = [f"{c}  —  {d.split('—')[1].strip()}"
                       for c, d in self.COMMANDS.items()
                       if c.startswith(text.split()[0])]
            if matches:
                self._show_popup(matches)
                return
        self._hide_popup()

    def _show_popup(self, items):
        self.cmd_popup.delete(0,"end")
        for item in items:
            self.cmd_popup.insert("end", "  " + item)
        # Position unter Eingabefeld
        try:
            x = self.input_box.winfo_rootx() - self.winfo_rootx()
            y = self.input_box.winfo_rooty() - self.winfo_rooty() - len(items)*22 - 8
            w = self.input_box.winfo_width()
            self.cmd_popup.place(x=x, y=y, width=w, height=len(items)*22)
            self.cmd_popup.lift()
            self._popup_visible = True
        except Exception:
            pass

    def _hide_popup(self):
        if self._popup_visible:
            self.cmd_popup.place_forget()
            self._popup_visible = False

    def _autocomplete_select(self, event=None):
        sel = self.cmd_popup.curselection()
        if not sel: return
        item = self.cmd_popup.get(sel[0]).strip()
        cmd  = item.split("—")[0].strip().split()[0]
        self.input_box.delete("1.0","end")
        self.input_box.insert("1.0", cmd + " ")
        self._hide_popup()

    def _set_lang(self, lang):
        """Sets reply language and highlights the active button."""
        self._lang_var.set(lang)
        for l, btn in self._lang_btns.items():
            btn.configure(fg_color=ACCENT2 if l==lang else "transparent")
        labels = {
            "Auto":     "🌐 Auto — mirrors your language",
            "Deutsch":  "🇩🇪 Always replying in German",
            "English":  "🇬🇧 Always replying in English",
            "Oskovian": "⚔️  Always replying in Oskovian",
        }
        self._sys_msg(labels.get(lang, lang))

    # ── Bild ──────────────────────────────────────────────────────────────────
    def _pick_image(self):
        path = filedialog.askopenfilename(
            title="Bild auswählen",
            filetypes=[("Bilder","*.png *.jpg *.jpeg *.gif *.bmp *.webp"),("Alle","*.*")])
        if not path: return
        try:
            with open(path,"rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")
            img = Image.open(path); img.thumbnail((46,46),Image.LANCZOS)
            thumb = ImageTk.PhotoImage(img); self._thumb_refs.append(thumb)
            self.pending_image = (path, b64, thumb)
            self.img_thumb_label.configure(image=thumb)
            cur = self.selected_model.get()
            vision_ok = any(v in cur for v in ["llava","moondream","bakllava"])
            tip = "" if vision_ok else "  ⚠️ llava oder qwen2.5-vl nötig"
            self.img_name_label.configure(
                text=f"📷  {Path(path).name}{tip}",
                text_color="#fbbf24" if vision_ok else RED)
            self.img_preview_frame.grid()
            self.img_btn.configure(fg_color=ACCENT2)
        except Exception as e:
            self._sys_msg(f"❌  Bild Fehler: {e}")

    def _clear_image(self):
        self.pending_image=None
        self.img_preview_frame.grid_remove()
        self.img_btn.configure(fg_color=BG_INPUT)

    # ── Nachrichten ───────────────────────────────────────────────────────────
    def _chat_insert(self, text, tag):
        self.chat_box.configure(state="normal")
        self.chat_box._textbox.insert("end", text, tag)
        self.chat_box.configure(state="disabled")
        self.chat_box._textbox.see("end")

    def _sys_msg(self, text):
        self._chat_insert(f"\n  {text}\n", "sys_msg")

    def _print_msg(self, sender, text, is_user=False):
        nt = "user_name" if is_user else "ai_name"
        mt = "user_msg"  if is_user else "ai_msg"
        pr = "  👤 " if is_user else "  🐟 "
        self._chat_insert(f"\n{pr}{sender}\n", nt)
        self._chat_insert(f"  {text}\n", mt)

    def _clear_chatbox(self):
        self.chat_box.configure(state="normal")
        self.chat_box.delete("1.0","end")
        self.chat_box.configure(state="disabled")

    # ── Befehls-System ────────────────────────────────────────────────────────
    COMMANDS = {
        "/github":          "🐙  /github user/repo       — GitHub Repo laden",
        "/search":          "🔍  /search <frage>         — Internet durchsuchen",
        "/wiki":            "📖  /wiki <thema>           — Wikipedia nachschlagen",
        "/youtube":         "▶️   /youtube <url>         — YouTube Video analysieren",
        "/pdf":             "📄  /pdf                    — PDF-Datei analysieren",
        "/code":            "💻  /code <beschreibung>    — Code in Wissensbasis suchen",
        "/run":             "▶   /run <python>           — Python ausführen",
        "/files":           "📁  /files                  — Erstellte Dateien",
        "/learn":           "🧠  /learn <text>           — Text direkt lernen",
        "/todo":            "✅  /todo <aufgabe>         — TODO hinzufügen",
        "/todos":           "📋  /todos                  — TODOs anzeigen",
        "/done":            "✅  /done <nummer>          — TODO abhaken",
        "/timer":           "⏱   /timer <sekunden> <msg> — Timer stellen",
        "/profile":         "👤  /profile <name>         — KI-Profil wechseln",
        "/profiles":        "👤  /profiles               — Alle Profile anzeigen",
        "/speak":           "🔊  /speak <text>           — Text vorlesen (ElevenLabs)",
        "/bot":             "🤖  /bot <name>            — Bot erstellen/ausführen",
        "/bots":            "📋  /bots                  — Alle Bots anzeigen",
        "/crypto":          "🪙  /crypto                — Crypto-Guesser öffnen",
        "/memory":          "🧠  /memory                 — Gedächtnis anzeigen",
        "/forget":          "🗑  /forget                 — Gedächtnis löschen",
        "/theme":           "🎨  /theme <name>           — Theme wechseln",
        "/clear":           "🗑  /clear                  — Chat leeren",
        "/zusammenfassung": "📝  /zusammenfassung        — Chat zusammenfassen",
        "/help":            "❓  /help                   — Alle Befehle",
        "/repos":           "📦  /repos                  — Repos anzeigen",
        "/langs":           "🔷  /langs                  — Sprachen anzeigen",
    }

    def _handle_command(self, text):
        """Gibt True zurück wenn Befehl erkannt, False wenn normal weiter."""
        parts = text.strip().split(None, 1)
        cmd   = parts[0].lower()
        arg   = parts[1].strip() if len(parts) > 1 else ""

        if cmd == "/help":
            lines = "Verfügbare Befehle:\n\n"
            for c, desc in self.COMMANDS.items():
                lines += f"  {desc}\n"
            self._print_msg(AI_NAME, lines)
            return True

        if cmd == "/github":
            if not arg:
                self._print_msg(AI_NAME, "Benutzung: /github user/repo  z.B. /github microsoft/vscode")
                return True
            # URL bauen
            url = arg if arg.startswith("http") else f"https://github.com/{arg}"
            self.github_url_entry.delete(0,"end")
            self.github_url_entry.insert(0, url)
            self._clone_github_repo()
            return True

        if cmd == "/search":
            if not arg:
                self._print_msg(AI_NAME, "Benutzung: /search <suchbegriff>")
                return True
            self.is_typing=True
            self.send_btn.configure(state="disabled")
            self.ghost.set_state(GhostCanvas.THINK)
            threading.Thread(target=self._web_search, args=(arg,), daemon=True).start()
            return True

        if cmd == "/code":
            if not arg:
                self._print_msg(AI_NAME, "Benutzung: /code <was du suchst>  z.B. /code bubble sort")
                return True
            results = self._search_learned_code(arg)
            self._print_msg(AI_NAME, results)
            return True

        if cmd == "/files":
            files = list(Path(FILES_FOLDER).glob("*"))
            if not files:
                self._print_msg(AI_NAME, "Noch keine Dateien erstellt.")
            else:
                msg = f"Erstellte Dateien ({len(files)}):\n\n"
                for f in sorted(files)[-20:]:
                    msg += f"  📄  {f.name}  ({f.stat().st_size} Bytes)\n"
                self._print_msg(AI_NAME, msg)
                self._open_file_btn(str(Path(FILES_FOLDER).resolve()))
            return True

        if cmd == "/learn":
            if not arg:
                self._print_msg(AI_NAME, "Benutzung: /learn <text>")
                return True
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            Path(LEARN_FOLDER, f"cmd_{ts}.txt").write_text(arg, encoding="utf-8")
            self._load_learn_folder()
            self._print_msg(AI_NAME, f"✓ Gelernt! ({len(arg)} Zeichen)")
            self.ghost.set_state(GhostCanvas.HAPPY)
            self.after(2000, lambda: self.ghost.set_state(GhostCanvas.IDLE))
            return True

        if cmd == "/clear":
            self._clear_chatbox()
            self.chat_history = []
            self.current_entry = None
            self._sys_msg("Chat geleert ✨")
            return True

        if cmd == "/repos":
            if not self.learned_repos:
                self._print_msg(AI_NAME, "Noch keine Repos geladen. Benutze /github user/repo")
            else:
                msg = f"Geladene Repos ({len(self.learned_repos)}):\n\n"
                for r in self.learned_repos:
                    msg += (f"  🐙  {r['repo']}  [{r['language']}  ⭐{r['stars']}]\n"
                            f"     {r['description'][:60]}\n"
                            f"     {r['files_loaded']} Dateien\n\n")
                self._print_msg(AI_NAME, msg)
            return True

        if cmd == "/langs":
            if not self.learned_code:
                self._print_msg(AI_NAME, "Noch kein Code gelernt.")
            else:
                langs = {}
                for _, lang, content in self.learned_code:
                    langs[lang] = langs.get(lang,0) + 1
                msg = f"Gelernte Sprachen ({len(langs)}):\n\n"
                for lang, count in sorted(langs.items(), key=lambda x:-x[1]):
                    msg += f"  🔷  {lang:15}  {count} Datei(en)\n"
                self._print_msg(AI_NAME, msg)
            return True

        if cmd == "/memory":
            self._refresh_memory_box()
            d = self.memory.data
            msg = f"🧠  Gedächtnis ({len(d.get('facts',[]))} Fakten):\n\n"
            if d.get("name"): msg += f"  Name: {d['name']}\n"
            msg += f"  Sitzungen: {d.get('session_count',0)}\n"
            for f in d.get("facts",[])[-15:]:
                msg += f"  • {f}\n"
            if not d.get("facts") and not d.get("name"):
                msg += "  (Noch leer — einfach erzählen wer du bist!)"
            self._print_msg(AI_NAME, msg)
            return True

        if cmd == "/forget":
            self._clear_memory()
            self._print_msg(AI_NAME, "🗑  Gedächtnis gelöscht. Frischer Start!")
            return True

        if cmd == "/theme":
            if not arg:
                names = ", ".join(THEMES.keys())
                self._print_msg(AI_NAME, f"Verfügbare Themes:\n{names}\n\nBeispiel: /theme 🌊 Ocean")
                return True
            # Ähnlichstes Theme finden
            match = next((t for t in THEMES if arg.lower() in t.lower()), None)
            if match:
                self._apply_theme(match)
            else:
                self._print_msg(AI_NAME, f"Theme '{arg}' nicht gefunden. Verfügbar: {', '.join(THEMES.keys())}")
            return True

        if cmd == "/run":
            if not arg:
                self._print_msg(AI_NAME, "Benutzung: /run print('Hallo Welt')")
                return True
            self._run_python(arg)
            return True

        if cmd == "/wiki":
            if not arg:
                self._print_msg(AI_NAME, "Benutzung: /wiki Python Programmierung")
                return True
            self.is_typing=True; self.send_btn.configure(state="disabled")
            self.ghost.set_state(GhostCanvas.THINK)
            threading.Thread(target=self._wiki_search, args=(arg,), daemon=True).start()
            return True

        if cmd == "/youtube":
            if not arg:
                self._print_msg(AI_NAME, "Benutzung: /youtube https://youtube.com/watch?v=...")
                return True
            self.is_typing=True; self.send_btn.configure(state="disabled")
            self.ghost.set_state(GhostCanvas.THINK)
            threading.Thread(target=self._youtube_analyze, args=(arg,), daemon=True).start()
            return True

        if cmd == "/pdf":
            path = filedialog.askopenfilename(
                title="PDF auswählen",
                filetypes=[("PDF","*.pdf"),("Alle","*.*")])
            if not path: return True
            self.is_typing=True; self.send_btn.configure(state="disabled")
            self.ghost.set_state(GhostCanvas.THINK)
            threading.Thread(target=self._analyze_pdf, args=(path, arg), daemon=True).start()
            return True

        if cmd == "/todo":
            if not arg:
                self._print_msg(AI_NAME, "Benutzung: /todo Einkaufen gehen  oder  /todo Meeting @2025-06-01")
                return True
            due = None
            due_m = re.search(r'@(\d{4}-\d{2}-\d{2})', arg)
            if due_m:
                due = due_m.group(1)
                arg = arg.replace(due_m.group(0), "").strip()
            self.todos.add(arg, due)
            self._print_msg(AI_NAME, f"✅  TODO: {arg}" + (f"  📅 {due}" if due else ""))
            return True

        if cmd == "/todos":
            self._print_msg(AI_NAME, "📋  TODOs:\n\n" + self.todos.format_list())
            return True

        if cmd == "/done":
            try:
                idx = int(arg) - 1
                if self.todos.done(idx):
                    self._print_msg(AI_NAME, f"✅  TODO #{int(arg)} erledigt! 🎉")
                else:
                    self._print_msg(AI_NAME, "Ungültige Nummer.")
            except ValueError:
                self._print_msg(AI_NAME, "Benutzung: /done 1")
            return True

        if cmd == "/timer":
            parts2 = arg.split(None, 1)
            try:
                secs = int(parts2[0])
                msg  = parts2[1] if len(parts2) > 1 else "⏱ Zeit ist um!"
                self._set_timer(secs, msg)
                mins = secs // 60; rest = secs % 60
                time_str = f"{mins}m {rest}s" if mins else f"{secs}s"
                self._print_msg(AI_NAME, f"⏱  Timer: {time_str} — '{msg}'")
            except (ValueError, IndexError):
                self._print_msg(AI_NAME, "Benutzung: /timer 60 Pause vorbei!")
            return True

        if cmd == "/profile":
            if not arg:
                self._print_msg(AI_NAME,
                    f"Aktives Profil: {self.profiles.active}\n\n"
                    "Alle: " + ", ".join(self.profiles.profiles.keys()))
                return True
            match = next((p for p in self.profiles.profiles if arg.lower() in p.lower()), None)
            if match:
                self.profiles.active = match
                self._print_msg(AI_NAME, f"👤  Profil: {match}")
                self.ghost.set_state(GhostCanvas.HAPPY)
                self.after(2000, lambda: self.ghost.set_state(GhostCanvas.IDLE))
            else:
                self._print_msg(AI_NAME, "Nicht gefunden. Verfügbar: " +
                    ", ".join(self.profiles.profiles.keys()))
            return True

        if cmd == "/profiles":
            msg = "👤  Profile:\n\n"
            for name, data in self.profiles.profiles.items():
                active = "  ◀ aktiv" if name == self.profiles.active else ""
                msg += f"  {name}{active}\n     {data['system'][:70]}...\n\n"
            self._print_msg(AI_NAME, msg)
            return True

        if cmd == "/speak":
            if not arg:
                self._print_msg(AI_NAME, "Benutzung: /speak Hallo! Wie geht es dir?")
                return True
            if not self.apis.has("elevenlabs"):
                self._print_msg(AI_NAME,
                    "🔊  ElevenLabs Key fehlt!\n"
                    "    Einstellungen → APIs → ElevenLabs eintragen.\n"
                    "    Kostenlos: https://elevenlabs.io")
                return True
            threading.Thread(target=self._tts_elevenlabs, args=(arg,), daemon=True).start()
            return True

        if cmd == "/model":
            if not arg:
                self._print_msg(AI_NAME,
                    f"Aktuell: {self.selected_model.get()}\n"
                    "Wechseln: /model llama3  /model claude  /model gemini  /model gpt4")
                return True
            self._switch_model(arg)
            return True

        if cmd == "/bots":
            bots = self.bot_manager.bots
            if not bots:
                self._print_msg(AI_NAME, "Keine Bots. Erstelle einen mit /bot oder 🤖-Button!")
                return True
            msg = f"🤖  Bots ({len(bots)}):\n\n"
            for b in bots:
                status = "● läuft" if b.get("running") else "○ gestoppt"
                msg += f"  {b['name']}  [{status}]\n  {b['desc']}\n\n"
            self._print_msg(AI_NAME, msg)
            return True

        if cmd == "/bot":
            if not arg:
                self._open_bot_dialog()
                return True
            # Bot nach Name suchen und ausführen
            bot = next((b for b in self.bot_manager.bots
                        if arg.lower() in b["name"].lower()), None)
            if bot:
                self._run_bot(bot)
            else:
                self._print_msg(AI_NAME, f"Bot '{arg}' nicht gefunden. /bots zeigt alle Bots.")
            return True

        if cmd == "/crypto":
            self._open_crypto()
            return True

        return False  # kein Befehl erkannt

    def _search_learned_code(self, query):
        """Sucht in gelernten Code-Dateien nach ähnlichen Mustern."""
        if not self.learned_code:
            return "Noch kein Code gelernt. Benutze /github oder lade Dateien im Lernen-Tab."

        query_words = query.lower().split()
        results = []

        for fname, lang, content in self.learned_code:
            score = 0
            lower = content.lower()
            for word in query_words:
                score += lower.count(word)
            if score > 0:
                # Relevante Zeile finden
                best_line = ""
                best_score = 0
                for line in content.split("\n"):
                    s = sum(line.lower().count(w) for w in query_words)
                    if s > best_score:
                        best_score = s
                        best_line = line.strip()
                results.append((score, fname, lang, best_line[:80], content))

        if not results:
            return f"Nichts gefunden für '{query}' in {len(self.learned_code)} Code-Dateien."

        results.sort(key=lambda x: -x[0])
        top = results[:3]

        msg = f"🔍  Gefunden für '{query}':\n\n"
        for score, fname, lang, best_line, content in top:
            msg += f"  📄  {fname}  [{lang}]\n"
            msg += f"     Relevanz: {'█' * min(score,10)}  ({score} Treffer)\n"
            if best_line:
                msg += f"     → {best_line}\n"
            msg += "\n"

        msg += f"Soll ich Code ähnlich wie in diesen Dateien schreiben? Sag einfach was du brauchst!"

        # Top-Ergebnis als Extra-Kontext in nächste Anfrage injizieren
        if top:
            _, _, lang, _, content = top[0]
            snippet = "\n".join(content.split("\n")[:30])
            self.chat_history.append({
                "role": "system",
                "content": f"[Relevanter Code aus Wissensbasis — {lang}]\n{snippet}"
            })

        return msg

    def _web_search(self, query):
        """Sucht im Internet über DuckDuckGo API."""
        try:
            self.after(0, lambda: self._sys_msg(f"🔍  Suche: {query}..."))

            # DuckDuckGo Instant Answer API (kein Key nötig)
            resp = requests.get(
                "https://api.duckduckgo.com/",
                params={"q": query, "format": "json", "no_html": "1",
                        "skip_disambig": "1", "no_redirect": "1"},
                headers={"User-Agent": "Ghostfish/1.0"},
                timeout=10)
            resp.raise_for_status()
            data = resp.json()

            results = []

            # Abstract
            if data.get("AbstractText"):
                results.append(f"📖  {data['AbstractText'][:400]}")
                if data.get("AbstractURL"):
                    results.append(f"   Quelle: {data['AbstractURL']}")

            # Related Topics
            topics = data.get("RelatedTopics", [])[:5]
            if topics:
                results.append("\n🔗  Verwandte Themen:")
                for t in topics:
                    if isinstance(t, dict) and t.get("Text"):
                        results.append(f"   • {t['Text'][:120]}")

            # Answer (z.B. Berechnungen)
            if data.get("Answer"):
                results.insert(0, f"✅  {data['Answer']}")

            if not results:
                # Fallback: Web-Suche über HTML-Scraping
                results = self._ddg_web_search(query)

            search_text = "\n".join(results) if results else f"Keine direkten Ergebnisse für '{query}'."

            # Ergebnis an Ollama weitergeben für bessere Antwort
            extra = f"[Suchergebnis für '{query}']\n{search_text}"
            self.chat_history.append({"role":"user","content":
                f"Ich habe nach '{query}' gesucht. Hier sind die Ergebnisse:\n\n{search_text}\n\nFasse das kurz zusammen und ergänze was du weißt."})

            self.after(0, lambda: self._print_msg("🔍 Suche", search_text[:600]))

            # Ollama fragen
            sys_prompt = self._build_system_prompt()
            msgs = [{"role":"system","content":sys_prompt}] + self.chat_history[-10:]
            resp2 = requests.post(
                f"{OLLAMA_URL}/api/chat",
                json={"model":self.selected_model.get(),"messages":msgs,
                      "stream":False,"options":{"temperature":0.7}},
                timeout=120)
            if resp2.ok:
                reply = resp2.json()["message"]["content"]
                self.chat_history.append({"role":"assistant","content":reply})
                self.after(0, lambda: self._print_msg(AI_NAME, reply))
                self.after(0, self._autosave_current)

        except Exception as e:
            self.after(0, lambda: self._chat_insert(f"\n  ❌  Suche fehlgeschlagen: {e}\n","err_msg"))
        finally:
            self.is_typing = False
            self.after(0, lambda: self.send_btn.configure(state="normal"))
            self.after(0, lambda: self.ghost.set_state(GhostCanvas.IDLE))

    def _ddg_web_search(self, query):
        """Fallback: DuckDuckGo HTML-Lite Suche."""
        try:
            resp = requests.get(
                "https://html.duckduckgo.com/html/",
                params={"q": query},
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
                timeout=10)
            # Einfaches Parsen ohne beautifulsoup
            text = resp.text
            results = []
            # Ergebnis-Snippets extrahieren
            snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</a>', text, re.DOTALL)
            titles   = re.findall(r'class="result__a"[^>]*>(.*?)</a>', text, re.DOTALL)
            for i, (title, snippet) in enumerate(zip(titles[:4], snippets[:4])):
                title   = re.sub(r'<[^>]+>','', title).strip()
                snippet = re.sub(r'<[^>]+>','', snippet).strip()
                results.append(f"  {i+1}. {title}\n     {snippet[:150]}")
            return results
        except Exception:
            return []

    def _send_message(self):
        if self.is_typing: return
        text = self.input_box.get("1.0","end").strip()
        has_img = self.pending_image is not None
        if not text and not has_img: return

        self.input_box.delete("1.0","end")
        self._print_msg("Du", text or "(Bild gesendet)", is_user=True)
        if has_img:
            self._chat_insert(f"  📷  {Path(self.pending_image[0]).name}\n","img_msg")

        # ── Befehl prüfen ─────────────────────────────────────────────────────
        if text.startswith("/"):
            if self._handle_command(text):
                return  # Befehl wurde verarbeitet

        # ── Autocomplete Hinweis: wenn Nutzer "suche" oder "such" schreibt ───
        low = text.lower()
        if any(w in low for w in ["such im internet","google","such online","suche nach"]):
            # Automatisch /search nutzen
            query = re.sub(r'such\w*\s*(im\s*internet|online|nach|:)?\s*', '', low, flags=re.I).strip()
            if query:
                self.is_typing=True
                self.send_btn.configure(state="disabled")
                self.ghost.set_state(GhostCanvas.THINK)
                self.chat_history.append({"role":"user","content":text})
                threading.Thread(target=self._web_search, args=(query,), daemon=True).start()
                return

        img_b64 = self.pending_image[1] if has_img else None
        if has_img: self._clear_image()

        # ── Auto-Internet erkennen ────────────────────────────────────────────
        auto_search_words = ["aktuell","heute","news","wetter","preis","aktie",
                             "live","gerade","current","latest","today","weather",
                             "stock","kurs","bitcoin","ethereum","crypto"]
        needs_search = (not text.startswith("/") and not has_img and
                        any(w in text.lower() for w in auto_search_words))

        if needs_search:
            self._sys_msg(f"🔍  Auto-Suche...")
            search_result = self._quick_web_search(text)
            if search_result:
                self.chat_history.append({
                    "role":"user",
                    "content": f"{text}\n\n[Suchergebnis]:\n{search_result}"
                })
            else:
                self.chat_history.append({"role":"user","content":text,"_img":img_b64})
        else:
            self.chat_history.append({"role":"user","content":text or "Beschreibe dieses Bild.","_img":img_b64})

        self.word_count += len(text.split())
        if self.word_count >= 60:
            self._auto_learn(); self.word_count=0

        self.is_typing=True
        self.send_btn.configure(state="disabled")
        self.ghost.set_state(GhostCanvas.THINK)
        threading.Thread(target=self._query_ollama,args=(text,img_b64),daemon=True).start()

    def _query_ollama(self, user_text, img_b64):
        # Fakten aus Nutzernachricht extrahieren
        if user_text:
            self.memory.extract_facts(user_text)

        model = self.selected_model.get()

        # ── Externe APIs ──────────────────────────────────────────────────────
        if model == "claude-via-api":
            threading.Thread(target=self._query_claude,
                             args=(user_text,), daemon=True).start()
            return
        if model == "gemini-via-api":
            threading.Thread(target=self._query_gemini,
                             args=(user_text,), daemon=True).start()
            return
        if model in ("gpt-4o-mini","gpt-4o","gpt-3.5-turbo"):
            threading.Thread(target=self._query_openai,
                             args=(user_text, model), daemon=True).start()
            return

        try:
            has_image = img_b64 is not None

            # ── MoE Router: besten Agent + Modell wählen ──────────────────────
            task = self.moe.detect_task(user_text or "", has_image)
            node_url, routed_model, node_name, node_icon, node_id =                 self.moe.route(task, force_model=model if model != "qwen2.5:latest" else None)

            # Zeige welcher Agent antwortet
            if node_id != "local":
                self.after(0, lambda: self._sys_msg(
                    f"{node_icon}  Agent: {node_name}  |  Modell: {routed_model}  |  Aufgabe: {task}"))
            elif task == "code":
                self.after(0, lambda: self._sys_msg(
                    f"💻  Code-Expert: {routed_model}"))

            # ── Bild-spezifischer System-Prompt ──────────────────────────────
            if has_image:
                img_sys = (
                    "Du analysierst ein Bild. WICHTIGE REGELN:\n"
                    "- Beschreibe NUR was du WIRKLICH siehst — nichts erfinden\n"
                    "- Wenn du unsicher bist → sag 'ich bin nicht sicher ob...'\n"
                    "- Keine Annahmen über Personen, Namen, Orte wenn nicht klar sichtbar\n"
                    "- Kurz und präzise. Kein erfundener Kontext.\n"
                    "- Auf Deutsch antworten, kurz wie eine WhatsApp-Nachricht"
                )
                sys_prompt = img_sys
                temp  = 0.1
                top_p = 0.8
            else:
                sys_prompt = self._build_system_prompt()
                temp  = self.profiles.get_temp()
                top_p = 0.92

            msgs = [{"role":"system","content":sys_prompt}]
            for m in self.chat_history[-16:]:
                entry = {"role":m["role"],"content":m["content"]}
                if m.get("_img") and m["role"]=="user":
                    entry["images"]=[m["_img"]]
                msgs.append(entry)
            if img_b64 and msgs:
                msgs[-1]["images"]=[img_b64]

            # Bild-Modell-Warnung
            cur_model = self.selected_model.get()
            vision_models = ["llava","llava-phi3","llava:13b","moondream","bakllava",
                             "qwen2.5-vl","minicpm-v","llama3.2-vision"]
            if has_image and not any(v in cur_model for v in vision_models):
                self.after(0, lambda: self._sys_msg(
                    f"⚠️  '{cur_model}' unterstützt keine Bilder!\n"
                    "    Für Bilder: ollama pull llava\n"
                    "    Oder:       ollama pull qwen2.5-vl"))

            # ── Streaming via MoE Router (node_url + routed_model) ───────────
            resp = requests.post(
                f"{node_url}/api/chat",
                json={"model": routed_model,
                      "messages": msgs,
                      "stream": True,
                      "options": {
                          "temperature": temp,
                          "top_p": top_p,
                          "repeat_penalty": 1.15,
                          "num_predict": 512,
                      }},
                timeout=300,
                stream=True)
            resp.raise_for_status()

            self.after(0, self._stream_start)

            full_reply = ""
            for line in resp.iter_lines():
                if not line: continue
                try:
                    chunk = json.loads(line.decode("utf-8"))
                    token = chunk.get("message",{}).get("content","")
                    if token:
                        full_reply += token
                        self.after(0, lambda t=token: self._stream_append(t))
                    if chunk.get("done"):
                        break
                except Exception:
                    continue

            reply = full_reply.strip()
            if has_image:
                reply = self._filter_hallucination(reply)

            # ── Zufälligen Code filtern ───────────────────────────────────────
            # Wenn die Nutzer-Nachricht NICHT nach Code fragt → Code-Blöcke entfernen
            code_keywords = ["code","programm","script","funktion","schreib","erstell",
                             "mach mir","zeig mir","def ","class ","function","import ",
                             "#include","<!doctype","/youtube","/pdf","/wiki"]
            user_wants_code = any(k in user_text.lower() for k in code_keywords)

            if not user_wants_code:
                # Entferne versehentliche Code-Blöcke
                reply = re.sub(r'```[\w]*\n.*?```', '', reply, flags=re.DOTALL).strip()
                # Entferne DATEI_START Blöcke
                reply = re.sub(r'DATEI_START.*?DATEI_ENDE', '', reply, flags=re.DOTALL).strip()
                # Entferne zufällige Einzel-Code-Zeilen (def, class, for usw. am Zeilenanfang)
                lines = reply.split('\n')
                clean_lines = []
                for line in lines:
                    stripped = line.strip()
                    is_code_line = any(stripped.startswith(kw) for kw in
                        ['def ','class ','for ','while ','if __','import ','from ',
                         '#include','int main','public class','func ','fn '])
                    if not is_code_line:
                        clean_lines.append(line)
                reply = '\n'.join(clean_lines).strip()
                if not reply:
                    reply = "hmm, da ist was schiefgelaufen 😅 versuch nochmal"

            for m in self.chat_history: m.pop("_img",None)
            self.chat_history.append({"role":"assistant","content":reply})

            # Syntax-Highlighting
            self.after(100, lambda: self._highlight_chat_code(reply))

            # Autosave
            self.after(0, self._autosave_current)
            self.after(0, self._render_history)

            # Dateien nur speichern wenn Code gewollt
            saved = []
            if user_wants_code:
                saved = self._extract_files(reply)
                for fp in saved:
                    self.after(0, lambda p=fp: self._chat_insert(f"\n  📁  Datei: {p}\n","file_msg"))
                    self.after(0, lambda p=fp: self._open_file_btn(p))
                if "```" in reply:
                    self.after(200, lambda: self._add_run_buttons(reply))

            # Auto-TTS wenn aktiviert
            if self.tts_var.get() and reply and not saved:
                tts_text = reply[:300]  # max 300 Zeichen sprechen
                threading.Thread(target=self._tts_elevenlabs,
                                 args=(tts_text,), daemon=True).start()

            positive = any(w in reply.lower() for w in
                ["super","toll","danke","haha","lol","nice","cool","freue","wow","😊","😄","🎉"])

            self.after(0, lambda: self.ghost.set_state(
                GhostCanvas.HAPPY if (positive or saved) else GhostCanvas.TALK))
            self.after(2500, lambda: self.ghost.set_state(GhostCanvas.IDLE))

        except requests.exceptions.ConnectionError:
            self.after(0, lambda: self._chat_insert(
                "\n  ❌  Ollama nicht erreichbar!\n"
                "  → $env:OLLAMA_ORIGINS='*'; ollama serve\n","err_msg"))
            self.after(0, lambda: self.ghost.set_state(GhostCanvas.IDLE))
        except Exception as e:
            self.after(0, lambda: self._chat_insert(f"\n  ❌ {e}\n","err_msg"))
            self.after(0, lambda: self.ghost.set_state(GhostCanvas.IDLE))
        finally:
            self.is_typing=False
            self.after(0, lambda: self.send_btn.configure(state="normal"))

    # ── Claude (Anthropic) ────────────────────────────────────────────────────
    def _query_claude(self, user_text):
        key = self.apis.get("anthropic")
        try:
            self.after(0, self._stream_start)
            sys_p = self._build_system_prompt()
            msgs  = [{"role":m["role"],"content":m["content"]}
                     for m in self.chat_history[-14:]]

            resp = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={"x-api-key":key,"anthropic-version":"2023-06-01",
                         "content-type":"application/json"},
                json={"model":"claude-sonnet-4-20250514","max_tokens":2048,
                      "system":sys_p,"messages":msgs,"stream":True},
                timeout=120, stream=True)

            if resp.status_code == 401:
                self.after(0, lambda: self._chat_insert(
                    "\n  ❌  Claude: Ungültiger API-Key. Einstellungen → APIs prüfen.\n","err_msg"))
                return

            full = ""
            for line in resp.iter_lines():
                if not line: continue
                line = line.decode("utf-8")
                if line.startswith("data: "):
                    try:
                        data = json.loads(line[6:])
                        token = data.get("delta",{}).get("text","")
                        if token:
                            full += token
                            self.after(0, lambda t=token: self._stream_append(t))
                    except: continue

            self.chat_history.append({"role":"assistant","content":full})
            if "```" in full:
                self.after(200, lambda: self._add_run_buttons(full))
            self.after(0, self._autosave_current)

        except Exception as e:
            self.after(0, lambda: self._chat_insert(f"\n  ❌ Claude: {e}\n","err_msg"))
        finally:
            self.is_typing=False
            self.after(0, lambda: self.send_btn.configure(state="normal"))
            self.after(0, lambda: self.ghost.set_state(GhostCanvas.IDLE))

    # ── Gemini (Google) ───────────────────────────────────────────────────────
    def _query_gemini(self, user_text):
        key = self.apis.get("gemini")
        try:
            self.after(0, self._stream_start)
            sys_p = self._build_system_prompt()
            # Gemini Format
            contents = []
            for m in self.chat_history[-14:]:
                role = "user" if m["role"]=="user" else "model"
                contents.append({"role":role,"parts":[{"text":m["content"]}]})

            resp = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/"
                f"gemini-1.5-flash:streamGenerateContent?key={key}&alt=sse",
                json={"system_instruction":{"parts":[{"text":sys_p}]},
                      "contents":contents,
                      "generationConfig":{"temperature":self.profiles.get_temp()}},
                timeout=120, stream=True)

            if resp.status_code == 400:
                self.after(0, lambda: self._chat_insert(
                    "\n  ❌  Gemini: Ungültiger Key oder API nicht aktiviert.\n","err_msg"))
                return

            full = ""
            for line in resp.iter_lines():
                if not line: continue
                line = line.decode("utf-8")
                if line.startswith("data: "):
                    try:
                        data = json.loads(line[6:])
                        token = (data.get("candidates",[{}])[0]
                                 .get("content",{}).get("parts",[{}])[0].get("text",""))
                        if token:
                            full += token
                            self.after(0, lambda t=token: self._stream_append(t))
                    except: continue

            self.chat_history.append({"role":"assistant","content":full})
            if "```" in full:
                self.after(200, lambda: self._add_run_buttons(full))
            self.after(0, self._autosave_current)

        except Exception as e:
            self.after(0, lambda: self._chat_insert(f"\n  ❌ Gemini: {e}\n","err_msg"))
        finally:
            self.is_typing=False
            self.after(0, lambda: self.send_btn.configure(state="normal"))
            self.after(0, lambda: self.ghost.set_state(GhostCanvas.IDLE))

    # ── OpenAI (GPT) ──────────────────────────────────────────────────────────
    def _query_openai(self, user_text, model):
        key = self.apis.get("openai")
        try:
            self.after(0, self._stream_start)
            sys_p = self._build_system_prompt()
            msgs  = [{"role":"system","content":sys_p}]
            msgs += [{"role":m["role"],"content":m["content"]}
                     for m in self.chat_history[-14:]]

            resp = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"},
                json={"model":model,"messages":msgs,"stream":True,
                      "temperature":self.profiles.get_temp()},
                timeout=120, stream=True)

            if resp.status_code == 401:
                self.after(0, lambda: self._chat_insert(
                    "\n  ❌  OpenAI: Ungültiger API-Key.\n","err_msg"))
                return

            full = ""
            for line in resp.iter_lines():
                if not line: continue
                line = line.decode("utf-8")
                if line.startswith("data: ") and "[DONE]" not in line:
                    try:
                        data  = json.loads(line[6:])
                        token = data["choices"][0].get("delta",{}).get("content","")
                        if token:
                            full += token
                            self.after(0, lambda t=token: self._stream_append(t))
                    except: continue

            self.chat_history.append({"role":"assistant","content":full})
            if "```" in full:
                self.after(200, lambda: self._add_run_buttons(full))
            self.after(0, self._autosave_current)

        except Exception as e:
            self.after(0, lambda: self._chat_insert(f"\n  ❌ OpenAI: {e}\n","err_msg"))
        finally:
            self.is_typing=False
            self.after(0, lambda: self.send_btn.configure(state="normal"))
            self.after(0, lambda: self.ghost.set_state(GhostCanvas.IDLE))

    # ── Halluzinations-Filter ─────────────────────────────────────────────────
    def _filter_hallucination(self, text):
        """Entfernt nur eindeutige Halluzinations-Muster, keine validen Beschreibungen."""
        if not text:
            return text

        lines = text.split('\n')
        clean = []

        # Nur sehr eindeutige Halluzinations-Muster entfernen
        hard_hallucination = [
            r'the (name|title|label) (is|says|reads) ["\'][\w\s]+["\']',
            r'(copyright|©|trademark|®)\s*\d{4}',
            r'I (can clearly|am able to) (confirm|verify) (that )?this is',
            r'based on (my|the) (training|knowledge),? (I|this)',
        ]

        for line in lines:
            skip = False
            for pattern in hard_hallucination:
                if re.search(pattern, line, re.I):
                    skip = True
                    break
            if not skip:
                clean.append(line)

        result = '\n'.join(clean).strip()
        return result if len(result) >= 10 else text

    # ── Streaming UI ──────────────────────────────────────────────────────────
    def _stream_start(self):
        """Inserts Ghostfish header and marks stream position."""
        self.chat_box.configure(state="normal")
        tb = self.chat_box._textbox
        tb.insert("end", f"\n  🐟 {AI_NAME}\n", "ai_name")
        tb.insert("end", "  ", "ai_msg")
        self._stream_msg_start = tb.index("end-1c")
        self.chat_box.configure(state="disabled")

    def _stream_append(self, token):
        """Hängt Token an laufende Antwort an."""
        self.chat_box.configure(state="normal")
        self.chat_box._textbox.insert("end", token, "ai_msg")
        self.chat_box.configure(state="disabled")
        self.chat_box._textbox.see("end")

    # ── Syntax-Highlighting ───────────────────────────────────────────────────
    def _highlight_chat_code(self, reply):
        """Hebt Code-Blöcke in der letzten Antwort hervor."""
        try:
            tb = self.chat_box._textbox
            self.chat_box.configure(state="normal")

            # Tags für Syntax
            for name, color in SYNTAX.items():
                tb.tag_configure(f"hl_{name}", foreground=color,
                                 font=("Courier",12))
            tb.tag_configure("hl_code_bg", background="#0d0d20",
                             font=("Courier",12))
            tb.tag_configure("hl_string", foreground=SYNTAX["string"],
                             font=("Courier",12))

            # Code-Blöcke finden und markieren
            content = tb.get("1.0","end")
            # Sprache erkennen
            lang = "python"
            for m in re.finditer(r'```(\w+)', reply):
                lang = m.group(1).lower()
                break

            kw_data = KEYWORDS.get(lang, KEYWORDS.get("python",{}))

            for match in re.finditer(r'```\w*\n?(.*?)```', reply, re.DOTALL):
                code = match.group(1)
                start_idx = content.find(code)
                if start_idx == -1: continue

                # Zeilen & Spalten berechnen
                before = content[:start_idx]
                row = before.count("\n") + 1
                col = len(before) - before.rfind("\n") - 1

                for i, line in enumerate(code.split("\n")):
                    r = row + i
                    # Keywords highlighten
                    for ktype, words in kw_data.items():
                        for word in words:
                            for wm in re.finditer(r'\b' + re.escape(word) + r'\b', line):
                                c0 = wm.start()
                                c1 = wm.end()
                                try:
                                    tb.tag_add(f"hl_{ktype}",
                                               f"{r}.{c0+col if i==0 else c0}",
                                               f"{r}.{c1+col if i==0 else c1}")
                                except: pass
                    # Strings
                    for sm in re.finditer(r'(["\'])(.*?)\1', line):
                        try:
                            tb.tag_add("hl_string",
                                       f"{r}.{sm.start()}",
                                       f"{r}.{sm.end()}")
                        except: pass
                    # Kommentare
                    for cm in re.finditer(r'(#|//|--).+$', line):
                        try:
                            tb.tag_add("hl_comment",
                                       f"{r}.{cm.start()}",
                                       f"{r}.{len(line)}")
                        except: pass

            self.chat_box.configure(state="disabled")
        except Exception:
            pass

    # ── Code ausführen ────────────────────────────────────────────────────────
    def _add_run_buttons(self, reply):
        """Fügt Run-Buttons unter Python-Code-Blöcken ein."""
        runnable = re.findall(r'```(?:python|py)\n(.*?)```', reply, re.DOTALL)
        for i, code in enumerate(runnable):
            code = code.strip()
            self.chat_box.configure(state="normal")
            btn = ctk.CTkButton(
                self.chat_box,
                text=f"  ▶  Python ausführen",
                command=lambda c=code: self._run_python(c),
                height=26, corner_radius=6,
                fg_color="#1a3020", hover_color="#2a4030",
                border_width=1, border_color=GREEN,
                text_color=GREEN, font=ctk.CTkFont(size=11))
            self.chat_box._textbox.window_create("end", window=btn)
            self.chat_box._textbox.insert("end", "\n")
            self.chat_box.configure(state="disabled")

    def _run_python(self, code):
        """Führt Python-Code aus und zeigt Output im Chat."""
        self._sys_msg("▶  Führe Python-Code aus...")
        def run():
            try:
                with tempfile.NamedTemporaryFile(mode="w", suffix=".py",
                                                 delete=False, encoding="utf-8") as f:
                    f.write(code)
                    tmp = f.name
                result = subprocess.run(
                    [sys.executable, tmp],
                    capture_output=True, text=True, timeout=15)
                Path(tmp).unlink(missing_ok=True)
                out = result.stdout.strip()
                err = result.stderr.strip()
                if out:
                    self.after(0, lambda: self._chat_insert(
                        f"\n  📤  Output:\n  {out}\n","ai_msg"))
                if err:
                    self.after(0, lambda: self._chat_insert(
                        f"\n  ⚠️  Fehler:\n  {err}\n","err_msg"))
                if not out and not err:
                    self.after(0, lambda: self._sys_msg("✓ Kein Output (Code lief durch)"))
            except subprocess.TimeoutExpired:
                self.after(0, lambda: self._chat_insert(
                    "\n  ⏱  Timeout nach 15 Sekunden.\n","err_msg"))
            except Exception as e:
                self.after(0, lambda: self._chat_insert(f"\n  ❌ {e}\n","err_msg"))
        threading.Thread(target=run, daemon=True).start()

    # ── Datei-Erkennung ───────────────────────────────────────────────────────
    def _extract_files(self, reply):
        saved=[]
        for fname, content in re.findall(
                r'DATEI_START\s*dateiname:\s*(.+?)\s*inhalt:\s*(.*?)\s*DATEI_ENDE',
                reply, re.DOTALL|re.IGNORECASE):
            fname = fname.strip().replace("/","_")
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            out = Path(FILES_FOLDER)/fname
            if out.exists():
                out = Path(FILES_FOLDER)/f"{Path(fname).stem}_{ts}{Path(fname).suffix}"
            out.write_text(content.strip(), encoding="utf-8")
            saved.append(str(out.resolve()))
        if not saved:
            ext_map={"python":"py","py":"py","c":"c","cpp":"cpp","javascript":"js",
                     "js":"js","html":"html","java":"java","rust":"rs","bash":"sh",
                     "go":"go","sql":"sql","json":"json","css":"css","txt":"txt"}
            ts=datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            for i,(lang,code) in enumerate(re.findall(r'```(\w*)\n(.*?)```',reply,re.DOTALL)):
                ext=ext_map.get(lang.lower(),"txt")
                out=Path(FILES_FOLDER)/f"code_{ts}_{i+1}.{ext}"
                out.write_text(code.strip(),encoding="utf-8")
                saved.append(str(out.resolve()))
        return saved

    def _open_file_btn(self, filepath):
        def open_it():
            if os.name=="nt": os.startfile(filepath)
            else: os.system(f"xdg-open '{filepath}'")
        self.chat_box.configure(state="normal")
        btn=ctk.CTkButton(
            self.chat_box, text=f"  📂  {Path(filepath).name}",
            command=open_it, height=26, corner_radius=6,
            fg_color=BG_INPUT, hover_color=BG_CARD,
            border_width=1, border_color=BLUE,
            text_color=BLUE, font=ctk.CTkFont(size=11), anchor="w")
        self.chat_box._textbox.window_create("end", window=btn)
        self.chat_box._textbox.insert("end","\n")
        self.chat_box.configure(state="disabled")
        self.chat_box._textbox.see("end")

    def _open_files_folder(self):
        folder=str(Path(FILES_FOLDER).resolve())
        if os.name=="nt": os.startfile(folder)
        else: os.system(f"xdg-open '{folder}'")

    # ── Lernen Tab ────────────────────────────────────────────────────────────
    def _build_learn_tab(self):
        tab = self.tabs.tab("🧠  Lernen")
        tab.grid_rowconfigure(5, weight=1)
        tab.grid_columnconfigure(0, weight=1)

        # ── Sub-Tabs: Text vs Code ────────────────────────────────────────────
        sub = ctk.CTkTabview(tab, fg_color=BG_CARD,
                             segmented_button_fg_color=BG_INPUT,
                             segmented_button_selected_color=ACCENT2,
                             segmented_button_selected_hover_color=ACCENT,
                             height=260)
        sub.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        sub.add("✍️  Text")
        sub.add("💻  Code-Dateien")
        self._build_text_learn_sub(sub.tab("✍️  Text"))
        self._build_code_learn_sub(sub.tab("💻  Code-Dateien"))

        # ── Code-Wissensbasis Anzeige ─────────────────────────────────────────
        hdr = ctk.CTkFrame(tab, fg_color="transparent")
        hdr.grid(row=1, column=0, sticky="ew")
        hdr.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(hdr, text="📚  Wissensbasis",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=TEXT_DIM).grid(row=0, column=0, sticky="w", pady=(0,4))

        # Stats-Zeile
        self.stats_frame = ctk.CTkFrame(tab, fg_color=BG_CARD, corner_radius=8)
        self.stats_frame.grid(row=2, column=0, sticky="ew", pady=(0,8))
        self.stats_frame.grid_columnconfigure((0,1,2,3), weight=1)

        self.stat_text  = self._stat_card(self.stats_frame, "Texte",      "0", 0)
        self.stat_code  = self._stat_card(self.stats_frame, "Code-Dateien","0", 1)
        self.stat_lines = self._stat_card(self.stats_frame, "Code-Zeilen", "0", 2)
        self.stat_langs = self._stat_card(self.stats_frame, "Sprachen",   "0", 3)

        # Dateiliste
        self.files_box = ctk.CTkTextbox(tab, state="disabled",
                                        font=ctk.CTkFont("Courier", 11),
                                        corner_radius=10, fg_color=BG_CARD)
        self.files_box.grid(row=3, column=0, sticky="nsew")
        tab.grid_rowconfigure(3, weight=1)

        # Löschen-Button unten
        ctk.CTkButton(tab, text="🗑  Alle Lern-Daten löschen",
                      command=self._clear_all_learn,
                      fg_color="transparent", border_width=1,
                      border_color=RED, text_color=RED,
                      hover_color=BG_CARD, font=ctk.CTkFont(size=11)
                      ).grid(row=4, column=0, sticky="e", pady=(6,0))

    def _stat_card(self, parent, label, value, col):
        f = ctk.CTkFrame(parent, fg_color=BG_INPUT, corner_radius=8)
        f.grid(row=0, column=col, padx=6, pady=8, sticky="ew")
        val_lbl = ctk.CTkLabel(f, text=value,
                               font=ctk.CTkFont("Helvetica", 20, "bold"),
                               text_color=ACCENT)
        val_lbl.pack(pady=(8,2))
        ctk.CTkLabel(f, text=label, font=ctk.CTkFont(size=10),
                     text_color=TEXT_DIM).pack(pady=(0,8))
        return val_lbl

    def _build_text_learn_sub(self, tab):
        tab.grid_rowconfigure(1, weight=1)
        tab.grid_columnconfigure(0, weight=1)
        self.learn_text = ctk.CTkTextbox(tab, height=100,
                                          font=ctk.CTkFont("Helvetica", 12),
                                          corner_radius=8, fg_color=BG_INPUT,
                                          border_color=ACCENT2, border_width=1)
        self.learn_text.grid(row=0, column=0, sticky="ew", pady=(4,8))
        self.learn_text.insert("1.0", "Hier deinen Text einfügen (WhatsApp, Kommentare, E-Mails usw.)...")

        br = ctk.CTkFrame(tab, fg_color="transparent")
        br.grid(row=1, column=0, sticky="w")
        ctk.CTkButton(br, text="✓  Text lernen", command=self._learn_text,
                      fg_color=ACCENT2, hover_color=ACCENT,
                      font=ctk.CTkFont(size=12)).pack(side="left", padx=(0,8))
        ctk.CTkButton(br, text="🗑  Leeren",
                      command=lambda: self.learn_text.delete("1.0","end"),
                      fg_color="transparent", border_width=1,
                      border_color=ACCENT2, text_color=ACCENT,
                      hover_color=BG_CARD).pack(side="left")

    def _build_code_learn_sub(self, tab):
        tab.grid_rowconfigure(4, weight=1)
        tab.grid_columnconfigure(0, weight=1)

        # ── GitHub Repo Bereich ───────────────────────────────────────────────
        gh_frame = ctk.CTkFrame(tab, fg_color=BG_CARD, corner_radius=10)
        gh_frame.grid(row=0, column=0, sticky="ew", pady=(4,10))
        gh_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(gh_frame, text="🐙  GitHub Repo",
                     font=ctk.CTkFont("Helvetica", 12, "bold"),
                     text_color=ACCENT).grid(row=0, column=0, columnspan=3,
                                             sticky="w", padx=12, pady=(10,6))

        ctk.CTkLabel(gh_frame, text="URL:",
                     font=ctk.CTkFont(size=11), text_color=TEXT_DIM
                     ).grid(row=1, column=0, padx=(12,6), pady=(0,8), sticky="w")

        self.github_url_entry = ctk.CTkEntry(
            gh_frame, placeholder_text="https://github.com/user/repo",
            fg_color=BG_INPUT, border_color=ACCENT2, border_width=1,
            font=ctk.CTkFont("Courier", 12))
        self.github_url_entry.grid(row=1, column=1, sticky="ew", padx=(0,8), pady=(0,8))

        self.github_btn = ctk.CTkButton(
            gh_frame, text="⬇  Laden",
            command=self._clone_github_repo,
            fg_color=ACCENT2, hover_color=ACCENT,
            font=ctk.CTkFont(size=12), width=90)
        self.github_btn.grid(row=1, column=2, padx=(0,12), pady=(0,8))

        self.github_status = ctk.CTkLabel(
            gh_frame, text="", font=ctk.CTkFont(size=11),
            text_color=TEXT_DIM, justify="left", wraplength=450)
        self.github_status.grid(row=2, column=0, columnspan=3,
                                padx=12, pady=(0,10), sticky="w")

        # ── Lokale Dateien ────────────────────────────────────────────────────
        ctk.CTkLabel(tab,
            text="Oder lokale Dateien / Ordner hinzufügen:",
            font=ctk.CTkFont(size=11), text_color=TEXT_DIM,
            justify="left").grid(row=1, column=0, sticky="w", pady=(0,6))

        btn_row = ctk.CTkFrame(tab, fg_color="transparent")
        btn_row.grid(row=2, column=0, sticky="ew", pady=(0,8))

        ctk.CTkButton(btn_row, text="📄  Datei(en)",
                      command=self._add_code_files,
                      fg_color=ACCENT2, hover_color=ACCENT,
                      font=ctk.CTkFont(size=12)).pack(side="left", padx=(0,8))

        ctk.CTkButton(btn_row, text="📁  Ordner",
                      command=self._add_code_folder,
                      fg_color="transparent", border_width=1,
                      border_color=ACCENT2, text_color=ACCENT,
                      hover_color=BG_CARD, font=ctk.CTkFont(size=12)).pack(side="left", padx=(0,8))

        ctk.CTkButton(btn_row, text="📂  Code-Ordner öffnen",
                      command=self._open_code_folder,
                      fg_color="transparent", border_width=1,
                      border_color=TEXT_DIM, text_color=TEXT_DIM,
                      hover_color=BG_CARD, font=ctk.CTkFont(size=11)).pack(side="left")

        # Unterstützte Formate
        ext_str = "  ".join(sorted(CODE_EXTENSIONS.keys()))
        ctk.CTkLabel(tab, text=f"Formate: {ext_str}",
                     font=ctk.CTkFont("Courier", 10), text_color=TEXT_DIM,
                     wraplength=500, justify="left").grid(row=3, column=0, sticky="w")

    def _learn_text(self):
        text = self.learn_text.get("1.0","end").strip()
        if len(text) < 15: return
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        Path(LEARN_FOLDER, f"eingabe_{ts}.txt").write_text(text, encoding="utf-8")
        self.learn_text.delete("1.0","end")
        self._load_learn_folder()
        self.ghost.set_state(GhostCanvas.HAPPY)
        self.after(2000, lambda: self.ghost.set_state(GhostCanvas.IDLE))

    # ── GitHub Repo klonen ────────────────────────────────────────────────────
    def _clone_github_repo(self):
        url = self.github_url_entry.get().strip().rstrip("/")
        if not url:
            self._gh_status("⚠️  Bitte GitHub URL eingeben.", RED)
            return

        # URL normalisieren
        if not url.startswith("http"):
            url = "https://github.com/" + url
        if not "github.com" in url:
            self._gh_status("⚠️  Nur GitHub URLs werden unterstützt.", RED)
            return

        # Repo-Name extrahieren
        parts = url.rstrip("/").split("/")
        if len(parts) < 2:
            self._gh_status("⚠️  Ungültige URL.", RED)
            return
        repo_name = parts[-1].replace(".git","")
        owner     = parts[-2] if len(parts) >= 2 else "unknown"

        self.github_btn.configure(state="disabled", text="⏳ Lädt...")
        self._gh_status(f"📡  Verbinde mit GitHub: {owner}/{repo_name}...", TEXT_DIM)
        self.ghost.set_state(GhostCanvas.THINK)

        threading.Thread(
            target=self._do_clone,
            args=(url, owner, repo_name),
            daemon=True
        ).start()

    def _do_clone(self, url, owner, repo_name):
        """Lädt das Repo über die GitHub API (kein git nötig!)."""
        try:
            # Repo-Info abrufen
            api_url  = f"https://api.github.com/repos/{owner}/{repo_name}"
            headers  = {"Accept": "application/vnd.github.v3+json",
                        "User-Agent": "Ghostfish"}

            info_resp = requests.get(api_url, headers=headers, timeout=15)
            if info_resp.status_code == 404:
                self.after(0, lambda: self._gh_status(
                    "❌  Repo nicht gefunden. Ist es öffentlich?", RED))
                return
            if info_resp.status_code == 403:
                self.after(0, lambda: self._gh_status(
                    "❌  GitHub Rate-Limit erreicht. Bitte 1 Minute warten.", RED))
                return
            info_resp.raise_for_status()
            info = info_resp.json()

            default_branch = info.get("default_branch","main")
            lang           = info.get("language","Unbekannt")
            stars          = info.get("stargazers_count",0)
            description    = info.get("description","") or ""

            self.after(0, lambda: self._gh_status(
                f"📦  {owner}/{repo_name}  [{lang}  ⭐{stars}]\n"
                f"    {description[:80]}\n"
                f"📂  Lese Dateiliste...", TEXT_DIM))

            # Dateibaum über API abrufen
            tree_url  = f"https://api.github.com/repos/{owner}/{repo_name}/git/trees/{default_branch}?recursive=1"
            tree_resp = requests.get(tree_url, headers=headers, timeout=20)
            tree_resp.raise_for_status()
            tree = tree_resp.json()

            if tree.get("truncated"):
                self.after(0, lambda: self._gh_status(
                    "⚠️  Repo sehr groß — lade nur die ersten Dateien.", "#fbbf24"))

            # Code-Dateien filtern
            blobs = [
                item for item in tree.get("tree",[])
                if item["type"] == "blob"
                and Path(item["path"]).suffix.lower() in CODE_EXTENSIONS
                and not any(skip in item["path"] for skip in [
                    "node_modules","vendor",".git","dist","build",
                    "__pycache__",".venv","venv","test","tests",
                    "spec","fixture","mock","migrations"
                ])
                and item.get("size",0) < 150_000  # max 150KB
            ]

            if not blobs:
                self.after(0, lambda: self._gh_status(
                    "⚠️  Keine Code-Dateien gefunden (oder alle zu groß).", "#fbbf24"))
                return

            # Max 80 Dateien laden
            blobs = blobs[:80]
            total  = len(blobs)
            loaded = 0
            errors = 0

            # Repo-Unterordner anlegen
            repo_dir = Path(CODE_FOLDER) / f"{owner}_{repo_name}"
            repo_dir.mkdir(exist_ok=True)

            for i, blob in enumerate(blobs):
                file_path = blob["path"]
                raw_url   = f"https://raw.githubusercontent.com/{owner}/{repo_name}/{default_branch}/{file_path}"

                self.after(0, lambda i=i, t=total: self._gh_status(
                    f"⬇️  Lade Dateien... {i+1}/{t}", TEXT_DIM))

                try:
                    r = requests.get(raw_url, headers=headers, timeout=15)
                    if r.status_code != 200:
                        errors += 1
                        continue

                    content = r.text.strip()
                    if len(content) < 20:
                        continue

                    # Ordnerstruktur beibehalten
                    out_path = repo_dir / Path(file_path).name
                    # Bei Namenskollision Pfad-Teil hinzufügen
                    if out_path.exists():
                        safe = file_path.replace("/","_")
                        out_path = repo_dir / safe

                    out_path.write_text(content, encoding="utf-8", errors="ignore")
                    loaded += 1

                except Exception:
                    errors += 1

            # README laden für Kontext
            for readme in ["README.md","readme.md","README.rst"]:
                try:
                    r = requests.get(
                        f"https://raw.githubusercontent.com/{owner}/{repo_name}/{default_branch}/{readme}",
                        headers=headers, timeout=10)
                    if r.status_code == 200:
                        (repo_dir / readme).write_text(r.text, encoding="utf-8", errors="ignore")
                        break
                except Exception:
                    pass

            # Repo-Info als .json speichern (für System-Prompt Kontext)
            meta = {
                "repo":        f"{owner}/{repo_name}",
                "url":         url,
                "language":    lang,
                "description": description,
                "stars":       stars,
                "files_loaded":loaded,
                "branch":      default_branch
            }
            (repo_dir / "_repo_info.json").write_text(
                json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

            self.after(0, lambda: self._gh_done(owner, repo_name, loaded, errors, lang))

        except requests.exceptions.ConnectionError:
            self.after(0, lambda: self._gh_status(
                "❌  Keine Internetverbindung.", RED))
        except Exception as e:
            self.after(0, lambda: self._gh_status(f"❌  Fehler: {e}", RED))
        finally:
            self.after(0, lambda: self.github_btn.configure(
                state="normal", text="⬇  Laden"))
            self.after(0, lambda: self.ghost.set_state(GhostCanvas.IDLE))

    def _gh_status(self, text, color=None):
        self.github_status.configure(text=text)
        if color:
            self.github_status.configure(text_color=color)

    def _gh_done(self, owner, repo_name, loaded, errors, lang):
        self._gh_status(
            f"✅  {owner}/{repo_name} gelernt!\n"
            f"    {loaded} Dateien geladen  •  {errors} Fehler  •  Sprache: {lang}",
            GREEN)
        self._load_learn_folder()
        self._sys_msg(
            f"✅  GitHub Repo '{owner}/{repo_name}' gelernt! "
            f"{loaded} Code-Dateien in der Wissensbasis.")
        self.ghost.set_state(GhostCanvas.HAPPY)
        self.after(3000, lambda: self.ghost.set_state(GhostCanvas.IDLE))

    def _add_code_files(self):
        """Einzelne oder mehrere Code-Dateien hinzufügen."""
        exts = " ".join(f"*{e}" for e in CODE_EXTENSIONS)
        paths = filedialog.askopenfilenames(
            title="Code-Dateien auswählen",
            filetypes=[("Code-Dateien", exts), ("Alle Dateien", "*.*")])
        if not paths: return
        count = 0
        for path in paths:
            count += self._copy_code_file(path)
        self._load_learn_folder()
        self._sys_msg(f"✓  {count} Code-Datei(en) gelernt!")
        self.ghost.set_state(GhostCanvas.HAPPY)
        self.after(2000, lambda: self.ghost.set_state(GhostCanvas.IDLE))

    def _add_code_folder(self):
        """Ganzen Ordner mit Code-Dateien rekursiv einlesen."""
        folder = filedialog.askdirectory(title="Code-Ordner auswählen")
        if not folder: return
        count = 0
        for ext in CODE_EXTENSIONS:
            for path in Path(folder).rglob(f"*{ext}"):
                # node_modules, .git usw. überspringen
                if any(p in str(path) for p in ["node_modules",".git","__pycache__",".venv","venv"]):
                    continue
                count += self._copy_code_file(str(path))
        self._load_learn_folder()
        self._sys_msg(f"✓  {count} Code-Dateien aus Ordner gelernt!")
        self.ghost.set_state(GhostCanvas.HAPPY)
        self.after(2000, lambda: self.ghost.set_state(GhostCanvas.IDLE))

    def _copy_code_file(self, src_path):
        """Kopiert eine Code-Datei in den Code-Lernordner."""
        try:
            src = Path(src_path)
            if src.stat().st_size > 500_000:  # max 500KB pro Datei
                return 0
            content = src.read_text(encoding="utf-8", errors="ignore").strip()
            if not content or len(content) < 20:
                return 0
            # Zielname: original Name + Timestamp für Eindeutigkeit
            ts  = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:19]
            out = Path(CODE_FOLDER) / f"{src.stem}_{ts}{src.suffix}"
            out.write_text(content, encoding="utf-8")
            return 1
        except Exception:
            return 0

    def _open_code_folder(self):
        p = str(Path(CODE_FOLDER).resolve())
        if os.name == "nt": os.startfile(p)
        else: os.system(f"xdg-open '{p}'")

    def _clear_all_learn(self):
        from tkinter import messagebox
        if not messagebox.askyesno("Löschen?",
            "Alle Text- und Code-Lern-Daten löschen?\n(Gespeicherte Chats bleiben erhalten)"):
            return
        for f in glob.glob(f"{LEARN_FOLDER}/*"): Path(f).unlink(missing_ok=True)
        for f in glob.glob(f"{CODE_FOLDER}/*"):  Path(f).unlink(missing_ok=True)
        self._load_learn_folder()
        self._sys_msg("🗑  Alle Lern-Daten gelöscht.")

    def _auto_learn(self):
        msgs = [m["content"] for m in self.chat_history if m["role"]=="user"]
        if len(msgs) >= 3:
            combined = "\n".join(msgs[-10:])
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            Path(LEARN_FOLDER, f"chat_auto_{ts}.txt").write_text(combined, encoding="utf-8")
            self.learned_texts.append(combined)

    def _load_learn_folder(self):
        """Lädt Text- UND Code-Dateien (inkl. GitHub Repos) und baut die Wissensbasis auf."""
        self.learned_texts = []
        self.learned_code  = []   # [(filename, language, content)]
        self.learned_repos = []   # [meta_dict] für Repo-Infos

        # ── Text-Dateien ──────────────────────────────────────────────────────
        txt_files = sorted(glob.glob(f"{LEARN_FOLDER}/*.txt") +
                           glob.glob(f"{LEARN_FOLDER}/*.md"))
        for f in txt_files:
            try:
                c = Path(f).read_text(encoding="utf-8").strip()
                if c: self.learned_texts.append(c)
            except: pass

        # ── Code-Dateien (direkt + aus Repo-Unterordnern) ─────────────────────
        total_lines = 0
        languages   = set()
        code_files  = []

        def scan_code_dir(directory):
            nonlocal total_lines
            for ext, lang in CODE_EXTENSIONS.items():
                for f in sorted(glob.glob(f"{directory}/**/*{ext}", recursive=True)):
                    if "_repo_info.json" in f: continue
                    try:
                        c = Path(f).read_text(encoding="utf-8", errors="ignore").strip()
                        if c and len(c) > 20:
                            lines = c.count("\n") + 1
                            rel   = Path(f).relative_to(CODE_FOLDER)
                            self.learned_code.append((str(rel), lang, c))
                            code_files.append((str(rel), lang, lines))
                            total_lines += lines
                            languages.add(lang)
                    except: pass

        scan_code_dir(CODE_FOLDER)

        # ── Repo-Infos ────────────────────────────────────────────────────────
        for info_file in glob.glob(f"{CODE_FOLDER}/**/_repo_info.json", recursive=True):
            try:
                meta = json.loads(Path(info_file).read_text(encoding="utf-8"))
                self.learned_repos.append(meta)
            except: pass

        # ── Stats updaten ─────────────────────────────────────────────────────
        self.stat_text.configure(text=str(len(self.learned_texts)))
        self.stat_code.configure(text=str(len(self.learned_code)))
        self.stat_lines.configure(text=f"{total_lines:,}".replace(",","."))
        self.stat_langs.configure(text=str(len(languages)))
        repos_n = len(self.learned_repos)
        self.learn_info.configure(
            text=f"{len(self.learned_texts)} Texte\n"
                 f"{len(self.learned_code)} Code\n"
                 f"{repos_n} Repos")

        # ── Dateiliste rendern ────────────────────────────────────────────────
        self.files_box.configure(state="normal")
        self.files_box.delete("1.0","end")

        if self.learned_repos:
            self.files_box.insert("end", f"── 🐙  GitHub Repos ({repos_n}) ──\n")
            for meta in self.learned_repos:
                self.files_box.insert("end",
                    f"  ⭐  {meta['repo']}  [{meta['language']}  ⭐{meta['stars']}]\n"
                    f"     {meta['description'][:70]}\n"
                    f"     {meta['files_loaded']} Dateien geladen\n\n")

        if self.learned_texts:
            self.files_box.insert("end", f"── ✍️  Texte ({len(self.learned_texts)}) ──\n")
            for f in txt_files:
                try:
                    c = Path(f).read_text(encoding="utf-8").strip()
                    self.files_box.insert("end", f"  📄  {Path(f).name}\n")
                    self.files_box.insert("end", f"     {c[:60].replace(chr(10),' ')}…\n\n")
                except: pass

        if code_files:
            direct = [(n,l,li) for n,l,li in code_files if "/" not in n]
            repo_f = [(n,l,li) for n,l,li in code_files if "/" in n]
            if direct:
                self.files_box.insert("end", f"\n── 💻  Code-Dateien ({len(direct)}) ──\n")
                for fname, lang, lines in direct:
                    self.files_box.insert("end", f"  🔷  {fname}  [{lang}  {lines} Zeilen]\n")
            if repo_f:
                self.files_box.insert("end", f"\n── 📁  Repo-Code ({len(repo_f)} Dateien) ──\n")
                shown_repos = set()
                for fname, lang, lines in repo_f[:5]:
                    repo_part = fname.split("/")[0]
                    if repo_part not in shown_repos:
                        self.files_box.insert("end", f"  📂  {repo_part}/\n")
                        shown_repos.add(repo_part)
                    self.files_box.insert("end", f"      {Path(fname).name}  [{lang}]\n")
                if len(repo_f) > 5:
                    self.files_box.insert("end", f"      ... und {len(repo_f)-5} weitere\n")

        if not self.learned_texts and not code_files:
            self.files_box.insert("end",
                "  Noch nichts gelernt.\n\n"
                "  → GitHub: URL eingeben im 'Code-Dateien' Tab\n"
                "  → Lokal: Dateien oder Ordner hinzufügen\n"
                "  → Text: im 'Text' Tab eingeben\n")

        self.files_box.configure(state="disabled")

    def _reload_learn(self):
        self._load_learn_folder()
        self._sys_msg(f"✓  {len(self.learned_texts)} Texte + {len(self.learned_code)} Code-Dateien geladen.")

    def _open_learn_folder(self):
        p=str(Path(LEARN_FOLDER).resolve())
        if os.name=="nt": os.startfile(p)
        else: os.system(f"xdg-open '{p}'")

    # ── TODOs Tab ─────────────────────────────────────────────────────────────
    def _build_todos_tab(self):
        tab = self.tabs.tab("✅  TODOs")
        tab.grid_rowconfigure(2, weight=1)
        tab.grid_columnconfigure(0, weight=1)

        # Eingabe
        inp = ctk.CTkFrame(tab, fg_color="transparent")
        inp.grid(row=0, column=0, sticky="ew", pady=(0,8))
        inp.grid_columnconfigure(0, weight=1)

        self.todo_entry = ctk.CTkEntry(
            inp, placeholder_text="Neue Aufgabe...  (optional @2025-12-31 für Datum)",
            fg_color=BG_INPUT, border_color=ACCENT2, border_width=1,
            font=ctk.CTkFont(size=13))
        self.todo_entry.grid(row=0, column=0, sticky="ew", padx=(0,8))
        self.todo_entry.bind("<Return>", lambda e: self._todo_add_ui())

        ctk.CTkButton(inp, text="＋", width=42, height=36,
                      fg_color=ACCENT2, hover_color=ACCENT,
                      font=ctk.CTkFont(size=18),
                      command=self._todo_add_ui
                      ).grid(row=0, column=1)

        # Filter-Buttons
        frow = ctk.CTkFrame(tab, fg_color="transparent")
        frow.grid(row=1, column=0, sticky="ew", pady=(0,6))
        self._todo_filter = ctk.StringVar(value="all")
        for label, val in [("Alle","all"),("Offen","open"),("Erledigt","done")]:
            ctk.CTkRadioButton(frow, text=label, variable=self._todo_filter, value=val,
                               command=self._todo_refresh,
                               font=ctk.CTkFont(size=12),
                               fg_color=ACCENT2, hover_color=ACCENT
                               ).pack(side="left", padx=8)

        # Liste
        self.todo_scroll = ctk.CTkScrollableFrame(
            tab, fg_color=BG_CARD, corner_radius=10)
        self.todo_scroll.grid(row=2, column=0, sticky="nsew")
        self.todo_scroll.grid_columnconfigure(0, weight=1)
        self._todo_widgets = []
        self._todo_refresh()

    def _todo_add_ui(self):
        text = self.todo_entry.get().strip()
        if not text: return
        due = None
        due_m = re.search(r'@(\d{4}-\d{2}-\d{2})', text)
        if due_m:
            due = due_m.group(1)
            text = text.replace(due_m.group(0), "").strip()
        self.todos.add(text, due)
        self.todo_entry.delete(0, "end")
        self._todo_refresh()

    def _todo_refresh(self):
        for w in self._todo_widgets:
            try: w.destroy()
            except: pass
        self._todo_widgets = []

        filt = self._todo_filter.get()
        items = self.todos.todos
        if filt == "open": items = [t for t in items if not t["done"]]
        if filt == "done": items = [t for t in items if t["done"]]

        if not items:
            lbl = ctk.CTkLabel(self.todo_scroll,
                text="Keine Aufgaben 🎉\nEinfach oben eingeben oder /todo im Chat!",
                font=ctk.CTkFont(size=12), text_color=TEXT_DIM)
            lbl.grid(row=0, column=0, pady=30)
            self._todo_widgets.append(lbl)
            return

        for i, todo in enumerate(items):
            real_idx = self.todos.todos.index(todo)
            frame = ctk.CTkFrame(self.todo_scroll, fg_color=BG_INPUT if not todo["done"] else BG_CARD,
                                  corner_radius=8)
            frame.grid(row=i, column=0, sticky="ew", padx=6, pady=3)
            frame.grid_columnconfigure(1, weight=1)
            self._todo_widgets.append(frame)

            # Checkbox
            var = tk.BooleanVar(value=todo["done"])
            cb = ctk.CTkCheckBox(frame, text="", variable=var, width=20,
                                  fg_color=ACCENT2, hover_color=ACCENT,
                                  command=lambda idx=real_idx, v=var: self._todo_toggle(idx, v))
            cb.grid(row=0, column=0, padx=(10,6), pady=8)

            # Text
            color = TEXT_DIM if todo["done"] else "#e0e0ff"
            font  = ctk.CTkFont(size=13, overstrike=todo["done"])
            text_lbl = ctk.CTkLabel(frame, text=todo["text"],
                                     font=font, text_color=color,
                                     anchor="w", justify="left")
            text_lbl.grid(row=0, column=1, sticky="w", pady=8)

            if todo.get("due"):
                due_lbl = ctk.CTkLabel(frame, text=f"📅 {todo['due']}",
                                        font=ctk.CTkFont(size=10), text_color=BLUE)
                due_lbl.grid(row=1, column=1, sticky="w", pady=(0,4))

            # Löschen
            del_btn = ctk.CTkButton(frame, text="🗑", width=28, height=28,
                                     fg_color="transparent", hover_color=BG_CARD,
                                     text_color=TEXT_DIM, font=ctk.CTkFont(size=13),
                                     command=lambda idx=real_idx: self._todo_delete(idx))
            del_btn.grid(row=0, column=2, padx=(0,8))

    def _todo_toggle(self, idx, var):
        if var.get():
            self.todos.done(idx)
        else:
            self.todos.todos[idx]["done"] = False
            self.todos.save()
        self._todo_refresh()

    def _todo_delete(self, idx):
        self.todos.delete(idx)
        self._todo_refresh()

    # ── APIs Tab ──────────────────────────────────────────────────────────────
    def _build_apis_tab(self):
        tab = self.tabs.tab("🔑  APIs")
        tab.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(tab,
            text="Alle APIs sind optional — die App funktioniert ohne sie.\n"
                 "Mit API-Keys werden zusätzliche Features freigeschaltet.",
            font=ctk.CTkFont(size=12), text_color=TEXT_DIM,
            justify="left").grid(row=0, column=0, sticky="w", pady=(0,12))

        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.grid(row=1, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)

        self._api_entries = {}
        row = 0
        for service_id, info in ApiManager.SERVICES.items():
            frame = ctk.CTkFrame(scroll, fg_color=BG_CARD, corner_radius=10)
            frame.grid(row=row, column=0, sticky="ew", pady=4, padx=2)
            frame.grid_columnconfigure(1, weight=1)

            # Icon + Name
            ctk.CTkLabel(frame,
                text=f"{info['icon']}  {info['name']}",
                font=ctk.CTkFont("Helvetica", 13, "bold"),
                text_color=ACCENT).grid(row=0, column=0, columnspan=3,
                                         sticky="w", padx=12, pady=(10,2))
            ctk.CTkLabel(frame,
                text=info["desc"],
                font=ctk.CTkFont(size=11), text_color=TEXT_DIM
                ).grid(row=1, column=0, columnspan=3, sticky="w", padx=12, pady=(0,6))

            if not info.get("no_key"):
                # Key-Eingabe
                entry = ctk.CTkEntry(
                    frame, placeholder_text=f"{info['name']} API Key...",
                    fg_color=BG_INPUT, border_color=ACCENT2, border_width=1,
                    show="*", font=ctk.CTkFont("Courier", 12))
                existing = self.apis.get(service_id)
                if existing:
                    entry.insert(0, existing)
                entry.grid(row=2, column=0, sticky="ew", padx=(12,6), pady=(0,10))

                # Status
                status_color = GREEN if self.apis.has(service_id) else TEXT_DIM
                status_text  = "✓ Konfiguriert" if self.apis.has(service_id) else "Nicht konfiguriert"
                status_lbl = ctk.CTkLabel(frame, text=status_text,
                                           font=ctk.CTkFont(size=11),
                                           text_color=status_color)
                status_lbl.grid(row=2, column=1, sticky="w", padx=4)

                def save_key(sid=service_id, e=entry, sl=status_lbl):
                    key = e.get().strip()
                    self.apis.set(sid, key)
                    if key:
                        sl.configure(text="✓ Gespeichert", text_color=GREEN)
                    else:
                        sl.configure(text="Gelöscht", text_color=TEXT_DIM)

                ctk.CTkButton(frame, text="Speichern", width=90, height=30,
                              fg_color=ACCENT2, hover_color=ACCENT,
                              font=ctk.CTkFont(size=12),
                              command=save_key
                              ).grid(row=2, column=2, padx=(0,12), pady=(0,10))

                # Link
                import webbrowser
                ctk.CTkButton(frame, text=f"🌐  {info['url']}",
                              command=lambda u=info['url']: webbrowser.open(u),
                              fg_color="transparent", hover_color=BG_INPUT,
                              text_color=BLUE, font=ctk.CTkFont(size=10),
                              anchor="w"
                              ).grid(row=3, column=0, columnspan=3, sticky="w",
                                     padx=12, pady=(0,8))
                self._api_entries[service_id] = entry
            else:
                # Kein Key nötig
                ctk.CTkLabel(frame, text="✅  Kein API-Key nötig — immer verfügbar",
                             font=ctk.CTkFont(size=11), text_color=GREEN
                             ).grid(row=2, column=0, columnspan=3, sticky="w",
                                    padx=12, pady=(0,10))
            row += 1

        # Externe KI-Modelle Info
        row2 = row
        ctk.CTkLabel(scroll,
            text="\n📡  Externe KI-Modelle\n"
                 "Mit API-Keys kannst du /model claude, /model gemini oder /model gpt4 nutzen.\n"
                 "Without a key, Ghostfish runs fully local via Ollama — no internet needed!",
            font=ctk.CTkFont(size=11), text_color=TEXT_DIM,
            justify="left", wraplength=500
            ).grid(row=row2, column=0, sticky="w", pady=8, padx=4)

    # ── Einstellungen Tab ─────────────────────────────────────────────────────
    def _build_settings_tab(self):
        tab=self.tabs.tab("⚙️  Einstellungen"); tab.grid_columnconfigure(1,weight=1)
        rows=[("Ollama URL","url_entry",OLLAMA_URL),
              ("Obsidian Ordner","obsidian_entry",OBSIDIAN_FOLDER),
              ("Dateien Ordner","files_entry",FILES_FOLDER),
              ("KI Name","name_entry",AI_NAME)]
        for i,(lbl,attr,default) in enumerate(rows):
            ctk.CTkLabel(tab,text=lbl,font=ctk.CTkFont(size=12),
                         text_color=TEXT_DIM).grid(row=i,column=0,sticky="w",padx=(0,12),pady=6)
            e=ctk.CTkEntry(tab,fg_color=BG_INPUT,border_color=ACCENT2,border_width=1)
            e.insert(0,default); e.grid(row=i,column=1,sticky="ew",pady=6)
            setattr(self,attr,e)
        r=len(rows)
        ctk.CTkLabel(tab,text="Persönlichkeit",font=ctk.CTkFont(size=12),
                     text_color=TEXT_DIM).grid(row=r,column=0,columnspan=2,sticky="w",pady=(10,4))
        self.system_text=ctk.CTkTextbox(tab,height=120,font=ctk.CTkFont("Helvetica",12),
                                        corner_radius=10,fg_color=BG_INPUT,
                                        border_color=ACCENT2,border_width=1)
        self.system_text.grid(row=r+1,column=0,columnspan=2,sticky="ew",pady=(0,10))
        self.system_text.insert("1.0",SYSTEM_BASE)
        ctk.CTkButton(tab,text="✓  Speichern",command=self._save_settings,
                      fg_color=ACCENT2,hover_color=ACCENT,font=ctk.CTkFont(size=13)
                      ).grid(row=r+2,column=0,columnspan=2,sticky="w",pady=(0,14))

        # ── Theme ─────────────────────────────────────────────────────────────
        ctk.CTkLabel(tab, text="🎨  Theme",
                     font=ctk.CTkFont(size=12), text_color=TEXT_DIM
                     ).grid(row=r+3, column=0, sticky="w", pady=(4,4))
        theme_row = ctk.CTkFrame(tab, fg_color="transparent")
        theme_row.grid(row=r+4, column=0, columnspan=2, sticky="ew", pady=(0,10))
        for i, tname in enumerate(THEMES.keys()):
            ctk.CTkButton(theme_row, text=tname,
                          command=lambda n=tname: self._apply_theme(n),
                          width=100, height=28, corner_radius=8,
                          fg_color=BG_INPUT, hover_color=BG_SEL,
                          border_width=1, border_color=ACCENT2,
                          text_color=ACCENT, font=ctk.CTkFont(size=10)
                          ).pack(side="left", padx=3)

        # ── Gedächtnis ────────────────────────────────────────────────────────
        ctk.CTkLabel(tab, text="🧠  Gedächtnis",
                     font=ctk.CTkFont(size=12), text_color=TEXT_DIM
                     ).grid(row=r+5, column=0, sticky="w", pady=(4,4))

        self.memory_box = ctk.CTkTextbox(tab, height=90,
                                          font=ctk.CTkFont("Courier",11),
                                          fg_color=BG_INPUT, corner_radius=8,
                                          border_color=ACCENT2, border_width=1)
        self.memory_box.grid(row=r+6, column=0, columnspan=2, sticky="ew", pady=(0,6))
        self._refresh_memory_box()

        mem_row = ctk.CTkFrame(tab, fg_color="transparent")
        mem_row.grid(row=r+7, column=0, columnspan=2, sticky="w", pady=(0,10))
        ctk.CTkButton(mem_row, text="🔄  Aktualisieren",
                      command=self._refresh_memory_box,
                      fg_color="transparent", border_width=1,
                      border_color=ACCENT2, text_color=ACCENT,
                      hover_color=BG_CARD, font=ctk.CTkFont(size=11)
                      ).pack(side="left", padx=(0,8))
        ctk.CTkButton(mem_row, text="🗑  Gedächtnis löschen",
                      command=self._clear_memory,
                      fg_color="transparent", border_width=1,
                      border_color=RED, text_color=RED,
                      hover_color=BG_CARD, font=ctk.CTkFont(size=11)
                      ).pack(side="left")

        ctk.CTkLabel(tab,
            text="Ollama: $env:OLLAMA_ORIGINS='*'; ollama serve\n"
                 "Bild-Modell: ollama pull llava\n"
                 "Text-Modell: ollama pull llama3\n\n"
                 "Chats: 'gespeicherte_chats/'  |  Gedächtnis: geist_gedaechtnis.json",
            font=ctk.CTkFont("Courier",10),text_color=TEXT_DIM,
            justify="left",wraplength=500
        ).grid(row=r+8,column=0,columnspan=2,sticky="w",pady=4)

    def _apply_theme(self, theme_name):
        """Wendet ein Theme auf alle UI-Elemente an."""
        global ACCENT, ACCENT2, BG_DARK, BG_MID, BG_CARD, BG_INPUT, BG_SEL, TEXT_DIM, GREEN, RED, BLUE
        t = THEMES.get(theme_name, THEMES["🌙 Lila Nacht"])
        ACCENT=t["ACCENT"]; ACCENT2=t["ACCENT2"]; BG_DARK=t["BG_DARK"]
        BG_MID=t["BG_MID"]; BG_CARD=t["BG_CARD"]; BG_INPUT=t["BG_INPUT"]
        BG_SEL=t["BG_SEL"]; TEXT_DIM=t["TEXT_DIM"]; GREEN=t["GREEN"]
        RED=t["RED"]; BLUE=t["BLUE"]
        self.current_theme = theme_name
        # Haupt-Farben updaten
        self.configure(fg_color=BG_DARK)
        self.ghost.configure(bg=BG_MID)
        # Chat-Tags neu setzen
        tb = self.chat_box._textbox
        tb.tag_configure("user_name", foreground=GREEN)
        tb.tag_configure("ai_name",   foreground=ACCENT)
        tb.tag_configure("sys_msg",   foreground=TEXT_DIM)
        tb.tag_configure("err_msg",   foreground=RED)
        self._sys_msg(f"🎨  Theme '{theme_name}' aktiviert!")

    def _refresh_memory_box(self):
        """Zeigt aktuellen Gedächtnis-Inhalt."""
        try:
            self.memory_box.configure(state="normal")
            self.memory_box.delete("1.0","end")
            d = self.memory.data
            if d.get("name"):
                self.memory_box.insert("end", f"Name: {d['name']}\n")
            self.memory_box.insert("end", f"Sitzungen: {d.get('session_count',0)}\n")
            for fact in d.get("facts",[])[-10:]:
                self.memory_box.insert("end", f"• {fact}\n")
            if not d.get("facts") and not d.get("name"):
                self.memory_box.insert("end", "(Noch nichts gelernt — einfach chatten!)")
            self.memory_box.configure(state="disabled")
        except Exception: pass

    def _clear_memory(self):
        self.memory.data = {"name":"","facts":[],"preferences":{},
                            "topics":[],"session_count":0}
        self.memory.save()
        self._refresh_memory_box()
        self._sys_msg("🗑  Gedächtnis gelöscht.")

    def _save_settings(self):
        global OLLAMA_URL,OBSIDIAN_FOLDER,FILES_FOLDER,AI_NAME
        OLLAMA_URL=self.url_entry.get().strip().rstrip("/")
        OBSIDIAN_FOLDER=self.obsidian_entry.get().strip()
        FILES_FOLDER=self.files_entry.get().strip()
        AI_NAME=self.name_entry.get().strip() or "Ghostfish"
        for f in [OBSIDIAN_FOLDER,FILES_FOLDER]: Path(f).mkdir(exist_ok=True)
        self._sys_msg("✓  Gespeichert.")
        self._check_ollama()

    # ── Hilfsfunktionen ───────────────────────────────────────────────────────
    def _build_system_prompt(self):
        base = self.system_text.get("1.0","end").strip()
        name = self.name_entry.get().strip() or AI_NAME
        lang = getattr(self, '_lang_var', None)
        lang_val = lang.get() if lang else "Auto"

        prompt = f"Your name is '{name}'. {base}\n"

        # ── Sprach-Anweisung ─────────────────────────────────────────────────
        if lang_val == "Deutsch":
            prompt += "\nAlways reply in German (Deutsch). No exceptions.\n"
        elif lang_val == "English":
            prompt += "\nAlways reply in English. No exceptions.\n"
        elif lang_val == "Oskovian":
            prompt += (
                "\nAlways reply FULLY in Oskovian language using the dictionary below. "
                "Use English/German only for concepts not in the dictionary.\n"
            )
            prompt += OSKOVIAN_DICT + "\n"
        elif lang_val == "Auto":
            prompt += "\nDetect the user's language and reply in the same language.\n"
            prompt += "\nIf the user writes in Oskovian, use this dictionary:\n"
            prompt += OSKOVIAN_DICT + "\n"

        # ── Gedächtnis ───────────────────────────────────────────────────────
        prompt += self.memory.to_prompt()

        # ── Repo-Kontext ─────────────────────────────────────────────────────
        if self.learned_repos:
            prompt += "\n═══ LEARNED GITHUB REPOS ═══\n"
            for meta in self.learned_repos:
                prompt += (f"Repo: {meta['repo']}  |  Language: {meta['language']}\n"
                           f"Description: {meta['description']}\n"
                           f"Files loaded: {meta['files_loaded']}\n\n")

        # ── Text-Stil ────────────────────────────────────────────────────────
        if self.learned_texts:
            prompt += "\n═══ WRITING STYLE (mirror subtly) ═══\n"
            for i, t in enumerate(self.learned_texts[:4], 1):
                prompt += f"Example {i}: \"{t[:180].replace(chr(10),' | ')}\"\n"

        # ── Code-Wissensbasis ────────────────────────────────────────────────
        if self.learned_code:
            langs = {}
            for fname, lang_name, content in self.learned_code:
                if lang_name not in langs: langs[lang_name] = []
                langs[lang_name].append((fname, content))
            prompt += "\n═══ CODE KNOWLEDGE BASE ═══\n"
            prompt += f"Languages learned: {', '.join(langs.keys())}\n"
            shown = 0
            for lang_name, files in langs.items():
                if shown >= 4: break
                fname, content = files[0]
                excerpt = "\n".join(content.split("\n")[:30])
                prompt += f"── {lang_name} ({fname}) ──\n{excerpt}\n\n"
                shown += 1
            prompt += ("IMPORTANT: Use learned style & patterns, complete runnable code, "
                       "comments in user's language, error handling.\n")
        return prompt

    def _check_ollama(self):
        def _chk():
            try:
                r=requests.get(f"{OLLAMA_URL}/api/tags",timeout=5)
                models=[m["name"] for m in r.json().get("models",[])]
                self.after(0,lambda:self._set_online(True,models or ["llava"]))
            except: self.after(0,lambda:self._set_online(False,[]))
        threading.Thread(target=_chk,daemon=True).start()

    def _set_online(self, online, models):
        if online:
            self.status_dot.configure(text="● online", text_color=GREEN)
            if models:
                self.model_menu.configure(values=models)
                cur = self.selected_model.get()
                # Qwen bevorzugen wenn verfügbar
                if cur not in models:
                    preferred = next(
                        (m for m in models if "qwen" in m.lower()),
                        next((m for m in models if "llama" in m.lower()), models[0])
                    )
                    self.selected_model.set(preferred)
                    self.model_menu.set(preferred)
            self.ghost.set_state(GhostCanvas.HAPPY)
            self.after(2500, lambda: self.ghost.set_state(GhostCanvas.IDLE))
        else:
            self.status_dot.configure(text="● offline", text_color=RED)

    # ── Wikipedia ─────────────────────────────────────────────────────────────
    def _wiki_search(self, query):
        try:
            self.after(0, lambda: self._sys_msg(f"📖  Wikipedia: {query}..."))
            url = "https://de.wikipedia.org/api/rest_v1/page/summary/" + urllib.parse.quote(query)
            r = requests.get(url, timeout=10, headers={"User-Agent":"Ghostfish/1.0"})
            if r.status_code == 404:
                # Englisch probieren
                url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + urllib.parse.quote(query)
                r = requests.get(url, timeout=10, headers={"User-Agent":"Ghostfish/1.0"})
            r.raise_for_status()
            data = r.json()
            extract = data.get("extract","Kein Inhalt gefunden.")
            title   = data.get("title", query)
            wiki_url= data.get("content_urls",{}).get("desktop",{}).get("page","")

            self.after(0, lambda: self._print_msg("📖 Wikipedia",
                f"{title}\n\n{extract[:800]}{'...' if len(extract)>800 else ''}\n\n{wiki_url}"))

            # An Ollama zur Zusammenfassung
            self.chat_history.append({"role":"user","content":
                f"Wikipedia über '{query}':\n{extract[:1000]}\n\nFasse kurz zusammen und ergänze."})
            sys_p = self._build_system_prompt()
            msgs  = [{"role":"system","content":sys_p}] + self.chat_history[-8:]
            resp  = requests.post(f"{OLLAMA_URL}/api/chat",
                json={"model":self.selected_model.get(),"messages":msgs,
                      "stream":False,"options":{"temperature":0.6}}, timeout=120)
            if resp.ok:
                reply = resp.json()["message"]["content"]
                self.chat_history.append({"role":"assistant","content":reply})
                self.after(0, lambda: self._print_msg(AI_NAME, reply))
        except Exception as e:
            self.after(0, lambda: self._chat_insert(f"\n  ❌ Wiki: {e}\n","err_msg"))
        finally:
            self.is_typing=False
            self.after(0, lambda: self.send_btn.configure(state="normal"))
            self.after(0, lambda: self.ghost.set_state(GhostCanvas.IDLE))

    # ── YouTube ───────────────────────────────────────────────────────────────
    def _youtube_analyze(self, url):
        try:
            self.after(0, lambda: self._sys_msg(f"▶️  YouTube wird geladen..."))
            # Video-ID extrahieren
            vid_match = re.search(r'(?:v=|youtu\.be/|/v/)([a-zA-Z0-9_-]{11})', url)
            if not vid_match:
                self.after(0, lambda: self._print_msg(AI_NAME,
                    "❌  Ungültige YouTube URL. Beispiel:\n"
                    "    /youtube https://www.youtube.com/watch?v=dQw4w9WgXcQ"))
                return
            vid_id = vid_match.group(1)

            # Oembed für Titel/Kanal
            oembed_url = f"https://www.youtube.com/oembed?url=https://youtu.be/{vid_id}&format=json"
            meta = {}
            try:
                mr = requests.get(oembed_url, timeout=8)
                if mr.ok: meta = mr.json()
            except: pass

            title   = meta.get("title", "Unbekannter Titel")
            channel = meta.get("author_name", "Unbekannter Kanal")

            self.after(0, lambda: self._sys_msg(f"📺  {title} — {channel}"))

            # Transkript via yt-dlp (optional, falls installiert)
            transcript = ""
            try:
                result = subprocess.run(
                    ["yt-dlp", "--skip-download", "--write-auto-sub",
                     "--sub-lang","de,en","--sub-format","vtt",
                     "-o", str(Path(tempfile.gettempdir())/"geist_yt_%(id)s"),
                     f"https://youtu.be/{vid_id}"],
                    capture_output=True, text=True, timeout=30)
                # VTT-Datei lesen
                for vtt in Path(tempfile.gettempdir()).glob(f"geist_yt_{vid_id}*.vtt"):
                    raw = vtt.read_text(encoding="utf-8", errors="ignore")
                    # VTT-Tags entfernen
                    transcript = re.sub(r'<[^>]+>','', raw)
                    transcript = re.sub(r'\d{2}:\d{2}:\d{2}\.\d+ --> .+\n','', transcript)
                    transcript = re.sub(r'\n{3,}','\n\n', transcript).strip()
                    vtt.unlink(missing_ok=True)
                    break
            except FileNotFoundError:
                pass  # yt-dlp nicht installiert
            except Exception:
                pass

            # Prompt für Ollama
            if transcript:
                context = f"YouTube Video: '{title}' von {channel}\n\nTranskript:\n{transcript[:3000]}"
            else:
                context = (f"YouTube Video: '{title}' von {channel}\n"
                          f"URL: {url}\n"
                          f"Video-ID: {vid_id}\n\n"
                          "Kein Transkript verfügbar (yt-dlp nicht installiert).\n"
                          "Beschreibe was du über dieses Video weißt und gib Tipps.")

            self.chat_history.append({"role":"user","content":
                f"{context}\n\nFasse das Video zusammen und erkläre die wichtigsten Punkte."})

            self.after(0, self._stream_start)
            sys_p = self._build_system_prompt()
            msgs  = [{"role":"system","content":sys_p}] + self.chat_history[-6:]
            resp  = requests.post(f"{OLLAMA_URL}/api/chat",
                json={"model":self.selected_model.get(),"messages":msgs,
                      "stream":True,"options":{"temperature":0.7}},
                timeout=180, stream=True)

            full = ""
            for line in resp.iter_lines():
                if not line: continue
                try:
                    chunk = json.loads(line.decode("utf-8"))
                    token = chunk.get("message",{}).get("content","")
                    if token:
                        full += token
                        self.after(0, lambda t=token: self._stream_append(t))
                    if chunk.get("done"): break
                except: continue

            self.chat_history.append({"role":"assistant","content":full})

            # YouTube Link als Button
            yt_url = f"https://youtu.be/{vid_id}"
            self.after(0, lambda: self._url_button(f"▶  {title}", yt_url))

        except Exception as e:
            self.after(0, lambda: self._chat_insert(f"\n  ❌ YouTube: {e}\n","err_msg"))
        finally:
            self.is_typing=False
            self.after(0, lambda: self.send_btn.configure(state="normal"))
            self.after(0, lambda: self.ghost.set_state(GhostCanvas.IDLE))

    def _url_button(self, label, url):
        """Klickbarer URL-Button im Chat."""
        import webbrowser
        self.chat_box.configure(state="normal")
        btn = ctk.CTkButton(
            self.chat_box, text=label,
            command=lambda: webbrowser.open(url),
            height=28, corner_radius=6,
            fg_color="#1a1a2e", hover_color="#2a2a40",
            border_width=1, border_color=RED,
            text_color=RED, font=ctk.CTkFont(size=11))
        self.chat_box._textbox.window_create("end", window=btn)
        self.chat_box._textbox.insert("end", "\n")
        self.chat_box.configure(state="disabled")

    # ── PDF Analyse ───────────────────────────────────────────────────────────
    def _analyze_pdf(self, path, question=""):
        try:
            self.after(0, lambda: self._sys_msg(f"📄  Lese PDF: {Path(path).name}..."))

            text = ""
            # Methode 1: pdfplumber (beste Qualität)
            try:
                import pdfplumber
                with pdfplumber.open(path) as pdf:
                    pages = pdf.pages[:20]  # max 20 Seiten
                    for p in pages:
                        t = p.extract_text()
                        if t: text += t + "\n\n"
            except ImportError:
                pass

            # Methode 2: pypdf fallback
            if not text:
                try:
                    import pypdf
                    reader = pypdf.PdfReader(path)
                    for page in reader.pages[:20]:
                        t = page.extract_text()
                        if t: text += t + "\n\n"
                except ImportError:
                    pass

            # Methode 3: pdfminer fallback
            if not text:
                try:
                    from pdfminer.high_level import extract_text as pm_extract
                    text = pm_extract(path, maxpages=15)
                except ImportError:
                    pass

            if not text:
                self.after(0, lambda: self._print_msg(AI_NAME,
                    "❌  PDF konnte nicht gelesen werden.\n"
                    "    Installiere: pip install pdfplumber\n"
                    "    oder:        pip install pypdf"))
                return

            text = text.strip()[:6000]
            fname = Path(path).name
            q = question or "Fasse dieses Dokument zusammen und erkläre die wichtigsten Punkte."

            self.chat_history.append({"role":"user","content":
                f"PDF: '{fname}'\n\nInhalt:\n{text}\n\nFrage: {q}"})

            self.after(0, self._stream_start)
            sys_p = self._build_system_prompt()
            msgs  = [{"role":"system","content":sys_p}] + self.chat_history[-6:]
            resp  = requests.post(f"{OLLAMA_URL}/api/chat",
                json={"model":self.selected_model.get(),"messages":msgs,
                      "stream":True,"options":{"temperature":0.6}},
                timeout=180, stream=True)

            full = ""
            for line in resp.iter_lines():
                if not line: continue
                try:
                    chunk = json.loads(line.decode("utf-8"))
                    token = chunk.get("message",{}).get("content","")
                    if token:
                        full += token
                        self.after(0, lambda t=token: self._stream_append(t))
                    if chunk.get("done"): break
                except: continue

            self.chat_history.append({"role":"assistant","content":full})

        except Exception as e:
            self.after(0, lambda: self._chat_insert(f"\n  ❌ PDF: {e}\n","err_msg"))
        finally:
            self.is_typing=False
            self.after(0, lambda: self.send_btn.configure(state="normal"))
            self.after(0, lambda: self.ghost.set_state(GhostCanvas.IDLE))

    # ── Timer ─────────────────────────────────────────────────────────────────
    def _set_timer(self, seconds, message):
        def _ring():
            self.after(0, lambda: self._print_msg(AI_NAME, f"⏰  {message}"))
            self.after(0, lambda: self.ghost.set_state(GhostCanvas.HAPPY))
            self.after(3000, lambda: self.ghost.set_state(GhostCanvas.IDLE))
            # Systemton
            try:
                if os.name == "nt":
                    import winsound
                    winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            except: pass
        timer = threading.Timer(seconds, _ring)
        timer.daemon = True
        timer.start()
        self._timers.append(timer)

    # ── Mikrofon / Spracheingabe ──────────────────────────────────────────────
    def _toggle_mic(self):
        if self._mic_active:
            self._mic_active = False
            self.mic_btn.configure(fg_color=BG_INPUT, text="🎙")
            return

        # Prüfen ob SpeechRecognition installiert
        try:
            import speech_recognition as sr
        except ImportError:
            self._sys_msg(
                "🎙  speech_recognition nicht installiert!\n"
                "    pip install SpeechRecognition pyaudio")
            return

        self._mic_active = True
        self.mic_btn.configure(fg_color=RED, text="⏹")
        self._sys_msg("🎙  Höre zu... (nochmal klicken zum Stoppen)")
        threading.Thread(target=self._listen_mic, daemon=True).start()

    def _listen_mic(self):
        try:
            import speech_recognition as sr
            r = sr.Recognizer()
            r.pause_threshold = 1.5
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source, duration=0.5)
                try:
                    audio = r.listen(source, timeout=10, phrase_time_limit=30)
                except sr.WaitTimeoutError:
                    self.after(0, lambda: self._sys_msg("🎙  Kein Audio erkannt."))
                    return

            if not self._mic_active:
                return

            self.after(0, lambda: self._sys_msg("🔄  Verarbeite Sprache..."))

            # Erst Whisper lokal versuchen (falls installiert)
            text = None
            try:
                import whisper
                model = whisper.load_model("base")
                # Audio zu WAV temp-Datei
                import io as _io
                wav_data = audio.get_wav_data()
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                    f.write(wav_data); tmp = f.name
                result = model.transcribe(tmp, language="de")
                text = result["text"].strip()
                Path(tmp).unlink(missing_ok=True)
            except ImportError:
                pass

            # Fallback: Google STT (kostenlos, braucht Internet)
            if not text:
                try:
                    text = r.recognize_google(audio, language="de-DE")
                except sr.UnknownValueError:
                    self.after(0, lambda: self._sys_msg("🎙  Sprache nicht erkannt."))
                    return
                except sr.RequestError:
                    # Englisch probieren
                    try:
                        text = r.recognize_google(audio, language="en-US")
                    except Exception:
                        self.after(0, lambda: self._sys_msg("🎙  Erkennungs-Fehler."))
                        return

            if text:
                # Text ins Eingabefeld schreiben und senden
                self.after(0, lambda t=text: self._mic_insert_and_send(t))

        except Exception as e:
            self.after(0, lambda: self._sys_msg(f"🎙  Fehler: {e}"))
        finally:
            self._mic_active = False
            self.after(0, lambda: self.mic_btn.configure(fg_color=BG_INPUT, text="🎙"))

    def _mic_insert_and_send(self, text):
        """Fügt erkannten Text ins Eingabefeld ein und sendet."""
        self.input_box.delete("1.0","end")
        self.input_box.insert("1.0", text)
        self._sys_msg(f"🎙  Erkannt: {text}")
        self.after(300, self._send_message)

    # ── TTS: ElevenLabs ──────────────────────────────────────────────────────
    def _tts_elevenlabs(self, text, voice_id=None):
        key = self.apis.get("elevenlabs")
        if not key: return
        try:
            vid = voice_id or "pNInz6obpgDQGcFmaJgB"  # Adam — gut für Deutsch
            resp = requests.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{vid}",
                headers={"xi-api-key": key, "Content-Type":"application/json"},
                json={"text": text[:500],
                      "model_id": "eleven_multilingual_v2",
                      "voice_settings": {"stability":0.5,"similarity_boost":0.75,
                                         "style":0.3,"use_speaker_boost":True}},
                timeout=30)
            if resp.status_code == 401:
                self.after(0, lambda: self._sys_msg("❌  ElevenLabs Key ungültig."))
                return
            if resp.status_code == 429:
                self.after(0, lambda: self._sys_msg("⚠️  ElevenLabs Limit erreicht."))
                return
            resp.raise_for_status()

            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                f.write(resp.content); tmp_path = f.name

            played = False
            # playsound
            try:
                from playsound import playsound
                playsound(tmp_path); played = True
            except: pass
            # Windows nativ
            if not played and os.name == "nt":
                try: os.startfile(tmp_path); played = True
                except: pass
            # mpv / ffplay
            if not played:
                for player in ["mpv","ffplay","vlc"]:
                    try:
                        subprocess.Popen([player,"--really-quiet",tmp_path],
                                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        played = True; break
                    except FileNotFoundError: continue
            if not played:
                self.after(0, lambda: self._sys_msg(
                    "⚠️  Kein Audio-Player. pip install playsound"))
        except Exception as e:
            self.after(0, lambda: self._chat_insert(f"\n  ❌ TTS: {e}\n","err_msg"))

    # ── Modell wechseln (Ollama + externe APIs) ───────────────────────────────
    def _switch_model(self, arg):
        arg_low = arg.lower()

        # Claude (Anthropic)
        if "claude" in arg_low:
            if not self.apis.has("anthropic"):
                self._print_msg(AI_NAME,
                    "🤖  Anthropic API-Key fehlt!\n"
                    "    Einstellungen → APIs → Anthropic Key eintragen.\n"
                    "    https://console.anthropic.com")
                return
            self.selected_model.set("claude-via-api")
            self._print_msg(AI_NAME, "🤖  Wechsle zu Claude (Anthropic API)")
            return

        # Gemini
        if "gemini" in arg_low:
            if not self.apis.has("gemini"):
                self._print_msg(AI_NAME,
                    "✨  Gemini API-Key fehlt!\n"
                    "    Einstellungen → APIs → Gemini Key eintragen.\n"
                    "    https://aistudio.google.com")
                return
            self.selected_model.set("gemini-via-api")
            self._print_msg(AI_NAME, "✨  Wechsle zu Gemini (Google API)")
            return

        # GPT
        if "gpt" in arg_low or "openai" in arg_low:
            if not self.apis.has("openai"):
                self._print_msg(AI_NAME,
                    "🟢  OpenAI API-Key fehlt!\n"
                    "    Einstellungen → APIs → OpenAI Key eintragen.\n"
                    "    https://platform.openai.com")
                return
            self.selected_model.set("gpt-4o-mini")
            self._print_msg(AI_NAME, "🟢  Wechsle zu GPT-4o mini (OpenAI API)")
            return

        # Ollama Modell
        self.selected_model.set(arg)
        self._print_msg(AI_NAME, f"🤖  Modell gewechselt zu: {arg}")

    # ── Bot-System ────────────────────────────────────────────────────────────
    def _open_bot_dialog(self):
        """Dialog zum Erstellen eines neuen Bots."""
        dlg = ctk.CTkToplevel(self)
        dlg.title("🤖 Bot erstellen")
        dlg.geometry("520x480")
        dlg.configure(fg_color=BG_DARK)
        dlg.grab_set()

        def lbl(text, row):
            ctk.CTkLabel(dlg, text=text, font=ctk.CTkFont(size=11),
                         text_color=TEXT_DIM).grid(row=row, column=0, sticky="w",
                                                   padx=16, pady=(8,2))
        def entry(row, placeholder=""):
            e = ctk.CTkEntry(dlg, fg_color=BG_INPUT, border_color=ACCENT2,
                             border_width=1, placeholder_text=placeholder)
            e.grid(row=row, column=0, sticky="ew", padx=16, pady=(0,4))
            return e

        dlg.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(dlg, text="🤖  Neuen Bot erstellen",
                     font=ctk.CTkFont("Helvetica", 15, "bold"),
                     text_color=ACCENT).grid(row=0, column=0, padx=16, pady=(16,8), sticky="w")

        lbl("Name", 1); name_e = entry(2, "z.B. News-Bot")
        lbl("Beschreibung", 3); desc_e = entry(4, "Was macht dieser Bot?")

        lbl("Persönlichkeit / System-Prompt", 5)
        sys_e = ctk.CTkTextbox(dlg, height=80, fg_color=BG_INPUT,
                                border_color=ACCENT2, border_width=1,
                                font=ctk.CTkFont(size=11))
        sys_e.grid(row=6, column=0, sticky="ew", padx=16, pady=(0,4))
        sys_e.insert("1.0", "Du bist ein hilfreicher Bot. Antworte kurz und präzise.")

        lbl("Auto-Suche Keywords (kommagetrennt, leer=manuell)", 7)
        search_e = entry(8, "AI news, tech, science")

        lbl("Auto-Intervall in Minuten (0 = nur manuell)", 9)
        interval_e = entry(10, "0")

        def do_create():
            name     = name_e.get().strip()
            desc     = desc_e.get().strip()
            system   = sys_e.get("1.0","end").strip()
            search   = search_e.get().strip()
            try: interval = int(interval_e.get().strip() or "0")
            except: interval = 0
            if not name: return

            bot = self.bot_manager.add(name, desc, system, search, interval)
            self._sys_msg(f"✅  Bot '{name}' erstellt!")
            dlg.destroy()

            # Auto-start wenn Intervall gesetzt
            if interval > 0:
                bot["running"] = True
                self.bot_manager.save()
                self.bot_manager.start_timer(bot["id"],
                    lambda bid: self._run_bot_by_id(bid), interval)

        ctk.CTkButton(dlg, text="✓  Bot erstellen",
                      fg_color=ACCENT2, hover_color=ACCENT,
                      font=ctk.CTkFont(size=13),
                      command=do_create).grid(row=11, column=0, pady=14, padx=16, sticky="ew")

    def _run_bot(self, bot):
        """Führt einen Bot aus — sucht wenn nötig und schickt an KI."""
        self._sys_msg(f"🤖  Bot '{bot['name']}' läuft...")
        self.ghost.set_state(GhostCanvas.THINK)
        threading.Thread(target=self._do_run_bot, args=(bot,), daemon=True).start()

    def _run_bot_by_id(self, bot_id):
        bot = next((b for b in self.bot_manager.bots if b["id"] == bot_id), None)
        if bot: self._run_bot(bot)

    def _do_run_bot(self, bot):
        try:
            user_msg = f"Führe deine Aufgabe aus: {bot['desc']}"

            # Auto-Suche wenn Keywords vorhanden
            if bot.get("search_kw"):
                keywords = [k.strip() for k in bot["search_kw"].split(",") if k.strip()]
                results  = []
                for kw in keywords[:3]:  # max 3 Keywords
                    r = self._quick_web_search(kw)
                    if r: results.append(f"[{kw}]\n{r}")
                if results:
                    user_msg = (f"Suchergebnisse:\n\n" +
                                "\n\n".join(results) +
                                "\n\nAnalyzing und berichte kurz.")

            sys_prompt = (bot.get("system") or
                          f"Du bist {bot['name']}. {bot['desc']}")
            msgs = [{"role":"system","content":sys_prompt},
                    {"role":"user","content":user_msg}]

            self.after(0, self._stream_start)
            r = requests.post(
                f"{OLLAMA_URL}/api/chat",
                json={"model": self.selected_model.get(),
                      "messages": msgs,
                      "stream": True,
                      "options": {"temperature": 0.6}},
                timeout=180, stream=True)

            full = ""
            for line in r.iter_lines():
                if not line: continue
                try:
                    chunk = json.loads(line.decode("utf-8"))
                    tok = chunk.get("message",{}).get("content","")
                    if tok:
                        full += tok
                        self.after(0, lambda t=tok: self._stream_append(t))
                    if chunk.get("done"): break
                except: continue

            self.chat_history.append({"role":"assistant","content":full})
            self.after(0, self._autosave_current)

        except Exception as e:
            self.after(0, lambda: self._chat_insert(f"\n  ❌ Bot: {e}\n","err_msg"))
        finally:
            self.after(0, lambda: self.ghost.set_state(GhostCanvas.IDLE))

    def _quick_web_search(self, query):
        """Schnelle DuckDuckGo Suche, gibt Text zurück."""
        try:
            url = (f"https://api.duckduckgo.com/?q={urllib.parse.quote(query)}"
                   f"&format=json&no_html=1&skip_disambig=1")
            r = requests.get(url, timeout=8,
                             headers={"User-Agent":"Ghostfish/1.0"})
            d = r.json()
            parts = []
            if d.get("Answer"):       parts.append(d["Answer"])
            if d.get("AbstractText"): parts.append(d["AbstractText"][:400])
            for t in (d.get("RelatedTopics") or [])[:3]:
                if isinstance(t, dict) and t.get("Text"):
                    parts.append(t["Text"][:150])
            return "\n".join(parts) if parts else ""
        except Exception:
            return ""

    # ── Crypto-Guesser ────────────────────────────────────────────────────────
    def _open_crypto(self):
        """Öffnet das Crypto-Guesser Fenster."""
        if self._crypto_win and self._crypto_win.winfo_exists():
            self._crypto_win.lift()
            return
        self._crypto_win = CryptoWindow(
            self,
            model_var=self.selected_model,
            system_fn=self._build_system_prompt)
        self._crypto_win.focus()

    # ── MoE Agent-Netzwerk ────────────────────────────────────────────────────
    def _update_moe_status(self):
        """Aktualisiert die Sidebar mit Agent-Status."""
        try:
            lines = []
            for nid, node in self.moe.nodes.items():
                dot  = "●" if node["online"] else "○"
                col  = GREEN if node["online"] else TEXT_DIM
                n    = len(node.get("models", []))
                lines.append(f"{dot} {node['icon']} {node['name']}")
                if node["online"]:
                    lines.append(f"   {n} Modelle")
            self.moe_status_lbl.configure(text="\n".join(lines))
        except Exception:
            pass

    def _open_moe_panel(self):
        """Öffnet das Agent-Netzwerk Konfigurations-Panel."""
        win = ctk.CTkToplevel(self)
        win.title("🔗  Agent-Netzwerk  —  Mixture of Experts")
        win.geometry("680x580")
        win.configure(fg_color=BG_DARK)
        win.grab_set()

        win.grid_columnconfigure(0, weight=1)
        win.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(win, text="🔗  Agent-Netzwerk",
                     font=ctk.CTkFont("Helvetica",16,"bold"),
                     text_color=ACCENT).grid(row=0,column=0,padx=16,pady=(16,8),sticky="w")

        scroll = ctk.CTkScrollableFrame(win, fg_color="transparent")
        scroll.grid(row=1,column=0,sticky="nsew",padx=12,pady=4)
        scroll.grid_columnconfigure(0,weight=1)

        # ── Node-Karten ────────────────────────────────────────────────────
        node_entries = {}
        for row_i, (nid, node) in enumerate(self.moe.nodes.items()):
            online = node["online"]
            fc     = BG_CARD
            bc     = GREEN if online else BG_INPUT

            card = ctk.CTkFrame(scroll, fg_color=fc, corner_radius=10,
                                border_width=1, border_color=bc)
            card.grid(row=row_i,column=0,sticky="ew",padx=4,pady=5)
            card.grid_columnconfigure(1,weight=1)

            # Header
            status_txt = "● ONLINE" if online else "○ Offline"
            status_col = GREEN if online else RED
            ctk.CTkLabel(card,
                text=f"{node['icon']}  {node['name']}",
                font=ctk.CTkFont("Helvetica",13,"bold"),
                text_color=ACCENT).grid(row=0,column=0,padx=12,pady=(10,4),sticky="w")
            ctk.CTkLabel(card, text=status_txt,
                font=ctk.CTkFont(size=11, weight="bold"), text_color=status_col
                ).grid(row=0,column=1,sticky="e",padx=12)

            # Rollen
            roles_txt = "  ".join(f"[{r}]" for r in node.get("role",[]))
            ctk.CTkLabel(card, text=f"Rollen: {roles_txt}",
                font=ctk.CTkFont(size=10), text_color=TEXT_DIM
                ).grid(row=1,column=0,columnspan=2,padx=12,sticky="w")

            # URL Eingabe
            ctk.CTkLabel(card, text="URL:",
                font=ctk.CTkFont(size=11), text_color=TEXT_DIM
                ).grid(row=2,column=0,padx=12,pady=(6,0),sticky="w")
            url_e = ctk.CTkEntry(card, fg_color=BG_INPUT,
                                  border_color=ACCENT2, border_width=1,
                                  font=ctk.CTkFont("Courier",11))
            url_e.insert(0, node["url"])
            url_e.grid(row=3,column=0,columnspan=2,sticky="ew",padx=12,pady=(2,4))

            # Modelle
            if node.get("models"):
                models_txt = "  ".join(node["models"][:6])
                ctk.CTkLabel(card,
                    text=f"Modelle: {models_txt}{'...' if len(node.get('models',[])) > 6 else ''}",
                    font=ctk.CTkFont("Courier",9), text_color=TEXT_DIM,
                    wraplength=580, justify="left"
                    ).grid(row=4,column=0,columnspan=2,padx=12,pady=(0,4),sticky="w")

            # Test-Button
            def test_node(nid_=nid, e=url_e, c=card, bc_=bc):
                url = e.get().strip()
                self.moe.set_node_url(nid_, url)
                self._sys_msg(f"🔄  Teste {nid_} @ {url}...")

            ctk.CTkButton(card, text="🔄 Testen & Speichern",
                height=28, fg_color=ACCENT2, hover_color=ACCENT,
                font=ctk.CTkFont(size=11),
                command=test_node
                ).grid(row=5,column=0,padx=12,pady=(4,10),sticky="w")

            node_entries[nid] = url_e

        # ── Expert-Routing Tabelle ─────────────────────────────────────────
        ctk.CTkLabel(scroll,
            text="⚙️  Expert-Routing  —  Welche Aufgabe → welcher Agent",
            font=ctk.CTkFont("Helvetica",12,"bold"),
            text_color=ACCENT).grid(row=len(self.moe.nodes),column=0,
                                     padx=4,pady=(12,6),sticky="w")

        route_frame = ctk.CTkFrame(scroll, fg_color=BG_CARD, corner_radius=10)
        route_frame.grid(row=len(self.moe.nodes)+1,column=0,sticky="ew",padx=4,pady=4)
        route_frame.grid_columnconfigure(2,weight=1)

        # Header
        for ci,txt in enumerate(["Aufgabe","Agent","Modell"]):
            ctk.CTkLabel(route_frame, text=txt,
                font=ctk.CTkFont(size=10, weight="bold"), text_color=TEXT_DIM
                ).grid(row=0,column=ci,padx=12,pady=6,sticky="w")

        task_icons = {"vision":"👁","code":"💻","chat":"💬",
                      "analysis":"📊","search":"🔍","crypto":"🪙"}
        node_names = list(self.moe.nodes.keys())

        for ri, (task,(nid,mdl)) in enumerate(self.moe.routes.items(), start=1):
            icon = task_icons.get(task,"🔧")
            ctk.CTkLabel(route_frame, text=f"{icon} {task}",
                font=ctk.CTkFont(size=11), text_color="#e2e8f0"
                ).grid(row=ri,column=0,padx=12,pady=3,sticky="w")

            node_var = ctk.StringVar(value=nid)
            ctk.CTkOptionMenu(route_frame, variable=node_var,
                values=node_names, width=100, height=24,
                fg_color=BG_INPUT, button_color=ACCENT2,
                button_hover_color=ACCENT,
                font=ctk.CTkFont(size=10),
                command=lambda v,t=task,mv=None: None
                ).grid(row=ri,column=1,padx=8,pady=3)

            mdl_e = ctk.CTkEntry(route_frame, fg_color=BG_INPUT,
                                   border_color=ACCENT2, border_width=1,
                                   font=ctk.CTkFont("Courier",10), height=24)
            mdl_e.insert(0, mdl)
            mdl_e.grid(row=ri,column=2,padx=(0,12),pady=3,sticky="ew")

        # ── Info ──────────────────────────────────────────────────────────
        info_txt = (
            "Setup PC 2 (Vision-Agent):\n"
            "1. Ollama auf PC 2 installieren\n"
            "2. PowerShell auf PC 2:\n"
            "   $env:OLLAMA_HOST='0.0.0.0:11434'\n"
            "   $env:OLLAMA_ORIGINS='*'\n"
            "   ollama serve\n"
            "3. Modell auf PC 2 laden:\n"
            "   ollama pull llava\n"
            "4. IP von PC 2 oben eintragen und testen\n\n"
            "Ghostfish detects automatically:\n"
            "  Bild gesendet   --> Vision-Agent (PC 2)\n"
            "  Code-Frage      --> Code-Expert Modell\n"
            "  Normal-Chat     --> Lokaler Agent"
        )
        ctk.CTkLabel(scroll, text=info_txt,
            font=ctk.CTkFont("Courier",10), text_color=TEXT_DIM,
            justify="left", wraplength=580
            ).grid(row=len(self.moe.nodes)+2,column=0,
                   padx=4,pady=12,sticky="w")

        ctk.CTkButton(win, text="✓  Schließen",
                      fg_color=ACCENT2, hover_color=ACCENT,
                      font=ctk.CTkFont(size=13),
                      command=win.destroy
                      ).grid(row=2,column=0,pady=10)

    def _save_to_obsidian(self):
        if not self.chat_history:
            self._sys_msg("⚠️  Kein Chat."); return
        ts=datetime.datetime.now()
        title=self.current_entry.title if self.current_entry else "Chat"
        fname=ts.strftime("Chat_%Y-%m-%d_%H-%M.md")
        path=Path(OBSIDIAN_FOLDER)/fname
        lines=[f"# 👻 {title}","",
               f"> **Modell:** `{self.selected_model.get()}`","","---",""]
        for m in self.chat_history:
            iu=m["role"]=="user"
            lines+=[f"#### {'👤 Du' if iu else f'🐟 {AI_NAME}'}","",m["content"],""]
        path.write_text("\n".join(lines),encoding="utf-8")
        self._sys_msg(f"✓  Gespeichert: {path.resolve()}")
        if os.name=="nt": os.startfile(str(path.resolve()))


if __name__=="__main__":
    app=GhostfishApp()
    app.mainloop()
