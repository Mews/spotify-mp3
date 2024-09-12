from tests.utils import load_data_from_file

from unittest.mock import MagicMock, patch

from PIL import Image

from src.spotifymp3.youtube import *


def test_get_track_from_youtube_data():
    track_data = load_data_from_file("youtube_track.txt")

    track = get_track_from_youtube_data(track_data)

    assert track.name == "Yale"

    assert track.artist == "Ken Carson"

    assert track.length_ms == 107000

    assert isinstance(track.cover, Image.Image)

@patch('youtubesearchpython.VideosSearch')
def test_get_tracks_from_youtube_search(mock_videos_search):
    mock_videos_search.return_value.result.return_value = load_data_from_file("youtube_search_result.txt")

    tracks = get_tracks_from_youtube_search("search query", limit=10, download_cover=False)

    assert all(isinstance(track, YoutubeTrack) for track in tracks)

    assert len(tracks) == 10

    assert all(track.cover is None for track in tracks)
