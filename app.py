import vlc
import tkinter as tk
from tkinter import filedialog
import re
import pickle
from PIL import Image, ImageTk

LAST_PLAYLIST_FILE = "last_playlist.pkl"

class IPTVApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # carrega una imatge i converteix-la en una instància de PhotoImage
        self.logo = ImageTk.PhotoImage(Image.open("icon.jpg"))
        self.iconphoto(False, self.logo)
        self.iconbitmap("icon.ico")
        self.title("IPTV Player")
        self.geometry("800x500")
        self.resizable(True, True)
        self.vlc_instance = vlc.Instance()
        self.player = self.vlc_instance.media_player_new()
        self.last_playlist_file = "last_playlist.pkl"
        self.media_list = None
        self.channels = {}
        self.groups = {}

        self.selected_group_index = None
        
        self.build_ui()
    def parse_m3u(self, content):
        channels = {}
        groups = {}

        lines = content.split("\n")

        for index in range(0, len(lines)):
            if lines[index].startswith("#EXTINF"):
                channel_info = lines[index].strip("#EXTINF:-1 ")

                group_match = re.search(r'group-title="(.*?)"', channel_info)
                if group_match:
                    group = group_match.group(1)
                else:
                    group = "No Group"

                name_match = re.search(r'tvg-name="(.*?)"', channel_info)
                if name_match:
                    name = name_match.group(1)
                else:
                    name = "Unknown"

                url = lines[index + 1].strip()

                if group not in groups:
                    groups[group] = []

                channel = {"name": name, "url": url}
                groups[group].append(channel)
                channels[url] = channel

        return channels, groups
    def build_ui(self):
        self.paned_window = tk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=1)

        self.lists_frame = tk.Frame(self.paned_window)
        self.paned_window.add(self.lists_frame, stretch="always")

        self.group_listbox = tk.Listbox(self.lists_frame)
        self.group_listbox.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.group_listbox.bind('<<ListboxSelect>>', self.group_selected)

        self.channel_listbox = tk.Listbox(self.lists_frame)
        self.channel_listbox.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.channel_listbox.bind('<<ListboxSelect>>', self.channel_selected)

        self.player_frame = tk.Frame(self.paned_window)
        self.paned_window.add(self.player_frame, stretch="always")
        self.player_frame.bind("<Double-Button-1>", self.toggle_fullscreen)
        
        # Afegeix el reproductor VLC al player_frame
        self.player.set_fullscreen(False)
        self.player.set_hwnd(self.player_frame.winfo_id())

        self.open_btn = tk.Button(self.player_frame, text="Open M3U", command=self.open_playlist)
        self.open_btn.pack(side=tk.BOTTOM)
        # Carrega la última llista de reproducció
        try:
            with open(LAST_PLAYLIST_FILE, "rb") as f:
                last_filepath, self.groups = pickle.load(f)
                self.media_list = self.parse_m3u(last_filepath)[1]
                self.load_playlist(last_filepath)
        except (FileNotFoundError, pickle.UnpicklingError, ValueError):
            pass  # No s'ha trobat la última llista o hi ha un error en el fitxer



    def open_playlist(self):
        file_path = filedialog.askopenfilename(filetypes=[("M3U Files", "*.m3u")])
        # Desa la última llista
        with open(LAST_PLAYLIST_FILE, "wb") as f:
            pickle.dump((file_path, self.groups), f)
        if file_path:
            self.load_playlist(file_path)

    def load_playlist(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        self.channels, self.groups = self.parse_m3u(content)

        self.update_group_list()

    

    def update_group_list(self):
        self.group_listbox.delete(0, tk.END)

        for index, group in enumerate(self.groups.keys()):
            self.group_listbox.insert(index, group)
            
    def update_channel_list(self, group):
        self.channel_listbox.delete(0, tk.END)

        for index, channel in enumerate(self.groups[group]):
            self.channel_listbox.insert(index, channel["name"])

    def group_selected(self, event):
        selection = self.group_listbox.curselection()
        if not selection:
            return
        self.selected_group_index = selection[0]
        group = self.group_listbox.get(self.selected_group_index)
        if not self.group_listbox.curselection():
            return

        group = self.group_listbox.get(self.group_listbox.curselection())
        self.update_channel_list(group)

    def channel_selected(self, event=None):
        if not self.channel_listbox.curselection():
            return

        channel_name = self.channel_listbox.get(self.channel_listbox.curselection())
        group = self.group_listbox.get(self.selected_group_index)

        for channel in self.groups[group]:
            if channel["name"] == channel_name:
                selected_channel = channel
                break

        media = self.vlc_instance.media_new(selected_channel["url"])
        self.player.set_media(media)
        self.player.play()

    def toggle_fullscreen(self, event=None):
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen:
            self.attributes('-fullscreen', True)
            self.player_frame.pack_forget()
            self.player.set_fullscreen(True)
        else:
            self.attributes('-fullscreen', False)
            self.player.set_fullscreen(False)
            self.player_frame.pack(fill=tk.BOTH, expand=True)

            
    def play_url(url):
        vlc_instance = vlc.Instance()
        player = vlc_instance.media_player_new()
        media = vlc_instance.media_new(url)
        player.set_media(media)
        player.play()


if __name__ == "__main__":
    app = IPTVApp()
    app.mainloop()
