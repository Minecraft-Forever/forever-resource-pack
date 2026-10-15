"""
Sprites for the twenty-five custom fish, eight of which are not fish.

<b>The band is a promise about the shape.</b> Every earlier version
drew all of them with one vocabulary - body, fins, scales, a gill line,
an eye - and then tried to carry the rarity with the palette. It cannot
be carried that way: a player holding one fish has no swatch to compare
it against, so a mythic read as a differently coloured epic, and the
whole set read as one band in four colours. Which it nearly was - ten
of the eighteen then in the set were an ordinary fish with one small
quirk, called epic.

So the ladder is in the silhouette now:

  * <b>rare</b> is an ordinary catch. Small fins, no glow, one quirk.
  * <b>epic</b> has something on it that no fish has - a lantern on a
    stalk, a ring of rasping teeth where the jaw should be, a bell full
    of nothing.
  * <b>legendary</b> is not an ordinary animal. Open jaws, a hole
    straight through, a shape not drawn side-on at all. Lit from
    inside, inside one ring of glow.
  * <b>mythic</b> has geometry that cannot hold together: light with
    nothing holding it up, sparks trailing behind nothing. Two rings.

<b>And then a second reversal, for a second report that was exact: the
majority follow the same formula.</b> They did, and it was a drawing
problem rather than a naming one. fishdraw.Fish grows a body along a
curved spine, puts a tail at one end and fins down the sides, which is
the right machine for a dace and the only machine there was - so
eighteen of the twenty-four came out as the same animal in different
colours, and no amount of renaming or recolouring was going to change
that.

The fix went into the engine first (see "bodies that are not grown on a
spine" in fishdraw.py: a superellipse, a tapered limb, a pincer, a
radial spread, a rim of tentacles, an eye that needs no spine), and
then eight of the plainest fish were replaced with things built out of
it: a crab, a prawn, a scallop and a starfish at rare, a jellyfish at
epic, a shark and a manta ray at legendary, and a kraken at mythic.
Which fish went is recorded in each replacement's own docstring.

<b>Then the Worldscale went and the serpent came back.</b> The plate
was deliberately not a creature, and a shape with no eye and no limbs
turns out to have nothing to be mythical about; the Zaratan - the
island-turtle - keeps what it was reaching for. The Krakenspawn is
crimson rather than blue, because two deep-blue mythics side by side
read as one however different the outlines are.

<b>And the serpent came back, built the other way round.</b> The
Leviathan Spawn was the first thing dropped, and it was the right
thing to drop; what was wrong was the drawing, not the idea. The
Leviathan that replaces it carries its rarity in the path rather than
the parts - a body long enough to double back on itself - and that
took a band slot, so the Starfall Koi drops to legendary and the
Stormtail drops to epic. Both read as those bands anyway: the koi is
a fish with sparks on it and the stormtail is a fish with a lightning
tail, and neither has geometry that cannot hold together.

<b>And the whole set went blockier without getting smaller.</b>
Drawing at a smaller grid is the obvious way and it is wrong twice
over: sixteen could not hold a jaw, and halving the grid halves the
silhouette too. That was measured rather than assumed - snapping the
whole sprite to a two-pixel grid, border included, turns the
shorecrab's claws into stumps and fuses the kraken's arms into a
skirt.

What reads as rendered is texture and tone. So: three tones rather
than five, no diamond scale lattice and no lateral line (both passes
deleted from the engine), a nearly black border rather than a tinted
one, and `fishdraw.Fish.chunk` quantising body and fin fills onto a
2x2 grid while the marks, the eye and the glow stay per-pixel.
Flattening the fins also erases their rays, which is why no maker had
to stop asking for them.

A resource pack is not held to vanilla's sixteen pixels - item textures
may be any power of two, which is what the 32x packs people have run
for years are - and these are thirty-two square. Sixteen is about forty
pixels of fish once the margin is gone, which is not enough for a jaw;
sixty-four stopped looking like Minecraft.

This file is the twenty-five descriptions. fishdraw.py is the engine,
and the module docstring there covers the shading, the outline (also a
reversal: the sixteen pixel set deliberately had none) and why each
piece is drawn the way it is.

Generated rather than stored as finished PNGs for two reasons. A
mismatched id renders as the missing-model cube with nothing on screen
to explain it, so the build cross-checks every id against Fish.java.
And the pack is served from a public repository, which redistributes
whatever is in it; this is unambiguously ours.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from build_models import write_png  # noqa: E402
import fishdraw as fd  # noqa: E402

PACK = os.path.dirname(HERE)
SIZE = fd.SIZE


def rgb(hexcode):
    value = int(hexcode, 16)
    return (value >> 16 & 255, value >> 8 & 255, value & 255)


def pal(outline, shadow, body, highlight, fin, mark, glow=None):
    return {"o": rgb(outline), "s": rgb(shadow), "b": rgb(body),
            "h": rgb(highlight), "f": rgb(fin), "m": rgb(mark),
            "g": rgb(glow or mark)}


#: Cancels the global body depth, for the things that are meant to be
#: thin.
#:
#: <b>A deeper body is right for a fish and wrong for a snake.</b>
#: fishdraw.GIRTH lifted the whole set because the whole set was
#: thinner than anything on a real sheet - but an eel, a lamprey and
#: the two serpents read on the <em>gaps</em>: a coil is a coil because
#: you can see through the middle of it, and humps are humps because
#: there is water between them. Fattening those closed the holes and
#: turned both serpents into sausages. So they opt out, by name.
SLENDER = 1.0 / fd.GIRTH


#: <b>Extra lean applied to every spined body, in degrees.</b>
#: Decoded from the vanilla textures, cod, salmon and tropical fish are
#: all drawn on a roughly 45-degree diagonal - head at the bottom left,
#: tail at the top right - and that is not a stylistic flourish, it is
#: how a long fish gets a nearly square bounding box. Vanilla's cod is
#: 13x14 in a 16x16 tile.
#:
#: Ours sat at about 22 degrees and came out 14 wide by 10 tall: width
#: already against the one-pixel margin while four rows of tile stayed
#: empty, and `build` cannot grow a sprite whose widest axis is already
#: at the limit. Measured, the shapes were never the problem - density
#: inside their own bounding box was 51% against vanilla's 51-53%. The
#: boxes were just the wrong shape.
#:
#: Swept at 0, -8, -14, -20, -26 and -32 degrees against the whole set.
#: -14 is the peak: fill 33.4% -> 35.3% and the bounding box 66% -> 70%
#: of the tile, against vanilla's 71%. Past it the curve flattens and
#: then falls back, because a steeper lean starts aiming tails and
#: dorsal tips into the corners and `build` has to shrink the body to
#: keep them inside. Density inside the box holds at 50% throughout,
#: which is the check that this is buying box shape and not just
#: spreading the same fish thinner.
TILT = -14.0


def _lean(point):
    """Rotate a spine control point about the middle of the design grid."""
    if not TILT:
        return point
    angle = math.radians(TILT)
    x, y = point[0] - 32.0, point[1] - 32.0
    return (32.0 + x * math.cos(angle) - y * math.sin(angle),
            32.0 + x * math.sin(angle) + y * math.cos(angle))


def shaped(head, bend, tail, back, belly, zoom=None, nudge=(0.0, 0.0),
           girth=1.0):
    """A fish on a curved spine, with its own back and belly profile.

    <b>`nudge` is used far more than `zoom`, and that is the lesson.</b>
    Shrinking a fish to stop its tail hanging off the tile also shrinks
    the body - and the body is the thing that reads as big, which is
    the whole point of the top bands being bigger. What actually hangs
    over the edge is the sprawl: a tendril, an orbit, a sail. Trim
    those, move the fish, leave the body alone.
    """
    if zoom is not None or nudge != (0.0, 0.0):
        fd.zoom(1.0 if zoom is None else zoom, nudge)
    fish = fd.Fish(fd.bezier([_lean(head), _lean(bend), _lean(tail)]))
    fish.flesh(fd.profile(back, girth), fd.profile(belly, girth))
    return fish


#: The ordinary profile: a snout, a swell behind the head, a narrow
#: wrist before the tail. Everything else here is a departure from it.
def rounded(peak, nose=1.5, wrist=0.42):
    return [(0, nose), (0.08, peak * 0.55), (0.22, peak * 0.9), (0.38, peak),
            (0.74, peak * wrist), (1.0, peak * 0.26)]


# --- The twenty-five --------------------------------------------------------
#
# Each is a function because a fish here can do something no other one
# does - hold its mouth open, punch a hole through itself, end in
# lightning, trail sparks that are not attached to anything.


# === Rare: an ordinary fish, about a quarter of an hour each ===============

def glass_minnow():
    """Slight and see-through, so: little body and an eye too big for it."""
    fish = shaped((14, 43.1), (28, 37.6), (44, 30.9),
                  rounded(9.6), rounded(10.4, nose=1.6),
                  nudge=(-2, 2))
    fish.light(floor=0.26, ceiling=0.98, rim=0.36)
    fish.gill(0.24, depth=0.14)
    fish.mouth()
    # Outline simplified and enlarged; see the silhouette note on the
    # tidewrack shark. The two-pixel belly fin went because it only
    # ever read as a notch in the edge.
    fish.caudal(spread=12, length=12, fork=0.56)
    fish.sail(0.34, 0.64, height=10)
    fish.paddle(0.30, length=11, drop=5.5)
    # You can read the lakebed through it, so: a spine and nothing else.
    fish.lateral(across=-0.52, start=0.20, stop=0.88, width=0.16, shade=0.34)
    # <b>The spine and ribs, because the fish is transparent.</b> It is
    # called a glass minnow and was drawn as a pale fish with a line on
    # it - five marking pixels, and nothing saying what the glass is
    # for. What you actually see through one is the skeleton, which is
    # also the cheapest detail available here: a lateral line along the
    # backbone and `slits` for the ribs, both already pixel-safe.
    fish.lateral(across=0.04, start=0.24, stop=0.80, width=0.09, shade=0.22)
    fish.slits(0.34, 0.70, 3, lo=-0.50, hi=0.60, shade=0.26)
    fish.eye(t=0.17, across=-0.34, radius=4.0)
    return fish


def copper_dace():
    """The plain one, and the yardstick the rest are departures from."""
    fish = shaped((13, 42.4), (27, 37.2), (42, 30.6),
                  rounded(9.8), rounded(11.0, nose=1.6),
                  nudge=(-4, 3))
    fish.light(floor=0.14, ceiling=0.96, rim=0.34)
    fish.gill(0.24, depth=0.22)
    fish.mouth()
    # Outline simplified and enlarged; see the silhouette note on the
    # tidewrack shark. The two-pixel belly fin went because it only
    # ever read as a notch in the edge.
    fish.caudal(spread=15, length=14, fork=0.46)
    fish.sail(0.34, 0.66, height=12)
    fish.paddle(0.29, length=12, drop=6)
    for t, across in ((0.38, -0.50), (0.54, -0.24), (0.68, -0.44)):
        fish.spot(t, across, 2.2, shade=0.34)
    fish.lateral(across=-0.10, start=0.26, stop=0.90)
    fish.eye(t=0.17, across=-0.32, radius=3.2)
    return fish


def silt_carp():
    """Deep, slow, and whiskered. It has been down there a while."""
    fish = shaped((13, 43.1), (28, 36.4), (43, 30.9),
                  [(0, 2.0), (0.10, 9), (0.38, 12.5), (0.74, 5.5), (1.0, 2.8)],
                  [(0, 2.2), (0.10, 10), (0.40, 13.5), (0.76, 5.5), (1.0, 2.8)],
                  nudge=(2, -4))
    fish.light(floor=0.16, ceiling=0.92, rim=0.30)
    fish.gill(0.23, depth=0.22)
    fish.mouth(t=0.06, depth=0.42)
    # Outline simplified and enlarged; see the silhouette note on the
    # tidewrack shark. The two-pixel belly fin went because it only
    # ever read as a notch in the edge.
    fish.caudal(spread=13, length=11, fork=0.26)
    fish.sail(0.32, 0.64, height=13)
    fish.paddle(0.30, length=12, drop=6)
    # Tastes of the bottom, and is coloured like it.
    fish.mottle(((0.32, -0.48), (0.52, 0.20), (0.70, -0.36)), radius=2.6)
    # Scale rows. A carp is the one fish in the set a player could name
    # from its scales alone, and `slits` is the way to get rows of them
    # that stay separate instead of merging into a shaded flank.
    fish.slits(0.36, 0.76, 4, lo=-0.72, hi=0.62, shade=0.30)
    for side in (-1, 1):
        fish.barbel(0.06, side, 7, curl=0.4)
    fish.eye(t=0.16, across=-0.36, radius=3.0)
    return fish


def nettle_dart():
    """Three inches of spite, most of it spine."""
    fish = shaped((16, 42.2), (30, 36.2), (44, 30.8),
                  [(0, 1.6), (0.10, 5.6), (0.40, 7.6), (0.80, 3.6), (1.0, 1.7)],
                  [(0, 1.8), (0.10, 6.2), (0.40, 8.2), (0.80, 3.6), (1.0, 1.7)],
                  nudge=(-1, -2))
    fish.light(floor=0.22, ceiling=0.99, rim=0.36)
    fish.gill(0.20, depth=0.18)
    fish.mouth()
    # Outline simplified and enlarged; see the silhouette note on the
    # tidewrack shark. The two-pixel belly fin went because it only
    # ever read as a notch in the edge.
    fish.caudal(spread=11, length=12, fork=0.54, rays=3)
    fish.spines(0.26, 0.64, 3, height=7)
    fish.sail(0.34, 0.66, height=9)
    # Three inches of spite, barred like a wasp.
    fish.stripes(4, start=0.30, stop=0.78, width=0.045, depth=0.78)
    fish.eye(t=0.15, across=-0.34, radius=2.6)
    return fish


def hollow_roach():
    """Picked clean: the ribs show and there is nothing behind the eye."""
    fish = shaped((14, 42.9), (28, 37), (43, 31.1),
                  rounded(9.2), rounded(9.9),
                  nudge=(-2, 2))
    fish.light(floor=0.20, ceiling=0.92, rim=0.30)
    fish.gill(0.22, depth=0.26)
    fish.mouth()
    # Outline simplified and enlarged; see the silhouette note on the
    # tidewrack shark. The two-pixel belly fin went because it only
    # ever read as a notch in the edge.
    fish.caudal(spread=13, length=14, fork=0.62)
    fish.sail(0.36, 0.66, height=10)
    # Through `slits`. These were six `band` calls - shade steps, which
    # at this tone count mostly quantise back into the flesh; the whole
    # set's worth of them moves 51 pixels across 25 sprites. A roach
    # the player is meant to see as barred needs the bars to be a
    # colour.
    fish.slits(0.32, 0.72, 3, lo=-0.85, hi=0.55, shade=0.30)
    fish.lateral(across=-0.14, start=0.26, stop=0.88)
    fish.socket(t=0.16, across=-0.34, radius=3.6)
    return fish


def saltwhisker():
    """A catfish. The four whiskers do all the work."""
    fish = shaped((14, 43.9), (28, 38.5), (43, 32.1),
                  [(0, 3.0), (0.12, 9.6), (0.30, 11.2), (0.74, 5.2), (1.0, 2.4)],
                  [(0, 3.4), (0.12, 10.8), (0.30, 12.6), (0.76, 5.2), (1.0, 2.4)],
                  nudge=(2, -7))
    fish.light(floor=0.08, ceiling=0.99, rim=0.34)
    fish.gill(0.26, depth=0.22)
    fish.mouth(t=0.07, depth=0.42)
    # Outline simplified and enlarged; see the silhouette note on the
    # tidewrack shark. The two-pixel belly fin went because it only
    # ever read as a notch in the edge.
    fish.caudal(spread=13, length=12, fork=0.20)
    fish.sail(0.30, 0.62, height=11)
    fish.paddle(0.28, length=13, drop=6, lean=0.75)
    for side, length, curl in ((-1, 8, 0.55), (-1, 6, 0.15),
                               (1, 9, 0.7), (1, 6, 0.3)):
        fish.barbel(0.06, side, length, curl=curl, thick=2.1)
    fish.lateral(across=-0.06, start=0.24, stop=0.88, width=0.15)
    fish.mottle(((0.40, -0.54), (0.64, -0.42)), radius=2.6)
    fish.slits(0.30, 0.74, 3, lo=-0.62, hi=0.66, shade=0.30)
    fish.eye(t=0.19, across=-0.40, radius=3.0)
    return fish


def shorecrab():
    """A shell with legs. The first thing here that is not built on a spine.

    <b>Where the diversity problem actually was, and it replaces the
    Greyback Chub.</b> Eighteen of the twenty-four were a diagonal body
    with a tail at one end and fins down the sides, because that is the
    only thing `shaped` can make. A crab has no spine to hang a profile
    off, so it is a dome, six legs, two claws and two eyes, and nothing
    about it can come out as a fish.
    """
    fish = fd.Fish(fd.bezier([(30, 30), (32, 32), (34, 34)]))
    fish.dome((32, 34), across=17, down=10.5, power=2.9,
              floor=0.18, ceiling=0.94, lift=0.26)
    # Legs in two segments, because a crab's bend outward then down and
    # a single bowed limb reads as a spider's.
    for near, knee, toe in (((19, 33), (10, 29), (6, 38)),
                            ((18, 38), (8, 38), (5, 47)),
                            ((20, 42), (12, 47), (10, 55)),
                            ((45, 33), (54, 29), (58, 38)),
                            ((46, 38), (56, 38), (59, 47)),
                            ((44, 42), (52, 47), (54, 55))):
        fish.limb(near, knee, thick=2.6, taper=0.2, kind=fd.FIN, shade=0.44,
                  over=(fd.EMPTY, fd.BODY))
        fish.limb(knee, toe, thick=2.2, taper=0.7, kind=fd.FIN, shade=0.34)
    # The claws, raised, which is the half of the silhouette that says
    # crab rather than beetle.
    for wrist, reach, lean in (((21, 27), (14, 20), -2.2),
                               ((43, 27), (50, 20), -0.94)):
        fish.limb(wrist, reach, thick=3.2, taper=0.25, kind=fd.BODY,
                  shade=0.46, over=(fd.EMPTY, fd.BODY))
        fish.claw(reach, lean, length=9, gape=0.62, thick=3.4, shade=0.5)
    fish.here(32, 29, 7.0, fd.MARK, 0.30, over=(fd.BODY,))
    fish.here(32, 30, 5.0, fd.BODY, 0.80, over=(fd.MARK,))
    for x, y in ((24, 37), (40, 37), (27, 41), (37, 41), (32, 42)):
        fish.here(x, y, 2.2, fd.MARK, 0.26, over=(fd.BODY,))
    for x in (27, 37):
        fish.limb((x, 26), (x, 22), thick=1.8, taper=0.1, kind=fd.BODY,
                  shade=0.3, over=(fd.EMPTY, fd.BODY))
        fish.stare(x, 22, radius=2.6)
    return fish


def reed_prawn():
    """A segmented C with a fan on the end, which is the shape of a prawn.

    In place of the Stonebite. It does use a spine - a prawn has one -
    but hooked right round,
    which is a silhouette nothing else here has. The legs and the two
    antennae are what stop it reading as an eel, and the gap in the C
    has to stay wide: closed up to two pixels the dark border meets in
    the middle and the whole hook reads as an open mouth.
    """
    fd.zoom(1.0, (2, -5))
    fish = fd.Fish(fd.bezier([(22, 19), (51, 27), (48, 51), (16, 54)]))
    fish.flesh(fd.profile([(0, 1.6), (0.06, 6.4), (0.18, 8.4), (0.34, 8.0),
                           (0.60, 6.4), (0.84, 4.4), (1.0, 2.6)]),
               fd.profile([(0, 1.8), (0.06, 6.8), (0.18, 9.0), (0.34, 8.4),
                           (0.60, 6.6), (0.84, 4.4), (1.0, 2.6)]))
    fish.light(floor=0.30, ceiling=0.99, rim=0.30)
    # The shell is plated, not scaled, so: cross bands rather than a
    # diamond lattice.
    # Three plates, not five. On a body this small a bar every two
    # pixels is not segmentation, it is a crack pattern.
    fish.stripes(3, start=0.36, stop=0.76, width=0.026, depth=0.86,
                 shade=0.34)
    fish.limb((22, 19), (9, 13), thick=2.4, taper=0.85, kind=fd.BODY,
              shade=0.34, over=(fd.EMPTY, fd.BODY))
    for end, bow in (((7, 32), 3.0), ((12, 44), -3.0)):
        fish.limb((20, 22), end, thick=1.6, taper=0.7, bow=bow, kind=fd.FIN,
                  shade=0.30)
    for leg_root, toe in (((29, 28), (20, 30)), ((31, 35), (21, 38)),
                          ((31, 42), (21, 46)), ((28, 48), (20, 52))):
        fish.limb(leg_root, toe, thick=1.8, taper=0.6, kind=fd.FIN, shade=0.34)
    fish.caudal(spread=8, length=9, fork=0.0, rays=4)
    fish.eye(t=0.07, across=-0.52, radius=3.0)
    return fish


def rivershell():
    """A fan with a scalloped rim and ribs, hinged at the bottom.

    In place of the Mossback Bream. <b>The shape that ruined the
    Worldscale is the right answer here.</b> A fan plus concentric arcs
    always reads as a seashell, which is exactly why four tries at the
    Worldscale - the mythic plate, since replaced by the Zaratan - had
    to be thrown away, and exactly why this one takes one try. The ribs are limbs
    with a negative taper, so they widen toward the rim the way a real
    one's do.
    """
    fish = fd.Fish(fd.bezier([(30, 30), (32, 32), (34, 34)]))
    hinge = (32, 52)
    fish.dome((32, 36), across=17, down=16, power=2.05,
              floor=0.22, ceiling=0.96, lift=0.22)
    # Cut the lower half down to the hinge: a dome alone is a pebble.
    for y in range(SIZE):
        for x in range(SIZE):
            if fish.kind[y][x] == fd.EMPTY:
                continue
            dx = abs((x + 0.5) / fd.K - hinge[0])
            dy = hinge[1] - (y + 0.5) / fd.K
            if dy < 16 and dx > dy * 1.05 + 1.5:
                fish.kind[y][x] = fd.EMPTY
    for i in range(13):
        angle = -2.62 + 1.1 * i / 6.0
        fish.limb(hinge, (hinge[0] + math.cos(angle) * 34,
                          hinge[1] + math.sin(angle) * 34),
                  thick=1.2, taper=-0.9, kind=fd.MARK,
                  shade=0.34 if i % 2 else 0.62, over=(fd.BODY,))
    for radius in (12, 20, 27):
        fish.arc(fd.place(*hinge), radius, -2.60, -0.54, thick=1.0,
                 kind=fd.MARK, shade=0.20, over=(fd.BODY, fd.MARK))
    # Ears either side of the hinge, which is how a scallop sits.
    for toe in ((20, 46), (44, 46)):
        fish.limb((32, 51), toe, thick=3.4, taper=0.55, kind=fd.BODY,
                  shade=0.42, over=(fd.EMPTY, fd.BODY))
    fish.here(32, 51, 3.2, fd.MARK, 0.08, over=(fd.BODY, fd.MARK))
    return fish


def silt_star():
    """Five arms, no front, no eye, and no tail. Radial, not bilateral.

    In place of the Cinderperch. Every other sprite in the set has a
    head at one end, because every other sprite was grown on a spine. This one has no end to put a
    head on, which is the loudest way the set can say that not
    everything in the water is a fish.
    """
    fish = fd.Fish(fd.bezier([(30, 30), (32, 32), (34, 34)]))
    centre = (32, 33)
    for i in range(5):
        angle = -math.pi / 2 + i * 2 * math.pi / 5
        # Flat-shaded per arm rather than smoothly: at this size a
        # faceted star reads as a star and a smooth one as a stain.
        shade = 0.52 - 0.34 * (math.cos(angle) + math.sin(angle)) / 2
        tip = (centre[0] + math.cos(angle) * 24,
               centre[1] + math.sin(angle) * 24)
        fish.limb(centre, tip, thick=6.0, taper=0.74, kind=fd.BODY,
                  shade=shade, over=(fd.EMPTY, fd.BODY))
        for k in (0.30, 0.48, 0.66, 0.82):
            fish.here(centre[0] + (tip[0] - centre[0]) * k,
                      centre[1] + (tip[1] - centre[1]) * k,
                      max(0.7, 1.9 * (1 - k)), fd.MARK, 0.22,
                      over=(fd.BODY,))
    fish.dome(centre, across=8, down=8, power=2.2, floor=0.34,
              ceiling=0.98, lift=0.2, over=(fd.EMPTY, fd.BODY))
    for i in range(6):
        angle = i * 2 * math.pi / 6
        fish.here(centre[0] + math.cos(angle) * 4.6,
                  centre[1] + math.sin(angle) * 4.6,
                  1.0, fd.MARK, 0.24, over=(fd.BODY,))
    fish.here(centre[0] + 2.4, centre[1] - 2.0, 1.6, fd.GLOW, 0.9,
              over=(fd.BODY, fd.MARK))
    return fish


# === Epic: a fish with something on it that no fish has ====================

def emberfin():
    """Fins that trail like something still burning."""
    fish = shaped((13, 43), (26, 37.2), (40, 32),
                  rounded(7.6), rounded(8.4),
                  nudge=(5, 1))
    fish.light(floor=0.14, ceiling=0.96, rim=0.38)
    fish.gill(0.23, depth=0.22)
    fish.mouth()
    # Three big trailing shapes rather than four competing ones: the
    # tail streamer, one tall dorsal and one long pectoral. See the
    # silhouette note on the tidewrack shark.
    fish.ribbon(spread=8, length=19, sway=-6)
    fish.sail(0.28, 0.70, height=15, peak=0.62)
    fish.paddle(0.28, length=15, drop=8)
    fish.horns(2, 7, spread=0.45, t=0.13)
    for t in (0.34, 0.48, 0.62):
        fish.spot(t, -0.45, 3.0)
    # Warm to the touch, hours after the water.
    fish.mottle(((0.32, -0.42), (0.48, 0.26), (0.64, -0.22)), radius=2.8,
                shade=0.86)
    fish.eye(t=0.16, across=-0.32, radius=3.2)
    return fish


def moonscale():
    """A disc with a moon cut into it, and the only round one in the set."""
    fish = shaped((18, 40.8), (30, 34.2), (42, 31.2),
                  [(0, 2.0), (0.10, 9), (0.40, 15), (0.70, 11), (1.0, 3.2)],
                  [(0, 2.4), (0.10, 10), (0.42, 16), (0.72, 11), (1.0, 3.2)],
                  nudge=(-3, -2))
    fish.light(floor=0.22, ceiling=0.99, rim=0.40)
    fish.gill(0.20, depth=0.20)
    fish.mouth()
    # Outline simplified and enlarged, per the silhouette test set out
    # on the tidewrack shark. The small belly fin is gone - at two
    # pixels it never read as a fin, only as a notch in the edge - and
    # what remains is drawn big enough to survive as a shape.
    fish.caudal(spread=14, length=13, fork=0.46)
    fish.sail(0.30, 0.62, height=12)
    fish.paddle(0.30, length=13, drop=7)
    import math
    fish.crescent(fish.pt(0.46, -0.08), 9.0, math.radians(35), bite=0.86)
    fish.eye(t=0.15, across=-0.36, radius=3.4)
    return fish


def bramble_eel():
    """Long, bent, and thorned the whole way down."""
    # Undulated and thickened, for the reason set out on the ash
    # lamprey: a straight diagonal thin body has a square bounding box
    # and fills only its diagonal, so it seats at a size that leaves
    # the tile mostly empty.
    fd.zoom(0.92, (0, 0))
    fish = fd.Fish(fd.serpentine((12, 52), (54, 14), waves=1.45,
                                 amplitude=16.0))
    fish.flesh(fd.profile([(0, 2.4), (0.10, 5.6), (0.45, 6.4), (0.85, 4.0),
                           (1.0, 1.9)], SLENDER),
               fd.profile([(0, 2.6), (0.10, 5.9), (0.45, 6.7), (0.85, 4.0),
                           (1.0, 1.9)], SLENDER))
    fish.light(floor=0.16, ceiling=0.92, rim=0.34)
    fish.gill(0.16, depth=0.20)
    fish.mouth()
    fish.caudal(spread=5, length=8, fork=0.5, rays=4)
    fish.spines(0.22, 0.84, 5, height=5.5)
    fish.sail(0.30, 0.92, height=1.8, side=1, rays=0)
    # Comes up with the hook already somewhere else.
    fish.stripes(4, start=0.30, stop=0.80, width=0.030, depth=0.60)
    fish.eye(t=0.11, across=-0.36, radius=2.8)
    return fish


def lantern_smelt():
    """An anglerfish; everything hangs off the lure."""
    fish = shaped((18, 44), (30, 38.8), (45, 33),
                  rounded(8.0), rounded(9.0),
                  nudge=(0, -4))
    fish.light(floor=0.18, ceiling=0.96, rim=0.36)
    fish.gill(0.26, depth=0.20)
    # Outline simplified and enlarged, per the silhouette test set out
    # on the tidewrack shark. The small belly fin is gone - at two
    # pixels it never read as a fin, only as a notch in the edge - and
    # what remains is drawn big enough to survive as a shape.
    fish.caudal(spread=14, length=13, fork=0.42)
    fish.sail(0.40, 0.68, height=11)
    fish.paddle(0.30, length=12, drop=6.5)
    fish.maw(length=15, gape=0.95, teeth=3, hinge=0.24)
    # <b>Shorter, because the lure was setting the sprite's size.</b>
    # At eighteen units it reached further from the body than any part
    # of the fish, so `build` scaled the whole animal down until the
    # lure tip cleared the tile - this one measured fourteen units of
    # body depth, as much as the driftbell, and came out at 25% fill
    # against the driftbell's 40%. Nearly all of the difference was one
    # stalk.
    fish.lure(length=12, radius=3.6, at=0.40)
    # <b>Photophores, which the fish is named after and did not have.</b>
    # A lanternfish is identified in every field guide by the row of
    # light organs along its underside, and this one carried its lure
    # and nothing else - four marking pixels in the whole tile. They
    # are GLOW rather than MARK so they read as lit instead of
    # painted, and they run the belly line where a real row runs.
    for t in (0.34, 0.45, 0.56, 0.67, 0.78):
        fish.spot(t, 0.66, 1.6, kind=fd.GLOW, shade=0.96)
    fish.lateral(across=-0.18, start=0.28, stop=0.84, width=0.11, shade=0.26)
    fish.slits(0.22, 0.32, 2, lo=-0.70, hi=0.35, shade=0.22)
    fish.eye(t=0.24, across=-0.34, radius=3.6, lit=True)
    return fish


def ash_lamprey():
    """No jaw at all: a ring of rasping teeth and a tube behind it."""
    # <b>A straight diagonal is the worst shape a thin body can
    # have.</b> Measured, this was the emptiest sprite in the set - 43
    # painted pixels against the next worst at 54 and vanilla's ~95 -
    # and the cause is not the fit loop giving up. It is that a
    # diagonal line has a <em>square</em> bounding box and fills only
    # the diagonal of it, so `build` scales until the corners of an
    # almost-empty box touch the tile and stops with the body still a
    # thread across the middle.
    #
    # Undulating it fixes both halves of that: the humps put flesh in
    # the parts of the box a straight line leaves empty, and the body
    # can then be thicker without the sprite growing. It is also what
    # an eel does.
    # <b>Amplitude has to beat thickness, or the humps weld shut.</b>
    # The first pass at undulating this put a 10.5-unit wave on a
    # 7.2-unit body - the crests were barely wider than the flesh, so
    # the curve filled its own troughs and the fish came out a lump
    # that happened to be fatter than the thread it replaced. The
    # ratio is the thing to hold, not the fill percentage.
    fd.zoom(0.92, (0, 0))
    # <b>One gentle bend, not a wave train.</b> At 1.05 waves the
    # head pointed away from the body mass and the sucker - which is
    # drawn forward of the snout by design - ended up a pale disc
    # sitting on its own in the corner. A lamprey does not need to
    # zigzag to read as a lamprey; it needs a long tube and that
    # mouth, and one bend puts flesh in the box without aiming the
    # head out of it.
    fish = fd.Fish(fd.serpentine((14, 50), (52, 15), waves=0.60,
                                 amplitude=11.0))
    fish.flesh(fd.profile([(0, 4.4), (0.14, 6.8), (0.55, 7.4), (0.88, 4.4),
                           (1.0, 2.0)], SLENDER),
               fd.profile([(0, 4.6), (0.14, 7.0), (0.55, 7.6), (0.88, 4.4),
                           (1.0, 2.0)], SLENDER))
    fish.light(floor=0.16, ceiling=0.94, rim=0.34)
    fish.caudal(spread=5, length=8, fork=0.2, rays=3)
    fish.sail(0.52, 0.94, height=3.5, rays=0)
    fish.sail(0.60, 0.94, height=2.5, side=1, rays=0)
    # The gill row, which on a lamprey is seven holes and not a plate.
    for i in range(6):
        fish.spot(0.17 + i * 0.045, -0.15, 1.5, shade=0.26)
    fish.sucker(radius=6.8, teeth=8)
    fish.stripes(3, start=0.40, stop=0.80, width=0.030, depth=0.55)
    fish.eye(t=0.22, across=-0.30, radius=3.2)
    return fish


def driftbell():
    """A bell with nothing inside it, and a few feet of trailing sting.

    In place of the Gloamfin, which was a fish with a long fin. Not a
    fish at all, which is the easiest way to be more than a fish with a
    quirk: no spine, no tail, no fins, no eye, and lit from the
    inside because that is what a jellyfish does.

    <b>The first pass came out as a lampshade.</b> Nine tentacles at
    two design units each are a solid curtain once the dark border has
    gone round every one of them - the border is a pixel on each side,
    so a gap of two pixels between strands is no gap at all. Four
    strands with room to swing read as tentacles; nine read as a
    skirt.
    """
    fish = fd.Fish(fd.bezier([(30, 30), (32, 32), (34, 34)]))
    for root, end, bow in (((22, 30), (16, 52), 5.0), ((27, 33), (25, 56), -4.0),
                           ((37, 33), (40, 55), 4.0), ((42, 30), (49, 51), -5.0)):
        fish.limb(root, end, thick=1.5, taper=0.5, bow=bow, kind=fd.FIN,
                  shade=0.34)
    for root, end, bow in (((29, 32), (27, 46), 2.4), ((32, 33), (33, 49), -2.2),
                           ((35, 32), (38, 45), 2.2)):
        fish.limb(root, end, thick=3.0, taper=0.66, bow=bow, kind=fd.MARK,
                  shade=0.58)
    fish.dome((32, 22), across=17, down=12, power=2.25,
              floor=0.34, ceiling=0.99, lift=0.28, over=(fd.EMPTY, fd.FIN))
    # The rim of a bell is a row of scallops, not a straight cut.
    for i in range(8):
        k = (i + 0.5) / 8
        fish.here(32 + (k - 0.5) * 2 * 15.6,
                  22 + 11.4 * math.sqrt(max(0.0, 1 - ((k - 0.5) * 2) ** 2)),
                  2.1, fd.MARK, 0.34, over=(fd.BODY,))
    fish.arc(fd.place(32, 22), 8.0, 0.40, 2.74, thick=1.2, kind=fd.GLOW,
             shade=0.95, over=(fd.BODY, fd.MARK))
    for angle in (0.70, 1.36, 1.78, 2.44):
        fish.here(32 + math.cos(angle) * 7.6, 22 + math.sin(angle) * 7.6,
                  2.3, fd.GLOW, 0.98, over=(fd.BODY, fd.MARK, fd.GLOW))
    fish.trim(shade=0.88, on=(fd.BODY,),
              keep=lambda x, y: y > fd.place(32, 20)[1])
    return fish


# === Legendary: not a fish =================================================
#
# <b>And bigger than one.</b> A legendary drawn at the same scale as a
# rare is a rare in a brighter colour, whatever is bolted onto it - the
# first pass gave them holes and plates and jaws and they still took up
# the same corner of the tile as a minnow. Size is the cue that lands
# before any detail does, so the bands grow: a rare sits in the middle
# of its square, a legendary crowds it, a mythic runs off the edges.

def voidgill():
    """One hole straight through it, and what is behind it is not water.

    <b>Eleven features in a tile fourteen pixels wide, and then too
    few.</b> It carried tendrils, two sails, a maw, horns, two glow
    spots, two holes and a sheen, all sized for a thirty-two pixel
    grid, and came out a purple mess. The first repair stripped it to
    one hole and five fins on the theory that sixteen pixels cannot
    hold more - which turned out to be false, and the reason is
    recorded at `fishdraw.BORDER`: half the tile was going to black
    outline, so the hole and the fins were competing for seven pixels
    rather than fourteen.

    <b>What was actually wrong, twice over, was placement.</b> The
    first version put eleven marks on top of each other. The second
    put the one surviving hole at t=0.52 with the eye at t=0.17 on a
    short body, so hole and eye ended up adjacent and the pair read as
    one enormous socket - the sprite looked like a skull, not a fish.
    So the hole moves back past the midpoint and leaves a clear run of
    flesh between itself and the eye, which is what makes it read as a
    hole <em>in</em> something rather than a feature <em>of</em> a face.

    At this size a hole has to be three pixels across before it reads
    as a hole at all rather than as a dark mark, and the detail that
    went back on - the anal fin, the gill slits, the second lit line -
    goes in front of it, where there is body to put it on.
    """
    fish = shaped((12, 44), (27, 38), (44, 31),
                  [(0, 2.4), (0.10, 9), (0.26, 13), (0.44, 14),
                   (0.78, 6), (1.0, 3.4)],
                  [(0, 2.6), (0.10, 10), (0.26, 14), (0.46, 15.5),
                   (0.80, 6), (1.0, 3.4)],
                  nudge=(2, -2))
    fish.light(floor=0.10, ceiling=0.92, rim=0.46)
    fish.mouth(t=0.05, span=0.6, depth=0.36)
    # <b>Fewer shapes on the outline, each drawn large.</b> Judged by
    # the silhouette test described on the tidewrack shark: render the
    # sprite flat black and see whether it still names the animal. A
    # handful of two-pixel fins leaving the body at different angles
    # does not survive that test - they merge into roughness. The
    # detail inside the silhouette is untouched.
    fish.caudal(spread=15, length=13, fork=0.42, rays=3)
    fish.sail(0.28, 0.58, height=14, peak=0.45)
    fish.paddle(0.30, length=13, drop=7)
    # In front of the hole, where there is flesh to carry them.
    fish.slits(0.17, 0.30, 3, lo=-0.76, hi=0.30, shade=0.20)
    fish.lateral(across=0.30, start=0.26, stop=0.52, width=0.11, shade=0.34)
    fish.sheen(across=-0.62, start=0.20, stop=0.50)
    fish.hole(0.64, -0.04, 7.0)
    fish.eye(t=0.165, across=-0.34, radius=3.4, lit=True)
    return fish
def stormtail():
    """The tail is a lightning fork, and some of it has come loose."""
    fish = shaped((12, 46.3), (25, 41.2), (36, 36.7),
                  [(0, 2.0), (0.10, 8), (0.34, 11), (0.76, 5), (1.0, 2.6)],
                  [(0, 2.2), (0.10, 9), (0.36, 12), (0.78, 5), (1.0, 2.6)],
                  nudge=(4, -4))
    fish.light(floor=0.14, ceiling=0.96, rim=0.46)
    fish.gill(0.26, depth=0.20)
    fish.mouth()
    fish.bolt(length=17, width=3.0,
              zigzag=((0.28, -0.32), (0.50, 0.20), (0.74, -0.28),
                      (1.0, 0.24)))
    # The bolt is the tail, so the body needs one clear dorsal to
    # balance it rather than a comb of five spines and a belly fin.
    fish.sail(0.28, 0.62, height=13, peak=0.42)
    fish.spines(0.30, 0.56, 3, height=5)
    fish.paddle(0.30, length=13, drop=6.5)
    fish.horns(3, 5, spread=0.55, t=0.15)
    # Two, not six. `despur` spares GLOW on purpose - a spark is
    # meant to float clear of the body - so six of them survive as six
    # unconnected specks, and six specks around a fish that already
    # ends in lightning is confetti competing with the bolt.
    fish.motes([(8, -10, 1.8), (14, -6, 1.4)])
    fish.sheen(across=-0.64)
    fish.lateral(across=-0.20, start=0.24, stop=0.80, shade=0.88)
    fish.slits(0.34, 0.70, 3, lo=-0.55, hi=0.75, shade=0.22)
    fish.eye(t=0.18, across=-0.34, radius=3.4, lit=True)
    return fish


def mirelash():
    """A long rounded zig-zag: humps, which is the oldest picture of a
    serpent there is.

    <b>It used to be the Mirecoil and it used to be the coil.</b> The
    two serpents swapped shapes, because the coil is the stronger of
    the two and it was the one sitting a band lower; the name went with
    the shape. Nothing here is a coil any more, so nothing here is
    called one.

    <b>The amplitude is set by the border and the aura, not by
    taste.</b> Adjacent humps sit two amplitudes apart, the body eats
    two half-widths of that, and what is left has to survive a
    one-pixel border on each facing edge plus the band's aura. Under
    about ten design units the lot meets in the middle and the humps
    fuse into a lumpy sausage - which is what three settings of it
    were. Fewer, larger bends read; more, smaller ones do not. This one
    can afford slightly tighter bends than the mythic could, because a
    legendary wears one ring of aura rather than two.
    """
    fd.zoom(0.86, (0, 0))
    # <b>Thickened through the middle.</b> The mid-body was 2.6 units
    # - well under a pixel of half-width - so the zigzag enclosed more
    # background than flesh and measured the sparsest sprite in the
    # set, 33% density inside its own box against vanilla's 51%. A
    # zigzag only reads as a body if the body is thicker than the gaps
    # it leaves between its own limbs.
    fish = fd.Fish(fd.serpentine((12, 52), (54, 14), waves=1.75,
                                 amplitude=13.0))
    fish.flesh(fd.profile([(0, 1.6), (0.030, 5.6), (0.080, 6.6), (0.160, 4.2),
                           (0.34, 4.6), (0.62, 4.0), (0.86, 2.4), (1.0, 0.9)],
                          SLENDER),
               fd.profile([(0, 1.8), (0.030, 6.0), (0.080, 7.0), (0.160, 4.4),
                           (0.34, 4.8), (0.62, 4.0), (0.86, 2.4), (1.0, 0.9)],
                          SLENDER))
    fish.light(floor=0.16, ceiling=0.94, rim=0.36)
    # The mane, which is what it had when it was the coil.
    fish.spines(0.22, 0.84, 7, height=4.2)
    fish.caudal(spread=9, length=10, fork=0.45, rays=0)
    # Was five `band` calls - shade steps, which mostly quantise back
    # into the flesh. A banded serpent needs the bands to be a colour.
    fish.slits(0.26, 0.82, 5, lo=-0.88, hi=0.88, shade=0.26)
    fish.maw(length=11, gape=0.60, teeth=3, hinge=0.06)
    fish.sheen(across=-0.58, start=0.20, stop=0.86)
    fish.lateral(across=-0.22, start=0.24, stop=0.84, shade=0.30)
    fish.eye(t=0.05, across=-0.40, radius=3.0, lit=True)
    return fish


def tidewrack_shark():
    """A pointed snout, a tall triangular dorsal and a crescent tail.

    In place of the Gilded Sturgeon. <b>Still a fish, and the one
    silhouette nobody mistakes for another.</b> The rest of this band got
    there by bolting something unnatural on - a hole, a plate, a maw -
    and the shark gets there with nothing bolted on at all: there is no
    second animal in the game whose outline reads as a shark.

    <b>It was once stripped to six features, and that was the wrong
    repair.</b> The sprite had fourteen and came out a lumpy grey mass,
    so the fins, the gill slits and the lateral line were cut back
    until only nose, dorsal and tail were left. It read - and it read
    as a far poorer sprite than the ones it was being measured against,
    which are not sparse at all. They are dense. The detail was never
    the problem; see `fishdraw.BORDER` for what was.

    Two things were actually wrong, and both were arithmetic rather
    than taste. The gill slits were shade steps half a pixel wide, and
    at four tones a shade step inside a body quantises into the flesh
    and disappears - so five of them bought a smear and cost the snout
    its contrast. Drawn through `slits`, which claims a whole pixel per
    mark and refuses to sit beside another, the same five are five
    slits.

    The second was a plain mistake: the pale `sheen` was set two
    pixels wide and run down the <em>back</em>, which is the one place
    a shark is not pale. It is a dark-backed, white-bellied animal and
    `light` already draws that - floor at the spine, ceiling at the
    belly. The sheen goes back to being what it is for, a thin lit line
    marking the legendary band.

    So the detail is all back and then some: two dorsals, pectoral,
    pelvic and anal, five gill slits, a lateral line, and a white belly
    under a dark back. The spine stays nearly level, because the thing
    that says shark is the profile from nose to tail and a diagonal
    body spends half the tile on the diagonal instead.
    """
    fish = shaped((10, 40.4), (29, 36.4), (48, 32.6),
                  [(0, 1.0), (0.08, 4.4), (0.22, 8.2), (0.38, 8.8),
                   (0.62, 6.4), (0.80, 3.4), (1.0, 2.6)],
                  [(0, 1.2), (0.08, 5.2), (0.22, 9.4), (0.40, 10.0),
                   (0.62, 6.6), (0.80, 3.4), (1.0, 2.6)],
                  nudge=(-1, 0))
    # Dark along the spine, white at the belly, and most of the
    # modelling on the animal comes from this one call.
    fish.light(floor=0.06, ceiling=0.99, rim=0.30)
    # Lunate, upper lobe the longer one. The lean was four times this
    # once, which was right on a level spine and became a spike the
    # moment the body tilted: lobe length adds to the body's own
    # direction, so tilting the body aims the lean out of the tile.
    # <b>Four shapes on the outline, and they are big.</b> Tested by
    # the only measure that matters for this - render the sprite as a
    # flat silhouette and see whether it still says shark. The vanilla
    # cod and tropical fish both pass that test easily, because each is
    # one smooth teardrop plus one tail fan and nothing else. This one
    # failed it completely: seven separate fins - two dorsals, an anal,
    # two pectorals, a pelvic and the tail - each a pixel or two
    # across, and in silhouette they merge into a lumpy mass with no
    # animal in it.
    #
    # So the outline carries only what names the animal: a pointed
    # snout, one tall triangular dorsal, one pectoral, and a crescent
    # tail - each drawn large enough to survive as a shape. The second
    # dorsal, the anal and the pelvic are gone; at this size they never
    # read as fins, only as roughness on the edge.
    #
    # This is not the "cut the detail" mistake from earlier in the
    # file. Detail belongs <em>inside</em> the silhouette, and all of
    # it stays: the gill slits, the lateral line, the countershading,
    # the lit back. What comes off is geometry that was only ever
    # breaking up the outline.
    fish.caudal(spread=16, length=13, fork=0.44, rays=3, lean=1.5)
    fish.sail(0.24, 0.50, height=17, peak=0.30, rays=2)
    fish.paddle(0.28, length=14, drop=6, lean=0.95, rays=2)
    fish.mouth(t=0.055, span=0.62, depth=0.34)
    # Three, which is what the span holds. This line asked for five
    # first - the count the old shade-step version nominally drew - and
    # `slits` quietly declined two of them, because five marks with a
    # clear pixel between each need four pixels and the gill region of
    # this body is under two. That is the primitive doing its job:
    # the old code drew all five on top of each other and called it a
    # gill plate. Three land, three show, and the snout keeps its
    # contrast.
    fish.slits(0.20, 0.38, 3, lo=-0.78, hi=0.30, shade=0.18)
    fish.lateral(across=0.10, start=0.42, stop=0.82, width=0.10, shade=0.34)
    fish.sheen(across=-0.58, start=0.26, stop=0.72)
    fish.eye(t=0.150, across=-0.40, radius=2.6, lit=True)
    return fish
def abyss_ray():
    """Two wings, two head lobes and a whip, seen from above.

    In place of the Frostbite Pike. Everything else in the set is drawn
    side-on, because a fish drawn from above is a splinter. A ray is the opposite - side-on it is a
    splinter and from above it is a diamond with wings - so this is the
    one sprite looking down at the water instead of across it, and that
    alone makes it unmistakable in a row of them.
    """
    fish = fd.Fish(fd.bezier([(30, 30), (32, 32), (34, 34)]))
    # power below two is what brings a superellipse to a point, and a
    # wingtip is a point.
    fish.dome((32, 29), across=25, down=14, power=1.35,
              floor=0.14, ceiling=0.92, lift=0.20)
    fish.dome((32, 30), across=7.5, down=15, power=2.4,
              floor=0.26, ceiling=0.99, lift=0.28, over=(fd.EMPTY, fd.BODY))
    # Drawn after the wings, not before: under them it was swallowed
    # whole and the ray came out with no tail at all.
    fish.limb((32, 42), (35, 58), thick=3.2, taper=0.84, bow=3.0,
              kind=fd.FIN, shade=0.30, over=(fd.EMPTY,))
    for root, tip in (((28, 17), (25, 8)), ((36, 17), (39, 8))):
        fish.limb(root, tip, thick=3.0, taper=0.5, kind=fd.BODY, shade=0.42,
                  over=(fd.EMPTY, fd.BODY))
    # Bigger than they were. At radius 1.6-2.0 design units a spot is
    # under half a pixel and collapses to a single one wherever it
    # happens to land; a manta's blotches are the marking anybody
    # would name, so they are drawn at a size that survives.
    for x, y, r in ((18, 26, 3.2), (13, 30, 2.6), (22, 34, 2.8),
                    (46, 26, 3.2), (51, 30, 2.6), (42, 34, 2.8),
                    (32, 38, 2.4)):
        fish.here(x, y, r, fd.MARK, 0.24, over=(fd.BODY,))
    for x, y in ((21, 29), (43, 29), (26, 35), (38, 35)):
        fish.here(x, y, 1.5, fd.GLOW, 0.95, over=(fd.BODY, fd.MARK))
    fish.trim(shade=0.9, on=(fd.BODY,),
              keep=lambda x, y: y > fd.place(32, 29)[1])
    for x in (27, 37):
        fish.stare(x, 19, radius=4.4, lit=True)
    return fish


# === Mythic: geometry that cannot hold together ============================

def leviathan():
    """A serpent rolled into a coil, maned all the way round.

    <b>The sixth shape, chosen by being pointed at.</b> The sequence
    was: a big blue fish with a sail (nobody could tell which one it
    was); an arch; a coil with the head reared out of the top; humps;
    then humps and coil swapped bands. What finally settled it was a
    screenshot of the Mirecoil as it used to be - a tight green spiral
    with a spiky mane - and "make the mythic that, with a little
    pizazz".

    So the mythic is the tight spiral now, and it is the right call for
    a reason the swap had already half found: a coil passes over
    itself, so its outline has a hole in it, and a hole is the loudest
    thing a silhouette can have.

    <b>The pizazz is three things, and a fourth that was taken back
    out.</b> Horns and whiskers off the head, so it is a dragon rather
    than a snail; glowing nodes along the inside of the coil; sparks
    coming off it, which is the mythic band's one rule - geometry that
    cannot hold together. The fourth was lighting the tip of every
    mane spike, and it turned the sprite into a cyan smear: the coil
    reads because a thin bright groove runs over a dark body, and
    anything else bright competes with the groove.
    """
    fd.zoom(0.88, (1, 0))
    fish = fd.Fish(fd.spiral((32, 32), turns=1.25, outer=23, inner=5,
                             start=2.5))
    # <b>The head has to be a head, not the thick end of a rope.</b>
    # It used to peak at 8.0 against a body of 5.8 - a bulge of forty
    # per cent, which at four design units to the pixel is under one
    # pixel of difference, so the eye landed on what read as another
    # coil segment and the animal had no findable front. It peaks at
    # 11.6 now and the neck behind it is pinched to 3.4, which is the
    # part that actually does the work: a head reads by the narrowing
    # behind it, not by its own width.
    fish.flesh(fd.profile([(0, 3.0), (0.045, 9.6), (0.100, 11.6), (0.185, 3.4),
                           (0.50, 5.8), (0.88, 3.2), (1.0, 1.5)], SLENDER),
               fd.profile([(0, 3.2), (0.045, 10.0), (0.100, 12.0), (0.185, 3.6),
                           (0.50, 6.0), (0.88, 3.2), (1.0, 1.5)], SLENDER))
    fish.light(floor=0.18, ceiling=0.97, rim=0.42)
    # <b>The mane stops at the shoulder, and that is what gave it a
    # head.</b> Run all the way round the coil - 0.14 to 0.92, eleven
    # spikes - it closed the circle, and a closed circle of spikes is a
    # cog. Nothing about the front end could get out of it, so the
    # sprite had no findable front however the head itself was drawn.
    # Ending the mane at the shoulder leaves the back two thirds as
    # plain coil, which is the contrast the head reads against.
    fish.spines(0.16, 0.58, 7, height=6.5)
    fish.caudal(spread=6, length=8, fork=0.5, rays=0)
    # Segments, through `slits` rather than `band`. The six bands this
    # replaces were shade steps, and at four tones a shade step inside
    # a body quantises into the flesh: they had never drawn anything.
    fish.slits(0.30, 0.86, 5, lo=-0.85, hi=0.85, shade=0.24)
    fish.maw(length=13, gape=0.80, teeth=3, hinge=0.075)
    fish.horns(3, 11, spread=0.54, t=0.15)
    for side in (-1, 1):
        fish.barbel(0.035, side, 7, curl=0.5)
    fish.sheen(across=-0.52, width=0.12, start=0.18, stop=0.88)
    for t in (0.46, 0.78):
        fish.spot(t, 0.52, 2.2, kind=fd.GLOW, shade=0.95)
    fish.motes([(-10, -13, 1.8), (-4, -18, 1.5)])
    fish.eye(t=0.090, across=-0.36, radius=3.4, lit=True)
    return fish


def krakenspawn():
    """A mantle, two eyes too big for it, and a skirt of arms.

    <b>A reversal, and the report that caused it was exact.</b> The
    mythic used to be a Leviathan Spawn - a big blue fish with a sail,
    a maw and whiskers - and what came back was "I don't even know
    which one the leviathan is". Correct: at this size a sea serpent
    drawn as a straight body with fins is a large fish, and a large
    fish beside twenty ordinary ones is an ordinary one. A kraken's
    outline is not available to anything else.

    <b>Eight separate arms is the trap, and it caught me twice.</b>
    First at thirty-two pixels, where they came out as one blob and the
    cause turned out to be the aura rather than the arms. Then again at
    sixteen, where eight arms drawn as eight limbs read as a spider -
    straight dark bars radiating from a body, because at four design
    units to the pixel a tapered limb is a one-pixel line and a
    one-pixel line is a stick.

    <b>So the arms are one shape with notches cut up into it.</b> Which
    is what a real sheet does, and the reason is arithmetic: five arms
    across fourteen pixels leaves gaps under two pixels wide, and a
    one-pixel border eats a gap that size from both sides. A skirt with
    four notches gives five arm tips and the gaps are <em>cut</em>
    rather than left, so they survive the border. Two tentacles curl
    away from the sides where there is open water to curl into, and
    those two are the only ones drawn as limbs.
    """
    fd.zoom(1.0, (0, 0))
    fish = fd.Fish(fd.bezier([(30, 30), (32, 32), (34, 34)]))
    # <b>Three arms, and the count is arithmetic rather than anatomy.</b>
    # At four design units to the pixel an arm is one pixel wide, and a
    # one-pixel border takes a pixel off each side of every gap - so
    # two arms closer than three pixels are one arm. Three fit across
    # the tile and eight do not, however many a kraken has. The skirt
    # with notches cut in it was the other way round and read as a
    # dress: a solid trapezoid is a solid trapezoid whatever is carved
    # out of its hem.
    for root, end, bow in (((26, 41), (13, 55), -6.0),
                           ((32, 42), (32, 61), 5.0),
                           ((38, 41), (51, 55), 6.0)):
        fish.limb(root, end, thick=5.2, taper=0.58, bow=bow,
                  kind=fd.BODY, shade=0.30, over=(fd.EMPTY, fd.BODY))
    # <b>The head carries it.</b> Everything that says octopus at this
    # size is up here - a bulb wider than it is tall with two eyes far
    # too big for it. The arms only have to be present.
    fish.dome((32, 27), across=15, down=14, power=1.9,
              floor=0.14, ceiling=0.96, lift=0.30, over=(fd.EMPTY, fd.BODY))
    for x, y in ((28, 17), (36, 20)):
        fish.here(x, y, 1.8, fd.GLOW, 0.95, over=(fd.BODY, fd.MARK))
    # Suckers, down the two arms that have room for them. On the
    # middle one they would land where the three roots overlap and
    # read as a stain.
    for x, y in ((23, 47), (20, 52), (41, 47), (44, 52),
                 (30, 50), (34, 55)):
        fish.here(x, y, 1.4, fd.MARK, 0.96, over=(fd.BODY,))
    # <b>The mantle was seventy-six pixels of flat red.</b> Measured
    # across the set it had two marking pixels, the fewest of any
    # sprite, and the dome's own shading cannot break that up because
    # a smooth dome is exactly what the shading draws. An octopus's
    # skin is its most recognisable feature after its arms, so it gets
    # patches - placed off-centre, because a symmetrical scatter reads
    # as a pattern and a lopsided one reads as skin.
    for x, y, r in ((25, 20, 2.8), (38, 23, 2.4), (31, 16, 2.2),
                    (41, 31, 2.6), (22, 32, 2.2), (33, 35, 2.2)):
        fish.here(x, y, r, fd.MARK, 0.30, over=(fd.BODY,))
    for x in (25, 39):
        fish.stare(x, 30, radius=4.6, lit=True)
    # One spark, and clear of the bell. Two of these sat right against
    # the mantle's top edge and read as a chipped pixel rather than as
    # anything thrown off.
    fish.motes([(-11, -17, 1.6)])
    return fish


def starfall_koi():
    """Slow, showy, and shedding sparks it will not get back.

    <b>A koi is a fish defined by its blotches, and this one had
    twenty pixels of glitter instead.</b> Counted off the grid: thirty
    body pixels, twenty-one fin, and <em>twenty</em> glow - six lit
    spots scattered down the flank, a ring orbiting it and seven
    motes. Two-thirds as much sparkle as animal, spread evenly enough
    that none of it read as anything. What arrived was a pink blob.

    So the glitter is concentrated instead of scattered. The on-body
    spots are gone: they were competing with the thing that actually
    makes a koi legible, which is big irregular patches of a second
    colour. Those are drawn in MARK, because at four tones a patch
    drawn as a shade step lands in the same bucket as the flesh. The
    comet survives as a short trail of motes off the tail, where it is
    <em>outside</em> the silhouette and so cannot muddy it, and that is
    also the only place a spark can be and still look thrown.
    """
    fish = shaped((14, 43.0), (27, 36.4), (41, 32.0),
                  [(0, 2.0), (0.10, 8.4), (0.34, 12.6), (0.74, 5.6), (1.0, 3.0)],
                  [(0, 2.2), (0.10, 9.4), (0.36, 14.0), (0.76, 5.6), (1.0, 3.0)],
                  nudge=(0, -1))
    fish.light(floor=0.16, ceiling=0.98, rim=0.42)
    fish.gill(0.24, depth=0.20)
    fish.mouth()
    # <b>Fewer shapes on the outline, each drawn large.</b> Judged by
    # the silhouette test described on the tidewrack shark: render the
    # sprite flat black and see whether it still names the animal. A
    # handful of two-pixel fins leaving the body at different angles
    # does not survive that test - they merge into roughness. The
    # detail inside the silhouette is untouched.
    fish.ribbon(spread=9, length=15, sway=4)
    fish.sail(0.20, 0.68, height=13, peak=0.55)
    fish.paddle(0.26, length=14, drop=8, lean=0.85, rays=4)
    # The blotches, which are the fish. Three large ones rather than
    # six small: at this size a two-pixel patch is a speck.
    fish.mottle(((0.30, -0.46), (0.52, 0.30), (0.72, -0.40)), radius=3.4,
                shade=0.30)
    fish.slits(0.40, 0.64, 2, lo=-0.70, hi=0.70, shade=0.26)
    for side in (-1, 1):
        fish.barbel(0.06, side, 6, curl=0.5)
    fish.sheen(across=-0.60, start=0.22, stop=0.80)
    # The comet, and the part that is not attached to anything. Kept
    # off the body on purpose - a spark inside the silhouette is a
    # smudge, and a spark outside it is a spark.
    fish.motes([(7, -7, 1.8), (12, -5, 1.5), (16, -8, 1.2), (11, 7, 1.5)])
    fish.eye(t=0.19, across=-0.34, radius=3.0, lit=True)
    return fish
def zaratan():
    """The island-turtle: a carapace with a forest on it, and flippers.

    <b>Side on, after three attempts at redrawing it from an angle
    were all worse.</b> The complaint was fair - side on, a turtle is a
    dome with legs under it, a letterbox that leaves all four corners
    of the square empty. Plan view fixes the corners and loses the
    animal, because everything that says turtle is a thing you can only
    see from the side of it. Three-quarter is the right answer in
    principle and needs the shell to be most of the silhouette; thrown
    out, the flippers measured three times the shell's width, so
    seating it left a five-pixel shell with sticks on it, and pulled in
    they stopped reading as flippers at all.

    None of the three was recognisable as a turtle, and this one is.
    That settles it until somebody has a better idea than "at an
    angle": a sprite that reads is worth more than a framing that is
    theoretically better use of the tile.

    <b>In place of the Worldscale, which was a plate.</b> That one was
    deliberately not a creature - its own flavour line said the fish was
    never on the end of the line - and it took four tries to stop
    reading as food before it settled as a bevelled rhombus. It was
    still a bevelled rhombus, and the report on it was that it did not
    look mythical. Fair: a shape with no eye and no limbs has nothing to
    be mythical <em>about</em>.

    So: the aspidochelone, the zaratan, the island that sailors moor to
    and then lose. It keeps what the Worldscale was reaching for - a
    thing too large to see the whole of - and it has the one silhouette
    in the set built from a dome, four limbs and three trees.

    <b>The carapace has to be a lid, not a tub.</b> Drawn as a whole
    superellipse the shell's lower half is the widest thing on the
    sprite and the animal reads as a bathtub with a fern in it. So it
    goes down first, on an empty grid, and is cut flat at the rim
    before anything else exists to be cut with it; the body, the
    flippers and the head are then drawn underneath with `over` set to
    EMPTY so they tuck beneath rather than over.

    The soil runs across the crown only. Followed all the way round the
    rim - which is the obvious way to write it - it turns the shell
    green from edge to edge and the dome stops reading at all.
    """
    fd.zoom(0.90, (2, -1))
    fish = fd.Fish(fd.bezier([(30, 30), (32, 32), (34, 34)]))
    rim, cx, rx, ry = 37.0, 34.0, 21.0, 15.0

    def surface(x):
        k = min(1.0, abs(x - cx) / rx)
        return rim - ry * (1 - k ** 2.0) ** 0.5

    fish.dome((cx, rim), across=rx, down=ry, power=2.0,
              floor=0.20, ceiling=0.97, lift=0.30)
    for y in range(SIZE):
        for x in range(SIZE):
            if fish.kind[y][x] == fd.BODY and (y + 0.5) / fd.K > rim:
                fish.kind[y][x] = fd.EMPTY
    for radius in (8.0, 15.0):
        fish.arc(fd.place(cx, rim), radius, math.pi + 0.12,
                 2 * math.pi - 0.12, thick=1.0, kind=fd.MARK, shade=0.14,
                 over=(fd.BODY,))
    for angle in (3.55, 3.93, 4.32, 4.71, 5.10, 5.49, 5.87):
        fish.limb((cx + math.cos(angle) * 15.5, rim + math.sin(angle) * 11.0),
                  (cx + math.cos(angle) * 21.5, rim + math.sin(angle) * 15.5),
                  thick=1.0, taper=0.0, kind=fd.MARK, shade=0.14,
                  over=(fd.BODY,))
    fish.dome((cx, 41), across=15.5, down=5.0, power=2.2, floor=0.10,
              ceiling=0.62, lift=0.08, over=(fd.EMPTY,))
    for near, toe, thick in (((24, 39), (13, 50), 5.4), ((45, 39), (53, 48), 4.8)):
        fish.limb(near, toe, thick=thick, taper=0.44, kind=fd.BODY,
                  shade=0.26, over=(fd.EMPTY,))
    fish.limb((22, 36), (12, 36), thick=5.2, taper=0.10, kind=fd.BODY,
              shade=0.34, over=(fd.EMPTY,))
    # <b>Darker than it was.</b> At floor 0.30 / ceiling 0.96 the head
    # was the palest thing on the sprite - brighter than the shell it
    # belongs to - and read as a sheep's. A turtle's head is the same
    # leather as its legs.
    fish.dome((10, 35), across=6.6, down=5.2, power=1.9, floor=0.16,
              ceiling=0.58, lift=0.14, over=(fd.EMPTY,))
    fish.here(5.5, 36.5, 1.6, fd.MARK, 0.12, over=(fd.BODY,))
    for i in range(22):
        x = cx - rx * 0.70 + 2 * rx * 0.70 * i / 21.0
        fish.here(x, surface(x) + 1.2, 1.8, fd.MARK, 0.30, over=(fd.BODY,))
    for x, height, radius, lantern in ((23, 4, 4.2, False), (34, 7, 5.0, True),
                                       (44, 3, 3.6, False)):
        top = surface(x)
        fish.limb((x, top + 1), (x, top - height), thick=2.0, taper=0.3,
                  kind=fd.MARK, shade=0.18, over=(fd.EMPTY,))
        fish.here(x, top - height - radius * 0.5, radius, fd.FIN, 0.46,
                  over=(fd.EMPTY, fd.MARK))
        fish.here(x - radius * 0.36, top - height - radius * 0.9,
                  radius * 0.48, fd.FIN, 0.92, over=(fd.FIN,))
        if lantern:
            # Somebody lit a fire on it once, and it is still up there.
            fish.here(x + radius * 0.7, top - height + 1, 1.2, fd.GLOW, 0.97,
                      over=(fd.EMPTY, fd.FIN, fd.MARK))
    fish.here(47, surface(47) - 1.5, 3.2, fd.MARK, 0.34, over=(fd.EMPTY, fd.BODY))
    # <b>The plates go on last, and dark.</b> They used to be drawn
    # immediately after the dome, in the same MARK as the soil and at a
    # similar shade, so the crown buried the ones it crossed and the
    # rest had nothing to contrast against: the shell came out a plain
    # brown hump. Drawn after everything, at the dark end of MARK, they
    # are the one thing that makes it a carapace rather than a rock.
    for radius in (7.5, 14.0):
        fish.arc(fd.place(cx, rim), radius, math.pi + 0.16,
                 2 * math.pi - 0.16, thick=1.0, kind=fd.MARK, shade=0.04,
                 over=(fd.BODY, fd.MARK))
    for angle in (3.66, 4.19, 4.71, 5.24, 5.76):
        fish.limb((cx + math.cos(angle) * 6.0, rim + math.sin(angle) * 4.5),
                  (cx + math.cos(angle) * 20.5, rim + math.sin(angle) * 14.5),
                  thick=1.0, taper=0.0, kind=fd.MARK, shade=0.04,
                  over=(fd.BODY, fd.MARK))
    # <b>Small.</b> At 2.2 the pale socket was half the head and the
    # whole front of the animal read as white. Vanilla puts one dark
    # pixel in a patch of the body's own lightest tone, and the patch
    # is a patch, not a face.
    # <b>Unlit.</b> `lit` surrounds the pupil with a patch of the
    # palest tone, which is right on a pale fish - it is what vanilla
    # does - and wrong on a head deliberately shaded down to leather:
    # a two-pixel white patch on dark brown read as a white snout.
    fish.stare(9, 34.5, radius=1.5)
    return fish


#: <b>The sprite table has no band column any more.</b> It had one -
#: PLAIN, LIT, BURNING - and all it ever did was pick how many rings of
#: aura `pixels` drew round the outside. The aura is gone (see
#: fishdraw.Fish.pixels), so the column fed nothing. Which band a fish
#: is in lives in Fish.java, where it decides the odds; how loud it
#: looks lives in its own maker, where it decides the drawing.
FISH = {
    "glass_minnow": (glass_minnow, pal("24454f", "6b96a3", "a5cbd6", "dcf1f7", "bfe3ee", "ffffff")),
    "copper_dace": (copper_dace, pal("331c0f", "703c1c", "a85f28", "d98f45", "b8702f", "4e9480")),
    "silt_carp": (silt_carp, pal("221a0f", "4a3a22", "756039", "a08a5c", "5c4a2c", "8fa06a")),
    "nettle_dart": (nettle_dart, pal("24300c", "4e6418", "7d9a28", "b3cc55", "63801f", "d8ee7a")),
    "hollow_roach": (hollow_roach, pal("23232b", "474956", "6f7183", "a3a7b8", "595c6d", "d9dce8")),
    "saltwhisker": (saltwhisker, pal("2b2e26", "585d4d", "878d76", "b6bda3", "9aa188", "edf0e0")),
    "shorecrab": (shorecrab, pal("3d1008", "8a2a12", "c9502a", "f08a5a", "a83a1c", "ffd9c0")),
    "reed_prawn": (reed_prawn, pal("3b2026", "7a4650", "b87380", "e8b0b6", "9c5a62", "8f5a63")),
    "rivershell": (rivershell, pal("2e2318", "63513a", "9a8565", "cfbe9c", "7d6a4c", "b58fb0")),
    "silt_star": (silt_star, pal("331d10", "6d3a20", "a85f33", "d99a5e", "8a4c28", "f0d2a0")),
    "emberfin": (emberfin, pal("45190c", "8a3514", "c75f22", "f6a845", "ff8c2b", "ffe08a")),
    "moonscale": (moonscale, pal("222b45", "4a5a80", "7e8fb8", "c3d0ec", "dfe8fa", "ffffff", "aebde6")),
    "bramble_eel": (bramble_eel, pal("1d2a18", "3d5830", "61844a", "92b676", "2e4423", "cfe0a8")),
    "lantern_smelt": (lantern_smelt, pal("262413", "5f5920", "9b8f2b", "d6c646", "6d6626", "fff6b0", "ffe873")),
    "ash_lamprey": (ash_lamprey, pal("1a1418", "3a2e38", "5e4d5a", "8c7786", "463a44", "d8b8cf")),
    "driftbell": (driftbell, pal("1b1733", "3a3466", "6b63a8", "aaa2e0", "cfc8ff", "ffffff", "d8cfff")),
    "stormtail": (stormtail, pal("07102b", "133a85", "2070d6", "63b4ff", "cfeaff", "ffffff", "9fd4ff")),
    "voidgill": (voidgill, pal("0b0618", "2a1060", "4d23a8", "8d5df0", "35178a", "e6d4ff", "b388ff")),
    "mirelash": (mirelash, pal("07180a", "15541f", "2e9433", "61d957", "123f16", "b6ff7a", "9bff66")),
    "tidewrack_shark": (tidewrack_shark, pal("0d1620", "28404f", "4a6a7d", "9fc0cf", "32505f", "e8f6ff", "bfe6ff")),
    "abyss_ray": (abyss_ray, pal("070a1c", "17204a", "2c3a80", "6a7ad0", "1d2860", "9ff0ff", "7fe8ff")),
    "starfall_koi": (starfall_koi, pal("2b0a35", "6b1573", "b426a8", "ff7fe0", "e85fd0", "ffffff", "ffa8ec")),
    "leviathan": (leviathan, pal("06192a", "11506e", "1b86a8", "7fe4f5", "0d3a55", "d6fbff", "7fe9ff")),
    "krakenspawn": (krakenspawn, pal("1a0308", "5e0d1c", "a81d33", "f0566b", "38060f", "ffd9c2", "ff8a5c")),
    "zaratan": (zaratan, pal("14100c", "3d342a", "6d6052", "a79887", "2f6b2c", "cdbda0", "bfe6c8")),
}


def draw(fish_id, shrink, offset):
    """One render of one fish at a given scale and nudge."""
    maker, palette = FISH[fish_id]
    fd.SHRINK, fd.OFFSET = shrink, offset
    fd.zoom(1.0)
    fish = maker()
    # No chunking: at sixteen a pixel already is a whole vanilla pixel,
    # so there is nothing finer than the grid to flatten. See
    # fishdraw.SIZE for why the grid moved rather than the styling.
    # Trim pixels hanging off the silhouette by a single corner. See
    # fishdraw.despur: vanilla runs at 1.2% of painted pixels and ours
    # ran at 6.2%, which was the last visible difference between the
    # two sets once fill and tone count had been matched.
    fish.despur()
    fish.outline()
    return fish.pixels(palette)


def extent(pixels):
    """The drawn bounding box, or None for an empty sprite."""
    xs = [x for y in range(SIZE) for x in range(SIZE) if pixels[y][x][3]]
    ys = [y for y in range(SIZE) for x in range(SIZE) if pixels[y][x][3]]
    if not xs:
        return None
    return min(xs), min(ys), max(xs), max(ys)


#: How much margin a sprite leaves, per side.
#:
#: <b>One, which is what vanilla does, and the measurement said so
#: before I read it properly.</b> Decoding Minecraft 26.2's own item
#: textures puts the cod, the salmon and the tropical fish in a 16x16
#: tile with their drawn box at x2-14 by y1-14 - a pixel of margin top
#: and bottom, two at the sides. The pufferfish is the one that runs
#: x0-15, and it is the exception rather than the rule because it is a
#: ball; taking it as the rule is how this briefly shipped at zero,
#: with every sprite welded to its own corners.
#:
#: The number that matters is still the one it replaced: these used to
#: sit in about seventy per cent of their square, which at sixteen
#: pixels is eleven pixels of fish where fourteen will fit.
MARGIN = 1


def seated(fish_id, shrink):
    """Draw at this scale, centre it, and say where it landed.

    <b>Centred more than once, because moving it moves it.</b> The
    offset is computed from where the sprite landed and then applied by
    redrawing, and the redraw rounds to whole pixels again - so one
    pass leaves a sprite up to a pixel off centre, which costs it a
    whole size step: the bisection sees one side touching the margin
    and stops, when the shape would have fitted a notch larger had it
    been sitting straight. Three passes converge.
    """
    pixels = draw(fish_id, shrink, (0.0, 0.0))
    offset = (0.0, 0.0)
    for _ in range(3):
        box = extent(pixels)
        if box is None:
            return pixels, None
        slide = ((SIZE - 1 - box[2] - box[0]) / 2,
                 (SIZE - 1 - box[3] - box[1]) / 2)
        if abs(slide[0]) < 0.5 and abs(slide[1]) < 0.5:
            break
        offset = (offset[0] + slide[0] / fd.K, offset[1] + slide[1] / fd.K)
        pixels = draw(fish_id, shrink, offset)
    return pixels, extent(pixels)


def roomy(box):
    """Whether a drawn box keeps its margin on all four sides."""
    return (box is not None
            and box[0] >= MARGIN and box[1] >= MARGIN
            and box[2] <= SIZE - 1 - MARGIN and box[3] <= SIZE - 1 - MARGIN)


def build(fish_id):
    """Seat the sprite at the largest size that still keeps its margin.

    <b>Found by bisection, because growing until it touches is not the
    same as being the right size.</b> The first version of this scaled
    up until the drawn box hit the tile edge and then backed off a
    blunt six per cent, which is fine when one step does it and
    terrible when three do: a sprite that needed several ends up well
    under the size it could have had, and the set came out with its
    smallest member at twenty-four per cent of its tile against
    vanilla's floor of thirty-five. Small sprites are what read as
    blobs - the internal gaps go first.

    So: bisect the scale, and keep the largest one whose drawn box
    still has a pixel of margin on all four sides. Every probe is a
    full re-render at its own scale rather than a transform of the last
    one, so nothing is ever resampled - the sprite that ships was drawn
    once, at its final size, by the code that decided its shape.

    Centring happens inside each probe, because a fish does not sit in
    the middle of its own bounding box - one with a long tail hangs off
    to one side, and measuring before centring would reject a scale
    that fits perfectly well once it is moved.
    """
    low, high, best = 0.20, 4.0, None
    for _ in range(14):
        mid = (low + high) / 2
        pixels, box = seated(fish_id, mid)
        if roomy(box):
            best, low = pixels, mid
        else:
            high = mid
    if best is None:
        best, _ = seated(fish_id, 0.20)
        print("  ! %s will not seat in its tile" % fish_id)
    pixels = best
    fd.SHRINK, fd.OFFSET = 1.0, (0.0, 0.0)

    textures = os.path.join(PACK, "assets", "forever", "textures", "item")
    models = os.path.join(PACK, "assets", "forever", "models", "item")
    items = os.path.join(PACK, "assets", "forever", "items")
    for directory in (textures, models, items):
        os.makedirs(directory, exist_ok=True)
    write_png(os.path.join(textures, "%s.png" % fish_id), SIZE, SIZE, pixels)
    with open(os.path.join(models, "%s.json" % fish_id), "w") as handle:
        json.dump({"parent": "minecraft:item/generated",
                   "textures": {"layer0": "forever:item/%s" % fish_id}},
                  handle, indent=2)
        handle.write("\n")
    with open(os.path.join(items, "%s.json" % fish_id), "w") as handle:
        json.dump({"model": {"type": "minecraft:model",
                             "model": "forever:item/%s" % fish_id}},
                  handle, indent=2)
        handle.write("\n")


def fits(pixels):
    """Whether a sprite ended up inside its own texture.

    <b>Added after the top bands were scaled up to look like the band
    they are.</b> Growing them is the right instinct and it is how four
    of them came to have their tails cut off square at the edge of the
    tile - which at a glance reads as a drawing mistake rather than as
    a big fish. Nothing else in the pipeline would say so: a clipped
    sprite builds, publishes and renders perfectly happily.

    <b>It no longer complains about touching the edge, because the
    build now aims there.</b> Vanilla's own pufferfish runs from pixel
    nought to pixel fifteen. What it still catches is a sprite that
    came out empty or stuck to one side, which is what a broken maker
    looks like.
    """
    box = extent(pixels)
    if box is None:
        return False
    minX, minY, maxX, maxY = box
    return maxX - minX >= SIZE // 2 and maxY - minY >= SIZE // 3


def check_against_java():
    """A sprite whose id is not a fish is a missing-model cube in game."""
    java = os.path.join(os.path.dirname(os.path.dirname(PACK)),
                        "forever-plugin", "items", "src", "main", "java",
                        "dev", "forever", "items", "fish", "Fish.java")
    if not os.path.exists(java):
        return
    import re
    ids = set(re.findall(r'"([a-z_]+)", "[A-Z]', open(java).read()))
    mine = set(FISH)
    if ids and ids != mine:
        raise SystemExit(
            "the catalogue and the sprites disagree.\n"
            "  in Fish.java only: %s\n"
            "  in build_fish only: %s" % (sorted(ids - mine), sorted(mine - ids)))


def main():
    check_against_java()
    print("Building Forever fish sprites")
    for fish_id in FISH:
        build(fish_id)
    print("  %d fish at %dx%d" % (len(FISH), SIZE, SIZE))


if __name__ == "__main__":
    main()
