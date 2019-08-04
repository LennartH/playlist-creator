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

    def _query_artist(self, name: str) -> List[Artist]:
        raw_artists = self.client.search(name)["artist_hits"]
        return [Artist(name=raw["artist"]["name"], id=raw["artist"]["artistId"]) for raw in raw_artists]

    def load_artist_details(self, artist: Artist) -> ArtistDetails:
        raw_artist_info = self.client.get_artist_info(artist.id, include_albums=True, max_top_tracks=0, max_rel_artist=0)
        # TODO How to handle an artist without albums?
        if "albums" in raw_artist_info:
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
            name=raw_track["title"],
            genre=raw_track["genre"] if "genre" in raw_track else None,
            duration=dt.timedelta(milliseconds=int(raw_track["durationMillis"]))
        )
