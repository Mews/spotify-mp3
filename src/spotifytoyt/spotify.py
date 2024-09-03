from typing import List

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from track import SpotifyTrack, track_from_spotify_data


def create_spotify_client(client_id: str, client_secret: str) -> spotipy.Spotify:
    client_credentials_manager = SpotifyClientCredentials(
        client_id=client_id, client_secret=client_secret
    )

    return spotipy.Spotify(client_credentials_manager=client_credentials_manager)


def get_track_from_url(client: spotipy.Spotify, url: str) -> SpotifyTrack:
    track_data = client.track(url)

    return track_from_spotify_data(track_data)


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
        track_from_spotify_data(track_data["track"]) for track_data in result["items"]
    ]

    while result["next"]:
        result = client.next(result)
        tracks.extend(
            [
                track_from_spotify_data(track_data["track"])
                for track_data in result["items"]
            ]
        )

    return tracks
