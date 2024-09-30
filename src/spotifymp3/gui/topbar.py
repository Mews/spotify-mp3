import tkinter as tk
from tkfontawesome import icon_to_image
from src.spotifymp3.gui.utils import load_icon, get_root_tk, DownloadOptions
from src.spotifymp3.gui.pickers import *
from src.spotifymp3.track import *

class TopBar(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.youtube_plus_icon = load_icon("youtube-plus", scale_to_height=32)
        self.youtube_playlist_icon = load_icon("youtube-playlist", scale_to_height=32)
        self.spotify_plus_icon = load_icon("spotify-plus", scale_to_height=32)
        self.spotify_playlist_icon = load_icon("spotify-playlist", scale_to_height=32)
        self.download_icon = icon_to_image("download", "green", scale_to_height=32)
        self.clear_queue_icon = icon_to_image("trash", "gray", scale_to_height=32)
        self.settings_icon = icon_to_image("cog", "gray", scale_to_height=32)

        self.youtube_playlist_button = tk.Button(self, image=self.youtube_playlist_icon, text="Youtube playlist", compound=tk.TOP, font=("", 12), padx=10, pady=5, command=self.open_youtube_playlist_picker)
        self.youtube_playlist_button.pack(side=tk.LEFT, pady=5, padx=(5, 0), anchor="w")

        self.youtube_track_button = tk.Button(self, image=self.youtube_plus_icon, text="Youtube video", compound=tk.TOP, font=("", 12), padx=10, pady=5, command=self.open_youtube_track_picker)
        self.youtube_track_button.pack(side=tk.LEFT, pady=5, padx=(0, 5), anchor="w")

        self.spotify_playlist_button = tk.Button(self, image=self.spotify_playlist_icon, text="Spotify playlist", compound=tk.TOP, font=("", 12), padx=10, pady=5, command=self.open_spotify_playlist_picker)
        self.spotify_playlist_button.pack(side=tk.LEFT, pady=5, anchor="w")

        self.spotify_track_button = tk.Button(self, image=self.spotify_plus_icon, text="Spotify track", compound=tk.TOP, font=("", 12), padx=10, pady=5, command=self.open_spotify_track_picker)
        self.spotify_track_button.pack(side=tk.LEFT, pady=5, padx=(0, 5), anchor="w")
        
        self.download_button = tk.Button(self, image=self.download_icon, text="Download queue", compound=tk.TOP, font=("", 12), padx=10, pady=5, command=self.open_donwload_options_picker)
        self.download_button.pack(side=tk.LEFT, pady=5, padx=(5, 5), anchor="w")

        self.clear_queue_button = tk.Button(self, image=self.clear_queue_icon, text="Clear queue", compound=tk.TOP, font=("", 12), padx=10, pady=5, command=self.clear_queue)
        self.clear_queue_button.pack(side=tk.LEFT, pady=5, padx=(5, 5), anchor="w")

        self.settings_button = tk.Button(self, image=self.settings_icon, text="Settings", compound=tk.TOP, font=("", 12), padx=10, pady=5, command=self.open_settings_editor)
        self.settings_button.pack(side=tk.LEFT, pady=5, anchor="w")

    def open_youtube_playlist_picker(self):
        YoutubePlaylistPicker(self, handler=self.handle_picked_tracks)
    
    def open_youtube_track_picker(self):
        YoutubeTrackPicker(self, handler=self.handle_picked_tracks)

    def open_spotify_playlist_picker(self):
        SpotifyPlaylistPicker(self, handler=self.handle_picked_tracks)

    def open_spotify_track_picker(self):
        SpotifyTrackPicker(self, handler=self.handle_picked_tracks)

    def open_settings_editor(self):
        SettingsEditor(self)

    def handle_picked_tracks(self, tracks):
        #print(tracks)
        print(f"Loaded: {len(tracks)} tracks")

        convert_tracks = []

        for track in tracks:
            convert_track = ConvertTrack()

            if isinstance(track, SpotifyTrack):
                convert_track.spotify_track = track
            
            if isinstance(track, YoutubeTrack):
                convert_track.youtube_track = track
            
            convert_tracks.append(convert_track)

        app = get_root_tk(self)
        app.queue.extend(convert_tracks)
    
    def open_donwload_options_picker(self):
        DownloadOptionsPicker(self, handler=self.handle_download_options)

    def handle_download_options(self, download_options:DownloadOptions):
        app = get_root_tk(self)
        app.start_processing_queue(download_options)

    def clear_queue(self):
        app = get_root_tk(self)
        queue = app.queue
        print(f"Clearing {len(queue)} tracks from queue")
        queue.clear()
        app.queue_viewer.sheet.dehighlight_all()

    def disable_topbar(self):
        for widget in self.winfo_children():
            if isinstance(widget, tk.Button):
                widget.config(state="disabled")
    
    def enable_topbar(self):
        for widget in self.winfo_children():
            if isinstance(widget, tk.Button):
                widget.config(state="active")
