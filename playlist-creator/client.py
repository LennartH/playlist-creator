from typing import List
from abc import ABCMeta, abstractmethod
from util import WithLogger
from domain import *


class BaseClient(WithLogger, metaclass=ABCMeta):

    def search_artist(self, name: str) -> List[Artist]:
        query_result = self._query_artist(name)
        lower_name = name.lower()
        filtered_result = [artist for artist in query_result if lower_name == artist.name.lower()]
        return filtered_result if filtered_result else query_result

    @abstractmethod
    def _query_artist(self, name: str) -> List[Artist]:
        pass

    @abstractmethod
    def load_artist_details(self, artist: Artist) -> ArtistDetails:
        pass
