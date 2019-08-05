import datetime as dt

from typing import List
from gmusicapi import Mobileclient
from client import BaseClient
from domain import *


class GoogleMusicClient(BaseClient):

    def __init__(self):
        self._client = Mobileclient()

    @property
    def client(self) -> Mobileclient:
        return self._client

    def authenticate(self, device_id: str = None):
        self.client.oauth_login(device_id if device_id else Mobileclient.FROM_MAC_ADDRESS)

    def is_authenticated(self) -> bool:
        return self.client.is_authenticated()

    def _query_artist(self, name: str) -> List[Artist]:
        raw_artists = self.client.search(name)["artist_hits"]
        return [Artist(id=raw["artist"]["artistId"], name=raw["artist"]["name"]) for raw in raw_artists]

    def load_artist_details(self, artist: Artist) -> ArtistDetails:
        raw_artist_info = self.client.get_artist_info(artist.id, include_albums=True, max_top_tracks=0, max_rel_artist=0)
        if "albums" in raw_artist_info:
            # TODO Parallelization
            raw_album_infos = [self.client.get_album_info(raw_album["albumId"]) for raw_album in raw_artist_info["albums"]]
        else:
            raw_album_infos = []

        albums = [self._album_from_raw_data(raw_album) for raw_album in raw_album_infos]
        albums.sort(key=lambda a: a.year, reverse=True)

        if "artistArtRefs" in raw_artist_info:
            image_url = self._image_url_from_raw_data(raw_artist_info["artistArtRefs"])
        else:
            image_url = None
        return ArtistDetails(artist=artist, albums=albums, image_url=image_url)

    def load_top_tracks_of_artist(self, artist: Artist, n: int) -> List[Track]:
        raw_artist_info = self.client.get_artist_info(artist.id, include_albums=False, max_top_tracks=n, max_rel_artist=0)
        if "topTracks" in raw_artist_info:
            return [self._track_from_raw_data(raw_track) for raw_track in raw_artist_info["topTracks"]]
        else:
            return []

    def create_playlist(self, name: str, description: str = None, public=False) -> Playlist:
        playlist_id = self.client.create_playlist(name=name, description=description, public=public)
        return Playlist(id=playlist_id, name=name, description=description, is_public=public)

    def add_tracks_to_playlist(self, playlist: Playlist, tracks: List[Track]):
        self.client.add_songs_to_playlist(playlist.id, [track.id for track in tracks])

    @staticmethod
    def _image_url_from_raw_data(raw_art_refs: List[dict]) -> str:
        best_raw_art_ref = None
        for raw_art_ref in raw_art_refs:
            if not best_raw_art_ref or (best_raw_art_ref["autogen"] and not raw_art_ref["autogen"]) or (best_raw_art_ref["aspectRatio"] != 1 and raw_art_ref["aspectRatio"] == 1):
                best_raw_art_ref = raw_art_ref
        return best_raw_art_ref["url"] if best_raw_art_ref else None

    def _album_from_raw_data(self, raw_album: dict) -> Album:
        ordered_raw_tracks = sorted(raw_album["tracks"], key=lambda t: t["trackNumber"])
        return Album(
            name=raw_album["name"],
            year=raw_album["year"] if "year" in raw_album else None,
            tracks=[self._track_from_raw_data(track) for track in ordered_raw_tracks],
            image_url=raw_album["albumArtRef"]
        )

    @staticmethod
    def _track_from_raw_data(raw_track: dict) -> Track:
        return Track(
            id=raw_track["storeId"],
            name=raw_track["title"],
            genre=raw_track["genre"] if "genre" in raw_track else None,
            duration=dt.timedelta(milliseconds=int(raw_track["durationMillis"]))
        )
