
from argparse import ArgumentParser
from math import ceil
from pathlib import Path
import textwrap
from typing import Iterable

from requests import get

from apple_music_data import collate_albums, format_artwork_url, get_paylist_songs, AlbumInfo

from PIL import Image, ImageDraw, ImageColor, ImageFont, ImageOps
import qrcode

parser = ArgumentParser()
parser.add_argument('url')
parser.add_argument('--cols', type=int, default=None)

CACHE = Path('.cache')
CACHE.mkdir(exist_ok=True)

def obtain_albumart(albums: Iterable[AlbumInfo]):
    for a in albums:
        url = format_artwork_url(a.art, 600, 600, "jpg")
        file = CACHE / (url.split('/')[-3] + ".jpg")
        if not file.is_file():
            file.write_bytes(get(url).content)

        yield a, file



ARTIST_FONT = ImageFont.FreeTypeFont(
    '/Users/yunruse/Library/Fonts/Lora-VariableFont_wght.ttf',
    size=80,
)
TITLE_FONT = ImageFont.FreeTypeFont(
    '/Library/Fonts/SF-Compact-Rounded-Thin.otf',
    size=80,
)


if __name__ == '__main__':
    args = parser.parse_args()
    albums = collate_albums(get_paylist_songs(args.url))

    N = len(albums)

    args.cols = args.cols or round(N ** 0.5)
    rows = ceil(N / args.cols)

    imgw = 600
    imgh = 600
    gutterw = 900
    w = args.cols * (imgw + gutterw)
    h = rows * imgh

    image = Image.new('RGBA', (w, h))
    draw = ImageDraw.Draw(image)
    
    for i, (album, artfile) in enumerate(obtain_albumart(albums)):
        r = i // args.cols
        y = r * imgh

        c = i % args.cols
        x_art = c * imgw
        x_info = rows * imgw + c * gutterw

        artwork = Image.open(artfile)
        image.paste(artwork, (x_art, y))

        bg = ImageColor.getrgb('#' + album.art['bgColor'])
        GUTTER = 50
        LINEHEIGHT = 100

        TEXT_CHARS_PER_LINE = 20
        def wrap(text: str):
            return textwrap.wrap(
                text, TEXT_CHARS_PER_LINE)

        draw.rectangle((x_info, y, x_info+gutterw, y+imgh), bg)

        url = f'https://song.link/{album.song}'
        qr = qrcode.make(url, box_size=6, border=2)

        def qr_to_fade(qr):
            back = Image.new('RGBA', qr.size, (0, 0, 0, 0))
            back.paste(
                ImageColor.getrgb('#' + album.art['textColor1'] + '44'),
                mask=ImageOps.invert(qr)
            )
            return back
        
        image.alpha_composite(qr_to_fade(qr), (
            x_info + gutterw - qr.size[0],
            y + imgh - qr.size[1]))
        


        artist = wrap(album.artist.split(' & ')[0])
        title = wrap(album.name)

        draw.text(
            (
                x_info + GUTTER,
                y + GUTTER
            ),
            '\n'.join(artist),
            ImageColor.getrgb('#' + album.art['textColor3']),
            ARTIST_FONT
        )
        draw.text(
            (
                x_info + GUTTER,
                y + GUTTER + LINEHEIGHT*len(artist)
            ),
            '\n'.join(title),
            ImageColor.getrgb('#' + album.art['textColor4']),
            TITLE_FONT
        )
    
    image.save('output.png')