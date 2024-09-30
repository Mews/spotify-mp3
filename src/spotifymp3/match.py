import difflib
import math
from typing import List, Tuple

import cv2
import numpy as np
from PIL import Image
from skimage.metrics import structural_similarity as ssim

from src.spotifymp3 import youtube
from src.spotifymp3.track import SpotifyTrack, YoutubeTrack


def match_tracks(spotify_track: SpotifyTrack, yt_track: YoutubeTrack):
    # print("MATCHING", yt_track.link)
    score = 0

    # Artist score
    artist_score = max([difflib.SequenceMatcher(None, artist.lower(), yt_track.artist.lower()).ratio() for artist in spotify_track.artists])
    score += artist_score

    #for artist in spotify_track.artists:
        #score += difflib.SequenceMatcher(
        #    None, artist.lower(), yt_track.artist.lower()
        #).ratio()
    
    # Title score
    title_score = difflib.SequenceMatcher(None, spotify_track.name, yt_track.name).ratio()
    score += title_score

    # Length score
    length_score = match_lengths(spotify_track.length_ms, yt_track.length_ms)
    score += length_score

    # Cover score
    if not spotify_track.cover is None and not yt_track.cover is None:
        cover_score = match_covers(spotify_track.cover, yt_track.cover)
    else:
        cover_score = 0
    
    score += cover_score

    # View score
    #views_score = score_views(view_count=yt_track.view_count)
    #score += views_score

    # Keywords score
    keywords_score = score_keywords(track_title=yt_track.name)
    score += keywords_score


    return score


def match_lengths(length1: int, lenght2: int):
    disintegration = 0.00001
    diff = abs(length1 - lenght2)

    return math.exp(-disintegration * diff) * 1.75


def match_covers(cover1: Image.Image, cover2: Image.Image):
    image1 = np.array(cover1.convert("RGB"))
    image2 = np.array(cover2.convert("RGB"))

    if not image1.shape == image2.shape:
        image2 = cv2.resize(image2, (image1.shape[1], image1.shape[0]))

    score, _ = ssim(image1, image2, full=True, multichannel=True, channel_axis=-1)

    return float(score)


def score_views(view_count:int):
    k = 0.0000005
    m = 1
    return (1 - math.exp(-k * view_count))*m


def score_keywords(track_title:str):
    whitelist = ["official", "audio"]
    blacklist = ["video", "music video"]

    if any([bl_word in track_title.lower() for bl_word in blacklist]):
        return 0

    wl_matches = sum([wl_word in track_title.lower() for wl_word in whitelist])

    return (2 ** wl_matches - 1) / (2 ** len(whitelist) - 1)

    

def convert_spotify_track_to_youtube(
    spotify_track: SpotifyTrack, search_count: int = 10, download_cover: bool = True
) -> List[Tuple[float, str]]:
    potential_tracks = youtube.get_tracks_from_youtube_search(
        spotify_track.name + " " + spotify_track.artists[0],
        limit=search_count,
        download_cover=download_cover,
    )
    match_results = []

    for track in potential_tracks:
        score = match_tracks(spotify_track, track)
        match_results.append((score, track.link))

    sorted_results = sorted(match_results, key=lambda x: x[0], reverse=True)

    return sorted_results
