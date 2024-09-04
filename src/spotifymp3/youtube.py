from datetime import timedelta
from io import BytesIO
from typing import List

import requests
from PIL import Image
from pytube import Playlist, YouTube
from youtubesearchpython import VideosSearch

from src.spotifymp3.track import YoutubeTrack


def get_track_from_youtube_data(
    raw_track_data, download_cover: bool = True
) -> YoutubeTrack:
    name = raw_track_data["title"]

    link = raw_track_data["link"]

    artist = raw_track_data["channel"]["name"]

    # Parse song length
    duration_string: str = raw_track_data["duration"]

    duration_string = duration_string.split(":")

    if len(duration_string) == 3:
        hours = int(duration_string[0])
        minutes = int(duration_string[1])
        seconds = int(duration_string[2])

        length_ms = (
            timedelta(hours=hours, minutes=minutes, seconds=seconds).total_seconds()
            * 1000
        )

    if len(duration_string) == 2:
        minutes = int(duration_string[0])
        seconds = int(duration_string[1])

        length_ms = timedelta(minutes=minutes, seconds=seconds).total_seconds() * 1000

    # Download video thumbnail
    if download_cover:
        available_thumbnails = raw_track_data["thumbnails"]

        max_thumbnail_quality = -1
        best_thumbnail = None

        for thumbnail in available_thumbnails:
            pixel_count = thumbnail["height"] * thumbnail["width"]

            if pixel_count > max_thumbnail_quality:
                max_thumbnail_quality = pixel_count
                best_thumbnail = thumbnail

        cover_data = requests.get(best_thumbnail["url"]).content
        cover = Image.open(BytesIO(cover_data))

    else:
        cover = None

    return YoutubeTrack(
        name=name, artist=artist, length_ms=length_ms, cover=cover, link=link
    )


def get_track_from_youtube_object(
    youtube_object: YouTube, download_cover: bool = True
) -> YoutubeTrack:
    name = youtube_object.title
    artist = youtube_object.author
    length_ms = youtube_object.length * 1000

    cover_data = requests.get(youtube_object.thumbnail_url).content
    cover = Image.open(BytesIO(cover_data))

    return YoutubeTrack(
        name=name,
        artist=artist,
        length_ms=length_ms,
        cover=cover,
        link="https://www.youtube.com/watch?v="
        + youtube_object.vid_info["videoDetails"]["videoId"],
    )


def get_track_from_url(url: str) -> YoutubeTrack:
    yt = YouTube(url)

    return get_track_from_youtube_object(yt)


def get_tracks_from_youtube_search(
    search_query: str, limit: int = 10
) -> List[YoutubeTrack]:
    search = VideosSearch(search_query, limit=limit)

    tracks = []

    result = search.result()["result"]

    for video_data in result:
        tracks.append(get_track_from_youtube_data(video_data))

    return tracks


def get_playlist_track_urls(playlist_url: str) -> List[str]:
    playlist = Playlist(playlist_url)

    return list(playlist.video_urls)


def get_playlist_tracks(playlist_url: str) -> List[YoutubeTrack]:
    playlist = Playlist(playlist_url)

    tracks = []

    for video in playlist.videos:
        tracks.append(get_track_from_youtube_object(video))

    return tracks
