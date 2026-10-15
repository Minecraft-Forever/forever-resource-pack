"""Sprites for the enchantment runes: eight stones, five levels, two states.

<b>Why they are drawn at all.</b> A woken rune was a pottery sherd and
an uncut one a disc fragment - both real items players dig out of
suspicious sand and ancient cities. In a chest ours were pixel-identical
to those, and only the name told them apart, which is the same confusion
the runes left enchanted books to escape; we had just swapped which
vanilla item they collided with. The {@code item_model} component
repaints our own stacks without touching the real sherds.

<b>What a sprite says.</b> Theme, level, and whether it is awake. Not
which enchantment - there are thirty-four of those, and eight glyphs is
already at the limit of what reads at sixteen pixels. The name carries
the enchantment; the stone carries the rest.

<b>The level is the sigil.</b> Each theme is an ordered list of strokes,
cheapest first: a level one wears two of them where a level five wears
them all. A tally of dots along the foot is a readout bolted to a
drawing; a mark that grows is what a level actually is.

<b>The cut exists whether or not it is lit.</b> An uncut rune carries
its theme's sigil as an empty groove. <i>Reversed:</i> the rule used to
be that every uncut rune looked the same whatever its theme, on the
grounds that a blank is a blank. Poetically true, factually wrong - an
uncut Efficiency IV and an uncut Smite IV take different fragments to
wake and go on different gear. Uncut means unpaid-for, not undecided,
and a drawer of twenty identical grey stones that are twenty different
items is simply bad.

<b>Five things make a relic rather than a cartoon</b>, and the first
drafts got all five wrong: a black keyline (almost nothing in Minecraft
is outlined in black - things are outlined in a dark tone of their own
material); saturation (a neon glyph on grey is a game UI, where a relic
is mineral pigment, which is ground rock and therefore muted); neutral
grey (nothing old is grey); smooth outlines (a relic is a *fragment*, so
the stones are polygons with straight fracture edges rather than rows,
which can only ever make ovals); and too few tones laid too evenly.

Inlay is light set into dark everywhere, which is what inlay is - and it
is also what keeps the two states apart. A dark pigment on a pale stone
looks exactly like an empty groove, which had excavation's uncut and its
level five rendering as the same picture.

No image library, like everything else in this pack.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PACK = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from build_models import write_png  # noqa: E402

SIZE = 16


def _fill(poly):
    """The pixels inside a polygon, by ray casting on pixel centres.

    <b>Spans gave smooth shapes and smooth is the problem.</b> Defining
    a stone row by row makes convex blobs - circles, ovals, rounded
    rectangles - because that is what is easy to type. A sherd is a
    fragment: straight fracture edges meeting at angles, asymmetric,
    and sometimes with a bite taken out of one side. Vertices give that
    for free, and a concave notch is just a vertex pointing inward.
    """
    pixels = set()
    for y in range(SIZE):
        for x in range(SIZE):
            px, py, inside = x + 0.5, y + 0.5, False
            for i in range(len(poly)):
                (ax, ay), (bx, by) = poly[i], poly[(i + 1) % len(poly)]
                if (ay > py) != (by > py) and \
                        px < ax + (py - ay) / (by - ay) * (bx - ax):
                    inside = not inside
            if inside:
                pixels.add((x, y))
    return pixels


# Every one of these is a broken piece, not a shape. No two share a
# proportion and none of them is symmetrical.
POLYGONS = {
    # An ore chunk, cleaved on four sides.
    "mining": [(6, 1), (11, 2), (13, 6), (12, 10), (8, 13), (4, 11),
               (2, 7), (3, 3)],
    # A cut sod, with a step bitten out of its right shoulder.
    "excavation": [(3, 3), (10, 2), (12, 5), (10, 6), (13, 8), (12, 12),
                   (5, 13), (2, 10)],
    # A split stave: tall, narrow, kinked where it broke.
    "timber": [(6, 0), (11, 2), (11, 7), (13, 9), (11, 15), (6, 15),
               (4, 10), (6, 6), (4, 3)],
    # A broad flat stone with one corner knocked off.
    "farming": [(2, 3), (9, 2), (14, 6), (13, 10), (8, 12), (2, 11),
                (1, 6)],
    # A flake of slate, pointed, notched on the way down.
    "fishing": [(8, 0), (13, 4), (12, 7), (14, 10), (9, 14), (4, 12),
                (3, 8), (5, 3)],
    # A long sliver, struck off something bigger.
    "projectile": [(9, 0), (13, 4), (11, 8), (12, 12), (8, 15), (4, 12),
                   (5, 7), (6, 2)],
    # A slab, broken clean across one diagonal.
    "melee": [(2, 5), (7, 2), (13, 4), (14, 9), (10, 13), (4, 12),
              (1, 9)],
    # A heavy block sat on its flat, chipped along the top.
    "mace": [(5, 3), (9, 2), (11, 5), (14, 7), (13, 12), (3, 12),
             (2, 8), (4, 6)],
}

BODIES = {name: _fill(poly) for name, poly in POLYGONS.items()}

FIELDS = {
    "mining": (4, 2),
    "excavation": (2, 4),
    "timber": (5, 4),
    "farming": (1, 3),
    "fishing": (4, 1),
    "projectile": (5, 1),
    "melee": (2, 3),
    "mace": (2, 3),
}

BASE_STROKES = 2
BASE_OVERRIDE = {"mace": 3}
SIGILS = {
    "mining": [((5, 0), (3, 3)), ((3, 3), (6, 5)), ((6, 5), (4, 8)),
               ((3, 3), (1, 2)), ((6, 5), (8, 4)), ((4, 8), (3, 10))],
    "excavation": [((0, 2), (3, 2)), ((6, 2), (9, 2)), ((4, 3), (4, 7)),
                   ((2, 5), (4, 8)), ((7, 5), (4, 8)), ((7, 3), (7, 7))],
    "timber": [((2, 11), (2, 5)), ((2, 5), (0, 1)), ((2, 5), (4, 2)),
               ((4, 2), (4, 0)), ((0, 8), (2, 8)), ((2, 3), (0, 3))],
    "farming": [((0, 0), (3, 3)), ((7, 0), (4, 3)), ((3, 3), (4, 6)),
                ((4, 6), (7, 4)), ((1, 5), (2, 7)), ((6, 6), (8, 7))],
    "fishing": [((0, 1), (3, 4)), ((3, 4), (0, 7)), ((4, 3), (7, 6)),
                ((7, 6), (4, 9)), ((1, 8), (3, 10)), ((4, 10), (6, 11))],
    "projectile": [((0, 11), (5, 2)), ((5, 2), (2, 3)), ((5, 2), (5, 5)),
                   ((0, 8), (2, 10)), ((2, 6), (4, 8)), ((0, 5), (1, 4))],
    "melee": [((6, 0), (2, 5)), ((8, 1), (4, 6)), ((10, 2), (6, 7)),
              ((4, 0), (0, 4)), ((8, 5), (4, 10)), ((2, 6), (0, 8))],
    "mace": [((3, 2), (6, 2)), ((2, 4), (7, 4)), ((3, 6), (6, 6)),
             ((4, 0), (4, 9)), ((0, 4), (9, 4)), ((1, 1), (8, 8)),
             ((8, 1), (1, 8))],
}

# <b>One clay for all eight was wrong too.</b> A shelf of relics is a
# shelf of different materials - basalt, red clay, slate, sandstone -
# and that is a whole channel of difference that costs no brightness.
# So every rune is its own stone, and its pigment is chosen against
# that stone rather than against one shared background: light on the
# dark ones, dark on the pale ones, so none of them needs saturation
# to be legible.
STONES = {
    "mining": (0x64, 0x5C, 0x70),       # violet basalt
    "excavation": (0x6B, 0x46, 0x33),   # fired clay, dark
    "timber": (0x6E, 0x7A, 0x60),       # mossed stone
    "farming": (0x6E, 0x5C, 0x3E),      # dark earth
    "fishing": (0x68, 0x7A, 0x86),      # blue slate
    "projectile": (0x5C, 0x5C, 0x5E),   # flint
    "melee": (0x6A, 0x62, 0x5E),        # iron-grey
    "mace": (0x5A, 0x56, 0x5A),         # dark granite
}

THEMES = {
    "mining": (0xB4, 0x9A, 0xD6),       # pale amethyst on dark
    "excavation": (0xD4, 0x96, 0x52),   # ochre seam
    "timber": (0xC4, 0xCE, 0xA4),       # sap, on dark
    "farming": (0xD8, 0xBE, 0x5E),      # wheat seam
    "fishing": (0xA4, 0xD4, 0xD0),      # verdigris on dark
    "projectile": (0xE2, 0xE4, 0xDE),   # bone seam
    "melee": (0xB8, 0x62, 0x4C),        # rust, warm against grey
    "mace": (0x7E, 0x9C, 0xC4),         # cold steel, storm light
}

CLEAR = (0, 0, 0, 0)


def mix(a, b, t):
    return tuple(round(x + (y - x) * t) for x, y in zip(a[:3], b[:3])) + (255,)


def grain(x, y, seed):
    """Deterministic surface noise. Old things are never one tone."""
    h = ((x // 2) * 73856093) ^ ((y // 2) * 19349663) ^ (seed * 83492791)
    return ((h >> 7) & 0xFF) / 255.0


def stroke(points, a, b):
    (x0, y0), (x1, y1) = a, b
    steps = max(abs(x1 - x0), abs(y1 - y0))
    for i in range(steps + 1):
        t = i / steps if steps else 0
        x, y = round(x0 + (x1 - x0) * t), round(y0 + (y1 - y0) * t)
        points.add((x, y))
        points.add((x + 1, y) if abs(y1 - y0) >= abs(x1 - x0) else (x, y + 1))


def tones(theme):
    """Five tones of one stone, plus a rim that is a dark tone of it
    rather than black - the keyline was the loudest cartoon tell."""
    base = STONES[theme] + (255,)
    return (mix(base, (255, 255, 255, 255), 0.24), base,
            mix(base, (0, 0, 0, 255), 0.18), mix(base, (0, 0, 0, 255), 0.40),
            mix(base, (0, 0, 0, 255), 0.66))


def draw(theme, level, lit=True):
    seed = sum(ord(c) for c in theme)
    STONE_HI, STONE, STONE_LO, STONE_DEEP, RIM = tones(theme)
    filled = BODIES[theme]
    px = [[CLEAR for _ in range(SIZE)] for _ in range(SIZE)]

    for (x, y) in filled:
        up, left = (x, y - 1) in filled, (x - 1, y) in filled
        down, right = (x, y + 1) in filled, (x + 1, y) in filled
        base = STONE_HI if (not up or not left) else (
            STONE_DEEP if (not down or not right) else STONE)
        # A dozen tones a shade apart, which is what weathering looks
        # like. One flat fill with a rim is what plastic looks like.
        n = grain(x, y, seed)
        if n < 0.22:
            base = mix(base, STONE_LO, 0.30)
        elif n > 0.80:
            base = mix(base, STONE_HI, 0.22)
        px[y][x] = base

    fx, fy = FIELDS[theme]
    glyph = set()
    base = BASE_OVERRIDE.get(theme, BASE_STROKES)
    for a, b in SIGILS[theme][:min(base + level - 1, len(SIGILS[theme]))]:
        stroke(glyph, (a[0] + fx, a[1] + fy), (b[0] + fx, b[1] + fy))
    glyph &= filled

    pigment = THEMES[theme] + (255,)
    # An impression, not a light: the near wall darkens, the far wall
    # catches a little, and the channel holds pigment or holds shade.
    for (x, y) in glyph:
        n = (x, y + 1)
        if n in filled and n not in glyph:
            px[n[1]][n[0]] = mix(px[n[1]][n[0]], STONE_HI, 0.5)
    for (x, y) in glyph:
        shade = mix(STONE_DEEP, RIM, 0.55)
        if lit:
            top = (x, y - 1) not in glyph
            px[y][x] = mix(pigment, (255, 255, 255, 255), 0.18) if top \
                else mix(pigment, STONE_DEEP, 0.2)
        else:
            px[y][x] = shade

    for (x, y) in filled:
        for (dx, dy) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if n not in filled and 0 <= n[0] < SIZE and 0 <= n[1] < SIZE:
                px[n[1]][n[0]] = RIM
    return px


# --- names, files, and the checks that keep them honest ---------------

THEME_ORDER = ["mining", "excavation", "timber", "farming",
               "fishing", "projectile", "melee", "mace"]
LEVELS = range(1, 6)


def sprite_name(theme, level, lit):
    """The id the plugin asks for.

    Spelled here because this file is what makes them, and a second
    spelling anywhere else is a silent missing texture."""
    return "rune_%s_%d%s" % (theme, level, "" if lit else "_uncut")


def check():
    """What a glance at a contact sheet will not catch.

    Three failures happened while drawing these, every one of them
    invisible until somebody stared at a grid: two levels of a theme
    rendering identically, a rune's lit and unlit states rendering
    identically, and a stroke placed where the stone's own silhouette
    clipped it away, so the level above it drew nothing new."""
    seen = {}
    for theme in THEME_ORDER:
        for level in LEVELS:
            for lit in (True, False):
                key = tuple(tuple(p) for row in draw(theme, level, lit)
                            for p in row)
                if key in seen:
                    raise SystemExit(
                        "two runes draw the same picture: %s and %s"
                        % (seen[key], sprite_name(theme, level, lit)))
                seen[key] = sprite_name(theme, level, lit)
    for theme in THEME_ORDER:
        fx, fy = FIELDS[theme]
        filled = BODIES[theme]
        for i, (a, b) in enumerate(SIGILS[theme]):
            pts = set()
            stroke(pts, (a[0] + fx, a[1] + fy), (b[0] + fx, b[1] + fy))
            lost = len(pts - filled)
            if lost > len(pts) * 0.34:
                raise SystemExit(
                    "%s stroke %d is %d of %d outside its own stone, so "
                    "the level it belongs to draws almost nothing"
                    % (theme, i + 1, lost, len(pts)))


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
        handle.write(chr(10))
    with open(os.path.join(items, "%s.json" % name), "w") as handle:
        json.dump({"model": {"type": "minecraft:model",
                             "model": "forever:item/%s" % name}},
                  handle, indent=2)
        handle.write(chr(10))


def main():
    check()
    made = 0
    for theme in THEME_ORDER:
        for level in LEVELS:
            for lit in (True, False):
                write(sprite_name(theme, level, lit),
                      draw(theme, level, lit))
                made += 1
    print("  %d rune sprites" % made)


if __name__ == "__main__":
    main()
