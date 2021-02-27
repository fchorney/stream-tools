from datetime import datetime
from pathlib import Path
from time import sleep
from typing import List

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from yaml import Loader, load


def main():
    cfg = load_config()
    check_spotify(cfg["spotify"])


def load_config(filepath: Path = Path("config.yml")):
    try:
        yaml_str = filepath.open("rb").read()
    except Exception:
        raise

    return load(yaml_str, Loader=Loader)


def check_spotify(config):
    # Only check every X seconds
    sleep_time = 5

    # Log in using OAuth
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=config["client_id"],
            client_secret=config["client_secret"],
            redirect_uri=config["redirect_uri"],
            scope=config["scope"],
        )
    )

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
