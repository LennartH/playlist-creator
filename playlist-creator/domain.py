import datetime as dt

from typing import List, Set, Optional
from dataclasses import dataclass

__all__ = ["Artist", "ArtistDetails", "Album", "Track"]


@dataclass(frozen=True)
class Artist:
    id: str
    name: str

    def __str__(self):
        return self.name


@dataclass(frozen=True)
class ArtistDetails:
    artist: Artist
    albums: List["Album"]
    image_url: str

    @property
    def name(self) -> str:
        return self.artist.name

    @property
    def id(self) -> str:
        return self.artist.id

    @property
    def genres(self) -> Set[str]:
        genres = set()
        for album in self.albums:
            genres.update(album.genres)
        return genres

    def __str__(self):
        return str(self.name)


@dataclass(frozen=True)
class Album:
    name: str
    year: Optional[int]
    tracks: List["Track"]
    image_url: str

    @property
    def genres(self) -> Set[str]:
        return {track.genre for track in self.tracks if track.genre}

    def __str__(self):
        return f"{self.year} - {self.name}"


@dataclass(frozen=True)
class Track:
    id: str
    name: str
    genre: Optional[str]
    duration: dt.timedelta

    def __str__(self):
        return self.name
