from PIL import Image, ImageDraw
import re
import sys


def main():
    for url in sys.argv[1:]:
        img = Image.open(url).convert('RGBA')

        img.save(re.sub(r"[.].*$", "", re.sub(r"^.*\\", "", url)) + ".png")


if len(sys.argv) > 1:
    main()
