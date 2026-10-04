#!/usr/bin/env python3
"""
Builds the Forever resource pack's creature models and their textures.

Why this is generated rather than hand-written
----------------------------------------------
A Minecraft item model is a list of boxes, and every face of every box
carries UV coordinates pointing into a texture atlas. Written by hand
that is two files that have to agree about a rectangle each, for every
face of every box - and when they disagree the result is not an error,
it is a creature with a leg wearing part of its own ear. There is no way
to see that from here; it needs a client.

So both files come out of one description. Each box names a colour, this
script lays those colours out as flat swatches in the texture and points
every face of that box at its own swatch. The two cannot drift, because
neither is written down.

What it produces
----------------
    assets/forever/items/<name>.json          the item definition
    assets/forever/models/item/<name>.json    the geometry
    assets/forever/textures/item/<name>.png   the skin

Two JSON files, not one, and that is not a style choice. Since 1.21.4
the `minecraft:item_model` component points at an *item definition* in
`assets/<ns>/items/`, which then names a model in
`assets/<ns>/models/`. The first version of this pack wrote only the
model, so the component pointed at a file that did not exist and the
werewolf would have rendered as the missing-model cube. Checked against
the real 26.2 client jar rather than remembered.

Run it from the resourcepack directory:  python3 tools/build_models.py

The art is deliberately simple - solid-colour boxes, the shape doing the
work. It is a placeholder in the sense that somebody with Blockbench can
replace a model wholesale; it is not a placeholder in the sense of being
broken or unfinished, and a flat-shaded blocky werewolf is a perfectly
honest Minecraft creature.
"""

import json
import os
import struct
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
PACK = os.path.dirname(HERE)

# A model's coordinate space is 0..16 on each axis, and that cube is one
# block. Anything outside -16..32 is rejected by the client.
LOW, HIGH = -16, 32

# Every swatch is this many pixels square in the generated texture, which
# is plenty for a flat colour and keeps the file tiny.
SWATCH = 8


def box(name, colour, frm, to):
    """One cuboid: a name for the comment, a colour, and two corners."""
    return {"name": name, "colour": colour, "from": frm, "to": to}


# --- The werewolf ------------------------------------------------------------
#
# Bipedal, hunched, long-armed. Proportions are the whole of the
# character here: the head is pushed forward of the chest rather than
# sitting on top of it, the arms reach past the knees, and the legs are
# short. That reads as a thing that runs on two legs but would rather be
# on four, which is what a werewolf is.

# Black, and black is harder than it sounds. A creature in actual
# black is a silhouette: Minecraft shades every face of a cuboid
# differently, but it shades them by multiplying, and multiplying
# near-zero by anything is still near-zero - so a black model loses
# every edge and reads as a hole in the world rather than as a wolf.
#
# So: a very dark neutral with a blue cast rather than true black, and
# the separation between the tones widened to carry the shape where
# the shading no longer can. It reads black and it still has edges.
#
# The first pass at this was darker still and vanished at night - in
# daylight a crisp silhouette, after dusk a pair of floating eyes.
# These values are set so that the *darkest* face the client will draw
# - a north face at 0.6 of the base - is still above the background of
# an unlit arena. Picking the colour you want and letting the engine
# darken it is how you end up with a creature that only exists at noon.
FUR = (52, 52, 62)
FUR_DARK = (33, 33, 41)
# Lighter than the coat, not darker. An underbelly in the darker fur
# reads as a hole in the chest from the front, which is what the first
# render showed - and the problem is worse the darker the coat gets.
BELLY = (90, 90, 104)
MUZZLE = (68, 68, 80)
# Amber rather than red. Against brown fur red was the only thing that
# carried; against black it is muddy, and amber is both brighter and
# more lupine.
EYE = (255, 176, 32)
CLAW = (226, 222, 212)
# Streaks. Not pure white: against a near-black coat, white at full
# value is the brightest thing in a night arena and pulls the eye off
# the silhouette onto the stripes. A bone grey reads as white fur and
# stays part of the animal.
STREAK = (198, 196, 190)
# The axe. Gold pulled down from the item's own near-white yellow for
# the same reason the streaks are bone rather than white: at full value
# it is the brightest thing in a night arena and the eye goes to it
# instead of to the animal. This still reads unmistakably as gold.
GOLD = (236, 201, 90)
GOLD_DARK = (176, 142, 54)
HAFT = (104, 78, 48)

