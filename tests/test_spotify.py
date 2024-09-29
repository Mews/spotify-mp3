from unittest.mock import MagicMock, patch

from PIL import Image
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials

from src.spotifymp3.playlist import SpotifyPlaylist
from src.spotifymp3.spotify import *
from tests.utils import load_data_from_file, mock_image_bytes


def test_create_spotify_client():
    client = create_spotify_client("client id", "client secret")

    assert client is not None
    assert isinstance(client, Spotify)
    assert isinstance(client.auth_manager, SpotifyClientCredentials)


@patch("requests.get")
def test_get_track_from_spotify_data(mock_requests_get):
    mock_requests_get.return_value.content = mock_image_bytes()

    track_data = load_data_from_file("spotify_track.txt")

    track = get_track_from_spotify_data(track_data)

    assert track.name == "Free Young Thug"

    assert track.artists == ["jahhde", "Ifys"]

    assert track.length_ms == 149616

    assert isinstance(track.cover, Image.Image)


def test_get_playlist_track_urls():
    """
    playlist_tracks_1.txt and playlist_tracks_2.txt
    contain the paginated data returned from the playlist https://open.spotify.com/playlist/22EGM3OtabSMCSe9IVVEVZ?si=fb03f0e7a60147d4
    as of the 4th of september 2024,
    using spotipy.Spotify.playlist_tracks
    """

    mock_client = MagicMock()

    mock_client.playlist_tracks.return_value = load_data_from_file(
        "playlist_tracks_1.txt"
    )
    mock_client.next.return_value = load_data_from_file("playlist_tracks_2.txt")

    track_urls = get_playlist_track_urls(mock_client, "playlist url")

    assert len(track_urls) == 126
    assert track_urls[0] == "https://open.spotify.com/track/26QJuQfM8PVAWkIm1JRyqq"
    assert track_urls[1] == "https://open.spotify.com/track/71NkBajKZWS6eu6PomUm6u"
    assert track_urls[2] == "https://open.spotify.com/track/6ovJ4vtrLdONeRoTT4s4uw"
    assert track_urls[3] == "https://open.spotify.com/track/4c1LjGTCF8kMEikirzFgkm"
    assert track_urls[4] == "https://open.spotify.com/track/3OUfsApmvr7mwIm0rSbqbu"
    assert track_urls[69] == "https://open.spotify.com/track/0HTIrbUwwFn984RzVZm5Fk"
    assert track_urls[-1] == "https://open.spotify.com/track/4Y2uEMxni1MDrcJBDSWULX"


def test_get_playlist_tracks():
    """
    playlist_tracks_1.txt and playlist_tracks_2.txt
    contain the paginated data returned from the playlist https://open.spotify.com/playlist/22EGM3OtabSMCSe9IVVEVZ?si=fb03f0e7a60147d4
    as of the 4th of september 2024,
    using spotipy.Spotify.playlist_tracks
    """

    mock_client = MagicMock()

    mock_client.playlist_tracks.return_value = load_data_from_file(
        "playlist_tracks_1.txt"
    )
    mock_client.next.return_value = load_data_from_file("playlist_tracks_2.txt")

    tracks = get_playlist_tracks(mock_client, "playlist url", download_covers=False)

    assert len(tracks) == 126

    track1 = tracks[0]
    track70 = tracks[69]
    track95 = tracks[94]
    track126 = tracks[-1]

    assert track1.name == "ss"
    assert track1.artists == ["Ken Carson"]
    assert track1.length_ms == 184375
    assert track1.cover is None

    assert track70.name == "Yale"
    assert track70.artists == ["Ken Carson"]
    assert track70.length_ms == 106536
    assert track70.cover is None

    assert track95.name == "Fly Away"
    assert track95.artists == ["khai dreams", "Matt Jordan", "Atwood"]
    assert track95.length_ms == 115384
    assert track95.cover is None

    assert track126.name == "Summer"
    assert track126.artists == ["Good Kid"]
    assert track126.length_ms == 147031
    assert track126.cover is None


@patch("requests.get")
def test_get_playlist_track_urls(mock_requests_get):
    """
    spotify_playlist.txt
    contains the data returned from the playlist https://open.spotify.com/playlist/22EGM3OtabSMCSe9IVVEVZ?si=fb03f0e7a60147d4
    as of the 14th of september 2024,
    using spotipy.Spotify.playlist
    """

    mock_client = MagicMock()

    mock_client.playlist.return_value = load_data_from_file("spotify_playlist.txt")

    mock_requests_get.return_value.content = mock_image_bytes()

    playlist = get_playlist_from_url(mock_client, "playlist url")

    assert isinstance(playlist, SpotifyPlaylist)
    assert playlist.name == "test"
    assert isinstance(playlist.cover, Image.Image)
    assert playlist.song_count == 126
    assert playlist.author == "Mews"
    assert playlist.link == "playlist url"
