import math

import difflib

from typing import List, Tuple

import numpy as np
from PIL import Image
import cv2
from skimage.metrics import structural_similarity as ssim

import spotipy

from src.spotifymp3.track import SpotifyTrack, YoutubeTrack
from src.spotifymp3 import spotify, youtube

def match_tracks(spotify_track: SpotifyTrack, yt_track: YoutubeTrack):
    #print("MATCHING", yt_track.link)
    score = 0

    for artist in spotify_track.artists:
        score += difflib.SequenceMatcher(None, artist.lower(), yt_track.artist.lower()).ratio()
        #print("Artist:", difflib.SequenceMatcher(None, artist.lower(), yt_track.artist.lower()).ratio())

    score += difflib.SequenceMatcher(None, spotify_track.name, yt_track.name).ratio()
    #print("Title:", difflib.SequenceMatcher(None, spotify_track.name, yt_track.name).ratio())

    score += match_lengths(spotify_track.length_ms, yt_track.length_ms)
    #print("Length:", match_lengths(spotify_track.length_ms, yt_track.length_ms))

    if not spotify_track.cover is None and not yt_track.cover is None:
        score += match_covers(spotify_track.cover, yt_track.cover)
        #print("Cover:", match_covers(spotify_track.cover, yt_track.cover))
    
    return score
    

def match_lengths(length1: int, lenght2: int):
    if length1 == lenght2:
        return 1
    
    if abs(length1 - lenght2) > 180_000:
        return 0

    try:
        return 1 / (math.log10( (abs(length1- lenght2)) / 100 ))
    
    except:
        return 1


def match_covers(cover1: Image.Image, cover2: Image.Image):
    image1 = np.array(cover1.convert("RGB"))
    image2 = np.array(cover2.convert("RGB"))

    if not image1.shape == image2.shape:
        image2 = cv2.resize(image2, (image1.shape[1], image1.shape[0]))
    
    score, _ = ssim(image1, image2, full=True, multichannel=True, channel_axis=-1)

    return float(score)


def convert_spotify_track_to_youtube(client: spotipy.Spotify, spotify_track: SpotifyTrack) -> List[Tuple[float, str]]:
    potential_tracks = youtube.get_tracks_from_youtube_search(spotify_track.name + spotify_track.artists[0])

    match_results = []

    for track in potential_tracks:
        score = match_tracks(spotify_track, track)
        match_results.append((score, track.link))
    
    sorted_results = sorted(match_results, key=lambda x: x[0], reverse=True)

    return sorted_results
