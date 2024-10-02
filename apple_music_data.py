"""
Relevant datasets returned by the Apple Music API.
"""

from dataclasses import dataclass
from typing import Literal, TypedDict

import json
from collections import Counter

from requests import get
from bs4 import BeautifulSoup

from helpers import collate


class Artwork(TypedDict):
    url: str

    width: int
    height: int

    textColor1: str
    textColor2: str
    textColor3: str
    textColor4: str
    bgColor: str
    hasP3: bool

def format_artwork_url(art: 'Artwork', width=None, height=None, format="png"):
    return art['url'].format(
        w=width or art.width,
        h=height or art.height,
        f=format
    )

class PlayParams(TypedDict):
    id: str
    kind: str # song,

ExtendedAssetKind = Literal[
    'plus',
    'lightweight'
    'superLightweight'
    'lightweightPlus'
    'enhancedHls'
]

class ContentVersion(TypedDict):
    MZ_INDEXER: int
    RTCI: int

class MetaInfo(TypedDict):
    contentVersion: ContentVersion

class SongAttribs(TypedDict):
    url: str

    name: int
    albumName: str
    artistName: str

    artwork: Artwork
    composerName: str
    playParams: PlayParams
    extendedAssetsUrl: dict[ExtendedAssetKind, str]

    contentRating: str  # explicit, 
    audioTraits: list[str]
    durationInMillis: int

    relationships: dict  # TODO
    meta: MetaInfo


@dataclass(frozen=True)
class AlbumInfo:
    name: str
    artist: str
    art: Artwork
    song: str

class Song(TypedDict):
    id: str
    type: str # songs, 
    href: str
    attributes: SongAttribs



def get_paylist_songs(url) -> list[Song]:
    soup = BeautifulSoup(get(url).text, features='lxml')
    resp = json.loads(soup.select('#serialized-server-data')[0].text)[0]
    return resp["data"]["seoData"]["ogSongs"]

def _get_albums(playlist: list[Song]):
    for song in playlist:
        artwork = song['attributes']['artwork']
        # art_url = Artwork.get_url(artwork, 600, 600, "jpg")
        yield AlbumInfo(
            song['attributes']['albumName'],
            song['attributes']['artistName'],
            artwork,
            song['attributes']['url'],
        )

def collate_albums(songs: list[Song]):
    "Collate album info, using the most common artist name as canonical."
    def most_common_artist(col: list[AlbumInfo]):
        return Counter(map(lambda c: c.artist, col)).most_common()[0][0]

    return [
        AlbumInfo(
            col[0].name,
            most_common_artist(col),
            col[0].art,
            col[0].song,
        )
        for col in collate(_get_albums(songs), lambda a: a.name).values()]