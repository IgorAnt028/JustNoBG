from PIL import Image, ImageDraw
import re
import sys


def main():
    for url in sys.argv[1:]:
        img = Image.open(url).convert('RGBA')

        # Save old
        img.save("old_" + re.sub(r"^.*\\", "", url))

        # BG removing

        rep_value = (0, 0, 0, 0)

        seed = (0, 0)
        ImageDraw.floodfill(img, seed, rep_value, thresh=100)

        seed = (0, img.size[1] - 1)
        ImageDraw.floodfill(img, seed, rep_value, thresh=100)

        seed = (img.size[1] - 1, 0)
        ImageDraw.floodfill(img, seed, rep_value, thresh=100)

        seed = (img.size[0] - 1, img.size[1] - 1)
        ImageDraw.floodfill(img, seed, rep_value, thresh=100)

        # Borders
        pos = [0, 0, 0, 0]

        pixels = img.load()

        # X
        for x in range(img.size[0]):
            if pos[0] != 0:
                break

            for y in range(img.size[1]):
                if pixels[x, y] != (0, 0, 0, 0):
                    pos[0] = x

        # Y
        for y in range(img.size[1]):
            if pos[1] != 0:
                break

            for x in range(img.size[0]):
                if pixels[x, y] != (0, 0, 0, 0):
                    pos[1] = y

        # -X
        for x in range(img.size[0] - 1, 1, -1):
            if pos[2] != 0:
                break

            for y in range(img.size[1]):
                if pixels[x, y] != (0, 0, 0, 0):
                    pos[2] = x

        # -Y
        for y in range(img.size[1] - 1, 1, -1):
            if pos[3] != 0:
                break

            for x in range(img.size[0]):
                if pixels[x, y] != (0, 0, 0, 0):
                    pos[3] = y

        img.crop((pos[0], pos[1], pos[2], pos[3])).save(re.sub(r"^.*\\", "", url))


if len(sys.argv) > 1:
    main()
