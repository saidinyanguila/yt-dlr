from mutagen.id3 import (ID3, APIC, ID3NoHeaderError, TPE1, TPE2, TIT2, TALB, TDRC, TRCK, TCON)
from yt_dlp import YoutubeDL
import requests
import yt_dlp
import os
import re

### Search ###
def search_yt(query, max_results):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,  
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch{max_results}:{query}", download=False)

    results = []
    for entry in info['entries']:
        try :
            if entry['duration'] < 900:
                item = {
                    "video_id" : entry['id'],
                    "title" : entry['title'],
                    "author" : entry['channel'],
                    "title_clean" : clean_title(entry['title']),
                    "thumbnail" : entry['thumbnails'],
                    "duration" : seconds_minutes(entry['duration']),
                }

                results.append(item)
        except KeyError:
            pass

    return results

def download_mp3(video_id, title, artist, album, cover, year, genre, track_number):
    for file in os.listdir("website/static/downloads/"):
       os.remove(f"website/static/downloads/{file}") # Deletes every download before downloading new file

    url = f"https://www.youtube.com/watch?v={video_id}"

    ydl_opts = {
        "cookiefile": 'website/cookies/cookies.txt',
        'ffmpeg_location': 'website/ffmpeg/',
        "format": "bestaudio/best",
        "outtmpl": "website/static/downloads/%(title)s.%(ext)s",
        "js_runtimes": {'node': {}},
        "no_warnings": True,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
        info = ydl.extract_info(url, download=False)
    
        for file in os.listdir("website/static/downloads/"):
            if file == clean_filename(info["title"] + ".mp3"):
                try:
                    os.rename(("website/static/downloads/" + file), f"website/static/downloads/{clean_filename(artist)} - {clean_filename(title)}.mp3")
                except FileNotFoundError:
                    print(f"Error: The file '{file}' was not found.")
                except FileExistsError:
                    print(f"Error: The destination file '{file}' already exists.")
                except Exception as e:
                    print(f"An unexpected error occurred while renaming the file '{file}' : {e}")

                path = f"website/static/downloads/{clean_filename(artist)} - {clean_filename(title)}.mp3"
            
                try:
                    tags = ID3(path)
                except ID3NoHeaderError:
                    tags = ID3()

                tags.setall("TIT2", [TIT2(encoding=3, text=title)])     # title
                tags.setall("TPE1", [TPE1(encoding=3, text=artist)])    # artist
                tags.setall("TPE2", [TPE2(encoding=3, text=artist)])    # album artist
                tags.setall("TALB", [TALB(encoding=3, text=album)])     # album

                tags.setall("TDRC", [TDRC(encoding=3, text=year)])             # year
                tags.setall("TRCK", [TRCK(encoding=3, text=track_number)])     # track number
                tags.setall("TCON", [TCON(encoding=3, text=genre)])            # genre

                # Cover art
                cover_url = cover
                cover_data = download_cover(cover_url)

                tags.delall("APIC")
                tags.add(
                    APIC(
                        encoding=3,
                        mime="image/jpeg",
                        type=3,
                        desc="Cover",
                        data=cover_data,
                    )
                )

                tags.save(path, v2_version=3)

                return {
                    "status" : "success",
                    "file_path" : path
                }

def download_mp3_blank(video_id):
    for file in os.listdir("website/static/downloads/"):
        os.remove(f"website/static/downloads/{file}") # Deletes every download before downloading new file

    url = f"https://www.youtube.com/watch?v={video_id}"

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "website/static/downloads/%(title)s.%(ext)s",
        'ffmpeg_location': 'website/ffmpeg/',
        "js_runtime": "node",
        "no_warnings": True,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
        info = ydl.extract_info(url, download=False)

        for file in os.listdir("website/static/downloads/"):
            if file == info["title"] + ".mp3":
                try:
                    os.rename(("website/static/downloads/" + file), f"website/static/downloads/{clean_title(file)}")
                except FileNotFoundError:
                    pass
                    print(f"Error: The file '{file}' was not found.")
                except FileExistsError:
                    pass
                    print(f"Error: The destination file '{file}' already exists.")
                except Exception as e:
                    pass
                    print(f"An unexpected error occurred while renaming the file '{file}' : {e}")

                path = "static/downloads/" + clean_title(info["title"] + ".mp3")
        
                return path

### Download Cover ###
def download_cover(url: str):
    img = requests.get(url, timeout=10)
    img.raise_for_status()
    return img.content

### Convert ###
def seconds_minutes(seconds) -> str:
    minutes = int(seconds) // 60
    remaining_seconds = int(seconds) % 60
    if (remaining_seconds < 10):
        remaining_seconds = "0" + str(remaining_seconds)

    return f"{minutes}:{remaining_seconds}"

### Rename ###
def clean_title(title: str) -> str:
    # Remove bracketed content: ( ... ) and [ ... ]
    title = re.sub(r"\([^)]*\)", "", title)
    title = re.sub(r"\[[^\]]*\]", "", title)

    # Remove common YouTube junk words
    junk_words = [
        "official audio",
        "official video",
        "official music video",
        "official lyric video",
        "lyrics",
        "lyric video",
        "visualizer",
        "hd",
        "4k",
        ":",
        "/",
        "|",
        "\"",
        "'" 
    ]

    for word in junk_words:
        title = re.sub(word, "", title, flags=re.IGNORECASE)

    # Remove emojis and non-standard characters
    title = re.sub(
        r"["
        r"\U0001F600-\U0001F64F"  # emoticons
        r"\U0001F300-\U0001F5FF"  # symbols & pictographs
        r"\U0001F680-\U0001F6FF"  # transport & map
        r"\U0001F1E0-\U0001F1FF"  # flags
        r"\U00002700-\U000027BF"
        r"\U000024C2-\U0001F251"
        r"]+",
        "",
        title,
    )

    # Normalize whitespace
    title = re.sub(r"\s+", " ", title).strip()

    return title

def clean_filename(filename):
    # List of common characters forbidden in Windows/Linux/macOS filenames
    replacement="_"
    invalid_chars = [':', '\\', '/', '*', '?', '"', '<', '>', '|']
    
    # Replace each invalid character with the replacement character
    cleaned_name = filename
    for char in invalid_chars:
        cleaned_name = cleaned_name.replace(char, replacement)
        
    return cleaned_name