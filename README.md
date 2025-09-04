# 🎵 Spotify Playlist Downloader (Experimental)

> ⚠️ **Disclaimer**: This project is for **learning and personal experiments only**.  
> Do not use it to distribute copyrighted music. If you want offline listening, please use the official **Spotify Premium** download feature.

## 📦 What is this?
A simple Python script that can:
- Fetch all tracks from a Spotify playlist  
- Search for each track on YouTube automatically  
- Download them as MP3 files  
- Embed metadata (title, artist, album, year, cover art)  
- Save artist photos into your chosen folder  

## 🚀 How to Use (Step by Step)

```bash
git clone https://github.com/catherinerafael/SpotifyPlaylistDownloader.git
```

## 

```bash
pip install requests mutagen yt-dlp tkinter
```

## 

```bash
python main.py
```

## 📝 Notes: Spotify Client ID & Client Secret

This script **requires a Spotify Client ID and Client Secret** to access the Spotify Web API.  
Without them, the script cannot fetch playlist and track metadata.

### 🔑 How to get your Client ID and Secret
1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard).  
2. Log in with your Spotify account.  
3. Click **"Create an App"**.  
4. Fill in the App Name and Description (anything you like).  
5. Once the app is created, you will see **Client ID** on the app page.  
6. Click **Show Client Secret** to reveal your secret key.  
7. Copy both values and paste them into your `main.py` file:

   ```python
   CLIENT_ID = "your_client_id"
   CLIENT_SECRET = "your_client_secret"
