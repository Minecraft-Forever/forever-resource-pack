"""
Sprites that are not things: the glyphs our menus are drawn with.

<b>Why a sprite rather than an item.</b> A menu sometimes needs to say
something no item in the game says. The grindstone window wants an arrow
between the slot you put a thing in and the slot that shows what it
becomes - the same mark every furnace, anvil and smithing table draws -
and Minecraft has no item that looks like one. A spectral arrow was the
closest the game had and it reads as ammunition, because it is
ammunition: it points up and to the left, and it is fletched.

So these are drawn, and pointed at with the {@code item_model}
component exactly as the fish are. The base item stays a spectral arrow,
which is the honest fallback: somebody playing without the pack sees an
arrow rather than a mystery.

<b>Procedural rather than hand-drawn.</b> A right-pointing arrow is a
shaft and a triangle, and both are two numbers. Tuning it by moving a
number beats editing sixty-four characters of ASCII art and recounting
the columns, which is how a sprite ends up one pixel off centre.

No image library, like everything else in this pack: write_png takes a
grid of RGBA tuples.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PACK = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from build_models import write_png  # noqa: E402

SIZE = 16

CLEAR = (0, 0, 0, 0)
# Near-white rather than gold. The label beside it is gold and a gold
# arrow beside a gold word reads as one blob at inventory scale; this is
# a mark on a dark background, so the brightest thing wins.
BODY = (226, 226, 226, 255)
SHADE = (168, 168, 168, 255)

# The shaft, then the head. Both inclusive, both in texture pixels.
#
# <b>Smaller than it was, and the head now starts where the shaft
# stops.</b> The old numbers ran the head from x=8, overlapping the
# shaft's last column, and with the outline below the whole mark was
# fifteen pixels across - which in a twelve-pixel slot is a block with
# an arrow cut out of it rather than an arrow.
SHAFT_X = (2, 8)
SHAFT_Y = (6, 9)
HEAD_X = (9, 13)
HEAD_HALF = 5


def solid():
    """Which pixels the arrow itself covers."""
    filled = set()
    for x in range(SHAFT_X[0], SHAFT_X[1] + 1):
        for y in range(SHAFT_Y[0], SHAFT_Y[1] + 1):
            filled.add((x, y))
    # One row off each side per column, which is the 2:1 slope every
    # arrowhead in the game's own interface uses.
    #
    # <b>This was a proportional taper and it drew a lumpy head.</b> It
    # was round(HEAD_HALF * (1 - step / span)), which for the middle
    # column is round(2.5) - and Python rounds halves to even, so that
    # is 2 rather than 3. The head jumped from four rows to two, then
    # drew its last two columns identically, which is the notch under
    # the tip. A taper that counts down cannot round at all.
    half = HEAD_HALF
    for x in range(HEAD_X[0], HEAD_X[1] + 1):
        # The tip stays two pixels tall: a one-pixel tip disappears at
        # the scale this is drawn.
        for y in range(8 - max(1, half), 8 + max(1, half)):
            filled.add((x, y))
        half -= 1
    return filled


def draw():
    """
    Two tones and no outline.

    <b>The black keyline is gone.</b> It was the single thing making
    this read as a sticker laid on the window rather than part of it,
    and it is the same mistake the first rune sprites made - almost
    nothing in Minecraft is outlined in black; things are outlined in a
    dark tone of their own material, if at all. A near-white mark on a
    dark slot needs no help standing out, so the outline was buying
    contrast that was already there and paying for it in weight.

    What is left is the shape and one row of shade along its underside,
    which gives the light a direction and stops the arrow reading as a
    hole cut in the window.
    """
    filled = solid()
    pixels = [[CLEAR for _ in range(SIZE)] for _ in range(SIZE)]
    for (x, y) in filled:
        if 0 <= x < SIZE and 0 <= y < SIZE:
            below = (x, y + 1) not in filled
            pixels[y][x] = SHADE if below else BODY
    return pixels


def write(name, pixels):
    textures = os.path.join(PACK, "assets", "forever", "textures", "item")
    models = os.path.join(PACK, "assets", "forever", "models", "item")
    items = os.path.join(PACK, "assets", "forever", "items")
    for directory in (textures, models, items):
        os.makedirs(directory, exist_ok=True)
    write_png(os.path.join(textures, "%s.png" % name), SIZE, SIZE, pixels)
    with open(os.path.join(models, "%s.json" % name), "w") as handle:
        json.dump({"parent": "minecraft:item/generated",
                   "textures": {"layer0": "forever:item/%s" % name}},
                  handle, indent=2)
        handle.write("\n")
    with open(os.path.join(items, "%s.json" % name), "w") as handle:
        json.dump({"model": {"type": "minecraft:model",
                             "model": "forever:item/%s" % name}},
                  handle, indent=2)
        handle.write("\n")


def main():
    write("arrow_right", draw())
    print("  arrow_right")


if __name__ == "__main__":
    main()
