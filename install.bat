@echo off
chcp 65001 >nul
title Geist-AI Installer
color 0A

echo.
echo  ╔══════════════════════════════════════════╗
echo  ║        Geist-AI  —  Auto-Installer      ║
echo  ║   Lokale KI mit Ollama  (kein Account)  ║
echo  ╚══════════════════════════════════════════╝
echo.
echo  Dieser Installer richtet alles automatisch ein.
echo  Bitte warte und beantworte eventuelle Fragen.
echo.
pause

:: ─── Ordner für Geist-AI ────────────────────────────────────────────────────
set "INSTALL_DIR=%USERPROFILE%\Geist-AI"
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
cd /d "%INSTALL_DIR%"

echo.
echo  [1/6] Pruefe Python...
echo  ─────────────────────────────────────────────

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  Python nicht gefunden. Installiere Python 3.11...
    echo.
    :: Python via winget installieren
    winget install Python.Python.3.11 --silent --accept-package-agreements --accept-source-agreements
    if %errorlevel% neq 0 (
        echo.
        echo  winget hat nicht funktioniert.
        echo  Oeffne Python Download-Seite...
        start https://www.python.org/downloads/
        echo.
        echo  Bitte Python installieren, dann dieses Script nochmal starten.
        pause
        exit /b 1
    )
    :: PATH neu laden
    call refreshenv >nul 2>&1
    set "PATH=%PATH%;%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python311\Scripts"
) else (
    for /f "tokens=*" %%v in ('python --version 2^>^&1') do echo  Gefunden: %%v
)

echo.
echo  [2/6] Pruefe pip...
echo  ─────────────────────────────────────────────
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  pip nicht gefunden. Installiere pip...
    python -m ensurepip --upgrade
)
python -m pip install --upgrade pip --quiet
echo  pip OK

echo.
echo  [3/6] Installiere Python-Pakete...
echo  ─────────────────────────────────────────────
echo  (Das kann 1-3 Minuten dauern)
echo.

python -m pip install requests customtkinter pillow --quiet
if %errorlevel% neq 0 (
    echo  FEHLER bei pip install!
    echo  Versuche mit --user Flag...
    python -m pip install requests customtkinter pillow --user --quiet
)

:: Optionale Pakete
echo  Installiere optionale Pakete (Sprache, PDF)...
python -m pip install SpeechRecognition playsound pdfplumber --quiet 2>nul
echo  Pakete fertig.

echo.
echo  [4/6] Pruefe Ollama...
echo  ─────────────────────────────────────────────

where ollama >nul 2>&1
if %errorlevel% neq 0 (
    echo  Ollama nicht gefunden. Installiere Ollama...
    echo.
    :: Ollama Installer herunterladen
    curl -L "https://ollama.com/download/OllamaSetup.exe" -o "%TEMP%\OllamaSetup.exe"
    if %errorlevel% neq 0 (
        echo  Download fehlgeschlagen. Oeffne Ollama Download-Seite...
        start https://ollama.com/download
        echo.
        echo  Bitte Ollama manuell installieren, dann dieses Script nochmal starten.
        pause
        exit /b 1
    )
    echo  Starte Ollama Installer...
    "%TEMP%\OllamaSetup.exe" /S
    timeout /t 5 /nobreak >nul
    :: PATH updaten
    set "PATH=%PATH%;%LOCALAPPDATA%\Programs\Ollama"
    echo  Ollama installiert.
) else (
    echo  Ollama bereits installiert. OK
)

echo.
echo  [5/6] Lade KI-Modell herunter...
echo  ─────────────────────────────────────────────
echo  Waehle ein Modell:
echo.
echo   [1] qwen2.5:latest  (empfohlen, ~2GB, gut fuer alles)
echo   [2] llama3          (~4GB, sehr gut)
echo   [3] mistral         (~4GB, schnell)
echo   [4] Kein Modell     (ich lade es spaeter selbst)
echo.
set /p MODEL_CHOICE="Deine Wahl (1-4): "

if "%MODEL_CHOICE%"=="1" set "MODEL=qwen2.5:latest"
if "%MODEL_CHOICE%"=="2" set "MODEL=llama3"
if "%MODEL_CHOICE%"=="3" set "MODEL=mistral"
if "%MODEL_CHOICE%"=="4" goto SKIP_MODEL

if not defined MODEL set "MODEL=qwen2.5:latest"

echo.
echo  Starte Ollama im Hintergrund...
start /min "" ollama serve
timeout /t 3 /nobreak >nul

echo  Lade %MODEL% herunter... (kann 5-15 Min dauern je nach Internet)
ollama pull %MODEL%
if %errorlevel% neq 0 (
    echo.
    echo  Modell-Download fehlgeschlagen.
    echo  Starte Ollama manuell und fuehre aus:  ollama pull %MODEL%
)

:SKIP_MODEL

echo.
echo  [6/6] Kopiere Geist-AI...
echo  ─────────────────────────────────────────────

:: local_ai.py kopieren falls nicht schon da
if not exist "%INSTALL_DIR%\local_ai.py" (
    :: Aus dem gleichen Ordner wie install.bat kopieren
    set "SCRIPT_DIR=%~dp0"
    if exist "%SCRIPT_DIR%local_ai.py" (
        copy "%SCRIPT_DIR%local_ai.py" "%INSTALL_DIR%\local_ai.py" >nul
        echo  local_ai.py kopiert.
    ) else (
        echo  local_ai.py nicht gefunden neben install.bat.
        echo  Bitte local_ai.py in diesen Ordner legen:
        echo  %INSTALL_DIR%
        echo.
        explorer "%INSTALL_DIR%"
        pause
    )
) else (
    echo  local_ai.py bereits vorhanden. OK
)

:: Start-Script erstellen
echo @echo off > "%INSTALL_DIR%\Geist-AI starten.bat"
echo title Geist-AI >> "%INSTALL_DIR%\Geist-AI starten.bat"
echo cd /d "%INSTALL_DIR%" >> "%INSTALL_DIR%\Geist-AI starten.bat"
echo start /min "" ollama serve >> "%INSTALL_DIR%\Geist-AI starten.bat"
echo timeout /t 2 /nobreak ^>nul >> "%INSTALL_DIR%\Geist-AI starten.bat"
echo python local_ai.py >> "%INSTALL_DIR%\Geist-AI starten.bat"

:: Desktop Verknüpfung
set "SHORTCUT=%USERPROFILE%\Desktop\Geist-AI.lnk"
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT%'); $s.TargetPath = '%INSTALL_DIR%\Geist-AI starten.bat'; $s.WorkingDirectory = '%INSTALL_DIR%'; $s.Description = 'Geist AI starten'; $s.Save()" >nul 2>&1

echo.
echo  ╔══════════════════════════════════════════╗
echo  ║           Installation fertig!          ║
echo  ╚══════════════════════════════════════════╝
echo.
echo  Installiert in: %INSTALL_DIR%
echo.
echo  Starten:
echo   - Desktop: "Geist-AI" Verknuepfung doppelklicken
echo   - Oder:    "%INSTALL_DIR%\Geist-AI starten.bat"
echo.
echo  Hinweis: Ollama muss laufen wenn die App startet.
echo  Es startet automatisch im Hintergrund.
echo.

set /p START_NOW="Geist-AI jetzt starten? (j/n): "
if /i "%START_NOW%"=="j" (
    cd /d "%INSTALL_DIR%"
    start /min "" ollama serve
    timeout /t 2 /nobreak >nul
    python local_ai.py
)

echo.
echo  Viel Spass mit Geist-AI!
pause
