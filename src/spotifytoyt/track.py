from typing import List
from PIL import Image
import requests
from io import BytesIO


class Track:
    def __init__(self, 
                 name:str, 
                 artists:List[str],
                 length_ms:int,
                 cover:Image) -> None:
        
        self.name = name
        self.artists = artists
        self.length_ms = length_ms
        self.cover = cover


def track_from_spotify_data(raw_track_data):
    from pprint import pprint

    with open("rawtrackdata.txt", "w", encoding="utf-8") as out:
        pprint(raw_track_data, stream=out)

    name = raw_track_data["name"]

    length_ms = raw_track_data["duration_ms"]
    
    # Get all artist names
    artists = []
    artists_data = raw_track_data["artists"]

    for artist_data in artists_data:
        artists.append(artist_data["name"])
    
    # Download song cover
    available_images = raw_track_data["album"]["images"]

    max_height = -1

    for image in available_images:
        if image["height"] > max_height:
            max_height = image["height"]
            highest_quality_image = image
            
    cover_data = requests.get(highest_quality_image["url"]).content
    cover = Image.open(BytesIO(cover_data))

    return Track(name=name,
                 artists=artists,
                 length_ms=length_ms,
                 cover=cover)
