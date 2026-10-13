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


def box(name, colour, frm, to, rot=None):
    """
    One cuboid: a name for the comment, a colour, and two corners.

    <p>{@code rot} is (axis, angle, origin), and it is the difference
    between an animal and a stack of crates. Minecraft allows a single
    axis per element and only five angles - 0, +/-22.5, +/-45 - which is
    exactly enough to bend a leg at the hock, lean a spine over its feet
    and rake a set of claws forward, and not nearly enough to be subtle
    with. Everything here uses the x axis, which is the one that tilts a
    thing forward and back.

    <p>The sign is worth stating because it is easy to get backwards: a
    <b>negative</b> angle carries "up" towards "forward" and "forward"
    towards "down", so -22.5 on the chest is a hunch and -22.5 on the
    head is a lowered muzzle.
    """
    shape = {"name": name, "colour": colour, "from": frm, "to": to}
    if rot is not None:
        axis, angle, origin = rot
        shape["rotation"] = {"axis": axis, "angle": angle, "origin": origin}
    return shape


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
# The coat reads black by comparison, not by being black.
#
# <b>Reversed: the pelt was a dark blue-grey and the markings were white
# fur.</b> The reference art it is drawn from is two tones and nothing
# else - a near-black coat and a cool steel grey across the muzzle,
# chest, shoulders and forearms - and the way to get that out of a
# renderer that multiplies every face is to widen the gap rather than
# to chase the black. The coat stays exactly where it was, because the
# note above is the scar of a version that went darker and vanished
# after dusk; the light tone comes up instead, and against #677276 a
# (52, 52, 62) coat reads as black at any distance.
#
# Straight off the reference, which is one flat grey wherever the light
# falls.
PELT = (103, 114, 118)
# Half a step brighter, for the panels that stand proud of the coat, so
# a lit shoulder is a lit shoulder and not a patch of belly that has
# wandered. Still nowhere near white - see the note the streaks left
# behind: at full value a marking is the brightest thing in a night
# arena and pulls the eye off the silhouette.
PELT_LIT = (126, 137, 142)
# Lighter than the coat, not darker. An underbelly in the darker fur
# reads as a hole in the chest from the front, which is what the first
# render showed - and the problem is worse the darker the coat gets.
BELLY = PELT
MUZZLE = PELT
# Red, and it was amber. <i>Reversed, and the reason amber won is still
# true, which is why this is not the reference's crimson.</i> Red at the
# value a painting uses is the darkest thing on a near-black animal and
# turns to mud; the fix is to keep the hue and take the value up until
# it carries. This is about as dark as a red can be and still read as
# two lit eyes across an arena at night.
EYE = (240, 48, 48)
# Claws and teeth, which the reference draws in stark white and which
# are small enough to afford it - the rule about white pulling the eye
# was about markings covering half an animal.
CLAW = (236, 234, 228)

