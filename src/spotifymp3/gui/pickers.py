import os
import tkinter as tk
import traceback
import webbrowser
from datetime import timedelta
from threading import Thread
from tkinter import filedialog, messagebox
from typing import Union

from PIL import ImageTk

from src.spotifymp3 import spotify, youtube
from src.spotifymp3.gui.utils import DownloadOptions, get_root_tk, load_icon
from src.spotifymp3.playlist import SpotifyPlaylist, YoutubePlaylist
from src.spotifymp3.settings import (change_config, get_config,
                                     reset_default_configs)
from src.spotifymp3.track import SpotifyTrack, YoutubeTrack


class PlaylistPreview(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.cover_label = tk.Label(self, font=("TkDefaultFont", 16))
        self.cover_label.pack(side="top", pady=(7, 0), padx=3)

        self.title_label = tk.Label(self, text="Name: ", font=("TkDefaultFont", 13))
        self.title_label.pack(fill="x", side="top")

        self.song_count_label = tk.Label(
            self, text="0 songs", font=("TkDefaultFont", 13)
        )
        self.song_count_label.pack(fill="x", side="top")

        self.author_label = tk.Label(self, text="Author: ", font=("TkDefaultFont", 13))
        self.author_label.pack(fill="x", side="top")

    def load_playlist(self, playlist: Union[SpotifyPlaylist, YoutubePlaylist]):
        self.playlist = playlist

        self.update_preview()

    def update_preview(self):
        self.update_cover()

        self.title_label.config(text="Title: " + self.playlist.name)

        self.song_count_label.config(text=str(self.playlist.song_count) + " songs")

        self.author_label.config(text="Author: " + self.playlist.author)

    def update_cover(self):
        self.cover = self.playlist.cover

        cover_aspect_ratio = self.cover.width / self.cover.height

        target_width = 375

        self.cover = self.cover.resize(
            (target_width, round(target_width / cover_aspect_ratio))
        )

        self.cover = ImageTk.PhotoImage(self.cover)

        self.cover_label.config(image=self.cover)

    def reset_preview(self):
        self.cover_label.config(text="")
        self.cover_label.config(image="")
        self.title_label.config(text="Name: ")
        self.song_count_label.config(text="0 songs")
        self.author_label.config(text="Author: ")

    def show_message(self, message):
        self.reset_preview()
        self.cover_label.config(text=message)


class TrackPreview(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.cover_label = tk.Label(self, font=("TkDefaultFont", 16))
        self.cover_label.pack(side="top", pady=(7, 0), padx=3)

        self.title_label = tk.Label(self, text="Name: ", font=("TkDefaultFont", 13))
        self.title_label.pack(fill="x", side="top")

        self.artists_label = tk.Label(
            self, text="Artists: ", font=("TkDefaultFont", 13)
        )
        self.artists_label.pack(fill="x", side="top")

        self.length_label = tk.Label(self, text="Length: ", font=("TkDefaultFont", 13))
        self.length_label.pack(fill="x", side="top")

    def load_track(self, track: Union[SpotifyTrack, YoutubeTrack]):
        self.track = track

        self.update_preview()

    def update_preview(self):
        self.update_cover()

        self.title_label.config(text="Title: " + self.track.name)

        if isinstance(self.track, YoutubeTrack):
            self.artists_label.config(text="Artists: " + self.track.artist)
        elif isinstance(self.track, SpotifyTrack):
            self.artists_label.config(text="Artists: " + " ".join(self.track.artists))

        td = timedelta(milliseconds=self.track.length_ms)
        total_seconds = td.total_seconds()
        minutes, seconds = divmod(total_seconds, 60)

        self.length_label.config(
            text="Track length: " + f"{int(minutes)}:{round(seconds):02d}"
        )

    def update_cover(self):
        self.cover = self.track.cover

        cover_aspect_ratio = self.cover.width / self.cover.height

        target_width = 375

        self.cover = self.cover.resize(
            (target_width, round(target_width / cover_aspect_ratio))
        )

        self.cover = ImageTk.PhotoImage(self.cover)

        self.cover_label.config(image=self.cover)

    def reset_preview(self):
        self.cover_label.config(text="")
        self.cover_label.config(image="")
        self.title_label.config(text="Name: ")
        self.artists_label.config(text="Artists: ")
        self.length_label.config(text="Length: ")

    def show_message(self, message):
        self.reset_preview()
        self.cover_label.config(text=message)


class YoutubePlaylistPicker(tk.Toplevel):
    def __init__(self, master, handler, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.handler = handler

        self.title("Youtube playlist picker")

        self.geometry("800x500")
        self.resizable(True, False)

        self.input_frame = tk.Frame(self, relief="groove", borderwidth=5, width=400)
        self.input_frame.pack(side="left", fill="y")

        self.input_frame.pack_propagate(False)

        self.preview = PlaylistPreview(self, relief="groove", borderwidth=5)
        self.preview.pack(side="left", fill="both", expand=True)

        self.link_var = tk.StringVar()
        self.link_entry = tk.Entry(self.input_frame, textvariable=self.link_var)
        self.link_entry.pack(expand=True, fill="x", padx=10)
        self.link_var.trace_add("write", self.on_entry_change)

        self.download_covers_var = tk.BooleanVar()
        self.download_covers_var.set(True)
        self.download_covers_checkbox = tk.Checkbutton(
            self.input_frame,
            text="Download track covers?",
            variable=self.download_covers_var,
        )
        self.download_covers_checkbox.pack(expand=True)

        self.add_button = tk.Button(
            self.input_frame, text="Add playlist", command=self.on_add_button_press
        )
        self.add_button.pack(anchor="n", expand=True)

    def on_entry_change(self, var, index, mode):
        url = self.link_var.get()
        if url:
            self.preview.show_message("Loading playlist...")
            Thread(
                target=self.load_playlist_in_thread, args=(url,), daemon=True
            ).start()
        else:
            self.preview.show_message("")

    def load_playlist_in_thread(self, url):
        try:
            playlist = youtube.get_playlist_from_url(url)
            self.preview.load_playlist(playlist)
        except Exception as e:
            self.preview.show_message("An error occured\nloading the playlist")
            print("Error loading playlist", url)
            print(traceback.format_exc())

    def on_add_button_press(self):
        self.add_button.config(text="Fetching tracks...")
        self.update()

        try:
            tracks = youtube.get_playlist_tracks(
                self.link_var.get(), download_covers=self.download_covers_var.get()
            )
        except Exception as e:
            print("Error getting tracks from playlist", self.link_var.get())
            print(traceback.format_exc())

        if self.handler:
            self.handler(tracks)
            self.destroy()


class YoutubeTrackPicker(tk.Toplevel):
    def __init__(self, master, handler, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.handler = handler

        self.title("Youtube video picker")

        self.geometry("800x500")
        self.resizable(True, False)

        self.input_frame = tk.Frame(self, relief="groove", borderwidth=5, width=400)
        self.input_frame.pack(side="left", fill="y")

        self.input_frame.pack_propagate(False)

        self.preview = TrackPreview(self, relief="groove", borderwidth=5)
        self.preview.pack(side="left", fill="both", expand=True)

        self.link_var = tk.StringVar()
        self.link_entry = tk.Entry(self.input_frame, textvariable=self.link_var)
        self.link_entry.pack(expand=True, fill="x", padx=10)
        self.link_var.trace_add("write", self.on_entry_change)

        self.download_cover_var = tk.BooleanVar()
        self.download_cover_var.set(True)
        self.download_cover_checkbox = tk.Checkbutton(
            self.input_frame,
            text="Download track cover?",
            variable=self.download_cover_var,
        )
        self.download_cover_checkbox.pack(expand=True)

        self.add_button = tk.Button(
            self.input_frame, text="Add video", command=self.on_add_button_press
        )
        self.add_button.pack(anchor="n", expand=True)

    def on_entry_change(self, var, index, mode):
        url = self.link_var.get()
        if url:
            self.preview.show_message("Loading video...")
            Thread(target=self.load_track_in_thread, args=(url,), daemon=True).start()
        else:
            self.preview.show_message("")

    def load_track_in_thread(self, url):
        try:
            track = youtube.get_track_from_url(url)
            self.preview.load_track(track)
        except Exception as e:
            self.preview.show_message("An error occured\nloading the video")
            print("Error loading video", url)
            print(traceback.format_exc())

    def on_add_button_press(self):
        self.add_button.config(text="Fetching track...")
        self.update()

        try:
            track = youtube.get_track_from_url(
                self.link_var.get(), download_cover=self.download_cover_var.get()
            )
        except Exception as e:
            print("Error getting track", self.link_var.get())
            print(traceback.format_exc())

        if self.handler:
            self.handler([track])
            self.destroy()


class SpotifyPlaylistPicker(tk.Toplevel):
    def __init__(self, master, handler, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.handler = handler

        self.title("Spotify playlist picker")

        self.geometry("800x500")
        self.resizable(True, False)

        self.SPOTIFY_CLIENT = get_root_tk(self).SPOTIFY_CLIENT

        self.input_frame = tk.Frame(self, relief="groove", borderwidth=5, width=400)
        self.input_frame.pack(side="left", fill="y")

        self.input_frame.pack_propagate(False)

        self.preview = PlaylistPreview(self, relief="groove", borderwidth=5)
        self.preview.pack(side="left", fill="both", expand=True)

        self.link_var = tk.StringVar()
        self.link_entry = tk.Entry(self.input_frame, textvariable=self.link_var)
        self.link_entry.pack(expand=True, fill="x", padx=10)
        self.link_var.trace_add("write", self.on_entry_change)

        self.download_covers_var = tk.BooleanVar()
        self.download_covers_var.set(True)
        self.download_covers_checkbox = tk.Checkbutton(
            self.input_frame,
            text="Download track covers?",
            variable=self.download_covers_var,
        )
        self.download_covers_checkbox.pack(expand=True)

        self.add_button = tk.Button(
            self.input_frame, text="Add playlist", command=self.on_add_button_press
        )
        self.add_button.pack(anchor="n", expand=True)

    def on_entry_change(self, var, index, mode):
        url = self.link_var.get()
        if url:
            self.preview.show_message("Loading playlist...")
            Thread(
                target=self.load_playlist_in_thread, args=(url,), daemon=True
            ).start()
        else:
            self.preview.show_message("")

    def load_playlist_in_thread(self, url):
        try:
            playlist = spotify.get_playlist_from_url(self.SPOTIFY_CLIENT, url)
            self.preview.load_playlist(playlist)
        except Exception as e:
            self.preview.show_message("An error occured\nloading the playlist")
            print("Error loading playlist", url)
            print(traceback.format_exc())

    def on_add_button_press(self):
        self.add_button.config(text="Fetching tracks...")
        self.update()

        try:
            tracks = spotify.get_playlist_tracks(
                self.SPOTIFY_CLIENT,
                self.link_var.get(),
                download_covers=self.download_covers_var.get(),
            )
        except Exception as e:
            print("Error getting tracks from playlist", self.link_var.get())
            print(traceback.format_exc())

        if self.handler:
            self.handler(tracks)
            self.destroy()


class SpotifyTrackPicker(tk.Toplevel):
    def __init__(self, master, handler, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.handler = handler

        self.title("Spotify song picker")

        self.geometry("800x500")
        self.resizable(True, False)

        self.SPOTIFY_CLIENT = get_root_tk(self).SPOTIFY_CLIENT

        self.input_frame = tk.Frame(self, relief="groove", borderwidth=5, width=400)
        self.input_frame.pack(side="left", fill="y")

        self.input_frame.pack_propagate(False)

        self.preview = TrackPreview(self, relief="groove", borderwidth=5)
        self.preview.pack(side="left", fill="both", expand=True)

        self.link_var = tk.StringVar()
        self.link_entry = tk.Entry(self.input_frame, textvariable=self.link_var)
        self.link_entry.pack(expand=True, fill="x", padx=10)
        self.link_var.trace_add("write", self.on_entry_change)

        self.download_cover_var = tk.BooleanVar()
        self.download_cover_var.set(True)
        self.download_cover_checkbox = tk.Checkbutton(
            self.input_frame,
            text="Download track cover?",
            variable=self.download_cover_var,
        )
        self.download_cover_checkbox.pack(expand=True)

        self.add_button = tk.Button(
            self.input_frame, text="Add song", command=self.on_add_button_press
        )
        self.add_button.pack(anchor="n", expand=True)

    def on_entry_change(self, var, index, mode):
        url = self.link_var.get()
        if url:
            self.preview.show_message("Loading song...")
            Thread(target=self.load_track_in_thread, args=(url,), daemon=True).start()
        else:
            self.preview.show_message("")

    def load_track_in_thread(self, url):
        try:
            track = spotify.get_track_from_url(self.SPOTIFY_CLIENT, url)
            self.preview.load_track(track)
        except Exception as e:
            self.preview.show_message("An error occured\nloading the song")
            print("Error loading song", url)
            print(traceback.format_exc())

    def on_add_button_press(self):
        self.add_button.config(text="Fetching track...")
        self.update()

        try:
            track = spotify.get_track_from_url(
                self.SPOTIFY_CLIENT,
                self.link_var.get(),
                download_cover=self.download_cover_var.get(),
            )
        except Exception as e:
            print("Error getting track", self.link_var.get())
            print(traceback.format_exc())

        if self.handler:
            self.handler([track])
            self.destroy()


class DownloadOptionsPicker(tk.Toplevel):
    def __init__(self, master=None, handler=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.handler = handler

        self.title("Download Options")
        self.geometry("800x500")

        self.output_folder_var = tk.StringVar()
        self.youtube_limit_var = tk.IntVar(value=10)
        self.match_cover_var = tk.BooleanVar(value=True)
        self.add_metadata_var = tk.BooleanVar(value=True)
        self.embed_lyrics_var = tk.BooleanVar(value=True)

        tk.Label(self, text="Pick output folder:").pack(pady=(10, 0))
        output_folder_entry = tk.Entry(
            self, textvariable=self.output_folder_var, state="readonly"
        )
        output_folder_entry.pack(pady=(0, 5), padx=10, fill="x")

        browse_button = tk.Button(
            self, text="Browse...", command=self.open_folder_picker
        )
        browse_button.pack(pady=(0, 10))

        tk.Label(self, text="Youtube matches limit:").pack()
        youtube_limit_spinbox = tk.Spinbox(
            self, from_=1, to=1000, textvariable=self.youtube_limit_var
        )
        youtube_limit_spinbox.pack(pady=(0, 10))

        match_cover_checkbox = tk.Checkbutton(
            self, text="Match cover to thumbnails?", variable=self.match_cover_var
        )
        match_cover_checkbox.pack(pady=(5, 10))

        add_metadata_checkbox = tk.Checkbutton(
            self, text="Add metadata to songs?", variable=self.add_metadata_var
        )
        add_metadata_checkbox.pack(pady=(5, 10))

        embed_lyrics_checkbox = tk.Checkbutton(
            self, text="Embed lyrics?", variable=self.embed_lyrics_var
        )
        embed_lyrics_checkbox.pack(pady=(5, 10))

        download_button = tk.Button(
            self, text="Download queue", command=self.download_queue
        )
        download_button.pack(pady=(10, 0))

    def open_folder_picker(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.output_folder_var.set(folder_path)

        self.focus_force()

    def is_valid_output_folder(self, path):
        return os.path.exists(path) and os.access(path, os.W_OK)

    def download_queue(self):
        output_folder = self.output_folder_var.get()
        if not output_folder:
            self.show_warning("You must pick an output folder!")
        elif not self.is_valid_output_folder(output_folder):
            self.show_warning("The selected path is not valid or not writable!")
        else:
            print("Output folder:", output_folder)
            print("Youtube search limit:", self.youtube_limit_var.get())

            download_options = DownloadOptions()
            download_options.output_folder = output_folder
            download_options.youtube_search_limit = self.youtube_limit_var.get()
            download_options.download_covers = self.match_cover_var.get()
            download_options.save_metadata = self.add_metadata_var.get()
            download_options.embed_lyrics = self.embed_lyrics_var.get()

            self.handler(download_options)

            self.destroy()

    def show_warning(self, message):
        warning_window = tk.Toplevel(self)
        warning_window.title("Warning")
        tk.Label(warning_window, text=message).pack(padx=20, pady=20)
        tk.Button(warning_window, text="OK", command=warning_window.destroy).pack(
            pady=(0, 10)
        )


class SettingsEditor(tk.Toplevel):
    def __init__(self, master=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.TUTORIAL_URL = "https://github.com/Mews/spotify-mp3/blob/main/TUTORIAL.md"

        self.title("Settings Editor")
        self.geometry("800x500")

        self.client_id_var = tk.StringVar(value=get_config("spotify", "client_id"))
        self.client_secret_var = tk.StringVar(
            value=get_config("spotify", "client_secret")
        )

        tk.Label(self, text="Spotify Client Id:").pack(anchor="w", padx=10, pady=5)
        self.client_id_entry = tk.Entry(self, textvariable=self.client_id_var)
        self.client_id_entry.pack(fill="x", padx=10)

        tk.Label(self, text="Spotify Client Secret:").pack(anchor="w", padx=10, pady=5)
        self.client_secret_entry = tk.Entry(self, textvariable=self.client_secret_var)
        self.client_secret_entry.pack(fill="x", padx=10)

        link = tk.Label(
            self,
            text="How do I get my client id and client secret?",
            fg="blue",
            cursor="hand2",
        )
        link.pack(pady=10)
        link.bind("<Button-1>", lambda e: webbrowser.open(self.TUTORIAL_URL))

        self.save_button = tk.Button(self, text="Save settings", command=self.on_save)
        self.save_button.pack(side="bottom", pady=10)

        self.reset_button = tk.Button(
            self, text="Reset Default Settings", command=self.on_reset
        )
        self.reset_button.pack(side="bottom", pady=5)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def has_unsaved_changes(self):
        return self.client_id_var.get() != get_config(
            "spotify", "client_id"
        ) or self.client_secret_var.get() != get_config("spotify", "client_secret")

    def on_save(self):
        self.save_settings()
        self.destroy()

    def on_close(self):
        if self.has_unsaved_changes():
            response = messagebox.askyesno(
                "Unsaved Changes",
                "You have unsaved changes. Do you want to discard them?",
            )
            if response:  # Discard changes
                self.destroy()
        else:
            self.destroy()

    def save_settings(self):
        change_config("spotify", "client_id", self.client_id_var.get().strip())
        change_config("spotify", "client_secret", self.client_secret_var.get().strip())

    def on_reset(self):
        response = messagebox.askyesno(
            "Reset Settings", "Are you sure you want to restore the default settings?"
        )
        if response:
            reset_default_configs()

        self.client_id_var.set(get_config("spotify", "client_id"))
        self.client_secret_var.set(get_config("spotify", "client_secret"))
