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
# A shaded steel for the underside of the light fur. Three greys rather
# than two because the engine's own shading cannot separate two masses
# that touch: a forearm laid against a chest in one colour is one shape,
# whatever angle the faces are at.
PELT_DARK = (78, 87, 92)
# And a mid coat tone, for the same reason on the dark side. Limbs wear
# it so they read as limbs against the body rather than merging into it.
FUR_MID = (43, 43, 52)
# The inside of an open mouth. The one warm colour on the animal, and it
# is what makes a snarl read as a snarl rather than as a gap - a dark
# hole in a dark head is just a hole.
MAW = (74, 28, 30)
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
    # <b>Built as an animal, then given enough parts to stop being a
    # blob.</b> Two rebuilds: the first was a column of axis-aligned
    # cuboids, and rotation fixed the pose; this one is about the
    # masses, because a correctly posed animal made of six big boxes
    # is a correctly posed blob.
    #
    # Three things do the work, and none of them is more polygons for
    # their own sake:
    #
    # <b>A ragged outline.</b> A straight edge is the thing that reads
    # as a box from across an arena. Tufts on the ruff, elbows,
    # haunches and tail break every long edge the body has, and the
    # hackles down the spine break the one edge a hunched animal shows
    # most.
    #
    # <b>Tones that separate touching masses.</b> The engine shades by
    # face direction, so two parts that meet at the same angle in the
    # same colour are one shape however many boxes they are. Limbs
    # wear a mid coat tone and the light fur has a shaded grey, which
    # is what makes an arm read as an arm against a chest.
    #
    # <b>A face.</b> Brows over the eyes, a jaw that hangs open, teeth
    # in both of them and a dark red mouth behind. It is most of the
    # difference between a wolf's head and a grey box with eyes.

    # --- Legs, digitigrade: thigh forward, shin back, foot flat ------
    #
    # A wolf stands on its toes. What looks like a backwards knee is an
    # ankle, and the foot is the long bone between it and the ground.
    box("haunch_left", FUR, [3, 14, 2.5], [7.5, 21, 8.5], ("x", 22.5, [5.5, 20, 5.5])),
    box("haunch_right", FUR, [8.5, 14, 2.5], [13, 21, 8.5], ("x", 22.5, [10.5, 20, 5.5])),
    box("thigh_left", FUR_MID, [3.5, 11, 3], [7.5, 18, 8], ("x", 22.5, [5.5, 20, 5.5])),
    box("thigh_right", FUR_MID, [8.5, 11, 3], [12.5, 18, 8], ("x", 22.5, [10.5, 20, 5.5])),
    # A tuft at the back of each haunch, where a wolf's trousers are.
    box("haunch_tuft_left", FUR_DARK, [3.5, 15, 8], [7, 20, 10], ("x", 45, [5.5, 20, 8])),
    box("haunch_tuft_right", FUR_DARK, [9, 15, 8], [12.5, 20, 10], ("x", 45, [10.5, 20, 8])),
    box("shin_left", FUR_MID, [4, 4, 0], [7, 12, 4], ("x", -22.5, [5.5, 12, 2])),
    box("shin_right", FUR_MID, [9, 4, 0], [12, 12, 4], ("x", -22.5, [10.5, 12, 2])),
    # The hock, which is the joint that makes the Z legible.
    box("hock_left", FUR_DARK, [4.25, 10, 3.5], [6.75, 13, 5.5], ("x", -22.5, [5.5, 12, 2])),
    box("hock_right", FUR_DARK, [9.25, 10, 3.5], [11.75, 13, 5.5], ("x", -22.5, [10.5, 12, 2])),
    # Feet, split into three toes with a claw on each, because one box
    # with a pale cap on it is a boot.
    box("foot_left", FUR_DARK, [3.5, 0.75, -1.5], [7.5, 4, 4]),
    box("foot_right", FUR_DARK, [8.5, 0.75, -1.5], [12.5, 4, 4]),
    box("toe_left_0", FUR_MID, [3.6, 0, -4], [4.7, 2, -1], ("x", -22.5, [4.15, 2, -1])),
    box("toeclaw_left_0", CLAW, [3.75, 0, -5.5], [4.55, 1.4, -3.8], ("x", -22.5, [4.15, 2, -1])),
    box("toe_left_1", FUR_MID, [4.9, 0, -4], [6.0, 2, -1], ("x", -22.5, [5.45, 2, -1])),
    box("toeclaw_left_1", CLAW, [5.05, 0, -5.5], [5.85, 1.4, -3.8], ("x", -22.5, [5.45, 2, -1])),
    box("toe_left_2", FUR_MID, [6.2, 0, -4], [7.3, 2, -1], ("x", -22.5, [6.75, 2, -1])),
    box("toeclaw_left_2", CLAW, [6.35, 0, -5.5], [7.15, 1.4, -3.8], ("x", -22.5, [6.75, 2, -1])),
    box("toe_right_0", FUR_MID, [8.6, 0, -4], [9.7, 2, -1], ("x", -22.5, [9.15, 2, -1])),
    box("toeclaw_right_0", CLAW, [8.75, 0, -5.5], [9.55, 1.4, -3.8], ("x", -22.5, [9.15, 2, -1])),
    box("toe_right_1", FUR_MID, [9.9, 0, -4], [11.0, 2, -1], ("x", -22.5, [10.45, 2, -1])),
    box("toeclaw_right_1", CLAW, [10.05, 0, -5.5], [10.85, 1.4, -3.8], ("x", -22.5, [10.45, 2, -1])),
    box("toe_right_2", FUR_MID, [11.2, 0, -4], [12.3, 2, -1], ("x", -22.5, [11.75, 2, -1])),
    box("toeclaw_right_2", CLAW, [11.35, 0, -5.5], [12.15, 1.4, -3.8], ("x", -22.5, [11.75, 2, -1])),

    # --- Body: hips, a ribcage that tapers, a chest over its feet ----
    box("pelvis", FUR, [4, 16, 2.5], [12, 21, 8]),
    box("chest", FUR, [3, 20, 1], [13, 30, 8], ("x", -22.5, [8, 20, 6])),
    # The ribcage narrows where a chest meets a waist. Two boxes do
    # what one cannot: a taper.
    box("ribs", FUR_MID, [3.5, 20, 1.5], [12.5, 25, 7.5], ("x", -22.5, [8, 20, 6])),
    box("waist", FUR_MID, [4.5, 17.5, 2.5], [11.5, 21, 7]),
    box("belly", BELLY, [5, 17, 1.5], [11, 22, 6.5]),
    box("belly_shade", PELT_DARK, [5.25, 16.5, 2], [10.75, 18.5, 6]),
    # Pectorals, which is where the light fur starts on the reference.
    box("pec_left", PELT, [4.5, 23, 0.4], [7.6, 28, 2.4], ("x", -22.5, [8, 20, 6])),
    box("pec_right", PELT, [8.4, 23, 0.4], [11.5, 28, 2.4], ("x", -22.5, [8, 20, 6])),

    # --- The ruff, in tufts rather than as a collar ------------------
    #
    # A single slab around the neck is a scarf. Five pieces at
    # different heights, each standing proud of the chest, is fur.
    box("ruff", PELT, [3, 25, 1], [13, 30, 8.5], ("x", -22.5, [8, 20, 6])),
    box("ruff_shade", PELT_DARK, [3.2, 25, 1.2], [12.8, 26.8, 8.3], ("x", -22.5, [8, 20, 6])),
    box("ruff_tuft_0", PELT, [2.2, 25.5, 2.5], [4.6, 30.5, 7.5], ("x", -22.5, [8, 20, 6])),
    box("ruff_tuft_1", PELT, [11.4, 25.5, 2.5], [13.8, 30.5, 7.5], ("x", -22.5, [8, 20, 6])),
    box("ruff_tuft_2", PELT, [4.2, 29.5, 5.0], [7.0, 32.0, 8.8], ("x", -22.5, [8, 20, 6])),
    box("ruff_tuft_3", PELT, [9.0, 29.5, 5.0], [11.8, 32.0, 8.8], ("x", -22.5, [8, 20, 6])),
    box("ruff_tuft_4", PELT, [6.6, 30.0, 2.0], [9.4, 32.0, 6.0], ("x", -22.5, [8, 20, 6])),
    # Hackles: the raised ridge down the spine of an animal that has
    # already decided about you. Uneven on purpose - a row of matched
    # spikes is a stegosaurus.
    box("hackle_0", FUR_DARK, [7, 29.5, 3.0], [9, 31.5, 4.2], ("x", -22.5, [8, 20, 6])),
    box("hackle_1", FUR_DARK, [7, 29.5, 4.6], [9, 32.0, 5.8], ("x", -22.5, [8, 20, 6])),
    box("hackle_2", FUR_DARK, [7, 29.0, 6.2], [9, 31.0, 7.4], ("x", -22.5, [8, 20, 6])),

    # --- Head: brows, a tapering muzzle, and an open mouth -----------
    box("neck", FUR_MID, [5.5, 26, -1], [10.5, 30, 3], ("x", -22.5, [8, 20, 6])),
    box("head", FUR, [4.5, 24, -6], [11.5, 30.5, 1], ("x", -22.5, [8, 27, -2])),
    # A brow ridge over each eye, which is what makes a wolf look like
    # it means it. The eyes sit under them rather than on a flat face.
    box("brow_left", FUR_DARK, [4.7, 29.3, -6.6], [6.6, 30.4, -3.5], ("x", -22.5, [8, 27, -2])),
    box("brow_right", FUR_DARK, [9.4, 29.3, -6.6], [11.3, 30.4, -3.5], ("x", -22.5, [8, 27, -2])),
    box("eye_left", EYE, [4.9, 27.8, -6.9], [6.3, 29.3, -6.1], ("x", -22.5, [8, 27, -2])),
    box("eye_right", EYE, [9.7, 27.8, -6.9], [11.1, 29.3, -6.1], ("x", -22.5, [8, 27, -2])),
    box("cheek_left", PELT, [4.6, 25, -6.4], [5.6, 28, -3.5], ("x", -22.5, [8, 27, -2])),
    box("cheek_right", PELT, [10.4, 25, -6.4], [11.4, 28, -3.5], ("x", -22.5, [8, 27, -2])),
    # The upper jaw in two pieces, because a tapering snout is the one
    # shape a single box cannot make.
    box("muzzle", FUR_MID, [6.4, 25.5, -10], [9.6, 28.4, -5], ("x", -22.5, [8, 27, -2])),
    box("muzzle_tip", FUR_MID, [6.9, 25.8, -12.5], [9.1, 27.6, -9.5], ("x", -22.5, [8, 27, -2])),
    box("nose", FUR_DARK, [7.1, 26.5, -13.4], [8.9, 27.8, -12], ("x", -22.5, [8, 27, -2])),
    # The mouth. A dark hole in a dark head is a hole; a red one with
    # teeth in front of it is a snarl.
    box("maw", MAW, [6.7, 24.6, -11.5], [9.3, 25.8, -5.5], ("x", -22.5, [8, 27, -2])),
    # Upper teeth hang from the muzzle; lower teeth ride the jaw, which
    # is the head's own tilt and twenty-two degrees more of it - one
    # element takes one rotation, so an open mouth is a steeper angle
    # about the same pivot rather than a second joint.
    box("tooth_upper_0", CLAW, [6.85, 24.5, -11.6], [6.95, 25.9, -11.0], ("x", -22.5, [8, 27, -2])),
    box("tooth_upper_1", CLAW, [7.47, 24.5, -11.5], [7.8, 25.9, -10.9], ("x", -22.5, [8, 27, -2])),
    box("tooth_upper_2", CLAW, [8.09, 24.5, -11.4], [8.65, 25.9, -10.8], ("x", -22.5, [8, 27, -2])),
    box("tooth_upper_3", CLAW, [8.71, 24.5, -11.3], [9.5, 25.9, -10.7], ("x", -22.5, [8, 27, -2])),
    box("fang_upper_left", CLAW, [6.75, 23.6, -11.2], [7.0, 25.9, -10.4], ("x", -22.5, [8, 27, -2])),
    box("fang_upper_right", CLAW, [8.7, 23.6, -11.2], [9.7, 25.9, -10.4], ("x", -22.5, [8, 27, -2])),
    box("jaw", FUR_MID, [6.7, 23.2, -11.5], [9.3, 25.4, -5], ("x", -45, [8, 27, -2])),
    box("chin", PELT_DARK, [6.9, 23.4, -11.2], [9.1, 24.4, -8], ("x", -45, [8, 27, -2])),
    box("tooth_lower_0", CLAW, [6.9, 25.2, -11.2], [7.0, 26.4, -10.6], ("x", -45, [8, 27, -2])),
    box("tooth_lower_1", CLAW, [7.5, 25.2, -11.1], [7.8, 26.4, -10.5], ("x", -45, [8, 27, -2])),
    box("tooth_lower_2", CLAW, [8.1, 25.2, -11.0], [8.6, 26.4, -10.4], ("x", -45, [8, 27, -2])),
    box("tooth_lower_3", CLAW, [8.7, 25.2, -10.9], [9.4, 26.4, -10.3], ("x", -45, [8, 27, -2])),
    # Ears back and low: an animal mid-decision, not a dog being told.
    box("ear_left", FUR_DARK, [4.75, 30, 0], [7.0, 32, 2.5], ("x", -22.5, [8, 27, -2])),
    box("ear_right", FUR_DARK, [9.0, 30, 0], [11.25, 32, 2.5], ("x", -22.5, [8, 27, -2])),
    box("ear_inner_left", FUR_MID, [5.1, 30.1, -0.4], [6.65, 31.4, 0.2], ("x", -22.5, [8, 27, -2])),
    box("ear_inner_right", FUR_MID, [9.35, 30.1, -0.4], [10.9, 31.4, 0.2], ("x", -22.5, [8, 27, -2])),

    # --- Arms: two bones, a shoulder on top, claws on the end --------
    box("deltoid_left", FUR, [0.8, 24, 2], [4.6, 29, 8], ("x", -22.5, [8, 20, 6])),
    box("deltoid_right", FUR, [11.4, 24, 2], [15.2, 29, 8], ("x", -22.5, [8, 20, 6])),
    box("arm_left", FUR_MID, [0.5, 19, 2.5], [4, 28, 7.5], ("x", 22.5, [2.25, 28, 5])),
    box("arm_right", FUR_MID, [12, 19, 2.5], [15.5, 28, 7.5], ("x", 22.5, [13.75, 28, 5])),
    # Elbow tufts, pointing back the way the arm came.
    box("elbow_left", FUR_DARK, [0.4, 19, 6.5], [3.6, 22.5, 9], ("x", 45, [2, 20, 6])),
    box("elbow_right", FUR_DARK, [12.4, 19, 6.5], [15.6, 22.5, 9], ("x", 45, [14, 20, 6])),
    box("forearm_left", FUR, [0, 11, 0.5], [3.5, 20, 5.5], ("x", -22.5, [1.75, 20, 3])),
    box("forearm_right", FUR, [12.5, 11, 0.5], [16, 20, 5.5], ("x", -22.5, [14.25, 20, 3])),
    box("hand_left", FUR_DARK, [0, 8, 0], [3.5, 11.5, 5]),
    box("hand_right", FUR_DARK, [12.5, 8, 0], [16, 11.5, 5]),
    # Three claws a hand, raked forward and each with a dark knuckle
    # behind it so they read as fingers rather than as a comb.
    box("knuckle_left_0", FUR_MID, [0.1, 7.5, -0.5], [1.1, 9.5, 1.5]),
    box("claw_left_0", CLAW, [0.1, 4.5, -1.5], [1.05, 9, 2.5], ("x", 22.5, [0.57, 9, 1])),
    box("knuckle_left_1", FUR_MID, [1.3, 7.5, -0.5], [2.3, 9.5, 1.5]),
    box("claw_left_1", CLAW, [1.3, 4.5, -1.5], [2.25, 9, 2.5], ("x", 22.5, [1.77, 9, 1])),
    box("knuckle_left_2", FUR_MID, [2.5, 7.5, -0.5], [3.5, 9.5, 1.5]),
    box("claw_left_2", CLAW, [2.5, 4.5, -1.5], [3.45, 9, 2.5], ("x", 22.5, [2.97, 9, 1])),
    box("knuckle_right_0", FUR_MID, [12.6, 7.5, -0.5], [13.6, 9.5, 1.5]),
    box("claw_right_0", CLAW, [12.6, 4.5, -1.5], [13.55, 9, 2.5], ("x", 22.5, [13.07, 9, 1])),
    box("knuckle_right_1", FUR_MID, [13.8, 7.5, -0.5], [14.8, 9.5, 1.5]),
    box("claw_right_1", CLAW, [13.8, 4.5, -1.5], [14.75, 9, 2.5], ("x", 22.5, [14.27, 9, 1])),
    box("knuckle_right_2", FUR_MID, [15.0, 7.5, -0.5], [16.0, 9.5, 1.5]),
    box("claw_right_2", CLAW, [15.0, 4.5, -1.5], [15.95, 9, 2.5], ("x", 22.5, [15.47, 9, 1])),

    # --- Tail: three falling segments, tufted ------------------------
    box("tail", FUR_DARK, [6.3, 14, 7], [9.7, 19, 12], ("x", 22.5, [8, 19, 8])),
    box("tail_mid", FUR_MID, [6.6, 11.5, 10.5], [9.4, 16, 14.5], ("x", 45, [8, 15, 11])),
    box("tail_tip", FUR_DARK, [6.9, 8.5, 13], [9.1, 12.5, 16.5], ("x", 45, [8, 12, 13])),
    box("tail_tuft", PELT_LIT, [6.9, 8.6, 15.5], [9.1, 12, 16.8], ("x", 45, [8, 12, 13])),

    # --- The light fur, laid proud of the coat -----------------------
    #
    # Each piece carries the rotation of the part it sits on, or it
    # drifts off as the body leans. The reference has no white on it
    # anywhere but the claws and the teeth, so what looks like markings
    # is this same grey catching the light.
    box("blaze", PELT_LIT, [6.6, 20, 0.3], [9.4, 26, 1.2], ("x", -22.5, [8, 20, 6])),
    box("muzzle_stripe", PELT_LIT, [7, 28.3, -12.2], [9, 29.0, -5.5], ("x", -22.5, [8, 27, -2])),
    box("shoulder_left", PELT_LIT, [0.5, 24.5, 3.5], [1.1, 28.5, 7.5], ("x", -22.5, [8, 20, 6])),
    box("shoulder_right", PELT_LIT, [14.9, 24.5, 3.5], [15.5, 28.5, 7.5], ("x", -22.5, [8, 20, 6])),
    box("pale_left", PELT_LIT, [-0.2, 12, 1.5], [0.4, 18, 5], ("x", -22.5, [1.75, 20, 3])),
    box("pale_right", PELT_LIT, [15.6, 12, 1.5], [16.2, 18, 5], ("x", -22.5, [14.25, 20, 3])),

    # The golden axe, in the right fist. See sprite() for why this is a
    # panel wearing the real item texture rather than boxes.
    sprite("axe", "minecraft:item/golden_axe",
           [16.3, 1, -9], [17.1, 17, 7]),
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