WEREWOLF = [
    # <b>Rebuilt as an animal rather than as a stack of boxes.</b> The
    # first pass was a column of cuboids with a head on it, which is
    # what every axis-aligned model is: it read as a Minecraft mob,
    # which was the point, and not as a werewolf, which was also the
    # point. Elements can rotate, and five angles on one axis turns out
    # to be enough for the three things that carry an animal - a spine
    # leaning out over its feet, legs that bend twice, and a muzzle
    # that points at you.
    #
    # The leg is the whole trick. A wolf stands on its toes: what looks
    # like a backwards knee is an ankle, and the foot is the long bone
    # between it and the ground. Thigh forward, shin back, foot flat -
    # a Z rather than a post - and a thing standing like that looks
    # like it is about to move even when it is still.

    # Legs, digitigrade, built from the hip down.
    box("thigh_left", FUR, [3.5, 11, 3], [7.5, 20, 8], ("x", 22.5, [5.5, 20, 5.5])),
    box("thigh_right", FUR, [8.5, 11, 3], [12.5, 20, 8], ("x", 22.5, [10.5, 20, 5.5])),
    box("shin_left", FUR, [4, 4, 0], [7, 12, 4], ("x", -22.5, [5.5, 12, 2])),
    box("shin_right", FUR, [9, 4, 0], [12, 12, 4], ("x", -22.5, [10.5, 12, 2])),
    # Long feet, toes forward: the part a digitigrade animal stands on.
    box("foot_left", FUR_DARK, [3.5, 0, -4], [7.5, 4, 4]),
    box("foot_right", FUR_DARK, [8.5, 0, -4], [12.5, 4, 4]),

    # Hips, and a deep chest that narrows to them, leaning forward.
    box("pelvis", FUR, [4, 16, 2.5], [12, 21, 8]),
    box("chest", FUR, [3, 20, 1], [13, 30, 8], ("x", -22.5, [8, 20, 6])),
    box("belly", BELLY, [4.5, 17, 2], [11.5, 22, 7]),
    # The ruff: a heavy collar where the neck meets the shoulders,
    # which is most of why a drawn werewolf reads as a wolf wearing a
    # man rather than a man wearing a wolf's head. Wider than the chest
    # on every side so it is a collar and not a stripe, and never flush
    # with it - two faces in one plane fight for the same pixels and
    # flicker as the camera moves.
    box("ruff", PELT, [2.5, 25, 0.5], [13.5, 30.5, 8.5], ("x", -22.5, [8, 20, 6])),

    # Head, carried forward of the shoulders and tipped down, which is
    # where a wolf carries one and is the opposite of where a player
    # model does.
    box("head", FUR, [4.5, 24, -6], [11.5, 30.5, 1], ("x", -22.5, [8, 27, -2])),
    # A muzzle in two pieces, because a tapering snout is the one shape
    # a single box cannot make.
    box("muzzle", MUZZLE, [5.5, 24.5, -10], [10.5, 28.5, -5], ("x", -22.5, [8, 27, -2])),
    box("muzzle_tip", MUZZLE, [6.25, 24.75, -12.5], [9.75, 27.5, -9.5], ("x", -22.5, [8, 27, -2])),
    box("nose", FUR_DARK, [6.75, 25.75, -13.5], [9.25, 27.5, -12], ("x", -22.5, [8, 27, -2])),
    # Ears back and low rather than up and alert: an animal that has
    # already decided about you.
    box("ear_left", FUR_DARK, [4.75, 30, 0], [7, 32, 2.5], ("x", -22.5, [8, 27, -2])),
    box("ear_right", FUR_DARK, [9, 30, 0], [11.25, 32, 2.5], ("x", -22.5, [8, 27, -2])),
    box("eye_left", EYE, [5.75, 27.5, -6.4], [7.25, 29, -5.9], ("x", -22.5, [8, 27, -2])),
    box("eye_right", EYE, [8.75, 27.5, -6.4], [10.25, 29, -5.9], ("x", -22.5, [8, 27, -2])),

    # Arms in two bones, reaching forward and down. Long enough that the
    # hands hang below the knee, which is the proportion that says this
    # would rather be on four legs.
    box("arm_left", FUR, [0.5, 19, 2.5], [4, 28, 7.5], ("x", 22.5, [2.25, 28, 5])),
    box("arm_right", FUR, [12, 19, 2.5], [15.5, 28, 7.5], ("x", 22.5, [13.75, 28, 5])),
    box("forearm_left", FUR, [0, 11, 0.5], [3.5, 20, 5.5], ("x", -22.5, [1.75, 20, 3])),
    box("forearm_right", FUR, [12.5, 11, 0.5], [16, 20, 5.5], ("x", -22.5, [14.25, 20, 3])),
    box("hand_left", FUR_DARK, [0, 8, 0], [3.5, 11.5, 5]),
    box("hand_right", FUR_DARK, [12.5, 8, 0], [16, 11.5, 5]),
    # Three claws a hand, raked forward. One pale block on the end of an
    # arm reads as a glove; three that hang below it and point the way
    # the animal is going read as the second thing you look at after the
    # eyes, which is where the reference puts them.
    box("claw_left_0", CLAW, [0.1, 4.5, -1], [1.05, 9, 2.5], ("x", 22.5, [0.57, 9, 1])),
    box("claw_left_1", CLAW, [1.3, 4.5, -1], [2.25, 9, 2.5], ("x", 22.5, [1.77, 9, 1])),
    box("claw_left_2", CLAW, [2.5, 4.5, -1], [3.45, 9, 2.5], ("x", 22.5, [2.97, 9, 1])),
    box("claw_right_0", CLAW, [12.6, 4.5, -1], [13.55, 9, 2.5], ("x", 22.5, [13.07, 9, 1])),
    box("claw_right_1", CLAW, [13.8, 4.5, -1], [14.75, 9, 2.5], ("x", 22.5, [14.27, 9, 1])),
    box("claw_right_2", CLAW, [15.0, 4.5, -1], [15.95, 9, 2.5], ("x", 22.5, [15.47, 9, 1])),

    # A tail in two falling segments. One box reads as a plank; the bend
    # is what makes it hang.
    box("tail", FUR_DARK, [6.5, 14, 7], [9.5, 19, 12], ("x", 22.5, [8, 19, 8])),
    box("tail_tip", FUR_DARK, [7, 10, 11], [9, 15, 15], ("x", 45, [8, 15, 11])),

    # The light fur. Laid over the coat as thin slabs standing proud of
    # it rather than cut into it, and each one carries the rotation of
    # the part it sits on or it drifts off as the body leans.
    #
    # <i>These were white streaks.</i> The reference has no white on it
    # anywhere but the claws and the teeth; what looks like markings is
    # the same steel grey as the belly catching the light, so that is
    # what they are now. Asymmetry would read as damage, so they match.
    box("blaze", PELT_LIT, [6.5, 21, 0.4], [9.5, 29, 1.1], ("x", -22.5, [8, 20, 6])),
    box("muzzle_stripe", PELT_LIT, [7, 28.5, -12], [9, 29.1, -5], ("x", -22.5, [8, 27, -2])),
    box("shoulder_left", PELT_LIT, [0.3, 22, 3.5], [0.9, 27, 7], ("x", 22.5, [2.25, 28, 5])),
    box("shoulder_right", PELT_LIT, [15.1, 22, 3.5], [15.7, 27, 7], ("x", 22.5, [13.75, 28, 5])),
    box("pale_left", PELT_LIT, [-0.2, 12, 1.5], [0.4, 18, 5], ("x", -22.5, [1.75, 20, 3])),
    box("pale_right", PELT_LIT, [15.6, 12, 1.5], [16.2, 18, 5], ("x", -22.5, [14.25, 20, 3])),
    box("tail_pale", PELT_LIT, [7, 10, 14.4], [9, 14, 15.1], ("x", 45, [8, 15, 11])),

    # The golden axe, in the right fist. See sprite() for why this is a
    # panel wearing the real item texture rather than boxes.
    #
    # Moved out with the hand: the fist is lower and further forward
    # than it was, and an axe left at the old shoulder height would be
    # held by nothing.
    sprite("axe", "minecraft:item/golden_axe",
           [16.1, 1, -9], [16.9, 17, 7]),
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
        if "rotation" in shape:
            angle = shape["rotation"]["angle"]
            if angle not in (-45, -22.5, 0, 22.5, 45):
                raise SystemExit(
                    f"{name}: {shape['name']} is rotated {angle}, and the client "
                    f"takes only -45, -22.5, 0, 22.5 and 45")
            if shape["rotation"]["axis"] not in ("x", "y", "z"):
                raise SystemExit(f"{name}: {shape['name']} has no real axis")
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
        element = {
            "name": shape["name"],
            "from": shape["from"],
            "to": shape["to"],
            "faces": {face: {"uv": uv, "texture": "#skin"} for face in FACES},
        }
        if "rotation" in shape:
            element["rotation"] = shape["rotation"]
        elements.append(element)

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
