"""Turn the committed avatar packs into the animated PNGs the README shows.

Reads `assets/avatars/<id>/` as built by `build.py` and writes one looping APNG
per avatar and reaction to `docs/images/avatars/<id>/<reaction>.png`.
"""

from pathlib import Path
import json
import sys
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))

from build import AVATARS, OUT, ROOT

SHOWCASE = ROOT / 'docs' / 'images' / 'avatars'
REACTIONS = ('idle', 'working', 'finished', 'needs-you', 'hover', 'resting')
# Plays that end on a held pose linger there, so the loop doesn't snap straight back.
LINGER_MS = 900


def frames(pack, reaction):
    animation = pack['animations'][reaction]
    strip = Image.open(OUT / pack['id'] / animation['strip']).convert('RGBA')
    cell = pack['cell']['width']
    cells = [strip.crop((i * cell, 0, (i + 1) * cell, cell)) for i in range(animation['frameCount'])]
    played = [(cells[f['index']], f['durationMs']) for f in animation['frames']]
    if animation['playback'] != 'loop':
        last, ms = played[-1]
        played[-1] = (last, ms + LINGER_MS)
    return played


def save(played, path):
    images = [image for image, _ in played]
    if len(images) == 1:
        images[0].save(path, optimize=True)
        return
    images[0].save(
        path,
        save_all=True,
        append_images=images[1:],
        duration=[ms for _, ms in played],
        loop=0,
        disposal=0,
        blend=0,
        optimize=True,
    )


def main():
    for avatar in AVATARS:
        pack = json.loads((OUT / avatar.ID / 'avatar.json').read_text())
        directory = SHOWCASE / avatar.ID
        directory.mkdir(parents=True, exist_ok=True)
        for reaction in REACTIONS:
            save(frames(pack, reaction), directory / f'{reaction}.png')
        print(f'Showcased {avatar.ID}')


if __name__ == '__main__':
    main()
