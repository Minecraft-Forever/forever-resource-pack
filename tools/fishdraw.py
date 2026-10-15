"""
A drawing engine for the fish sprites, at four times vanilla's resolution.

<b>The fourth attempt, and the first at a size where detail is possible.</b>
The three before it were all sixteen by sixteen, because that is what
vanilla's items are. Two were generated and came out as torpedoes and
then as lumps; the third was drawn by hand and read correctly but was
still sixteen pixels, which is about thirty pixels of fish once the
transparent margin is gone. There is no amount of care that puts a gill
plate, a lateral line, scales and a lit eye into thirty pixels.

A resource pack is not held to sixteen. Item textures may be any power
of two - the 32x and 64x packs people have run for years are exactly
this - because `minecraft:item/generated` builds its model from the
alpha contour at whatever resolution it finds, and the model's size in
the world is fixed regardless. So these are sixty-four square, and a
fish gets roughly a thousand pixels of body to carry detail instead of
forty.

At that size the hand-drawn approach stops being the right one - four
thousand pixels per fish, two dozen of them - and generating becomes right,
which reverses the previous decision for the previous reason: the tool
should fit the size. What failed at sixteen was not generation itself,
it was that at sixteen pixels there is no room for a fin to be a pixel
off. At sixty-four there is.

What goes into each fish:

  * a body grown on a curved spine, with its own back and belly profile
  * countershading - dark along the back, pale at the belly, with a lit
    rim on top, which is how a real fish is coloured and why one reads
    as rounded rather than flat
  * a diamond scale lattice, faded out over the head and near the edges
  * a gill plate, a lateral line, a mouth
  * fins built as polygons with ray lines drawn through them
  * an eye with an iris, a pupil and a highlight

and then the whole thing is quantised to eight tones off a per-fish
ramp, which is what keeps it pixel art rather than a smooth render.
"""

import math

#: The grid the fish are described on, and the grid they are drawn on.
#:
#: <b>Sixty-four, then thirty-two, and finally back to vanilla's
#: sixteen - which was tried first and rejected first.</b> Sixty-four
#: had room for a gill plate and a lit eye and came out looking
#: rendered. Thirty-two was the classic 2x pack and survived four
#: rounds of "make it look more like Minecraft": fewer tones, no scale
#: lattice, a blacker border, a two-pixel border. Every one of them
#: helped and none of them finished the job, and the report after the
#: last was "sure the edges are blocky, but they look way too real
#: still".
#:
#: They do, and the reason is simple arithmetic that no amount of
#: styling gets round: a 32x sprite in a 16-pixel slot draws every
#: feature at half a vanilla pixel. Minecraft is made of whole ones.
#:
#: The first attempt at sixteen failed and the failure was real, but it
#: was not the resolution's fault - it was three hand-drawn sprites and
#: a generator that could only make torpedoes. The engine since then
#: grew a spine, profiles, fins, a maw, superellipses, limbs and a
#: coil, all described on a 64-unit grid and scaled on the way out, so
#: going back to sixteen costs the descriptions nothing. It is one
#: number.
#:
#: Everything below is written in DESIGN units and scaled on the way
#: in, so the descriptions read at the size they were composed at and
#: the output size is that one number.
DESIGN = 64
SIZE = 16
K = SIZE / DESIGN


#: A per-fish shrink, about the middle of the design grid.
#:
#: <b>One knob, because the alternative was retuning every number in a
#: maker.</b> Scaling the top bands up so they read as the band they are
#: is the right instinct and it is how several of them came to have
#: their tails cut off square at the edge of the tile. This pulls a
#: whole fish in without changing the proportions anybody tuned by eye.
#: `build()` resets it, and `check_fits` is what says when it is needed.
ZOOM = 1.0

#: A per-fish nudge in design units, applied after ZOOM.
#:
#: Most of what hangs off the edge of a tile hangs off <em>one</em> edge
#: by a pixel or two, because the fish is a little off centre rather
#: than too big. Shrinking it for that costs the size ladder the bands
#: are carried by, so this moves it instead.
SHIFT = (0.0, 0.0)


#: A shrink applied on top of whatever a maker asks for.
#:
#: <b>So that fitting the tile is the build's job and not a tuning
#: number in twenty-five makers.</b> Every maker's `zoom` is an
#: artistic choice - how much of its square this animal should fill -
#: and every one of them had been nudged by hand until `check_fits`
#: stopped complaining. That is fine until something global moves: the
#: border went from one pixel to two and nine sprites clipped; the grid
#: went from thirty-two to sixteen and nine clipped again, a different
#: nine. Hand-fitting the same numbers twice is the sign they should
#: not be hand-fitted.
#:
#: `build` now measures what a maker drew and scales it to fill the
#: tile, so a maker says what shape its animal is and the build decides
#: how big that comes out.
#:
#: <b>Filling the tile is most of what "looks like Minecraft" turned
#: out to mean.</b> Four rounds went at it through styling and a fifth
#: through resolution, and the thing nobody had looked at was that
#: these sprites sat in about seventy per cent of their square with
#: transparent margin all round, where every fish on a real mod sheet
#: runs edge to edge. At sixteen pixels that margin is the difference
#: between eleven pixels of fish and sixteen - which is to say about
#: double the detail, for free, at exactly the same pixel size.
SHRINK = 1.0


def zoom(amount, nudge=(0.0, 0.0)):
    global ZOOM, SHIFT
    ZOOM, SHIFT = amount * SHRINK, nudge


def px(value):
    """A length in design units, as a length on the drawn grid."""
    return value * K * ZOOM


#: A centring nudge in design units, on top of whatever a maker asks.
#:
#: The other half of SHRINK. Scaling a sprite up to fill its tile moves
#: it off centre unless the thing was centred to begin with, and almost
#: none of them are - a fish with a long tail sits left of middle. The
#: fit pass measures where it actually landed and puts this right.
OFFSET = (0.0, 0.0)


def place(x, y):
    """A point in design units, as a point on the drawn grid."""
    middle = DESIGN / 2
    return ((middle + (x - middle) * ZOOM + SHIFT[0] + OFFSET[0]) * K,
            (middle + (y - middle) * ZOOM + SHIFT[1] + OFFSET[1]) * K)


def rays_for(count):
    """Fin rays thin out with the grid; seven of them on a seven pixel tail
    is a solid block."""
    return max(1, int(round(count * K * 0.6)))


EMPTY = ""
BODY = "body"
FIN = "fin"
MARK = "mark"
GLOW = "glow"
IRIS = "iris"
PUPIL = "pupil"
EDGE = "edge"


def bezier(control, steps=180):
    """A Bezier of whatever degree the control points give, as (t, x, y)."""
    control = [place(x, y) for x, y in control]
    out = []
    for i in range(steps + 1):
        s = i / steps
        points = list(control)
        while len(points) > 1:
            points = [((1 - s) * a[0] + s * b[0], (1 - s) * a[1] + s * b[1])
                      for a, b in zip(points, points[1:])]
        out.append((s, points[0][0], points[0][1]))
    return out


def spiral(centre, turns, outer, inner, start=0.0, steps=200):
    """A coil, for the one fish whose shape is the coil.

    A Bezier cannot loop back past itself, so the serpent drawn with one
    came out as an arch - a rainbow with a head on it. This winds.
    """
    centre = place(*centre)
    outer, inner = px(outer), px(inner)
    out = []
    for i in range(steps + 1):
        k = i / steps
        angle = start + turns * 2 * math.pi * k
        radius = outer + (inner - outer) * k
        out.append((k, centre[0] + math.cos(angle) * radius,
                    centre[1] + math.sin(angle) * radius))
    return out


