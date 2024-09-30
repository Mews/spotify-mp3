from PIL import Image, ImageTk
import tkinter as tk
from typing import Any, Iterable
from dataclasses import dataclass

def load_icon(icon_name, scale_to_width=None, scale_to_height=None):
    if scale_to_width and scale_to_height:
        raise ValueError("Cant have both scale_to_width and scale_to_height")

    icon = Image.open(f"assets/icons/{icon_name}.png")
    
    aspect_ratio = icon.width / icon.height

    if scale_to_width:
        icon = icon.resize((scale_to_width, round(scale_to_width/aspect_ratio)))
    
    if scale_to_height:
        icon = icon.resize((round(scale_to_height*aspect_ratio), scale_to_height))
    
    return ImageTk.PhotoImage(icon)


def get_root_tk(widget):
    root_widget = widget.winfo_toplevel()

    while not isinstance(root_widget, tk.Tk):
        root_widget = root_widget.master

    return root_widget

class ObservableList(list):
    def __init__(self, callback=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.callback = callback
    
    def _trigger_callback(self):
        if self.callback:
            self.callback()

    def append(self, object: Any) -> None:
        x = super().append(object)
        self._trigger_callback()
        return x

    def extend(self, iterable: Iterable) -> None:
        x = super().extend(iterable)
        self._trigger_callback()
        return x

    def clear(self) -> None:
        x = super().clear()
        self._trigger_callback()
        return x

class DownloadOptions:
    def __init__(self):
        self.output_folder = None
        self.youtube_search_limit = 10
        self.download_covers = True
        self.save_metadata = True
