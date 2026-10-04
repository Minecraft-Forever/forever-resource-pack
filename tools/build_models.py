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


def sprite(name, texture, frm, to):
    """
    A flat panel wearing a real texture rather than a palette swatch.

    <p>For the things a box cannot be. A golden axe built out of
    cuboids is a gold slab and a brown stick, and reads as neither at
    any distance; the actual item is a 16x16 sprite, and Minecraft
    itself draws a held item as that sprite with a little depth. A
    pack may reference vanilla textures, so this is the real axe
    rather than an impression of one.

    <p><b>The thin axis must be x</b>, and the y and z spans must each
    be 16, or the sprite is stretched. The UVs below are written for
    the east and west faces specifically.

    <p>Orientation, worked out from the default-UV table rather than
    guessed, because a mirrored axe is the kind of thing that is only
    visible in game. A face with no uv gets, for east,
    [16-z2, 16-y2, 16-z1, 16-y1] - so u runs toward -z, which on this
    model is forward, and v runs downward. The golden axe sprite has
    its head at the top right and its haft running to the bottom left,
    which therefore lands as head up-and-forward, haft down-and-back.
    That is a raised axe, which is what was wanted, so east takes the
    sprite unflipped. West's default runs the other way along z, so it
    takes a reversed u to show the same face from the other side
    rather than a mirror image.
    """
    return {"name": name, "sprite": texture, "from": frm, "to": to}


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
    # <b>The real item's texture, not boxes.</b> It was built out of
    # cuboids first and that was wrong twice over: a gold slab and a
    # brown stick do not read as an axe at any distance, and both were
    # placed *inside* the arm box (x 12-15.5), so the haft was buried
    # in the limb and only the head showed - as, in the words of the
    # bug report, "a yellow patch on the arm".
    #
    # So it is a flat panel wearing minecraft:item/golden_axe, which is
    # what a held item is anyway: Minecraft draws items in hands as the
    # sprite with a little depth. A pack may reference vanilla textures,
    # so this costs nothing and is the actual axe rather than an
    # impression of one.
    #
    # Why not a real item in the mob's hand, which is where it started:
    # an invisible mob still renders what it holds, so it hung in the
    # air beside the model, and a held weapon's attack damage adds to
    # the attribute, so it was silently worth six damage. Why not a
    # second display entity carrying the item: a display's transform
    # rotates about its own origin, so an axe at the hand would pivot
    # about the hand while the body pivots about its feet, and the two
    # would come apart on every lunge. As part of this model it is
    # welded to the animal - one entity, one transform.
    #
    # Placed just clear of the arm (x 15.6, outside its 15.5) so
    # nothing is buried this time, and sized 16x16 in z and y so the
    # sprite is not stretched. See sprite() for how the corners were
    # chosen to put the haft through the fist.
    sprite("axe", "minecraft:item/golden_axe",
           [15.6, 5, -6], [16.4, 21, 10]),
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


def panel(name, shape, sprites):
    """One flat sprite panel. See sprite() for the orientation."""
    frm, to = shape["from"], shape["to"]
    for axis, label in ((1, "y"), (2, "z")):
        span = to[axis] - frm[axis]
        if abs(span - 16) > 1e-6:
            raise SystemExit(
                f"{name}: {shape['name']} spans {span} in {label}, not 16, so the "
                f"sprite would be stretched")
    key = shape["name"]
    if (key, shape["sprite"]) not in sprites:
        sprites.append((key, shape["sprite"]))
    reference = f"#{key}"
    full = [0, 0, 16, 16]
    # u reversed on the west face so both sides show the same hand of
    # the axe rather than one being its mirror.
    mirrored = [16, 0, 0, 16]
    return {
        "name": shape["name"],
        "from": frm,
        "to": to,
        "faces": {
            "east": {"uv": full, "texture": reference},
            "west": {"uv": mirrored, "texture": reference},
            # The four edges are a fraction of a unit wide and would
            # show the palette texture's first swatch if left out.
            # Given a sliver of the sprite they are simply invisible.
            "north": {"uv": full, "texture": reference},
            "south": {"uv": full, "texture": reference},
            "up": {"uv": full, "texture": reference},
            "down": {"uv": full, "texture": reference},
        },
    }


def build(name, boxes):
    colours = []
    for shape in boxes:
        if "colour" in shape and shape["colour"] not in colours:
            colours.append(shape["colour"])

    # One row of swatches. The texture is tiny, so there is no reason to
    # pack it cleverly and every reason to keep the arithmetic obvious.
    width = SWATCH * len(colours)
    height = SWATCH
    pixels = [[colours[x // SWATCH] + (255,) for x in range(width)]
              for _ in range(height)]

    elements = []
    # Extra textures, one key per distinct sprite, in the order met.
    sprites = []
    for shape in boxes:
        for value in shape["from"] + shape["to"]:
            if not LOW <= value <= HIGH:
                raise SystemExit(
                    f"{name}: {shape['name']} has {value}, outside the model space "
                    f"({LOW}..{HIGH}); the client refuses the whole model")
        if "sprite" in shape:
            elements.append(panel(name, shape, sprites))
            continue
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
        elements.append({
            "name": shape["name"],
            "from": shape["from"],
            "to": shape["to"],
            "faces": {face: {"uv": uv, "texture": "#skin"} for face in FACES},
        })

    model = {
        "credit": "Generated by tools/build_models.py - edit that, not this",
        "texture_size": [width, height],
        "textures": dict(
            {"skin": f"forever:item/{name}", "particle": f"forever:item/{name}"},
            **{key: value for key, value in sprites}),
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
