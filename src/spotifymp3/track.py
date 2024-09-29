from typing import List, Optional

from PIL import Image


class SpotifyTrack:
    def __init__(
        self,
        name: str,
        artists: List[str],
        length_ms: int,
        cover: Optional[Image.Image],
    ) -> None:
        self.name = name
        self.artists = artists
        self.length_ms = int(length_ms)
        self.cover = cover


class YoutubeTrack:
    def __init__(
        self,
        name: str,
        artist: str,
        length_ms: int,
        cover: Optional[Image.Image],
        link: str,
        view_count:int,
    ) -> None:
        self.name = name
        self.artist = artist
        self.length_ms = int(length_ms)
        self.cover = cover
        self.link = link
        self.view_count = view_count
