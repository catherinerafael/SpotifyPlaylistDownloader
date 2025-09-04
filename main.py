import requests
import base64
import re
import os
import tkinter as tk
from tkinter import filedialog
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, TDRC, TCON
from yt_dlp import YoutubeDL


CLIENT_ID = "your_client_id"
CLIENT_SECRET = "your_client_secret"


def get_token():
    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    b64_auth_str = base64.b64encode(auth_str.encode()).decode()
    headers = {"Authorization": f"Basic {b64_auth_str}"}
    data = {"grant_type": "client_credentials"}
    r = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)
    r.raise_for_status()
    return r.json()["access_token"]

def get_track_metadata(track_id, token):
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.spotify.com/v1/tracks/{track_id}"
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.json()

def get_playlist_tracks(playlist_id, token):
    headers = {"Authorization": f"Bearer {token}"}
    tracks = []
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    while url:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        data = r.json()
        tracks.extend([t["track"]["id"] for t in data["items"] if t["track"]])
        url = data.get("next")
    return tracks

def get_artist_genres(artist_id, token):
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.spotify.com/v1/artists/{artist_id}"
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        return r.json().get("genres", [])
    return []

def download_artist_photo(artist, token, output_folder):
    artist_name = safe_filename(artist["name"])
    file_path = os.path.join(output_folder, f"{artist_name}.jpg")
    if os.path.exists(file_path):
        return file_path
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.spotify.com/v1/artists/{artist['id']}"
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            data = r.json()
            images = data.get("images", [])
            if images:
                image_url = images[0]["url"]
                image_data = requests.get(image_url).content
                with open(file_path, "wb") as f:
                    f.write(image_data)
                return file_path
    except Exception as e:
        print(f"⚠️ Failed Download Artist Picture {artist_name}: {e}")
    return None


def safe_filename(name: str):
    return re.sub(r'[\\/*?:"<>|]', "", name)


def download_audio(query, filename, output_folder):
    full_path = os.path.join(output_folder, filename)
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": full_path,
        "quiet": True,
        "noplaylist": True,
        "postprocessors": [
            {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "128"}
        ],
        "ignoreerrors": True,
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"ytsearch1:{query}"])
        return full_path
    except Exception as e:
        print(f"❌ Failed Download {query}: {e}")
        return None

def embed_metadata(file, track_data, token):
    audio = MP3(file, ID3=ID3)
    if audio.tags is None:
        audio.add_tags()
    audio.tags["TIT2"] = TIT2(encoding=3, text=track_data.get("name", "Unknown"))
    audio.tags["TPE1"] = TPE1(
        encoding=3,
        text=[artist["name"] for artist in track_data.get("artists", [])]
    )
    audio.tags["TALB"] = TALB(encoding=3, text=track_data.get("album", {}).get("name", "Unknown"))
    release_date = track_data.get("album", {}).get("release_date", "")
    if release_date:
        year = release_date.split("-")[0]
        audio.tags["TDRC"] = TDRC(encoding=3, text=year)
    genres = track_data.get("album", {}).get("genres", [])
    for artist in track_data.get("artists", []):
        artist_genres = get_artist_genres(artist["id"], token)
        genres.extend(artist_genres)
    genres = list(set(genres))
    if genres:
        audio.tags["TCON"] = TCON(encoding=3, text=genres)
    images = track_data.get("album", {}).get("images", [])
    if images:
        cover_url = images[0]["url"]
        try:
            cover_data = requests.get(cover_url).content
            audio.tags["APIC"] = APIC(
                encoding=3,
                mime="image/jpeg",
                type=3, desc="Cover",
                data=cover_data
            )
        except Exception as e:
            print(f"⚠️ Failed Download Cover : {e}")
    audio.save()


def parse_playlist_url(url):
    match = re.search(r"playlist/([a-zA-Z0-9]+)", url)
    return match.group(1) if match else None


if __name__ == "__main__":
    spotify_url = input("Input Your Spotify List : ")
    root = tk.Tk()
    root.withdraw()
    output_folder = filedialog.askdirectory(title="Select Path To Save")
    if not output_folder:
        print("❌ Not Selected Path")
        exit()
    try:
        token = get_token()
    except Exception as e:
        print(f"❌ Failed To Get Token : {e}")
        exit()
    playlist_id = parse_playlist_url(spotify_url)
    if not playlist_id:
        print("❌ Playlist Link Not Valid")
        exit()
    try:
        track_ids = get_playlist_tracks(playlist_id, token)
    except Exception as e:
        print(f"❌ Failed Get Track : {e}")
        exit()
    print(f"🎵 Total Track In Playlist : {len(track_ids)}")


    for idx, tid in enumerate(track_ids, 1):
        try:
            track_data = get_track_metadata(tid, token)
            search_query = f"{track_data['name']} {track_data['artists'][0]['name']}"
        except Exception as e:
            print(f"⚠️ Gagal ambil metadata track {tid}: {e}")
            continue
        clean_name = safe_filename(f"{track_data['name']} - {track_data['artists'][0]['name']}")
        filename = f"{clean_name}.%(ext)s"
        print(f"⬇️ [{idx}/{len(track_ids)}]  Progress Download : {track_data['name']} - {track_data['artists'][0]['name']}")
        final_file = download_audio(search_query, filename, output_folder)
        if not final_file:
            continue
        final_file_mp3 = final_file.replace("%(ext)s", "mp3")
        if os.path.exists(final_file_mp3):
            try:
                embed_metadata(final_file_mp3, track_data, token)
            except Exception as e:
                print(f"⚠️ Failed Embed Metadata {search_query}: {e}")
        for artist in track_data.get("artists", []):
            download_artist_photo(artist, token, output_folder)

    print(f"✅ All Done. Saved To ...  {output_folder}")
