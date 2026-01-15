# SpotiFlopy
Automatically download Liked songs or Playlists

## **Features** 
- Downloads audio from YouTube using `yt-dlp`.
- Stores downloaded MP3s in a folder on your desktop.

---

## **How It Works** ⚙️
1. The script uses the Spotify API to download all liked songs, or download a linked playlist.
2. New songs are searched on YouTube and downloaded in MP3 format using `yt-dlp`.
3. The downloaded songs are saved to the **Songs** folder on your desktop.

---
## **Software to download
1. git -- https://git-scm.com/install/
2. python -- https://www.python.org/downloads/
3. ffmpeg -- https://www.gyan.dev/ffmpeg/builds/
---

## **Installation Instructions**

### 1. Clone the Repository:
```bash
git clone https://github.com/yourusername/yourprojectname.git
cd yourprojectname
```

### 2. Install Dependencies:
Make sure you have Python 3 installed. Then install the required packages:
```bash
python -m pip install -r requirements.txt
If you have trouble, you may have to install dependencies individually
```

### 3. Set Up Spotify API Credentials:
1. This requires setting up a Spotify Developer Account. You may need to have Spotify premium to do so.
   Without the developer account, you will not have a client_id and client_secret.
2. Create a .env file in the root directory of the project. (new text file, save as .env after filling in information)
3. Add your Spotify API credentials in the .env file:

```env
SPOTIPY_CLIENT_ID=your_spotify_client_id
SPOTIPY_CLIENT_SECRET=your_spotify_client_secret
SPOTIPY_REDIRECT_URI=http://127.0.0.1:8888/callback/
```
### 4. Run the script
```bash
python main.py
```

The first time you run the script, it will open a browser for you to authenticate with Spotify. After that, it will handle token refreshes automatically.
---

### 5. ffmpeg instructions

You may have to manually set the path via command prompt, even if you see it correctly set in Environment Variables.

# FFmpeg Installation Guide for Windows
## Download FFmpeg

1. Visit: https://www.gyan.dev/ffmpeg/builds/
2. Download the **"release essentials"** zip file (not the full build)
   - File will be named something like: `ffmpeg-release-essentials.zip`

## Install FFmpeg

1. Create a folder for FFmpeg:
   - Recommended location: `C:\ffmpeg`
   - You can use any location, but C:\ root is simplest

2. Extract the downloaded zip file:
   - Right-click the zip → "Extract All"
   - Extract to `C:\`
   - This creates a folder like `C:\ffmpeg-2024-01-12-git-xyz`
   - Rename this folder to just `C:\ffmpeg`

3. Verify the structure:
   - You should have: `C:\ffmpeg\bin\ffmpeg.exe`
   - Also present: `C:\ffmpeg\bin\ffprobe.exe`

## Add FFmpeg to System PATH

### Method 1: GUI (Recommended)

1. Open Environment Variables:
   - Press Windows key
   - Type "Environment Variables"
   - Click "Edit the system environment variables"
   - Click "Environment Variables" button at bottom

2. Edit System PATH:
   - In the "System variables" section (bottom half)
   - Find and select "Path"
   - Click "Edit"
   - Click "New"
   - Type: `C:\ffmpeg\bin`
   - Click "OK" on all windows

3. **IMPORTANT**: Close all terminals/command prompts and open new ones

### Method 2: Command Line (If GUI fails)

Open Command Prompt **as Administrator** and run:
```bash
# For current user only
setx PATH "%PATH%;C:\ffmpeg\bin"

# OR for system-wide (requires admin)
setx /M PATH "%PATH%;C:\ffmpeg\bin"
```

**Warning:** Be careful with setx - PATH has a 1024 character limit. If you get "WARNING: The data being saved is truncated", use this safer approach:
```bash
# Check current PATH length first
echo %PATH% | wc -c

# If close to 1024 characters, manually add via registry
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path /t REG_EXPAND_SZ /d "%PATH%;C:\ffmpeg\bin" /f
```

After using setx or reg:
1. Close ALL terminals
2. Open fresh terminal
3. Verify with `where ffmpeg`

## Verify Installation

Open a NEW Command Prompt or PowerShell and run:
```bash
ffmpeg -version
```

Expected output starts with:
```
ffmpeg version 202X-XX-XX-git-XXXXXX-essentials_build
```

Also verify ffprobe:
```bash
ffprobe -version
```
If this prints version info, FFmpeg is correctly installed and accessible to Python.