WEREWOLF = [
    # Torso: tilted forward by being deeper than it is wide.
    box("chest", FUR, [4, 14, 2], [12, 26, 9]),
    box("belly", BELLY, [5, 9, 3], [11, 15, 8]),
    # Head, forward of the chest rather than above it.
    box("head", FUR, [4.5, 23, -2], [11.5, 30, 4]),
    box("snout", MUZZLE, [6, 23.5, -6], [10, 27, -1]),
    box("nose", FUR_DARK, [6.5, 25, -7], [9.5, 27, -5.5]),
    # The ears top out at 32, which is the ceiling of the model space -
    # the generator refused an earlier version that reached 34, and the
    # client would have refused the whole model rather than the ear.
    box("ear_left", FUR_DARK, [4.5, 30, 0], [6.5, 32, 2]),
    box("ear_right", FUR_DARK, [9.5, 30, 0], [11.5, 32, 2]),
    box("eye_left", EYE, [5.5, 27, -2.4], [7, 28.5, -1.9]),
    box("eye_right", EYE, [9, 27, -2.4], [10.5, 28.5, -1.9]),
    # Arms, long enough to reach past the knee.
    box("arm_left", FUR, [0.5, 12, 3], [4, 25, 8]),
    box("arm_right", FUR, [12, 12, 3], [15.5, 25, 8]),
    box("claw_left", CLAW, [0.5, 10, 3.5], [4, 12, 7.5]),
    box("claw_right", CLAW, [12, 10, 3.5], [15.5, 12, 7.5]),
    # Legs, short and set back, digitigrade-ish.
    box("thigh_left", FUR, [4, 4, 4], [7.5, 14, 9]),
    box("thigh_right", FUR, [8.5, 4, 4], [12, 14, 9]),
    box("foot_left", FUR_DARK, [4, 0, 1], [7.5, 4, 8]),
    box("foot_right", FUR_DARK, [8.5, 0, 1], [12, 4, 8]),
    # Tail, low and heavy. Set at the base of the spine rather than
    # halfway up the back, which is where it sat first and read as a
    # second limb.
    box("tail", FUR_DARK, [6.5, 8, 8.5], [9.5, 14, 14]),

    # White streaks. Laid *over* the coat as thin slabs standing a
    # sixteenth proud of it, rather than cut into it - a box flush with
    # the surface it sits on makes the two faces fight for the same
    # pixels and flicker as the camera moves, which is a worse artefact
    # than any amount of plainness.
    #
    # Placed where a real animal's markings are rather than scattered:
    # a chest blaze, a stripe down the muzzle, a flash on each shoulder,
    # and a tipped tail. Asymmetry would read as damage, so they match.
    box("blaze", STREAK, [7, 15, 1.9], [9, 22, 2.4]),
    box("muzzle_stripe", STREAK, [7.25, 27, -6], [8.75, 27.5, -1]),
    box("shoulder_left", STREAK, [0.4, 20, 4], [1, 24, 7]),
    box("shoulder_right", STREAK, [15, 20, 4], [15.6, 24, 7]),
    box("tail_tip", STREAK, [6.5, 8, 13.4], [9.5, 12, 14.1]),

    # The golden axe, in the right fist.
    #
    # <b>Part of the model rather than an item in the mob's hand, and
    # that is the whole fix.</b> The boss used to really hold one - a
    # piglin brute spawns armed - and because the mob is invisible and
    # equipment is not, the axe hung in the air beside the werewolf
    # with nothing gripping it. It also quietly added six attack
    # damage, since a held weapon's damage adds to the attribute.
    #
    # Two other ways were available and are worse. Keeping the real
    # item means fighting the offset between a piglin brute's wrist and
    # this model's hand, which are different creatures at different
    # scales, forever. A second display entity carrying the item means
    # new sync code and a rotation problem: a display's transform
    # rotates about its own origin, so an axe placed at the hand would
    # pivot about the hand while the body pivots about its feet, and
    # the two would come apart on every lunge.
    #
    # As geometry it is simply welded to the animal: one entity, one
    # transform, locked through the lunge by construction. It costs the
    # real item's sprite, which was never going to match a model built
    # out of flat-shaded boxes anyway, and it costs the six damage -
    # deliberately, so the number in Bosses.java is the whole of this
    # boss's melee.
    #
    # Held head-up with the blade outward, which is a threat display
    # rather than a carry. Gripped at y=11, which is inside claw_right
    # (y 10-12), so the fist closes on the haft instead of near it.
    box("axe_haft", HAFT, [13.0, 6.5, 4.7], [14.6, 22, 6.3]),
    box("axe_collar", GOLD_DARK, [12.9, 18.8, 4.5], [14.7, 22.4, 6.5]),
    box("axe_blade", GOLD, [14.7, 18.0, 4.2], [17.4, 23.2, 6.8]),
    box("axe_edge", GOLD_DARK, [17.4, 18.6, 4.4], [17.9, 22.6, 6.6]),
]

