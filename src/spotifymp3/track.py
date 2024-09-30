from typing import List, Optional

from PIL import Image


class SpotifyTrack:
    def __init__(
        self,
        name: str,
        artists: List[str],
        length_ms: int,
        cover: Optional[Image.Image],
        album: str
    ) -> None:
        self.name = name
        self.artists = artists
        self.length_ms = int(length_ms)
        self.cover = cover
        self.album = album


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


class ConvertTrack:
    STATUS_CODES = {
        0: "In queue",
        1: "Pending...",
        2: "Converting...",
        3: "Converted!",
        4: "Downloading...",
        5: "Writing metadata...",
        6: "Finished!"
    }

    def __init__(self) -> None:
        self.status:int = 0
        self.spotify_track:SpotifyTrack = None
        self.youtube_track:YoutubeTrack = None
    
    def status_message(self) -> str:
        return self.STATUS_CODES[self.status]
