from PIL import Image

class SpotifyPlaylist:
    def __init__(self, name:str, cover:Image.Image, author:str, song_count:int, link:str) -> None:
        self.name = name
        self.cover = cover
        self.author = author
        self.song_count = song_count
        self.link = link

class YoutubePlaylist:
    def __init__(self, name:str, cover:Image.Image, author:str, song_count:int, link:str) -> None:
        self.name = name
        self.cover = cover
        self.author = author
        self.song_count = song_count
        self.link = link
