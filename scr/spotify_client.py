import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()

class SpotifyClient:
    def __init__(self):
        client_id = os.getenv("SPOTIFY_CLIENT_ID")
        client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

        if not client_id or not client_secret:
            raise RuntimeError(
                "Spotify credentials not found. "
                "Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in .env"
            )

        auth = SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        )
        self.sp = spotipy.Spotify(auth_manager=auth)

    def search_artist(self, name: str):
        result = self.sp.search(q=f"artist:{name}", type="artist", limit=1)
        items = result["artists"]["items"]
        if not items:
            raise ValueError(f"Artist not found: {name}")
        return items[0]

    def get_top_tracks(self, artist_id: str, country="US"):
        return self.sp.artist_top_tracks(artist_id, country=country)["tracks"]

    def get_audio_features(self, track_ids: list[str]):
        return self.sp.audio_features(track_ids)