CREATURES = {"werewolf": WEREWOLF}

FACES = ["north", "east", "south", "west", "up", "down"]


def write_png(path, width, height, pixels):
    """A minimal RGBA PNG, so the pack needs no image library to build."""
    raw = b"".join(
        b"\x00" + b"".join(struct.pack("BBBB", *pixels[y][x]) for x in range(width))
        for y in range(height)
    )

    def chunk(tag, data):
        body = tag + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body))

    header = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    with open(path, "wb") as out:
        out.write(b"\x89PNG\r\n\x1a\n")
        out.write(chunk(b"IHDR", header))
        out.write(chunk(b"IDAT", zlib.compress(raw, 9)))
        out.write(chunk(b"IEND", b""))


def build(name, boxes):
    colours = []
    for shape in boxes:
        if shape["colour"] not in colours:
            colours.append(shape["colour"])

    # One row of swatches. The texture is tiny, so there is no reason to
    # pack it cleverly and every reason to keep the arithmetic obvious.
    width = SWATCH * len(colours)
    height = SWATCH
    pixels = [[colours[x // SWATCH] + (255,) for x in range(width)]
              for _ in range(height)]

    elements = []
    for shape in boxes:
        index = colours.index(shape["colour"])
        # UVs are in sixteenths of the texture regardless of its real
        # size, so this converts pixels to that space.
        u0 = index * SWATCH * 16 / width
        u1 = (index + 1) * SWATCH * 16 / width
        # Inset by a hair. A face landing exactly on a swatch boundary
        # picks up its neighbour's colour along one edge when the client
        # filters the texture, which shows up as a seam.
        inset = (u1 - u0) * 0.15
        uv = [round(u0 + inset, 4), round(16 * 0.15, 4),
              round(u1 - inset, 4), round(16 * 0.85, 4)]
        for value in shape["from"] + shape["to"]:
            if not LOW <= value <= HIGH:
                raise SystemExit(
                    f"{name}: {shape['name']} has {value}, outside the model space "
                    f"({LOW}..{HIGH}); the client refuses the whole model")
        elements.append({
            "name": shape["name"],
            "from": shape["from"],
            "to": shape["to"],
            "faces": {face: {"uv": uv, "texture": "#skin"} for face in FACES},
        })

    model = {
        "credit": "Generated by tools/build_models.py - edit that, not this",
        "texture_size": [width, height],
        "textures": {"skin": f"forever:item/{name}", "particle": f"forever:item/{name}"},
        "elements": elements,
        "display": {
            # The display entity is spawned with the HEAD transform, so
            # this is the one that decides how it sits. Centred on the
            # model's own middle rather than on a block's corner.
            "head": {"translation": [0, 0, 0], "scale": [1, 1, 1]},
        },
    }

    # The item definition. What `minecraft:item_model` actually points
    # at since 1.21.4 - it names the model rather than being one.
    definition = {
        "model": {"type": "minecraft:model", "model": f"forever:item/{name}"},
    }

    items = os.path.join(PACK, "assets", "forever", "items")
    models = os.path.join(PACK, "assets", "forever", "models", "item")
    textures = os.path.join(PACK, "assets", "forever", "textures", "item")
    for directory in (items, models, textures):
        os.makedirs(directory, exist_ok=True)
    with open(os.path.join(items, f"{name}.json"), "w") as out:
        json.dump(definition, out, indent=2)
        out.write("\n")
    with open(os.path.join(models, f"{name}.json"), "w") as out:
        json.dump(model, out, indent=2)
        out.write("\n")
    write_png(os.path.join(textures, f"{name}.png"), width, height, pixels)
    print(f"  {name}: {len(elements)} boxes, {len(colours)} colours, {width}x{height}px")


def main():
    print("Building Forever creature models")
    for name, boxes in CREATURES.items():
        build(name, boxes)
    print("Done. Zip the pack with tools/pack.sh")


if __name__ == "__main__":
    main()
