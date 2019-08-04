import logging.config
import yaml

from typing import List
from itertools import zip_longest
from gmusic import GoogleMusicClient
from domain import Artist, ArtistDetails


def main():
    logger().info("Starting session")
    client = GoogleMusicClient()
    client.authenticate()

    # with open("few_artists.txt") as f:
    with open("artists.txt") as f:
        artist_names = [line.strip() for line in f.readlines() if line]
    logger().info(f"Searching for artists: {', '.join(artist_names)}")
    missing_artists = []
    unambiguous_artists = []
    ambiguous_artists = {}
    for name in artist_names:
        logger().debug(f"Searching {name}")
        artists = client.search_artist(name)
        if not artists:
            missing_artists.append(name)
        elif len(artists) == 1:
            unambiguous_artists.append(artists[0])
        else:
            ambiguous_artists[name] = artists

    logger().warning(f"The following artists could not be found: {', '.join(missing_artists)}")
    logger().info(f"{len(unambiguous_artists)} artists where unambiguous: {', '.join(map(str, unambiguous_artists))}")
    logger().info(f"{len(ambiguous_artists)} artists where ambiguous and have to be resolved manually: {', '.join(ambiguous_artists.keys())}")

    logger().info("Loading details of ambiguous artists")
    ambiguous_artists = {name: client.load_artists_details(artists) for name, artists in ambiguous_artists.items()}

    final_artists = list(unambiguous_artists)
    for name, artists_details in ambiguous_artists.items():
        selected_artist = resolve_conflict(name, artists_details)
        if selected_artist:
            final_artists.append(selected_artist)
    final_artists.sort(key=lambda a: a.name)
    logger().info(f"Final artist list to create the playlist for: {', '.join(map(str, final_artists))}")

    if not client.is_authenticated():
        client.authenticate()

    number_of_top_tracks = 5
    logger().info(f"Loading top {number_of_top_tracks} for final artists")
    tracks = client.load_top_tracks_of_artists(final_artists, n=number_of_top_tracks)
    logger().info(f"Loaded {len(tracks)} tracks")

    logger().info(f"Creating playlist and adding tracks")
    playlist = client.create_playlist("Generated Summer Breeze 2019")
    client.add_tracks_to_playlist(playlist, tracks)


def resolve_conflict(name: str, artists_details: List[ArtistDetails]) -> Artist:
    artists_output = "\n".join(f"\t{i+1}) {artist.name} - {', '.join(artist.genres)}" for i, artist in enumerate(artists_details))
    logger().info(f"Choose an artist for {name} (number for selection, 'a'/'albums' to display a table of albums or 0 to skip):\n{artists_output}")
    selection = None
    while selection is None:
        try:
            selection = input(f"Selection [1-{len(artists_details)}, a/albums, 0]: ").lower()
            if selection == "a" or selection == "albums":
                logger().info(f"Albums of matches:\n{create_albums_table(artists_details)}")
                selection = None
            else:
                selection = int(selection) - 1
                assert -1 <= selection < len(artists_details)
        except:
            logger().info(f"The input must be a number between 0 and {len(artists_details)} or 'a'/'albums'")
            selection = None
    return artists_details[selection].artist if selection >= 0 else None


def create_albums_table(artists_details: List[ArtistDetails]) -> str:
    columns = []
    for index, artist_details in enumerate(artists_details):
        max_album_name_width = max(map(len, (album.name for album in artist_details.albums)))
        rows = [
            f"{index+1}) {artist_details.name}",
            *(f"{album.year}) {album.name:{max_album_name_width}}   {', '.join(album.genres)}" for album in artist_details.albums)
        ]
        max_width = max(map(len, rows))
        rows = [f"{row:{'^' if i == 0 else ''}{max_width}}" for i, row in enumerate(rows)]
        columns.append(rows)

    number_of_rows = max(map(len, columns))
    for column in columns:
        filler = " " * len(column[0])
        for _ in range(number_of_rows - len(column)):
            column.append(filler)

    rows = [" | ".join(row) for row in zip_longest(*columns, fillvalue="")]
    rows.insert(1, "-" * len(rows[0]))
    return "\n".join(rows)


def logger():
    return logging.getLogger(__name__)


if __name__ == "__main__":
    with open("logging_config.yml") as f:
        logging.config.dictConfig(yaml.full_load(f))
    main()