def reared(centre, turns, outer, inner, start, head, neck=0.32, steps=220):
    """A coil with the head lifted clear of it, rather than lying in it.

    <b>`spiral` puts the head on the outside of the coil, which is the
    mirecoil and is already taken.</b> The leviathan drawn as an arch
    read as a rearing serpent and nothing else, and the report on it
    was that the mirecoil - a plain coil one band below - looked more
    interesting. It does: a coil is more shape than an arch is.

    So this is both. The last two thirds wind like `spiral`; the first
    third is a quadratic from a head placed anywhere, with its control
    point thrown out perpendicular to the line between the two, so the
    neck arrives at the coil tangentially instead of kinking into it.
    """
    cx, cy = centre
    ax = cx + math.cos(start) * outer
    ay = cy + math.sin(start) * outer
    bx = (head[0] + ax) / 2 - (ay - head[1]) * 0.42
    by = (head[1] + ay) / 2 + (ax - head[0]) * 0.42
    out = []
    for i in range(steps + 1):
        k = i / steps
        if k < neck:
            s = k / neck
            x = (1 - s) ** 2 * head[0] + 2 * s * (1 - s) * bx + s * s * ax
            y = (1 - s) ** 2 * head[1] + 2 * s * (1 - s) * by + s * s * ay
        else:
            s = (k - neck) / (1 - neck)
            angle = start + turns * 2 * math.pi * s
            radius = outer + (inner - outer) * s
            x = cx + math.cos(angle) * radius
            y = cy + math.sin(angle) * radius
        out.append((k,) + place(x, y))
    return out


def serpentine(start, end, waves, amplitude, steps=240, settle=0.18):
    """A body that undulates along a line: humps, rather than a coil.

    <b>The amplitude is set by the border and the aura, not by taste.</b>
    Adjacent humps are 2*amplitude apart and the body eats 2*half-width
    of that; what is left has to survive a one-pixel border on each
    facing edge and, on a mythic, two rings of aura as well. Under
    about ten design units of amplitude all of that meets in the middle
    and the humps fuse into a lumpy sausage - which is exactly what the
    first three attempts were. Fewer, larger bends read; more, smaller
    ones do not.

    `settle` ramps the wave in over the first stretch, so the head sits
    still instead of being flung out on the first crest.
    """
    ax, ay = start
    bx, by = end
    dx, dy = bx - ax, by - ay
    length = max(1e-6, math.hypot(dx, dy))
    nx, ny = -dy / length, dx / length
    out = []
    for i in range(steps + 1):
        k = i / steps
        grow = min(1.0, k / settle) if settle else 1.0
        swing = amplitude * grow * math.sin(waves * 2 * math.pi * k)
        out.append((k,) + place(ax + dx * k + nx * swing,
                                ay + dy * k + ny * swing))
    return out


#: How deep every body is, against the depth its maker asked for.
#:
#: <b>One number, because the whole set was too thin in the same way
#: and for the same reason.</b> Each profile was tuned by eye on a
#: 64-unit grid where a fish is forty units long and eight deep, which
#: looks right in isolation and is nothing like a real sheet: decoding
#: Minecraft's own cod puts its drawn pixels at 38% of its tile and
#: these were coming out at 23%. A sprite that thin is a streak
#: crossing a mostly empty square, and no amount of scaling it up
#: fixes that - scaling makes the streak longer too.
#:
#: Applied here rather than in twenty-five makers so that the depth of
#: the set is a thing that can be dialled and measured, which is how
#: it was settled: raise it, rebuild, compare the drawn-pixel density
#: against vanilla's 35-57%.
#:
#: <b>It works with the tilt and not on its own.</b> Deepening a body
#: that runs at forty degrees across the tile just makes a fatter
#: diagonal - the sprite still crosses a mostly empty square, because
#: the empty part is the two corners the diagonal misses. The fish on
#: a real sheet are both deep <em>and</em> shallowly tilted, around
#: twenty degrees, so the body lies along the square rather than
#: across it and the depth has somewhere to go. Fifteen spines were
#: flattened from thirty-three to forty-four degrees down to
#: twenty-two at the same time as this went up, and neither change
#: reads properly without the other.
GIRTH = 1.4

# <b>How much of the sprite the dark border is allowed to be.</b> At
# sixty-four pixels a one-pixel border was a thirtieth of the body and
# bought the blocky edge every detailed sprite of this kind has. The
# grid then moved to sixteen and the border came with it without being
# re-argued, which was a mistake worth measuring: decoded against the
# vanilla textures, our sprites were spending 50% of their painted
# pixels on border (mirelash 75%, zaratan 71%, krakenspawn 70%) where
# vanilla spends 15% - and cod and pufferfish spend none at all. Fill
# and colour count already matched vanilla almost exactly; the border
# was the entire difference, and it was eating the space that the
# detail was supposed to go in.
BORDER = 0
# Not near-black. Vanilla's darkest cod pixel is (107, 68, 43), a dark
# version of its own flesh rather than a line drawn around it.
BORDER_DARK = 0.70


def profile(pairs, scale=1.0):
    """Half-width down the body: piecewise linear through (t, width) pairs."""
    pairs = sorted((t, px(w * scale * GIRTH)) for t, w in pairs)

    def width(t):
        if t <= pairs[0][0]:
            return pairs[0][1]
        for (t0, w0), (t1, w1) in zip(pairs, pairs[1:]):
            if t <= t1:
                k = (t - t0) / max(1e-9, t1 - t0)
                return w0 + (w1 - w0) * k
        return pairs[-1][1]
    return width


def _mix(a, b, k):
    return tuple(int(round(a[i] + (b[i] - a[i]) * k)) for i in range(3))


def lighten(colour, k):
    return _mix(colour, (255, 255, 255), k)


def darken(colour, k):
    return _mix(colour, (0, 0, 0), k)


#: <b>The smallest luminance step between any two tones a sprite uses.</b>
#: Decoded from the vanilla item textures, the cod's five tones step by
#: 41, 26, 25 and 33 - every one a jump the eye resolves, so each pixel
#: reads as its own block. Ours averaged a minimum gap of 6, and the
#: worst sprites had gaps of 0, 1 and 2: the tidewrack shark's ramp ran
#: 0, 23, 13, 20, 50, 12, 66, meaning two of its tones were different
#: colours at identical lightness.
#:
#: Two pixels that differ by one or two points of luminance do not read
#: as two pixels. They read as one smudged area, which is what is left
#: once the silhouette is legible and the sprite still looks unclear.
#:
#: The cause is structural rather than a bad palette: BODY, FIN, MARK
#: and GLOW each ramp from their own base colour across the same
#: `LEVELS` steps, and nothing stops a fin mid-tone landing exactly
#: where a body mid-tone already is.
SEPARATION = 20.0


def _lum(colour):
    return 0.2126 * colour[0] + 0.7152 * colour[1] + 0.0722 * colour[2]


def _relight(colour, target):
    """Move a colour to a target luminance, keeping its hue."""
    now = _lum(colour)
    if now <= 1.0:
        level = int(max(0, min(255, round(target))))
        return (level, level, level)
    scale = target / now
    out = [int(max(0, min(255, round(v * scale)))) for v in colour]
    # Scaling cannot lighten a colour past white, so lift what is left
    # toward white instead of letting the step collapse.
    short = target - _lum(tuple(out))
    if short > 1.0:
        out = [int(max(0, min(255, round(v + short)))) for v in out]
    return tuple(out)


def spread(grid, gap=None):
    """Push a sprite's tones apart so no two are closer than `gap`.

    Works on the finished pixels rather than on the ramps, because what
    matters is the tones that actually ended up next to each other -
    a collision between a ramp's unused ends costs nothing.

    Only tones holding real area are moved. A one-pixel accent sitting
    between two body tones is not a ramp step and spacing it would
    shove the whole ladder apart for nothing.
    """
    gap = SEPARATION if gap is None else gap
    tally = {}
    for row in grid:
        for pixel in row:
            if pixel[3]:
                tally[pixel[:3]] = tally.get(pixel[:3], 0) + 1
    total = sum(tally.values())
    if not total:
        return grid
    ranked = sorted(tally, key=_lum)
    # A tone worth spacing: at least 4% of the sprite, or 3 pixels.
    solid = [c for c in ranked if tally[c] >= max(3, total * 0.04)]
    if len(solid) < 2:
        return grid
    # <b>The ladder has to fit between the darkest tone and white, and
    # checking that at the end is too late.</b> Walking up the list and
    # clamping whatever overshoots piles every bright tone onto the
    # ceiling, which is the exact fault this is here to remove: the
    # first version did that and left the stormtail with three tones at
    # luminance 245-246, a gap of zero.
    #
    # Nudging only where tones are too close also fails, because it
    # keeps the original wide spacing low down and runs out of room at
    # the top. So the positions are worked out first, and if the top
    # rung will not fit, the whole ladder is respaced evenly across the
    # room there actually is.
    low = _lum(solid[0])
    want = [low]
    for colour in solid[1:]:
        want.append(max(_lum(colour), want[-1] + gap))
    if want[-1] > 246.0:
        room = 246.0 - low
        even = room / (len(solid) - 1)
        want = [low + even * i for i in range(len(solid))]
    moved = {}
    for colour, target in zip(solid, want):
        if abs(target - _lum(colour)) > 0.5:
            moved[colour] = _relight(colour, target)
    if not moved:
        return grid
    return [[(moved.get(p[:3], p[:3]) + (p[3],)) if p[3] else p for p in row]
            for row in grid]


