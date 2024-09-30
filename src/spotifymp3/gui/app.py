import tkinter as tk
import traceback
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from typing import List

from mutagen.id3 import APIC, ID3, TALB, TIT2, TOAL, TPE1, USLT, ID3NoHeaderError
from mutagen.mp3 import MP3
from tksheet.sheet import Sheet
from yt_dlp import YoutubeDL
import syncedlyrics

from src.spotifymp3.gui.topbar import TopBar
from src.spotifymp3.gui.utils import (DownloadOptions, ObservableList,
                                      get_root_tk, replace_alnum)
from src.spotifymp3.match import convert_spotify_track_to_youtube
from src.spotifymp3.settings import get_config
from src.spotifymp3.spotify import create_spotify_client
from src.spotifymp3.track import *


class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.geometry("900x700")

        self.title("Spotify mp3")

        self.SPOTIFY_CLIENT = create_spotify_client(
            get_config("spotify", "client_id"), get_config("spotify", "client_secret")
        )

        self.icon_image = tk.PhotoImage(file="assets/icons/spotify-mp3.png")
        self.wm_iconphoto(True, self.icon_image)

        self.top_bar = TopBar(self)
        self.top_bar.pack(fill="x", anchor="n", side="top")

        self.queue_viewer = QueueViewer(self)
        self.queue_viewer.pack(expand=True, fill="both", anchor="n", padx=10, pady=10)

        self.queue = ObservableList(callback=self.queue_viewer.on_queue_change)
        self.executor = ThreadPoolExecutor()
        self.futures = []
        self.futures_to_convert_track = {}

    def process_convert_track(
        self,
        convert_track: ConvertTrack,
        download_options: DownloadOptions,
        retries: int = 3,
    ):
        # Convert spotify track to youtube track
        if convert_track.youtube_track:
            download_url = convert_track.youtube_track.link

            convert_track.status = 3
            self.after(100, self.queue_viewer.update_sheet_data)

        elif convert_track.spotify_track and not convert_track.youtube_track:
            convert_track.status = 2
            self.after(100, self.queue_viewer.update_sheet_data)

            match_results = convert_spotify_track_to_youtube(
                convert_track.spotify_track,
                search_count=download_options.youtube_search_limit,
                download_cover=download_options.download_covers,
            )

            best_match_url = match_results[0][1]

            download_url = best_match_url

            convert_track.status = 3
            self.after(100, self.queue_viewer.update_sheet_data)

        # Download track
        convert_track.status = 4
        self.after(100, self.queue_viewer.update_sheet_data)

        if convert_track.spotify_track:
            output_path = f"{download_options.output_folder}/{replace_alnum(convert_track.spotify_track.name)} {replace_alnum(convert_track.spotify_track.artists[0])}"

        else:
            output_path = f"{download_options.output_folder}/%(title)s"

        ydl_opts = {
            "format": "bestaudio",
            "extractaudio": True,
            # "audioformat": "mp3",
            "outtmpl": output_path,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
            "quiet": True,
            "no_warnings": True,
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([download_url])

        # Save metadata
        if download_options.save_metadata and convert_track.spotify_track:
            convert_track.status = 5
            self.after(100, self.queue_viewer.update_sheet_data)

            try:
                audio = MP3(output_path + ".mp3", ID3=ID3)
            except ID3NoHeaderError:
                audio.add_tags()

            audio["TIT2"] = TIT2(
                encoding=3, text=convert_track.spotify_track.name
            )  # Title
            audio["TPE1"] = TPE1(
                encoding=3, text=", ".join(convert_track.spotify_track.artists)
            )  # Artists
            audio["TALB"] = TALB(
                encoding=3, text=convert_track.spotify_track.album
            )  # Album
            audio["TOAL"] = TOAL(
                encoding=3, text=convert_track.spotify_track.album
            )  # Album

            # Add album cover
            if convert_track.spotify_track.cover:
                with BytesIO() as img_byte_array:
                    convert_track.spotify_track.cover.save(
                        img_byte_array, format="JPEG"
                    )  # Save as JPEG
                    img_byte_array.seek(0)  # Rewind the file-like object

                    # Add album cover image
                    audio.tags.add(
                        APIC(
                            encoding=3,
                            mime="image/jpeg",
                            type=3,  # front cover
                            desc="Cover",
                            data=img_byte_array.read(),
                        )
                    )

            # Embed lyrics
            if download_options.embed_lyrics:
                lyrics = syncedlyrics.search(convert_track.spotify_track.name + " " + convert_track.spotify_track.artists[0], plain_only=True)
                if lyrics:
                    audio["USLT"] = USLT(encoding=3, lang="eng", desc='', text=lyrics)

            audio.save(v2_version=3)

        convert_track.status = 6
        self.after(100, self.queue_viewer.update_sheet_data)

    def start_processing_queue(self, donwload_options: DownloadOptions):
        self.top_bar.disable_topbar()

        for track in self.queue:
            # self.process_convert_track(track, donwload_options)
            future = self.executor.submit(
                self.process_convert_track, track, donwload_options
            )
            future.add_done_callback(self.on_future_done)
            self.futures.append(future)
            self.futures_to_convert_track[future] = track

        self.after(100, self.check_for_queue_completion)

    def on_future_done(self, future):
        track = self.futures_to_convert_track[future]
        row = self.queue.index(track)

        try:
            future.result()
            self.queue_viewer.highlight_row(row, "#ccffcc")

        except Exception as e:
            print(f"Error while processing track: {e}")
            print(f"Stack trace: {traceback.format_exc()}")
            self.queue_viewer.highlight_row(row, "#ffcccc")

    def on_queue_completion(self):
        self.top_bar.enable_topbar()
        print("Finished processing queue!")

    def check_for_queue_completion(self):
        if all(future.done() for future in self.futures):
            self.on_queue_completion()
        else:
            self.after(100, self.check_for_queue_completion)


class QueueViewer(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.sheet = Sheet(
            self,
            headers=["Source", "Title", "Artists", "Status"],
            auto_resize_columns=75,
        )
        # self.sheet.set_column_widths([200 for i in range(4)])

        self.sheet.disable_bindings()
        # self.sheet.enable_bindings("column_width_resize")
        self.sheet.pack(expand=True, fill="both")

        # self.bind("<Configure>", self.adjust_column_widths)
        # self.adjust_column_widths()

    def get_queue(self) -> List[ConvertTrack]:
        return get_root_tk(self).queue

    """
    def adjust_column_widths(self, event=None):
        self.update_idletasks()

        total_width = self.sheet.winfo_width() - 50

        num_columns = len(self.sheet.headers())
        
        first_column_width = 100
        last_column_width = 150
        
        available_width = total_width - first_column_width - last_column_width
        
        middle_column_width = available_width // (num_columns - 2)
        
        widths = [first_column_width] + [middle_column_width] * (num_columns - 2) + [last_column_width]
        self.sheet.set_column_widths(widths)
    """

    def update_sheet_data(self):
        queue = self.get_queue()

        new_sheet_data = []

        for track in queue:
            if track.spotify_track:
                new_sheet_data.append(
                    [
                        "Spotify",
                        track.spotify_track.name,
                        ", ".join(track.spotify_track.artists),
                        track.status_message(),
                    ]
                )
            elif track.youtube_track:
                new_sheet_data.append(
                    [
                        "Youtube",
                        track.youtube_track.name,
                        track.youtube_track.artist,
                        track.status_message(),
                    ]
                )

        self.sheet.set_sheet_data(new_sheet_data)

        # self.adjust_column_widths()

    def on_queue_change(self):
        self.update_sheet_data()

    def highlight_row(self, row_index: int, color: str):
        self.sheet.highlight(row_index, bg=color)
