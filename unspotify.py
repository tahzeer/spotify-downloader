#!/usr/bin/env python

import os
import re
import shutil
import time
import urllib.request

import requests
import spotipy
from moviepy.editor import *
from mutagen.easyid3 import EasyID3
from mutagen.id3 import APIC, ID3
from pytube import YouTube
from rich.console import Console
from spotipy.oauth2 import SpotifyClientCredentials


SPOTIPY_CLIENT_ID = os.environ["SPOTIPY_CLIENT_ID"]
SPOTIPY_CLIENT_SECRET = os.environ["SPOTIPY_CLIENT_SECRET"]

# SPOTIPY_CLIENT_ID = ''
# SPOTIPY_CLIENT_SECRET = ''


auth_manager = SpotifyClientCredentials(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET
)
sp = spotipy.Spotify(auth_manager=auth_manager)


def main():
    url = check_url(input("Spotify URL: ").strip())

    if "track" in url:
        songs = [get_track_info(url)]
    elif "playlist" in url:
        songs = get_playlist_info(url)

    start = time.time()
    downloaded = 0
    for i, track_info in enumerate(songs, start=1):
        search_term = f"{track_info['artist_name']} {track_info['track_title']} audio"
        video_link = find_youtube(search_term)

        Console().print(
            f"[magenta][{i}/{len(songs)}][/magenta] Downloading '[cyan]{track_info['artist_name']} - {track_info['track_title']}[/cyan]'..."
        )
        audio = download_yt(video_link)
        if audio:
            set_metadata(track_info, audio)
            os.replace(audio, f"../music/{os.path.basename(audio)}")
            Console().print(
                "[blue]______________________________________________________________________"
            )
            downloaded += 1
        else:
            print("File exists. Skipping...")
    shutil.rmtree("../music/tmp")
    end = time.time()
    print()
    os.chdir("../music")
    print(f"Download location: {os.getcwd()}")
    Console().print(
        f"DOWNLOAD COMPLETED: {downloaded}/{len(songs)} song(s) dowloaded".center(
            70, " "
        ),
        style="on green",
    )
    Console().print(
        f"Total time taken: {round(end - start)} sec".center(70, " "), style="on yellow"
    )


def check_url(url):

    if re.search(r"^(https?://)?open\.spotify\.com/(playlist|track)/.+$", url):
        return url

    raise ValueError("Invalid Spotify URL")


def get_track_info(track_url):
    res = requests.get(track_url)

    if (res.status_code != 200):
        raise ValueError("Invalid Spotify Track URL")

    track = sp.track(track_url)
    # print(track)
    track_metadata = {
        "artist_name": track["artists"][0]["name"],
        "track_title": track["name"],
        "track_number": track["track_number"],
        "isrc": track["external_ids"]["isrc"],
        "album_art": track["album"]["images"][1]["url"],
        "album_name": track["album"]["name"],
        "release_date": track["album"]["release_date"],
        "artists": [artist["name"] for artist in track["artists"]],
    }
    return track_metadata


def get_playlist_info(playlist_url):
    res = requests.get(playlist_url)

    if (res.status_code != 200):
        raise ValueError("Invalid Spotify Playlist URL")

    pl = sp.playlist(playlist_url)

    if not pl["public"]:
        raise ValueError("Change your playlist state to Public")

    playlist = sp.playlist_tracks(playlist_url)

    tracks = [item["track"] for item in playlist["items"]]
    tracks_info = []

    for track in tracks:
        track_url = f"https://open.spotify.com/track/{track['id']}"
        track_info = get_track_info(track_url)
        tracks_info.append(track_info)

    return tracks_info


def find_youtube(query):
    phrase = query.replace(" ", "+")
    search_link = "https://www.youtube.com/results?search_query=" + phrase
    count = 0

    while count < 3:
        try:
            response = urllib.request.urlopen(search_link)
            break
        except:
            count += 1

    else:
        raise ValueError(
            "Please check your internet connection and try again later.")

    search_results = re.findall(r"watch\?v=(\S{11})", response.read().decode())
    first_video = "https://www.youtube.com/watch?v=" + search_results[0]

    return first_video


def download_yt(yt_link):

    yt = YouTube(yt_link)
    avoid_chars = ['/', '\\', '|', '?', '*', ':', '>', '<', '"']
    yt.title = "".join([i for i in yt.title if i not in avoid_chars])

    print(yt)

    video = yt.streams.filter(only_audio=True).first()
    video_file = video.download(output_path="../music/tmp")

    base = os.path.splitext(video_file)[0]
    audio_file = base + ".mp3"
    mp4_no_frame = AudioFileClip(video_file)
    mp4_no_frame.write_audiofile(audio_file, logger=None)
    mp4_no_frame.close()
    os.remove(video_file)
    os.replace(audio_file, f"../music/tmp/{yt.title}.mp3")
    audio_file = f"../music/tmp/{yt.title}.mp3"

    return audio_file


def set_metadata(metadata, file_path):

    mp3_file = EasyID3(file_path)

    mp3_file["albumartist"] = metadata["artist_name"]
    mp3_file["artist"] = metadata["artists"]
    mp3_file["album"] = metadata["album_name"]
    mp3_file["title"] = metadata["track_title"]
    mp3_file["date"] = metadata["release_date"]
    mp3_file["tracknumber"] = str(metadata["track_number"])
    mp3_file["isrc"] = metadata["isrc"]
    mp3_file.save()

    audio = ID3(file_path)
    with urllib.request.urlopen(metadata["album_art"]) as albumart:
        audio["APIC"] = APIC(encoding=3, mime="image/jpeg",
                             type=3, desc="cover", data=albumart.read())
    audio.save(v2_version=3)

    return


if __name__ == "__main__":
    main()