def tones(stops, levels):
    """A stepped ramp. Stepping is what keeps this pixel art and not a render."""
    out = []
    for i in range(levels):
        s = i / (levels - 1)
        for (s0, c0), (s1, c1) in zip(stops, stops[1:]):
            if s <= s1 or s1 == stops[-1][0]:
                k = (s - s0) / max(1e-9, s1 - s0)
                out.append(_mix(c0, c1, max(0.0, min(1.0, k))))
                break
    return out


class Fish:
    """One sprite under construction: what each pixel is, and how lit it is."""

    #: Four tones.
    #:
    #: <b>Down from eight, and then back up from three.</b> Eight was a
    #: smooth gradient and six still read as a render; vanilla's own
    #: cod gets about five. Three was an overshoot, taken while
    #: chasing "more Minecraft" from the colour side - and the thing
    #: that actually delivered that turned out to be the two-pixel
    #: border, not the tone count. A reference sheet from a fishing
    #: mod settled it: those sprites carry <em>more</em> tones than
    #: three and plenty of small marks, and still look blocky, because
    #: what makes them blocky is the size of the step and not the
    #: number of them. So four, with `chunk` putting the body fill in
    #: visible squares and the fins keeping their rays.
    # <b>Five tones per kind.</b> Measured against the vanilla item
    # textures our sprites carried 8.7 distinct colours against
    # vanilla's 10.3, and the shortfall showed worst on the subjects
    # with the least internal shape: the krakenspawn was down to five
    # colours in the whole tile and its mantle read as a flat red
    # cut-out.
    #
    # It has been 3 and it has been 4. Three was tried when the
    # complaint was that the sprites looked too smooth and too
    # rendered, and it cost detail that had to be given back. The
    # smoothness was never really the tone count - at sixteen pixels a
    # pixel is large enough that five tones still read as steps, not as
    # a gradient. Six is where it starts to go soft: the ray and the
    # mantle both pick up a visible ramp.
    LEVELS = 5

    def __init__(self, spine, size=SIZE):
        self.size = size
        self.kind = [[EMPTY] * size for _ in range(size)]
        self.shade = [[0.5] * size for _ in range(size)]
        self.along = [[0.0] * size for _ in range(size)]
        self.across = [[0.0] * size for _ in range(size)]
        self.back = profile([(0, 1)])
        self.belly = profile([(0, 1)])
        self.spine = []
        for index, (t, x, y) in enumerate(spine):
            lo = max(1, min(len(spine) - 2, index))
            _, x0, y0 = spine[lo - 1]
            _, x1, y1 = spine[lo + 1]
            dx, dy = x1 - x0, y1 - y0
            length = max(1e-9, math.hypot(dx, dy))
            ux, uy = dx / length, dy / length
            self.spine.append((t, x, y, -uy, ux, ux, uy))

    # -- frame ---------------------------------------------------------------

    def at(self, t):
        """The spine point at t: position, the across axis, the along axis.

        `across` is positive toward the belly, negative toward the back.
        """
        index = int(max(0.0, min(1.0, t)) * (len(self.spine) - 1))
        return self.spine[index]

    def pt(self, t, across=0.0, along=0.0):
        x, y, nx, ny, ux, uy = self.at(t)[1:]
        return (x + nx * across + ux * along, y + ny * across + uy * along)

    def edge(self, t, side):
        """A point on the body surface: side -1 is the back, +1 the belly."""
        width = self.back(t) if side < 0 else self.belly(t)
        return self.pt(t, side * width)

    # -- the body ------------------------------------------------------------

    def flesh(self, back, belly):
        """Fill the body, recording where each pixel sits along and across it."""
        self.back, self.belly = back, belly
        for y in range(self.size):
            for x in range(self.size):
                px, py = x + 0.5, y + 0.5
                best, pick = 1e18, None
                for index, (t, sx, sy, nx, ny, ux, uy) in enumerate(self.spine):
                    gap = (px - sx) ** 2 + (py - sy) ** 2
                    if gap < best:
                        best, pick = gap, index
                t, sx, sy, nx, ny, ux, uy = self.spine[pick]
                across = (px - sx) * nx + (py - sy) * ny
                width = self.back(t) if across < 0 else self.belly(t)
                if width <= 0:
                    continue
                # Past either end the nearest point is the cap, so measure
                # straight-line distance there and the snout comes out round.
                inside = (math.sqrt(best) <= width
                          if pick in (0, len(self.spine) - 1)
                          else abs(across) <= width)
                if not inside:
                    continue
                self.kind[y][x] = BODY
                self.along[y][x] = t
                self.across[y][x] = max(-1.0, min(1.0, across / width))

    def light(self, rim=0.30, floor=0.30, ceiling=0.86):
        """Countershade: dark along the back, pale at the belly, lit on top.

        This is how a fish is actually coloured, and it is the single
        thing that makes one read as a rounded body rather than a flat
        cut-out shape.
        """
        for y in range(self.size):
            for x in range(self.size):
                if self.kind[y][x] != BODY:
                    continue
                across = self.across[y][x]
                value = floor + (ceiling - floor) * (across + 1) / 2
                if across < -0.88:
                    # A thin line, not a band. Spread over the whole back it
                    # cancels the countershading it is supposed to sit on.
                    value += rim * (-across - 0.88) / 0.12
                if across > 0.84:
                    value -= 0.24 * (across - 0.84) / 0.16
                self.shade[y][x] = value

    def gill(self, t, depth=0.16):
        """The plate behind the head. One line, and the head stops being a nose."""
        span = 0.013 / K
        for y in range(self.size):
            for x in range(self.size):
                if self.kind[y][x] != BODY:
                    continue
                if abs(self.along[y][x] - t) < span \
                        and self.across[y][x] > -0.82:
                    self.shade[y][x] -= depth

    def lateral(self, across=-0.12, start=0.24, stop=0.92, shade=0.30,
                width=0.13):
        """The line down a fish's flank, in the mark colour.

        <b>Back, after being deleted with the scale lattice, and not
        for the same reason.</b> The lattice went because a per-pixel
        diamond grid is the most <em>rendered</em> thing a sprite can
        do. A lateral line is the opposite: one pixel wide, running the
        length of the body, and on more or less every fish anybody has
        drawn at this size. Taking both out in one move left nine of
        twenty-five sprites with no markings at all - flat coloured
        shapes with an eye.

        In MARK rather than as a shade step, because at four tones a
        shade step inside a body is often no step at all: it lands in
        the same bucket as the flesh around it and vanishes. A mark is
        a different colour and always shows.
        """
        for y in range(self.size):
            for x in range(self.size):
                if self.kind[y][x] != BODY:
                    continue
                if not start < self.along[y][x] < stop:
                    continue
                if abs(self.across[y][x] - across) < width:
                    self.kind[y][x] = MARK
                    self.shade[y][x] = shade

    def stripes(self, count, start=0.28, stop=0.86, width=0.035, depth=0.86,
                shade=0.26):
        """Bars across the body, in the mark colour.

        `depth` is how far down the flank they reach: one is a full
        band, a half is a row of blotches along the back.
        """
        for index in range(count):
            at = start + (stop - start) * index / max(1, count - 1)
            for y in range(self.size):
                for x in range(self.size):
                    if self.kind[y][x] != BODY:
                        continue
                    if abs(self.along[y][x] - at) > width:
                        continue
                    if abs(self.across[y][x] + 1) > 2 * depth:
                        continue
                    self.kind[y][x] = MARK
                    self.shade[y][x] = shade

    def slits(self, t0, t1, count, lo=-0.95, hi=0.55, shade=0.22, gap=1,
              kind=None):
        """Gill slits: one whole pixel each, and a clear pixel between.

        <b>The primitive that replaced counting features down.</b>
        `gill` and `band` both work by subtracting from `shade`, and at
        four tones a shade step inside a body is frequently no step at
        all - it quantises into the same bucket as the flesh around it
        and disappears. Worse, their span is a shade over half a pixel
        wide, so whether any given slit paints anything depends on
        where the body happened to land on the grid.

        Five slits drawn that way are not five slits. They are a smear
        that costs the snout its contrast and returns nothing, and the
        first conclusion drawn from the smear was the wrong one: that
        sixteen pixels cannot hold five gill slits, so the fix was to
        ask for fewer of them. It can hold them. What it cannot hold is
        five marks competing for the same three pixels.

        So this works in pixels rather than in body coordinates. Each
        slit claims the nearest whole body pixel in every row it
        crosses, paints it in MARK so it cannot quantise away, and
        refuses any pixel within `gap` of a slit already down. Ask for
        more than will fit and the extras decline to draw instead of
        turning their neighbours to mud.

        <b>The rule it generalises is the useful part.</b> Detail at
        this size is not a question of how much you ask for. It is a
        question of whether every mark you ask for lands on a pixel of
        its own.
        """
        kind = MARK if kind is None else kind
        taken = set()
        for index in range(count):
            at = t0 + (t1 - t0) * index / max(1, count - 1)
            run = []
            for y in range(self.size):
                best, pick = None, None
                for x in range(self.size):
                    if self.kind[y][x] != BODY:
                        continue
                    if not lo < self.across[y][x] < hi:
                        continue
                    far = abs(self.along[y][x] - at)
                    if best is None or far < best:
                        best, pick = far, x
                if pick is None:
                    continue
                if any((y, pick + step) in taken
                       for step in range(-gap, gap + 1)):
                    continue
                run.append((y, pick))
            for y, x in run:
                self.kind[y][x] = kind
                self.shade[y][x] = shade
                taken.add((y, x))

    def mottle(self, points, radius=1.9, shade=0.28):
        """Blotches at (t, across), for the ones that are patterned."""
        for at, across in points:
            self.spot(at, across, radius, kind=MARK, shade=shade)

    def mouth(self, t=0.045, span=0.5, depth=0.3):
        for y in range(self.size):
            for x in range(self.size):
                if self.kind[y][x] != BODY:
                    continue
                if self.along[y][x] < t and abs(self.across[y][x] - span) < 0.3:
                    self.shade[y][x] -= depth

    # -- drawing -------------------------------------------------------------

    def _polygon(self, points, kind, shade_of, over=(EMPTY,)):
        ys = [p[1] for p in points]
        top = max(0, int(min(ys)))
        bottom = min(self.size - 1, int(max(ys)) + 1)
        for y in range(top, bottom + 1):
            line = y + 0.5
            crossings = []
            for i in range(len(points)):
                (x1, y1), (x2, y2) = points[i], points[(i + 1) % len(points)]
                if (y1 <= line < y2) or (y2 <= line < y1):
                    crossings.append(x1 + (line - y1) * (x2 - x1) / (y2 - y1))
            crossings.sort()
            for i in range(0, len(crossings) - 1, 2):
                for x in range(max(0, int(crossings[i] + 0.5)),
                               min(self.size, int(crossings[i + 1] + 0.5))):
                    if self.kind[y][x] in over:
                        self.kind[y][x] = kind
                        self.shade[y][x] = shade_of(x + 0.5, y + 0.5)
                        if kind == EMPTY:
                            self.along[y][x] = 0.0

    def _line(self, start, end, kind, delta, over=(FIN,)):
        steps = int(max(abs(end[0] - start[0]), abs(end[1] - start[1])) * 2) + 1
        for i in range(steps + 1):
            k = i / steps
            x = int(start[0] + (end[0] - start[0]) * k)
            y = int(start[1] + (end[1] - start[1]) * k)
            if 0 <= x < self.size and 0 <= y < self.size \
                    and self.kind[y][x] in over:
                self.shade[y][x] += delta

    def _fin(self, anchor, outline, rays, span=1.0, over=(EMPTY,)):
        """Fill a fin and draw its rays. Tips lighter, rays a shade darker."""
        reach = max(math.hypot(p[0] - anchor[0], p[1] - anchor[1])
                    for p in outline) or 1.0

        def shade_of(x, y):
            far = math.hypot(x - anchor[0], y - anchor[1]) / reach
            return 0.30 + 0.45 * min(1.0, far)

        self._polygon(outline, FIN, shade_of, over=over)
        if rays:
            for i in range(rays):
                k = (i + 0.5) / rays * span + (1 - span) / 2
                index = k * (len(outline) - 1)
                lo = int(index)
                hi = min(len(outline) - 1, lo + 1)
                frac = index - lo
                tip = (outline[lo][0] + (outline[hi][0] - outline[lo][0]) * frac,
                       outline[lo][1] + (outline[hi][1] - outline[lo][1]) * frac)
                self._line(anchor, tip, FIN, -0.16)

    def caudal(self, spread, length, fork=0.40, rays=7, lean=0.0):
        """The tail. The notch is what stops it being a paddle."""
        spread, length, lean = px(spread), px(length), px(lean)
        rays = rays_for(rays)
        base = self.belly(1.0)
        anchor = self.pt(1.0, 0.0, -base * 0.6)
        outline = [
            self.pt(1.0, -base, 0),
            self.pt(1.0, -spread, length + lean),
            self.pt(1.0, -spread * 0.30, length * (1 - fork)),
            self.pt(1.0, spread * 0.30, length * (1 - fork)),
            self.pt(1.0, spread, length - lean),
            self.pt(1.0, base, 0),
        ]
        self._fin(anchor, outline, rays)

    def ribbon(self, spread, length, sway, rays=5):
        """A long trailing tail that drifts to one side."""
        spread, length, sway = px(spread), px(length), px(sway)
        rays = rays_for(rays)
        outline = [self.pt(1.0, -spread, 0)]
        for i in range(1, 7):
            k = i / 6
            outline.append(self.pt(1.0, -spread * (1 - k * 0.75) + sway * k * k,
                                   length * k))
        for i in range(6, -1, -1):
            k = i / 6
            outline.append(self.pt(1.0, spread * (1 - k * 0.85) + sway * k * k,
                                   length * k * 0.82))
        self._fin(self.pt(1.0, 0, 0), outline, rays)

    def sail(self, t0, t1, height, side=-1, rays=6, spikes=0, peak=0.5):
        """A dorsal or anal fin: the body edge, then out by `height`."""
        height = px(height)
        rays = rays_for(rays)
        steps = 12
        outline = [self.edge(t0 + (t1 - t0) * i / steps, side)
                   for i in range(steps + 1)]
        crest = []
        for i in range(steps, -1, -1):
            k = i / steps
            if spikes:
                tall = height * (0.55 + 0.45 * ((i % 2) == 0))
            else:
                shape = 1 - abs(k - peak) / max(peak, 1 - peak)
                tall = height * (0.25 + 0.75 * shape ** 0.7)
            t = t0 + (t1 - t0) * k
            width = self.back(t) if side < 0 else self.belly(t)
            crest.append(self.pt(t, side * (width + tall)))
        self._fin(self.pt((t0 + t1) / 2, 0), outline + crest, rays, span=0.45)

    def paddle(self, t, length, drop, side=1, rays=4, lean=0.55,
               onto_body=True):
        """A pectoral or pelvic fin: a teardrop trailing off the flank.

        Drawn over the body by default, because that is where a real one
        sits - in front of the flank, not budded off the outline.
        """
        length, drop = px(length), px(drop)
        rays = rays_for(rays)
        width = (self.back(t) if side < 0 else self.belly(t))
        anchor = self.pt(t, side * width * 0.7)
        outline = [
            anchor,
            self.pt(t, side * (width + drop * 0.35), length * lean * 0.4),
            self.pt(t, side * (width + drop), length * lean),
            self.pt(t, side * (width + drop * 0.45), length),
            self.pt(t, side * width * 0.9, length * 0.55),
        ]
        self._fin(anchor, outline, rays,
                  over=(EMPTY, BODY) if onto_body else (EMPTY,))

    def spines(self, t0, t1, count, height, side=-1, shade=0.42):
        """Separated thorns off the back. Spaced, or they are a comb."""
        height = px(height)
        for i in range(count):
            t = t0 + (t1 - t0) * i / max(1, count - 1)
            width = self.back(t) if side < 0 else self.belly(t)
            tip = self.pt(t + 0.02, side * (width + height))
            self._polygon([self.pt(t - 0.045, side * width * 0.8), tip,
                           self.pt(t + 0.045, side * width * 0.8)],
                          FIN, lambda x, y: shade)

    def bolt(self, length, width=3.2, zigzag=((0.34, -0.26), (0.58, 0.24),
                                              (0.82, -0.22), (1.0, 0.16))):
        """A tail that is a lightning fork rather than a fin."""
        length, width = px(length), max(1.1, px(width))
        points = [self.pt(1.0, 0, 0)]
        for along, across in zigzag:
            points.append(self.pt(1.0, across * length, along * length))
        for index, (start, end) in enumerate(zip(points, points[1:])):
            width = max(0.9, width * (0.82 if index else 1.0))
            steps = int(math.hypot(end[0] - start[0], end[1] - start[1])) + 1
            for i in range(steps + 1):
                k = i / steps
                self._blob(start[0] + (end[0] - start[0]) * k,
                           start[1] + (end[1] - start[1]) * k,
                           width / 2, GLOW, 0.8, over=(EMPTY, FIN))

    def barbel(self, t, side, length, curl=0.45, thick=1.9):
        """A whisker. Nothing else on a fish reads as a whisker."""
        length, thick = px(length), max(0.7, px(thick))
        width = self.back(t) if side < 0 else self.belly(t)
        start = self.pt(t, side * width * 0.8)
        for i in range(int(length * 3) + 1):
            k = i / max(1, int(length * 3))
            x = start[0] + (-self.at(t)[5] * length * k
                            + self.at(t)[3] * side * curl * length * k * k)
            y = start[1] + (-self.at(t)[6] * length * k
                            + self.at(t)[4] * side * curl * length * k * k)
            self._blob(x, y, thick * (1 - 0.3 * k), FIN, 0.34)

    def _blob(self, cx, cy, radius, kind, shade, over=(EMPTY,)):
        for y in range(max(0, int(cy - radius - 1)),
                       min(self.size, int(cy + radius + 2))):
            for x in range(max(0, int(cx - radius - 1)),
                           min(self.size, int(cx + radius + 2))):
                if math.hypot(x + 0.5 - cx, y + 0.5 - cy) <= radius \
                        and self.kind[y][x] in over:
                    self.kind[y][x] = kind
                    self.shade[y][x] = shade

    def arc(self, centre, radius, start, end, thick=2.0, kind=MARK,
            shade=0.5, over=(BODY, MARK, FIN)):
        """A curve of marks. A crescent placed freehand came out a scribble."""
        radius, thick = px(radius), px(thick)
        steps = max(6, int(abs(end - start) * radius))
        for i in range(steps + 1):
            angle = start + (end - start) * i / steps
            self._blob(centre[0] + math.cos(angle) * radius,
                       centre[1] + math.sin(angle) * radius,
                       thick, kind, shade, over=over)

    def crescent(self, centre, radius, angle, bite=0.80, kind=MARK,
                 shade=0.52, over=(BODY, MARK, FIN)):
        """A moon: a disc with a second disc taken out of it.

        Drawn as an arc of marks it came out as the letter C.
        """
        radius = px(radius)
        hole = (centre[0] + math.cos(angle) * radius * 0.46,
                centre[1] + math.sin(angle) * radius * 0.46)
        for y in range(self.size):
            for x in range(self.size):
                if self.kind[y][x] not in over:
                    continue
                if math.hypot(x + 0.5 - centre[0], y + 0.5 - centre[1]) > radius:
                    continue
                if math.hypot(x + 0.5 - hole[0], y + 0.5 - hole[1]) <= radius * bite:
                    continue
                self.kind[y][x] = kind
                self.shade[y][x] = shade

    def spot(self, t, across, radius, kind=MARK, shade=0.5):
        radius = max(0.55, px(radius))
        x, y = self.pt(t, across * (self.back(t) if across < 0
                                    else self.belly(t)))
        self._blob(x, y, radius, kind, shade, over=(BODY, FIN, MARK))

    def band(self, t, width, depth=0.16):
        for y in range(self.size):
            for x in range(self.size):
                if self.kind[y][x] != BODY:
                    continue
                if abs(self.along[y][x] - t) < width:
                    self.shade[y][x] -= depth

    def scutes(self, count, radius=2.0, side=-1):
        radius = max(0.6, px(radius))
        for i in range(count):
            t = 0.24 + 0.56 * i / max(1, count - 1)
            width = self.back(t) if side < 0 else self.belly(t)
            x, y = self.pt(t, side * width * 0.82)
            self._blob(x, y, radius, MARK, 0.72, over=(BODY, MARK))

    def tuft(self, t, length, side=-1):
        length = px(length)
        width = self.back(t) if side < 0 else self.belly(t)
        for i in range(int(length * 2) + 1):
            k = i / max(1, int(length * 2))
            x, y = self.pt(t + k * 0.05, side * (width + length * k))
            self._blob(x, y, max(0.6, px(1.7) * (1 - 0.45 * k)), MARK, 0.52)

    def lure(self, length, radius=3.2, at=0.14):
        """A bulb on a stalk, arching forward over the head.

        Anchored on the brow rather than the snout, and the stalk is
        drawn as one swept curve - built the other way it started inside
        the head and the bulb arrived unattached, which reads as a
        floating dot rather than an angler's lamp.
        """
        length, radius = px(length), px(radius)
        x0, y0, nx, ny, ux, uy = self.at(at)[1:]
        x0 -= nx * self.back(at) * 0.6
        y0 -= ny * self.back(at) * 0.6
        tip = None
        steps = int(length * 3)
        for i in range(steps + 1):
            k = i / steps
            out = length * math.sin(k * 1.7)
            fwd = length * 0.32 * k
            stalk = (x0 - nx * out - ux * fwd, y0 - ny * out - uy * fwd)
            self._blob(stalk[0], stalk[1],
                       max(0.7, px(2.4 - 0.6 * k)), FIN, 0.28)
            tip = stalk
        self._blob(tip[0], tip[1], radius, GLOW, 0.85, over=(EMPTY, FIN))

    def hole(self, t, across, radius):
        """Punch straight through. Only the voidgill, and only once."""
        radius = px(radius)
        x, y = self.pt(t, across * self.belly(t))
        for row in range(max(0, int(y - radius - 1)),
                         min(self.size, int(y + radius + 2))):
            for col in range(max(0, int(x - radius - 1)),
                             min(self.size, int(x + radius + 2))):
                if math.hypot(col + 0.5 - x, row + 0.5 - y) <= radius:
                    self.kind[row][col] = EMPTY

    def eye(self, t=0.11, across=-0.42, radius=3.6, lit=False):
        """A small one, and that is the whole of the lesson.

        <b>Two big white eyes with pupils in them read as goggles.</b>
        The sprites that showed it worst were the ray and the kraken,
        which have a flat face and a pair of them side by side; the
        report was that they looked ridiculous and nothing like
        Minecraft, and it is right. Nothing on a vanilla or mod fish
        sheet has a sclera - an eye there is one or two pixels of pale
        with a dark middle, and that is all. So: six tenths of the
        radius the makers ask for, and no highlight, because a
        highlight inside a three-pixel eye is one stray white pixel.
        """
        self._pupil(self.pt(t, across * self.back(t)), radius, lit)

    def _pupil(self, point, radius, lit):
        """One dark pixel in a patch of the body's lightest tone.

        <b>Vanilla's own construction, decoded rather than guessed.</b>
        Minecraft's cod has exactly one pure black pixel at x3 y11, and
        what makes it read is not the pixel - it is the patch of the
        body's <em>lightest</em> tone around it, sitting on flesh two
        shades darker. The salmon and the tropical fish are built the
        same way. No white sclera anywhere, which is what made our own
        eyes look like goggles when they had one.

        <b>And it has to be big enough to have an inside.</b> The
        radius was cut to six tenths back when these were drawn at
        thirty-two pixels, where that still left something; at sixteen
        it collapses to a single pixel, the pupil eats the whole of it
        and the eye disappears. Eight of twenty-five sprites had no eye
        pixels at all and fourteen more had one or two - which is why
        half the set had no findable head.
        """
        radius = max(1.2, px(radius) * 0.90)
        # Over GLOW as well: a lit body's sheen is drawn before the eye
        # and would otherwise swallow it.
        self._blob(point[0], point[1], radius, IRIS, 1.0,
                   over=(BODY, MARK, FIN, GLOW))
        self._blob(point[0], point[1], max(0.45, radius * 0.40), PUPIL, 0.0,
                   over=(IRIS,))
        self._darken_one(point, IRIS, PUPIL)

    def _darken_one(self, point, pale, dark):
        """Put the dark pixel in whatever pale actually got painted.

        <b>Two ways a pupil goes missing, and this is both of them.</b>
        A disc of radius under a half covers a pixel only when its
        centre happens to land inside one, so it can paint nothing at
        all. And an eye set near the edge of a body - or on a stalk two
        pixels wide - has most of its pale patch fall on empty water,
        so the pixel under the centre was never pale to begin with.
        Either way the sprite comes out with an empty socket, which
        reads worse than no eye.

        So: find the pale pixels that exist and darken the one nearest
        where the eye was meant to be.
        """
        best, pick = None, None
        for y in range(self.size):
            for x in range(self.size):
                if self.kind[y][x] != pale:
                    continue
                gap = (x + 0.5 - point[0]) ** 2 + (y + 0.5 - point[1]) ** 2
                if best is None or gap < best:
                    best, pick = gap, (y, x)
        if pick is not None:
            self.kind[pick[0]][pick[1]] = dark
            self.shade[pick[0]][pick[1]] = 0.0

    def socket(self, t=0.11, across=-0.42, radius=3.6):
        """For the one with nothing behind the eye.

        Built like `_pupil` and for the same measured reason: what
        makes an eye read at this size is the pale patch around it, not
        the dark part. A hole with no rim is just a gap in the flesh.
        """
        radius = max(1.2, px(radius) * 0.90)
        x, y = self.pt(t, across * self.back(t))
        self._blob(x, y, radius, MARK, 0.92, over=(BODY, MARK, FIN, GLOW))
        self._blob(x, y, max(0.45, radius * 0.45), EDGE, 0.0, over=(MARK,))
        self._darken_one((x, y), MARK, EDGE)

    # -- finishing -----------------------------------------------------------

    def maw(self, length, gape=0.55, teeth=4, hinge=0.16, shade=0.42):
        """An open jaw, hinged behind the snout.

        <b>The single loudest thing a sprite here can do.</b> A fish has
        a mouth; a thing with its mouth open and its teeth out is not a
        fish any more, and that is the whole job of the top two bands.

        <b>The snout is cut away first.</b> Drawn straight over the body
        the jaws land on flesh that is already there, the gap between
        them is filled by the old head, and the result is a flat-shaded
        nose rather than an open mouth - which is exactly how the first
        version came out. So: carve the whole cone in front of the
        hinge, put the two jaws back inside it, and what is left between
        them is the opening.

        Drawn after the body lighting, because the jaws are polygons
        rather than flesh and a later lighting pass would flatten them.
        """
        length = px(length)
        x, y, nx, ny, ux, uy = self.at(hinge)[1:]
        hinge_point = (x, y)
        tips, roots, throats = {}, {}, {}
        for side in (-1, 1):
            width = self.back(hinge) if side < 0 else self.belly(hinge)
            lean = gape / 2
            dx = -ux * math.cos(lean) + nx * side * math.sin(lean)
            dy = -uy * math.cos(lean) + ny * side * math.sin(lean)
            tips[side] = (x + dx * length, y + dy * length)
            roots[side] = (x + nx * side * width * 1.05,
                           y + ny * side * width * 1.05)
            throats[side] = (x + nx * side * width * 0.42,
                             y + ny * side * width * 0.42)
        self._polygon([hinge_point,
                       (x + (tips[-1][0] - x) * 1.25, y + (tips[-1][1] - y) * 1.25),
                       (x + (tips[1][0] - x) * 1.25, y + (tips[1][1] - y) * 1.25)],
                      EMPTY, lambda a, b: 0.0, over=(BODY, FIN, MARK, GLOW))
        for side in (-1, 1):
            self._polygon([roots[side], tips[side], throats[side]], BODY,
                          lambda a, b: shade, over=(EMPTY,))
            for i in range(teeth):
                k = (i + 0.55) / teeth
                self._blob(throats[side][0]
                           + (tips[side][0] - throats[side][0]) * k
                           - nx * side * 1.1,
                           throats[side][1]
                           + (tips[side][1] - throats[side][1]) * k
                           - ny * side * 1.1,
                           max(0.5, px(1.9)), MARK, 0.97, over=(EMPTY,))

    def horns(self, count, length, spread=0.5, t=0.14, side=-1, thick=2.2):
        """Spikes off the brow, swept up and forward."""
        length = px(length)
        x, y, nx, ny, ux, uy = self.at(t)[1:]
        width = self.back(t) if side < 0 else self.belly(t)
        for i in range(count):
            lean = (i - (count - 1) / 2) * spread
            base = (x + nx * side * width * 0.75, y + ny * side * width * 0.75)
            for step in range(int(length * 3) + 1):
                k = step / max(1, int(length * 3))
                out = (nx * side * 0.95 - ux * (0.45 + lean),
                       ny * side * 0.95 - uy * (0.45 + lean))
                self._blob(base[0] + out[0] * length * k,
                           base[1] + out[1] * length * k,
                           max(0.5, px(thick) * (1 - 0.72 * k)), FIN, 0.42)

    def tendrils(self, count, length, spread=0.9, thick=1.9, shade=0.38):
        """Filaments trailing off the tail. Nothing with fins has these."""
        length = px(length)
        x, y, nx, ny, ux, uy = self.at(1.0)[1:]
        for i in range(count):
            lean = (i - (count - 1) / 2) * spread
            for step in range(int(length * 3) + 1):
                k = step / max(1, int(length * 3))
                drift = lean * k * k * 3.2
                self._blob(x + ux * length * k + nx * drift,
                           y + uy * length * k + ny * drift,
                           max(0.5, px(thick) * (1 - 0.5 * k)), FIN, shade)

    def orbit(self, radius, start, end, at=0.5, thick=1.6, kind=GLOW, shade=0.92):
        """A ring of light with nothing holding it up.

        Detached geometry is the one thing a living animal cannot have,
        which is why only the top bands get it.
        """
        cx, cy = self.pt(at, 0)
        radius, thick = px(radius), max(0.55, px(thick))
        steps = max(10, int(abs(end - start) * radius * 1.5))
        for i in range(steps + 1):
            angle = start + (end - start) * i / steps
            self._blob(cx + math.cos(angle) * radius,
                       cy + math.sin(angle) * radius, thick, kind, shade,
                       over=(EMPTY,))

    def motes(self, specks, kind=GLOW, shade=0.96):
        """Loose sparks behind the tail, in (along, across, radius)."""
        for along, across, radius in specks:
            x, y = self.pt(1.0, px(across), px(along))
            self._blob(x, y, max(0.5, px(radius)), kind, shade, over=(EMPTY,))

    def sucker(self, radius, teeth=8):
        """A round rasping mouth. A lamprey has no jaw and it shows.

        Set slightly forward of the snout rather than on it: sitting
        flush it is the same width as the body and reads as the end of
        a tube.

        <b>Only slightly, and the teeth are no longer white.</b> The
        offset was 0.55 of the radius with the tooth ring at 0.97 -
        nearly the palest tone available - and on a dark body that
        combination stopped reading as a mouth on an animal and became
        a separate pale object floating beside a curved tube. At
        sixteen pixels "set forward" costs a whole pixel of gap, and a
        bright ring across the gap finishes the job.
        """
        radius = px(radius)
        x, y = self.pt(0.0, 0.0, -radius * 0.30)
        self._blob(x, y, radius, BODY, 0.34, over=(EMPTY, BODY))
        self._blob(x, y, radius * 0.5, MARK, 0.08, over=(BODY, MARK))
        for i in range(teeth):
            angle = i / teeth * 2 * math.pi
            self._blob(x + math.cos(angle) * radius * 0.74,
                       y + math.sin(angle) * radius * 0.74,
                       max(0.5, radius * 0.19), MARK, 0.78, over=(BODY, MARK))

    # --- bodies that are not grown on a spine --------------------------
    #
    # <b>Everything above this line makes a fish.</b> A spine, a profile,
    # a tail at one end and fins down the sides - which is the right
    # machine for a dace and the wrong one for a crab, and building
    # twenty-four things with it is how most of the set came to be the
    # same animal in different colours. A crab is a shell with legs, a
    # starfish has no front, a jellyfish is a bell with nothing inside
    # it. None of those has a spine to hang anything off.

    def here(self, x, y, radius, kind, shade, over=(EMPTY,)):
        """A blob at a point in design units, rather than along a spine."""
        point = place(x, y)
        self._blob(point[0], point[1], max(0.5, px(radius)), kind, shade, over)

    def dome(self, centre, across, down, power=2.2, kind=BODY,
             floor=0.20, ceiling=0.96, lift=0.24, over=(EMPTY,)):
        """A rounded body lit from the upper left, with no spine at all.

        `power` is the superellipse exponent and does most of the work:
        below two it comes to points (a ray's wings, a starfish's arm),
        at two it is an oval (a shell, a bell), above two it squares off
        (a carapace).
        """
        cx, cy = place(*centre)
        rx, ry = px(across), px(down)
        for y in range(self.size):
            for x in range(self.size):
                if self.kind[y][x] not in over:
                    continue
                dx, dy = (x + 0.5 - cx) / max(1e-6, rx), (y + 0.5 - cy) / max(1e-6, ry)
                deep = (abs(dx) ** power + abs(dy) ** power) ** (1 / power)
                if deep > 1.0:
                    continue
                lit = 0.5 - 0.42 * (dx + dy) / 2
                self.kind[y][x] = kind
                self.shade[y][x] = max(0.04, min(0.99,
                                                 floor + (ceiling - floor) * lit
                                                 + lift * (1 - deep) ** 1.6))

    def limb(self, start, end, thick, taper=0.45, bow=0.0, kind=FIN,
             shade=0.42, over=(EMPTY,)):
        """A tapered arm between two points, optionally bowed sideways.

        The one shape a leg, a tentacle, an antenna and a whip tail all
        are, which is why they are one method and not four.
        """
        ax, ay = place(*start)
        bx, by = place(*end)
        dx, dy = bx - ax, by - ay
        length = max(1e-6, math.hypot(dx, dy))
        nx, ny = -dy / length, dx / length
        steps = max(3, int(length * 2))
        for i in range(steps + 1):
            k = i / steps
            swing = px(bow) * math.sin(k * math.pi)
            self._blob(ax + dx * k + nx * swing, ay + dy * k + ny * swing,
                       max(0.45, px(thick) * (1 - taper * k)), kind, shade, over)

    def arms(self, centre, count, length, thick, turn=0.0, bow=0.0,
             kind=BODY, shade=0.5):
        """Limbs radiating from a point. A starfish has no front."""
        for i in range(count):
            angle = turn + i * 2 * math.pi / count
            self.limb(centre,
                      (centre[0] + math.cos(angle) * length,
                       centre[1] + math.sin(angle) * length),
                      thick, taper=0.72, bow=bow, kind=kind, shade=shade,
                      over=(EMPTY, BODY))

    def claw(self, at, angle, length, gape=0.55, thick=3.0, kind=BODY,
             shade=0.46):
        """A pincer: two tapered jaws off one wrist. Nothing else is one."""
        for side in (-1, 1):
            lean = angle + side * gape / 2
            self.limb(at, (at[0] + math.cos(lean) * length,
                           at[1] + math.sin(lean) * length),
                      thick, taper=0.6, kind=kind, shade=shade,
                      over=(EMPTY, BODY))

    def fringe(self, centre, across, down, count, length, sway=0.0,
               thick=2.0, kind=FIN, shade=0.38):
        """Tentacles hanging off the rim of a bell, spread along its width."""
        for i in range(count):
            k = (i + 0.5) / count
            x = centre[0] + (k - 0.5) * 2 * across * 0.86
            drop = down * math.sqrt(max(0.0, 1 - ((k - 0.5) * 2) ** 2)) * 0.6
            wave = sway * math.sin(k * 5.5)
            self.limb((x, centre[1] + drop),
                      (x + wave, centre[1] + drop + length),
                      thick, taper=0.65, bow=sway * 0.5, kind=kind,
                      shade=shade, over=(EMPTY,))

    def stare(self, x, y, radius=3.4, lit=False):
        """An eye at a point, for the things with no spine to hang one on."""
        self._pupil(place(x, y), radius, lit)

    def trim(self, shade=0.92, kind=GLOW, on=(BODY,), keep=None):
        """A lit line along the silhouette, for the things with no spine.

        <b>What `sheen` is for a body that has no back.</b> `sheen`
        runs its highlight at a fixed distance <em>across</em> the
        body, which it can only do because a fish has a spine, an along
        and an across. A bell, a carapace and a pair of wings have none
        of the three. What they do have is an edge, so the light goes
        on the edge, and the dark border laid down afterwards sits
        outside it.
        """
        lip = []
        for y in range(self.size):
            for x in range(self.size):
                if self.kind[y][x] not in on:
                    continue
                if keep is not None and not keep(x + 0.5, y + 0.5):
                    continue
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    a, b = x + dx, y + dy
                    if not (0 <= a < self.size and 0 <= b < self.size) \
                            or self.kind[b][a] == EMPTY:
                        lip.append((x, y))
                        break
        for x, y in lip:
            self.kind[y][x] = kind
            self.shade[y][x] = shade

    def sheen(self, across=-0.70, width=0.13, start=0.18, stop=0.90):
        """A lit line down the back, inside the silhouette.

        <b>What a legendary has that an epic does not.</b> The three
        bands were drawn with the same vocabulary - body, fins, scales,
        an eye - so the only thing saying which was which was the
        colour, and a player holding one has no swatch to compare it
        to. A fish that is visibly lit from inside is a different
        <em>kind</em> of thing, which is the distinction the bands are
        supposed to carry.
        """
        for y in range(self.size):
            for x in range(self.size):
                if self.kind[y][x] != BODY:
                    continue
                if not start < self.along[y][x] < stop:
                    continue
                if abs(self.across[y][x] - across) < width:
                    self.kind[y][x] = GLOW
                    self.shade[y][x] = 0.9

    def chunk(self, block=2, on=(BODY,)):
        """Flatten the tone of each kind onto a grid coarser than the texture.

        <b>Resolution is not the only thing that makes a sprite look
        pixelated.</b> The obvious way to make these blockier is to draw
        them smaller, and it is the wrong way twice over: sixteen was
        already tried and could not hold a jaw, and halving the grid
        halves the silhouette too, so the outline, the eye and the fin
        rays go with the gradient nobody wanted.

        What actually reads as smooth is the <em>fill</em> - a body
        shaded a tone per pixel. So the fill is quantised onto a 2x2
        grid and everything else is left alone: the silhouette, the
        border, the eye, the glow and the sheen stay at full
        resolution. The result is tone in visible blocks inside a crisp
        one-pixel outline, which is what a 32x pack looks like and what
        a downscale cannot give you.

        Only the kinds in `on` are touched, which is the knob between
        "a bit blockier" and "flat": with BODY alone the fins keep their
        rays, adding FIN flattens those too.
        """
        for top in range(0, self.size, block):
            for left in range(0, self.size, block):
                groups = {}
                for y in range(top, min(self.size, top + block)):
                    for x in range(left, min(self.size, left + block)):
                        if self.kind[y][x] in on:
                            groups.setdefault(self.kind[y][x], []).append((y, x))
                for cells in groups.values():
                    counts = {}
                    for y, x in cells:
                        level = max(0, min(self.LEVELS - 1,
                                           int(round(self.shade[y][x]
                                                     * (self.LEVELS - 1)))))
                        counts[level] = counts.get(level, 0) + 1
                    # The most common tone in the block, and the darker
                    # one on a tie - a highlight that wins a coin toss
                    # spreads over four pixels and reads as a blob.
                    best = min(counts, key=lambda k: (-counts[k], k))
                    for y, x in cells:
                        self.shade[y][x] = best / (self.LEVELS - 1)

    def despur(self, passes=1, keep=(GLOW,)):
        """Trim pixels left dangling off the silhouette by one corner.

        <b>The measurement that found this.</b> Decoded against the
        vanilla item textures, a painted pixel with one or fewer
        painted orthogonal neighbours - a spur - accounts for 1.2% of
        a vanilla sprite and 0.0% of the cod and the tropical fish.
        Ours ran at 6.2%, and on the stormtail 13.8%.

        It is the whole of the remaining difference in how crisp the
        two sets look, and it is not a detail problem: by the other
        measure taken at the same time, our mean same-colour patch is
        2.7 pixels against vanilla's 1.7, so our sprites are
        <em>flatter</em> than vanilla's, not noisier. The silhouettes
        were simply fraying - a fin ray or a spine tip reaching one
        pixel past the body and hanging there by a corner.

        A hand-placed sheet never has these because a person drawing a
        fin stops at the last pixel that still looks like fin. A
        generator aims a fin at an angle and takes whatever lands.

        GLOW is kept by default: sparks and motes are detached on
        purpose, and they are the one thing here that is supposed to
        float clear of the body.

        <b>Neighbours are counted diagonally as well, and that is not a
        refinement - counting only the four orthogonals destroys the
        sprite.</b> Consecutive pixels of a one-pixel diagonal line do
        not touch orthogonally at all, so under a four-way test every
        pixel of such a line reads as a spur and the whole limb is
        deleted in one pass. The first version did exactly that: it
        took the crab's legs, the driftbell's tentacles and the
        stormtail's lightning, and left the remains floating. Eight-way
        is the test that actually means "hanging by a corner".
        """
        for _ in range(passes):
            doomed = []
            for y in range(self.size):
                for x in range(self.size):
                    kind = self.kind[y][x]
                    if kind == EMPTY or kind in keep:
                        continue
                    touching = 0
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1),
                                   (1, 1), (1, -1), (-1, 1), (-1, -1)):
                        a, b = x + dx, y + dy
                        if 0 <= a < self.size and 0 <= b < self.size \
                                and self.kind[b][a] != EMPTY:
                            touching += 1
                    if touching <= 1:
                        doomed.append((x, y))
            if not doomed:
                break
            for x, y in doomed:
                self.kind[y][x] = EMPTY
                self.shade[y][x] = 0.0

    def outline(self, thickness=1):
        """A dark border one pixel thick, the way a vanilla sprite has one.

        <b>One vanilla pixel, which at this size is one pixel.</b> It
        was briefly two, back when the sprites were 32x and a single
        pixel of border was therefore <em>half</em> a vanilla one - the
        last and best of four attempts to buy the blocky look at double
        resolution. Three passes went at it from the
        colour side - fewer tones, no scale lattice, a blacker border -
        and all helped without fixing it, because what was wrong was
        never the colour. The report that landed it was "Minecraft
        objects are made of squares, the edges are way too smooth", and
        that is exactly right: a one-pixel border on a 32x sprite is
        <em>half</em> a vanilla pixel, so every diagonal is a fine ramp
        where vanilla has a staircase.

        None of the four worked, and the grid went to sixteen instead;
        see the note on SIZE. Snapping a 32x sprite onto a two-pixel
        grid was also tried, twice, and was wrong both ways.
        Voting each 2x2 square to its commonest kind erodes everything
        thinner than a square - the crab lost its legs, the kraken went
        to a red blob - and growing instead of voting welds them
        together, which is the same sprite with the gaps filled. That
        is what a 16x sheet gets away with only because a person placed
        every pixel; a generator places them by formula and the formula
        has no idea which pixel is load-bearing.

        So the silhouette keeps its half-pixel precision and the
        <em>border</em> takes the whole one. The edge reads as squares,
        and a two-pixel leg is still a leg.

        <b>And then reversed back, which is where it stands.</b> The
        paragraph that used to sit here argued the border in at
        sixty-four pixels and noted, correctly, that the sixteen pixel
        set had deliberately had none - a border costs a pixel of
        perimeter everywhere, which is most of a six pixel body.
        The grid moved to sixteen; the border came along; nobody
        re-argued it.

        Measuring settled it. Decoded against the vanilla textures our
        sprites were spending <b>50% of their painted pixels on
        border</b> - mirelash 75%, zaratan 71%, krakenspawn 70% -
        where vanilla spends 15%, and cod and pufferfish spend
        <em>none</em>. Fill (39% against 36%) and distinct colour count
        (9.6 against 10) already matched vanilla almost exactly. The
        border was the entire remaining difference.

        That also explains a complaint that three rounds of restyling
        had failed to fix. Half of every sprite being black meant every
        subject was a thin ribbon of colour inside a thick cartoon
        outline, and the cure that kept suggesting itself - draw fewer
        features, the tile cannot hold them - was treating the symptom.
        The tile could hold them. The border was sitting in their seat.

        So at sixteen `BORDER` is 0 and the shape rides on the
        silhouette, as vanilla's does. The code is kept, and so is the
        switch, because at sixty-four the original argument still holds.
        """
        if BORDER <= 0:
            return
        for _ in range(thickness):
            ring = []
            for y in range(self.size):
                for x in range(self.size):
                    if self.kind[y][x] != EMPTY:
                        continue
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        a, b = x + dx, y + dy
                        if 0 <= a < self.size and 0 <= b < self.size \
                                and self.kind[b][a] not in (EMPTY, EDGE):
                            ring.append((x, y))
                            break
            for x, y in ring:
                self.kind[y][x] = EDGE

    def pixels(self, palette):
        body = tones([(0.0, palette["o"]), (0.26, palette["s"]),
                      (0.55, palette["b"]), (0.82, palette["h"]),
                      (1.0, lighten(palette["h"], 0.45))], self.LEVELS)
        fin = tones([(0.0, darken(palette["f"], 0.5)), (0.45, palette["f"]),
                     (1.0, lighten(palette["f"], 0.4))], self.LEVELS)
        mark = tones([(0.0, darken(palette["m"], 0.55)), (0.5, palette["m"]),
                      (1.0, lighten(palette["m"], 0.4))], self.LEVELS)
        shine = tones([(0.0, palette["g"]), (1.0, lighten(palette["g"], 0.6))],
                      self.LEVELS)
        # Nearly black, rather than a dark version of the outline
        # colour. A tinted border reads as a thick edge on the
        # drawing; a black one reads as the line around a sprite.
        border = darken(palette["o"], BORDER_DARK)

        def step(value):
            return max(0, min(self.LEVELS - 1,
                              int(round(value * (self.LEVELS - 1)))))

        rows = []
        for y in range(self.size):
            row = []
            for x in range(self.size):
                kind = self.kind[y][x]
                level = step(self.shade[y][x])
                if kind == EMPTY:
                    row.append((0, 0, 0, 0))
                elif kind == BODY:
                    row.append(body[level] + (255,))
                elif kind == FIN:
                    row.append(fin[level] + (255,))
                elif kind == MARK:
                    row.append(mark[level] + (255,))
                elif kind == GLOW:
                    row.append(shine[level] + (255,))
                elif kind == IRIS:
                    # The white of the eye, on palette. A coloured iris
                    # on every fish reads as a cartoon; the lit ones ask
                    # for it by name.
                    row.append(lighten(palette["h"], 0.55) + (255,))
                elif kind == PUPIL:
                    row.append((12, 10, 16, 255))
                else:
                    row.append(border + (255,))
            rows.append(row)
        rows = spread(rows)

        # <b>No aura.</b> There used to be a halo of rings out past the
        # border - none for a rare, one for a legendary, two for a
        # mythic - so rarity could be read in a hotbar without reading
        # anything. It worked, and it cost the thing it was decorating:
        # a soft translucent ring two pixels out fills every gap a
        # silhouette has, so the kraken's eight arms came out as one
        # blob and a serpent's humps fused into a sausage. It is also
        # the least Minecraft thing the sprites did - nothing on a
        # vanilla or mod fish sheet wears a glow.
        #
        # The bands carry themselves instead, which is where they
        # belonged: a rare is an ordinary catch, a legendary is lit
        # from inside (see .sheen and .trim) and crowds its tile, and a
        # mythic has geometry that cannot hold together.
        return rows
