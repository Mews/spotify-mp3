from typing import List

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from track import SpotifyTrack, get_track_from_spotify_data

import requests
from io import BytesIO

from PIL import Image

def get_track_from_spotify_data(raw_track_data, download_cover:bool = True) -> SpotifyTrack:
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

        max_height = -1

        for image in available_images:
            if image["height"] > max_height:
                max_height = image["height"]
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


def get_track_from_url(client: spotipy.Spotify, url: str) -> SpotifyTrack:
    track_data = client.track(url)

    return get_track_from_spotify_data(track_data)


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
    client: spotipy.Spotify, playlist_url: str
) -> List[SpotifyTrack]:
    result = client.playlist_tracks(playlist_url)

    tracks = [
        get_track_from_spotify_data(track_data["track"]) for track_data in result["items"]
    ]

    while result["next"]:
        result = client.next(result)
        tracks.extend(
            [
                get_track_from_spotify_data(track_data["track"])
                for track_data in result["items"]
            ]
        )

    return tracks
