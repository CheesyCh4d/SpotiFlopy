# =====================================================================
# SpotiFlopy - One-Shot Environment Setup + Launcher
# Double-click SpotiFlopy.bat to run this. Do not run this file directly
# unless you know your PowerShell execution policy allows it.
#
# What this script does, in order:
#   1. Verifies Python is installed
#   2. Installs deno (JavaScript runtime yt-dlp needs) if missing
#   3. Installs ffmpeg (MP3 converter) if missing
#   4. Adds both to your PATH if missing
#   5. Installs/updates all Python packages (spotipy, yt-dlp,
#      python-dotenv, yt-dlp-ejs)
#   6. Verifies everything, then launches main2.py
#
# Every step is IDEMPOTENT: already-installed components are skipped.
# Safe to run repeatedly.
# =====================================================================

$ErrorActionPreference = "Stop"   # Stop the script on any error instead of plowing ahead

function Write-Section($text) {
    Write-Host ""
    Write-Host "==== $text ====" -ForegroundColor Cyan
}

function Add-ToUserPath($folder) {
    # Reads the PATH stored in your Windows user profile, appends the
    # folder if it is not already there, and writes it back.
    # Also updates THIS session's PATH so the rest of the script can
    # use the new tools immediately without a terminal restart.
    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
    if ($userPath -notlike "*$folder*") {
        [Environment]::SetEnvironmentVariable("Path", "$userPath;$folder", "User")
        Write-Host "  Added to user PATH: $folder"
    } else {
        Write-Host "  Already on user PATH: $folder"
    }
    if ($env:Path -notlike "*$folder*") {
        $env:Path = "$env:Path;$folder"
    }
}

# ---------------------------------------------------------------------
# STEP 1 - Python
# ---------------------------------------------------------------------
Write-Section "Step 1: Checking Python"
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "Python was NOT found on PATH." -ForegroundColor Red
    Write-Host "Install it from https://www.python.org/downloads/"
    Write-Host "During install, CHECK the box 'Add python.exe to PATH'."
    Write-Host "Then run this setup again."
    Read-Host "Press Enter to exit"
    exit 1
}
python --version
Write-Host "  Python OK."

# ---------------------------------------------------------------------
# STEP 2 - Deno (JavaScript runtime required by yt-dlp for YouTube)
# ---------------------------------------------------------------------
Write-Section "Step 2: Checking deno"
$denoExe = "$env:USERPROFILE\.deno\bin\deno.exe"
if (Get-Command deno -ErrorAction SilentlyContinue) {
    Write-Host "  deno already installed and on PATH."
} elseif (Test-Path $denoExe) {
    Write-Host "  deno installed but not on PATH. Fixing PATH."
    Add-ToUserPath "$env:USERPROFILE\.deno\bin"
} else {
    Write-Host "  deno not found. Installing..."
    irm https://deno.land/install.ps1 | iex
    Add-ToUserPath "$env:USERPROFILE\.deno\bin"
}
deno --version
Write-Host "  deno OK."

# ---------------------------------------------------------------------
# STEP 3 - ffmpeg (converts downloaded audio to MP3)
# ---------------------------------------------------------------------
Write-Section "Step 3: Checking ffmpeg"
if (Get-Command ffmpeg -ErrorAction SilentlyContinue) {
    Write-Host "  ffmpeg already installed and on PATH."
} else {
    # Check the two common install locations before downloading
    $candidates = @("C:\ffmpeg\bin", "$env:USERPROFILE\ffmpeg\bin")
    $found = $null
    foreach ($c in $candidates) {
        if (Test-Path "$c\ffmpeg.exe") { $found = $c; break }
    }
    if ($found) {
        Write-Host "  ffmpeg installed at $found but not on PATH. Fixing PATH."
        Add-ToUserPath $found
    } else {
        Write-Host "  ffmpeg not found. Downloading release-essentials build..."
        $zip = "$env:TEMP\ffmpeg.zip"
        $dest = "$env:USERPROFILE\ffmpeg"
        # gyan.dev provides a stable 'latest release' URL
        Invoke-WebRequest -Uri "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip" -OutFile $zip
        Write-Host "  Extracting..."
        Expand-Archive -Path $zip -DestinationPath "$env:TEMP\ffmpeg_extract" -Force
        # The zip contains one versioned folder (e.g. ffmpeg-7.1-essentials_build).
        # Move its contents to a clean, version-free folder so the PATH never breaks.
        $inner = Get-ChildItem "$env:TEMP\ffmpeg_extract" -Directory | Select-Object -First 1
        if (Test-Path $dest) { Remove-Item $dest -Recurse -Force }
        Move-Item $inner.FullName $dest
        Remove-Item $zip -Force
        Remove-Item "$env:TEMP\ffmpeg_extract" -Recurse -Force
        Add-ToUserPath "$dest\bin"
    }
}
ffmpeg -version | Select-Object -First 1
Write-Host "  ffmpeg OK."

# ---------------------------------------------------------------------
# STEP 4 - Python packages
# ---------------------------------------------------------------------
Write-Section "Step 4: Installing Python packages"
# --upgrade keeps yt-dlp current. YouTube changes constantly; an old
# yt-dlp is the #1 cause of sudden download failures.
python -m pip install --upgrade pip --quiet
python -m pip install --upgrade spotipy yt-dlp yt-dlp-ejs python-dotenv
Write-Host "  Packages OK."

# ---------------------------------------------------------------------
# STEP 5 - Verification
# ---------------------------------------------------------------------
Write-Section "Step 5: Verifying environment"
$denoFromPython = python -c "import shutil; print(shutil.which('deno'))"
Write-Host "  deno visible from Python : $denoFromPython"
$ytdlpVer = python -c "import yt_dlp; print(yt_dlp.version.__version__)"
Write-Host "  yt-dlp version           : $ytdlpVer"
python -m pip show yt-dlp-ejs > $null 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  yt-dlp-ejs               : installed"
} else {
    Write-Host "  yt-dlp-ejs               : MISSING" -ForegroundColor Red
}
if (-not (Test-Path ".env")) {
    Write-Host ""
    Write-Host "  WARNING: No .env file found in this folder." -ForegroundColor Yellow
    Write-Host "  Create one with your Spotify credentials before the script will work:"
    Write-Host "    SPOTIPY_CLIENT_ID=..."
    Write-Host "    SPOTIPY_CLIENT_SECRET=..."
    Write-Host "    SPOTIPY_REDIRECT_URI=http://127.0.0.1:8888/callback/"
}

# ---------------------------------------------------------------------
# STEP 6 - Launch
# ---------------------------------------------------------------------
Write-Section "Step 6: Launching SpotiFlopy"
if (Test-Path "main2.py") {
    python main2.py
} elseif (Test-Path "main.py") {
    python main.py
} else {
    Write-Host "  No main2.py or main.py found in this folder." -ForegroundColor Red
    Write-Host "  Place this setup in the SpotiFlopy project folder and rerun."
}

Write-Host ""
Read-Host "Done. Press Enter to close"
