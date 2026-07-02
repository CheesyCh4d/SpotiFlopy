# SpotiFlopy — Environment Setup Guide
**Fixing yt-dlp "No supported JavaScript runtime" and JS challenge warnings on Windows**

Last updated: July 2, 2026
Applies to: `main2.py` (Spotify Playlist Downloader), yt-dlp 2026.06.09+, Windows 10/11

---

## Background: Why These Steps Are Required

YouTube serves its audio/video stream URLs through obfuscated JavaScript. yt-dlp must execute that JavaScript to extract download links. This requires two components:

1. **A JavaScript runtime** — yt-dlp uses **deno** by default.
2. **A challenge-solver package** — `yt-dlp-ejs`, which contains the scripts that solve YouTube's signature and "n" challenges.

Without both, yt-dlp falls back to degraded extraction: some formats (including the highest-bitrate audio) are missing, and downloads break more frequently when YouTube changes its systems.

Bare `pip install yt-dlp` does **not** include the solver package. This is the root cause of the final warnings.

---

## Prerequisites (Assumed Already Working)

- Python 3.x installed and on PATH
- Project packages: `yt-dlp`, `spotipy`, `python-dotenv`
- ffmpeg installed (required for MP3 conversion via the script's postprocessor)
- Spotify API credentials in a `.env` file: `SPOTIPY_CLIENT_ID`, `SPOTIPY_CLIENT_SECRET`, `SPOTIPY_REDIRECT_URI`

---

## Step 1 — Install Deno

Run in PowerShell:

```powershell
irm https://deno.land/install.ps1 | iex
```

This downloads and installs the deno JavaScript runtime to:

```
%USERPROFILE%\.deno\bin\deno.exe
```

**Verify the binary exists:**

```powershell
Test-Path "$env:USERPROFILE\.deno\bin\deno.exe"
```

Expected output: `True`

---

## Step 2 — Add Deno to the User PATH

The installer does not always update PATH. Add it manually:

```powershell
[Environment]::SetEnvironmentVariable("Path", [Environment]::GetEnvironmentVariable("Path","User") + ";$env:USERPROFILE\.deno\bin", "User")
```

**What this does:** Appends the deno folder to the PATH stored in the Windows user profile (registry). Only *new* processes inherit the change.

---

## Step 3 — Restart Terminals (and Possibly the Machine)

PATH changes do not reach already-running processes.

1. Close **every** open terminal window.
2. If launching the script from an IDE (VS Code, PyCharm), close the IDE completely and reopen it — IDEs cache PATH at startup and pass the stale copy to integrated terminals.
3. If the warning still appears after that, reboot Windows. Explorer itself caches PATH and passes it to everything it launches.

**Verify in a new terminal:**

```
deno --version
```

Expected: version output (e.g., `deno 2.x.x`).

---

## Step 4 — Verify Deno Is Visible from Inside Python

The Python process may see a different PATH than the terminal. Confirm:

```powershell
python -c "import shutil; print(shutil.which('deno'))"
```

Expected: a full path, e.g. `C:\Users\<name>\.deno\bin\deno.EXE`
If it prints `None`, return to Step 3.

**Also confirm yt-dlp is current** (EJS support requires a recent build):

```powershell
python -c "import yt_dlp; print(yt_dlp.version.__version__)"
```

Expected: `2025.x` or later (verified working: `2026.06.09`).

---

## Step 5 — Install the Challenge-Solver Package

This was the final missing piece. Check whether it is installed:

```powershell
python -m pip show yt-dlp-ejs
```

If it reports `Package(s) not found`, install it:

```
pip install yt-dlp-ejs
```

**What this does:** Provides the JS challenge-solver scripts locally. yt-dlp uses deno to run these scripts and decode YouTube's signature and "n" challenges. With the package installed locally, no remote component download is needed.

---

## Step 6 — Confirm Everything Works

Run the script:

```
python main2.py
```

All three warning types should be gone:

- `No supported JavaScript runtime could be found` → fixed by Steps 1–4
- `Remote components challenge solver script (deno) ... were skipped` → fixed by Step 5
- `Signature solving failed` / `n challenge solving failed` → fixed by Step 5

Full format selection, including highest-bitrate audio, is now available.

---

## Optional / Superseded: Remote Components Config File

Before installing `yt-dlp-ejs`, an alternative was to allow yt-dlp to fetch the solver remotely at runtime via a global config file:

```powershell
New-Item -ItemType Directory -Force -Path "$env:APPDATA\yt-dlp"
Set-Content -Path "$env:APPDATA\yt-dlp\config.txt" -Value "--remote-components ejs:github"
```

**Status: no longer required.** The locally installed `yt-dlp-ejs` package supersedes remote fetching. The config file is harmless if left in place; delete it if unwanted:

```powershell
Remove-Item "$env:APPDATA\yt-dlp\config.txt"
```

Note: `--remote-components ejs:github` is a permission flag, not a standalone command. Running `yt-dlp --remote-components ejs:github` alone fails with "You must provide at least one URL."

---

## Troubleshooting Reference

| Symptom | Cause | Fix |
|---|---|---|
| `No supported JavaScript runtime could be found` | Deno not installed or not on PATH for the running process | Steps 1–4 |
| Warning persists in terminal but `deno --version` works | Script launched from a process with stale PATH (IDE, scheduler) | Restart IDE / reboot (Step 3) |
| `Signature solving failed` / `n challenge solving failed` | `yt-dlp-ejs` package missing | Step 5 |
| `ERROR: <id>: This video is not available` | Video deleted or region-blocked — unrelated to setup | None; script skips it |
| `shutil.which('deno')` returns `None` but terminal finds deno | Different Python environment or stale parent process | Restart the launching process; verify same terminal |

---

## Quick Rebuild Checklist (Fresh Machine)

```powershell
# 1. Install deno
irm https://deno.land/install.ps1 | iex

# 2. Add to PATH (if installer didn't)
[Environment]::SetEnvironmentVariable("Path", [Environment]::GetEnvironmentVariable("Path","User") + ";$env:USERPROFILE\.deno\bin", "User")

# 3. NEW terminal, then:
deno --version

# 4. Install Python packages
pip install yt-dlp yt-dlp-ejs spotipy python-dotenv

# 5. Verify
python -c "import shutil; print(shutil.which('deno'))"
python -m pip show yt-dlp-ejs

# 6. Run
python main2.py
```
