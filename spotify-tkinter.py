import tkinter as tk
from datetime import datetime
from pathlib import Path
from time import sleep
from tkinter import filedialog
from typing import List, Optional

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from yaml import Loader, load


class Application(tk.Frame):
    def __init__(self, config, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

        # Spotify
        self.config = config["spotify"]
        self.sp: Optional[spotipy.Spotify] = None
        self.filepath: Optional[Path] = None

    def create_widgets(self):
        self.login_btn = tk.Button(
            self, text="Login to Spotify", command=self.spotify_login
        )
        self.login_btn.grid(column=2, row=0)

        self.login_lbl = tk.Label(self, text="Logged in as:")
        self.login_lbl.grid(column=1, row=1)
        self.username_lbl = tk.Label(self, text="Nobody")
        self.username_lbl.grid(column=2, row=1)

        self.quit = tk.Button(self, text="QUIT", fg="red", command=self.master.destroy)
        self.quit.grid(column=2, row=2)

    def spotify_login(self):
        if self.sp is None:
            self.sp = spotipy.Spotify(
                auth_manager=SpotifyOAuth(
                    client_id=self.config["client_id"],
                    client_secret=self.config["client_secret"],
                    redirect_uri=self.config["redirect_uri"],
                    scope=self.config["scope"],
                )
            )

        user_info = self.sp.current_user()
        self.username_lbl["text"] = user_info["display_name"]

        if self.filepath is None:
            self.filepath = filedialog.askopenfilename()

        print(self.filepath)


def main():
    cfg = load_config()

    root = tk.Tk()
    root.title("Spotify Song Query")
    root.geometry("300x300")

    app = Application(cfg, master=root)
    app.mainloop()


def load_config(filepath: Path = Path("config.yml")):
    try:
        yaml_str = filepath.open("rb").read()
    except Exception:
        raise

    return load(yaml_str, Loader=Loader)


def check_spotify():
    # Only check every X seconds
    sleep_time = 5

    # We only need enough scope to get the current playing track
    scope = "user-read-playback-state"

    # Log in using OAuth
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    # Only print/update the file if the track we detect changes
    current_info = ""
    try:
        while True:
            current_track = sp.current_playback(market="CA")

            if current_track is None:
                info = "There is no track playing"
            else:
                item = current_track["item"]
                album_name = item["album"]["name"]

                artists_obj = item["artists"]

                artists: List[str] = []
                for artist_obj in artists_obj:
                    artists.append(artist_obj["name"])

                artists_name = ", ".join(artists)
                track_name = item["name"]

                info = (
                    f"Track: {track_name}\nArtist: {artists_name}\nAlbum: {album_name}"
                )

            if current_info != info:
                current_info = info
                print(f"{datetime.now()}\n{info}")
                with open("spotify-current-track.txt", "w") as f:
                    f.write(info)

            # Only query Spotify every X seconds
            sleep(sleep_time)
    except KeyboardInterrupt:
        print("Exiting...")


if __name__ == "__main__":
    main()
