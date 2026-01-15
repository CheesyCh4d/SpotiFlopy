import csv
import os
from pathlib import Path
from yt_dlp import YoutubeDL
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import re

# No special scope needed to read public playlists
scope = "user-library-read"

load_dotenv()
client_id = os.getenv("SPOTIPY_CLIENT_ID")
client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri=redirect_uri,
                                               scope=scope))

SONGS_TRACKER = "songs.csv"
DESKTOP_PATH = Path.home() / "Desktop" / "Songs"
# Ensure the Songs folder exists
DESKTOP_PATH.mkdir(parents=True, exist_ok=True)

def search_youtube(query: str) -> str:
    """
    Return the URL of the top YouTube result for the given query.
    Uses yt-dlp's built-in search extractor (no API key needed).
    """
    ydl_opts = {"quiet": True, "skip_download": True}
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch1:{query}", download=False)
        if not info["entries"]:
            raise ValueError(f"No YouTube results for {query!r}")
        return f"https://www.youtube.com/watch?v={info['entries'][0]['id']}"

def extract_playlist_id(playlist_url_or_id: str) -> str:
    """
    Extract playlist ID from various Spotify URL formats or return ID if already provided.
    Supports:
    - https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M
    - https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M?si=...
    - spotify:playlist:37i9dQZF1DXcBWIGoYBM5M
    - 37i9dQZF1DXcBWIGoYBM5M (direct ID)
    """
    # Remove any trailing parameters
    playlist_url_or_id = playlist_url_or_id.split('?')[0]
    
    # Extract from various URL formats
    patterns = [
        r'https://open\.spotify\.com/playlist/([a-zA-Z0-9]+)',
        r'spotify:playlist:([a-zA-Z0-9]+)',
        r'^([a-zA-Z0-9]{22})$'  # Direct ID (22 characters)
    ]
    
    for pattern in patterns:
        match = re.search(pattern, playlist_url_or_id)
        if match:
            return match.group(1)
    
    # If no pattern matches, assume it's already an ID
    return playlist_url_or_id

def getPlaylistTracks(playlist_id: str) -> list:
    """Get all tracks from any Spotify playlist (public or private if user has access)"""
    try:
        # Get playlist info first
        playlist_info = sp.playlist(playlist_id)
        print(f"Playlist: {playlist_info['name']} by {playlist_info['owner']['display_name']}")
        print(f"Total tracks: {playlist_info['tracks']['total']}")
        
        # Get all tracks
        results = sp.playlist_tracks(playlist_id, limit=50)
        all_tracks = []
        
        while results:
            for item in results['items']:
                if item['track'] and item['track']['name']:  # Check if track exists
                    track = item['track']
                    song_name = track['name']
                    artist_name = track['artists'][0]['name']
                    all_tracks.append(f"{song_name} by {artist_name}")
            
            if results['next']:
                results = sp.next(results)
            else:
                break
        
        return all_tracks
        
    except spotipy.exceptions.SpotifyException as e:
        if e.http_status == 404:
            raise ValueError("Playlist not found or is private")
        elif e.http_status == 403:
            raise ValueError("Access denied - playlist may be private")
        else:
            raise ValueError(f"Spotify API error: {e}")

def getLikedSongs():
    """Get all liked songs on Spotify"""
    results = sp.current_user_saved_tracks(limit=50)
    all_tracks = []
   
    while results:
        for item in results['items']:
            track = item['track']
            song_name = track['name']
            artist_name = track['artists'][0]['name']
            all_tracks.append(f"{song_name} by {artist_name}")
        if results['next']:
            results = sp.next(results)
        else:
            break
    return all_tracks

def getDownloadedSongs():
    """Read CSV and get already downloaded songs"""
    if not os.path.exists(SONGS_TRACKER):
        return []
    downloaded_songs = []
    with open(SONGS_TRACKER, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            if len(row) < 2:
                continue  # Skip rows that don't have both song name and artist
            song_name = row[0].strip()
            artist_name = row[1].strip()
            downloaded_songs.append(f"{song_name} by {artist_name}")
    return downloaded_songs  

def getNewSong(song, artist):
    """Add the new song into the CSV file"""
    with open(SONGS_TRACKER, 'a', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([song, artist])

def downloadSong(song: str, artist: str) -> None:
    """Download song from YouTube"""
    query = f"{song} by {artist}"
    youtube_url = search_youtube(query)
    
    # Try with ffmpeg first, fallback to basic audio format if ffmpeg not available
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": str(DESKTOP_PATH / f"{query}.%(ext)s"),
    }
    
    # Try to use ffmpeg for MP3 conversion
    try:
        ydl_opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }]
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
    except Exception as e:
        if "ffmpeg" in str(e).lower():
            print(f"  Warning: ffmpeg not found, downloading as original format")
            # Remove postprocessors and download in original format
            ydl_opts.pop("postprocessors", None)
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([youtube_url])
        else:
            raise e

def main():
    print("=== Spotify Playlist Downloader ===")
    print("1. Download from Liked Songs")
    print("2. Download from any Spotify playlist")
    
    choice = input("\nEnter your choice (1-2): ").strip()
    
    if choice == "1":
        # Original functionality - download liked songs
        print("\nFetching liked songs...")
        songs = getLikedSongs()
        print(f"Found {len(songs)} liked songs")
        
    elif choice == "2":
        # Download from any playlist
        playlist_input = input("\nEnter Spotify playlist URL or ID: ").strip()
        
        if not playlist_input:
            print("No playlist provided!")
            return
        
        try:
            playlist_id = extract_playlist_id(playlist_input)
            print(f"\nFetching playlist tracks...")
            songs = getPlaylistTracks(playlist_id)
            print(f"Found {len(songs)} songs in playlist")
            
        except ValueError as e:
            print(f"Error: {e}")
            return
        except Exception as e:
            print(f"Unexpected error: {e}")
            return
            
    else:
        print("Invalid choice!")
        return
    
    if not songs:
        print("No songs found!")
        return
    
    # Common download logic
    downloaded_songs = getDownloadedSongs()
    new_songs = [song for song in songs if song not in downloaded_songs]
    
    print(f'\nNew Songs: {len(new_songs)}')
    if len(new_songs) == 0:
        print("No new songs to download!")
        return
    
    # Show first few songs as preview
    print("Songs to download:")
    for i, song in enumerate(new_songs[:5], 1):
        print(f"  {i}. {song}")
    if len(new_songs) > 5:
        print(f"  ... and {len(new_songs) - 5} more")
    
    confirm = input(f"\nDownload {len(new_songs)} new songs? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Download cancelled.")
        return
    
    # Download new songs and track them in the CSV
    success_count = 0
    for i, song in enumerate(new_songs, 1):
        try:
            song_name, artist_name = song.split(' by ', 1)
            print(f"[{i}/{len(new_songs)}] Downloading: {song}")
            downloadSong(song_name, artist_name)
            getNewSong(song_name, artist_name)
            success_count += 1
        except Exception as e:
            print(f"Failed to download {song}: {e}")
    
    print(f"\nDownload complete! Successfully downloaded {success_count}/{len(new_songs)} songs")
    print(f"Files saved to: {DESKTOP_PATH}")

if __name__ == '__main__':
    main()
