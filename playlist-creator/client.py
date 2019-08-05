from typing import List
from abc import ABCMeta, abstractmethod
from util import WithLogger
from domain import *


# TODO Parallelization
# TODO Add context (e.g. to filter for genre, ...)
class BaseClient(WithLogger, metaclass=ABCMeta):

    def search_artist(self, name: str) -> List[Artist]:
        query_result = self._query_artist(name)
        lower_name = name.lower()
        filtered_result = [artist for artist in query_result if lower_name == artist.name.lower()]
        return filtered_result if filtered_result else query_result

    @abstractmethod
    def _query_artist(self, name: str) -> List[Artist]:
        pass

    def load_artists_details(self, artists: List[Artist]) -> List[ArtistDetails]:
        # TODO Try-Catch
        return [self.load_artist_details(artist) for artist in artists]

    @abstractmethod
    def load_artist_details(self, artist: Artist) -> ArtistDetails:
        pass

    def load_top_tracks_of_artists(self, artists: List[Artist], n: int) -> List[Track]:
        tracks = []
        for artist in artists:
            try:
                tracks.extend(self.load_top_tracks_of_artist(artist, n))
            except:
                self.logger().exception(f"Error loading top {n} tracks of {artist}")
        return tracks

    # TODO USe heuristics to get "better" top tracks?
    @abstractmethod
    def load_top_tracks_of_artist(self, artist: Artist, n: int) -> List[Track]:
        pass

    @abstractmethod
    def create_playlist(self, name: str, description: str = None, public=False) -> Playlist:
        pass

    @abstractmethod
    def add_tracks_to_playlist(self, playlist: Playlist, tracks: List[Track]):
        pass
