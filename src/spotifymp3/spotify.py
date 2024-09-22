from io import BytesIO
from typing import List

import requests
import spotipy
from PIL import Image
from spotipy.oauth2 import SpotifyClientCredentials

from src.spotifymp3.playlist import SpotifyPlaylist
from src.spotifymp3.track import SpotifyTrack


def get_track_from_spotify_data(
    raw_track_data, download_cover: bool = True
) -> SpotifyTrack:
    name = raw_track_data["name"]

    length_ms = raw_track_data["duration_ms"]

    # Get all artist names
    artists = []
    artists_data = raw_track_data["artists"]

    for artist_data in artists_data:
        artists.append(artist_data["name"])

    # Download song cover
    if download_cover:
        available_images = raw_track_data["album"]["images"]

        max_thumbnail_quality = -1

        for image in available_images:
            if not image["height"] or not image["width"]:
                highest_quality_image = image
                break

            pixel_count = image["height"] * image["width"]

            if pixel_count > max_thumbnail_quality:
                max_thumbnail_quality = pixel_count
                highest_quality_image = image

        cover_data = requests.get(highest_quality_image["url"]).content
        cover = Image.open(BytesIO(cover_data))

    else:
        cover = None

    return SpotifyTrack(name=name, artists=artists, length_ms=length_ms, cover=cover)


def create_spotify_client(client_id: str, client_secret: str) -> spotipy.Spotify:
    client_credentials_manager = SpotifyClientCredentials(
        client_id=client_id, client_secret=client_secret
    )

    return spotipy.Spotify(client_credentials_manager=client_credentials_manager)


def get_track_from_url(
    client: spotipy.Spotify, url: str, download_cover: bool = True
) -> SpotifyTrack:
    track_data = client.track(url)

    return get_track_from_spotify_data(track_data, download_cover)


def get_playlist_track_urls(client: spotipy.Spotify, playlist_url: str) -> List[str]:
    result = client.playlist_tracks(playlist_url)

    tracks = [
        track_data["track"]["external_urls"]["spotify"]
        for track_data in result["items"]
    ]

    while result["next"]:
        result = client.next(result)
        tracks.extend(
            [
                track_data["track"]["external_urls"]["spotify"]
                for track_data in result["items"]
            ]
        )

    return tracks


def get_playlist_tracks(
    client: spotipy.Spotify, playlist_url: str, download_covers: bool = True
) -> List[SpotifyTrack]:
    result = client.playlist_tracks(playlist_url)

    tracks = [
        get_track_from_spotify_data(track_data["track"], download_covers)
        for track_data in result["items"]
    ]

    while result["next"]:
        result = client.next(result)
        tracks.extend(
            [
                get_track_from_spotify_data(track_data["track"], download_covers)
                for track_data in result["items"]
            ]
        )

    return tracks


def get_playlist_from_url(
    client: spotipy.Spotify, playlist_url: str
) -> SpotifyPlaylist:
    result = client.playlist(playlist_url)

    name = result["name"]

    link = playlist_url

    song_count = result["tracks"]["total"]

    author = result["owner"]["display_name"]

    # Download cover
    available_images = result["images"]

    max_thumbnail_quality = -1

    for image in available_images:
        if not image["height"] or not image["width"]:
            highest_quality_image = image
            break

        pixel_count = image["height"] * image["width"]

        if pixel_count > max_thumbnail_quality:
            max_thumbnail_quality = pixel_count
            highest_quality_image = image

    cover_data = requests.get(highest_quality_image["url"]).content
    cover = Image.open(BytesIO(cover_data))

    return SpotifyPlaylist(
        name=name, cover=cover, author=author, song_count=song_count, link=link
    )
