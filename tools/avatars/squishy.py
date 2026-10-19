"""Squishy: a glossy pastel jelly bao squishy toy with a three-lobed pinched top, three long folds and a sparkle of glitter.

Unlike the hatched avatars it is shaded smooth, because a squishy reads as soft glossy foam, not paper.
"""

import math
import random
from PIL import Image, ImageChops, ImageFilter

from ink import SS, Canvas, ellipse, rotate, scale, wobble

ID = 'squishy'
NAME = 'Squishy'

JELLY = (246, 228, 246)
WARM = (250, 190, 222)
COOL = (184, 228, 248)
EDGE = (214, 168, 222)

EYE = (24, 20, 26)
IRIS = (78, 74, 86)
PINK = (250, 160, 180)
MOUTH = (232, 110, 140)
WHITE = (255, 255, 255)
SWEAT = (196, 222, 250)
STEAM = (232, 234, 244)
ACCENT = (203, 166, 247)
HEART = (243, 139, 168)
OUTLINE = (30, 24, 28)

BASE = (64, 104)


def pose(**changes):
    values = dict(lift=0, rise=0, sx=1, sy=1, tilt=0, knot=0, look=0, eyes='open', mouth='smile',
                  steam=None, twinkle=0, extras=())
    values.update(changes)
    return values


def arc(cx, cy, rx, ry, start, end, steps=40):
    return [(cx + rx * math.cos(math.radians(start + (end - start) * k / steps)),
             cy + ry * math.sin(math.radians(start + (end - start) * k / steps))) for k in range(steps + 1)]


def bezier(p0, p1, p2, n=18, t0=0, t1=1):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1])
            for t in (t0 + (t1 - t0) * i / n for i in range(n + 1))]


def accent(canvas, pts, width, rng, colour=ACCENT):
    canvas.line(pts, width + 1.8, rng)
    canvas.line(pts, width, rng, colour)


def heart(cx, cy, size):
    return [(cx + size * 16 * math.sin(t) ** 3 / 17,
             cy - size * (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)) / 17)
            for t in (math.tau * k / 60 for k in range(60))]


def bun():
    """A round jelly bun: widest just below the middle, a broad dome on top, a softly flattened base."""
    pts = []
    n = 200
    for k in range(n):
        a = math.tau * k / n
        x, y = math.cos(a), math.sin(a)
        rx = 46 * (1 - .04 * max(0, -y) ** 2)
        ry = 39 if y < 0 else 33
        flat = 3 * max(0, y) ** 6
        pts.append((64 + rx * x, 74 + ry * y - flat))
    return pts


def smooth(pts, rounds=3):
    for _ in range(rounds):
        out = []
        for i, a in enumerate(pts):
            b = pts[(i + 1) % len(pts)]
            out += [(a[0] * .75 + b[0] * .25, a[1] * .75 + b[1] * .25), (a[0] * .25 + b[0] * .75, a[1] * .25 + b[1] * .75)]
        pts = out
    return pts


def crown():
    """The pinched closure: a tall middle tip and two side tips flaring outward, with soft dips between."""
    return smooth([(41, 50), (44, 41), (46.5, 34), (49, 30), (52.5, 29), (56, 31.5), (58.5, 34.5), (60.5, 33),
                   (61.5, 28), (63, 24.5), (65, 24.5), (66.5, 28), (67.5, 33), (69.5, 34.5),
                   (72, 31.5), (75.5, 29), (79, 30), (81.5, 34), (84, 41), (87, 50), (64, 56)], 4)


def draw_eyes(canvas, cx, cy, p, rng, body):
    for side in (-1, 1):
        ex, ey = cx + side * 19 + p['look'], cy
        kind = p['eyes']
        if kind in ('open', 'wide'):
            w, h = {'open': (13, 14), 'wide': (14.5, 16)}[kind]
            canvas.paint(EYE, canvas.mask(body(wobble(ellipse(ex, ey, w, h), rng, .08))))
            canvas.paint(IRIS, canvas.mask(body(ellipse(ex + .5, ey + h * .2, w * .7, h * .42))))
            for gx, gy in ((-2.2, 3.4), (1.6, 4.4), (.2, 2.4), (3, 2.8)):
                canvas.paint(WHITE, canvas.mask(body(ellipse(ex + gx, ey + gy, .8, .8))))
            canvas.paint(WHITE, canvas.mask(body(ellipse(ex - w * .17, ey - h * .18, 5.4, 5.6))))
            canvas.paint(WHITE, canvas.mask(body(ellipse(ex + w * .24, ey + h * .16, 2, 2))))
        elif kind == 'dot':
            canvas.paint(EYE, canvas.mask(body(wobble(ellipse(ex, ey + 1, 6, 6.5), rng, .06))))
            canvas.paint(WHITE, canvas.mask(body(ellipse(ex - 1, ey - .4, 2, 2))))
        elif kind == 'happy':
            canvas.line(body([(ex - 6, ey + 3), (ex - 3, ey - 2.2), (ex, ey - 3.6), (ex + 3, ey - 2.2),
                              (ex + 6, ey + 3)]), 2.5, rng, EYE)
        elif kind == 'closed':
            canvas.line(body([(ex - 6, ey), (ex - 3, ey + 3.2), (ex, ey + 3.8), (ex + 3, ey + 3.2),
                              (ex + 6, ey)]), 2.4, rng, EYE)
        elif kind == 'blink':
            canvas.line(body([(ex - 5.6, ey + 1.4), (ex, ey + 2.2), (ex + 5.6, ey + 1.4)]), 2.4, rng, EYE)
        elif kind == 'squeeze':
            for dy in (-3, 3):
                canvas.line(body([(ex - side * 5, ey + dy), (ex + side * 3.4, ey)]), 2.4, rng, EYE)


def draw_mouth(canvas, cx, cy, p, rng, body):
    mouth = p['mouth']
    my = cy + 7
    if mouth == 'smile':
        canvas.line(body(arc(cx, my, 5.6, 4.6, 10, 170, 20)), 1.9, rng)
    elif mouth == 'open':
        jaw = arc(cx, my, 6, 6.4, 0, 180, 20)
        canvas.paint(OUTLINE, canvas.mask(body(scale(jaw, (cx, my + 2), 1.25, 1.2))))
        canvas.paint(MOUTH, canvas.mask(body(jaw)))
    elif mouth == 'o':
        canvas.paint(OUTLINE, canvas.mask(body(ellipse(cx, my + 2, 6.4, 7))))
        canvas.paint(MOUTH, canvas.mask(body(ellipse(cx, my + 2, 4.2, 4.8))))
    elif mouth == 'wobbly':
        canvas.line(body([(cx - 5, my + 1), (cx - 2.5, my - .5), (cx, my + 1), (cx + 2.5, my - .5), (cx + 5, my + 1)]),
                    1.7, rng)


def glaze(canvas, colour, mask, alpha):
    """Like Canvas.tint, but a soft mask fades the colour out instead of blending it toward black."""
    layer = Image.new('RGBA', canvas.image.size, colour + (0,))
    layer.putalpha(mask.point(lambda v: v * alpha // 255))
    canvas.image.alpha_composite(layer)


def sparkle_star(canvas, x, y, r, colour=WHITE):
    pts = []
    for k in range(8):
        a = math.tau * k / 8 - math.pi / 2
        rr = r if k % 2 == 0 else r * .28
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    canvas.paint(colour, canvas.mask(pts))


def render(p, seed):
    rng = random.Random(seed)
    canvas = Canvas(JELLY, JELLY, OUTLINE)
    rise = p['rise']
    sx, sy = p['sx'], p['sy']

    def squish(x, y):
        k = min(1, max(0, (y - 26) / (BASE[1] - 26)))
        fx = 1 + (sx - 1) * (.45 + .7 * math.sin(math.pi * k) + .35 * k)
        return 64 + (x - 64) * fx, BASE[1] + (y - BASE[1]) * sy

    def body(pts):
        pts = [squish(x, y) for x, y in pts]
        pts = [(x, y - rise) for x, y in pts]
        return rotate(pts, (64, BASE[1] - rise), p['tilt']) if p['tilt'] else pts

    def swing(pts):
        return body(rotate(pts, (64, 44), p['knot']))

    region = canvas.mask(body(wobble(bun(), rng, .2)))
    region = ImageChops.lighter(region, canvas.mask(swing(crown())))
    soft = lambda m, r: m.filter(ImageFilter.GaussianBlur(r * SS))
    inside = lambda m: ImageChops.multiply(m, region)

    canvas.paint(JELLY, region)
    glaze(canvas, WARM, inside(soft(canvas.mask(body(ellipse(42, 70, 52, 56))), 9)), 150)
    glaze(canvas, COOL, inside(soft(canvas.mask(body(ellipse(88, 78, 50, 50))), 9)), 150)
    glaze(canvas, WARM, inside(soft(canvas.mask(body(ellipse(64, 106, 96, 26))), 6)), 110)
    rim = ImageChops.subtract(region, soft(region, 2.5).point(lambda v: 255 if v > 200 else 0))
    glaze(canvas, EDGE, soft(rim, 1.4), 150)

    for _ in range(70):
        gx, gy = rng.uniform(22, 106), rng.uniform(34, 102)
        glint = canvas.mask(body(ellipse(gx, gy, rng.uniform(.6, 1.1), rng.uniform(.6, 1.1))))
        glaze(canvas, WHITE, inside(glint), rng.randint(140, 230))

    blurred = soft(region, 2.6 * .37)
    outer = blurred.point(lambda v: 255 if v > 22 else 0)
    inner = blurred.point(lambda v: 255 if v > 233 else 0)
    canvas.paint(OUTLINE, ImageChops.subtract(outer, inner))

    folds = [((64, 30), (65.5, 47), (64, 64)), ((58.5, 37), (43, 44), (33, 66)), ((69.5, 37), (85, 44), (95, 66))]
    for p0, p1, p2 in folds:
        shine = bezier((p0[0] - 1.6, p0[1] + 2), (p1[0] - 1.6, p1[1]), (p2[0] - 1.6, p2[1] - 2), t0=.15, t1=.8)
        canvas.line(body(shine), 1.3, rng, WHITE)
        canvas.line(swing(bezier(p0, p1, p2, t0=0, t1=.3))[:-1] + body(bezier(p0, p1, p2, t0=.3, t1=1)), 1.8, rng)

    canvas.line(body(arc(64, 74, 40, 33, 196, 236, 24)), 2.6, rng, WHITE)
    canvas.paint(WHITE, canvas.mask(body(ellipse(26, 84, 2.6, 3.4))))
    canvas.line(swing([(61.3, 31.5), (62, 28.5), (62.9, 26.8)]), 1.3, rng, WHITE)
    canvas.line(swing([(49.5, 34.5), (50.8, 32)]), 1.2, rng, WHITE)
    sparkle_star(canvas, *body([(94, 50)])[0], 4.2 + 1.6 * p['twinkle'])
    sparkle_star(canvas, *body([(30, 94)])[0], 2.6 + 1.2 * (1 - p['twinkle']))

    cx, cy = 64, 77
    draw_eyes(canvas, cx, cy, p, rng, body)
    draw_mouth(canvas, cx, cy, p, rng, body)
    extras = p['extras']
    for side in (-1, 1):
        glaze(canvas, PINK, canvas.mask(body(ellipse(cx + side * 26, cy + 9, 13, 7))),
                    235 if 'blush' in extras else 200)

    if p['steam'] is not None:
        for x0, top_y, phase in ((12, 34, 0), (116, 38, .5)):
            wisp = [(x0 + 2.6 * math.sin(math.tau * (t * 1.1 + phase + p['steam'] * .5)), 64 - (64 - top_y) * t)
                    for t in (k / 24 for k in range(25))]
            accent(canvas, wisp, 1.7, rng, STEAM)
    if 'bang' in extras:
        bx, by = 108, 20
        accent(canvas, [(bx, by - 8), (bx + .4, by)], 2.4, rng)
        canvas.paint(OUTLINE, canvas.mask(ellipse(bx + .5, by + 4.2, 4.8, 4.8)))
        canvas.paint(ACCENT, canvas.mask(ellipse(bx + .5, by + 4.2, 3, 3)))
    if 'zzz' in extras:
        for zx, zy, zs in ((96, 40, 6.5), (106, 29, 5)):
            accent(canvas, [(zx, zy), (zx + zs, zy), (zx, zy + zs), (zx + zs, zy + zs)], 1.7, rng)
    if 'sparkle' in extras:
        for sx_, sy_, r in ((14, 30, 4.6), (114, 24, 3.8)):
            cross = ([(sx_ - r, sy_), (sx_ + r, sy_)], [(sx_, sy_ - r), (sx_, sy_ + r)])
            for stroke in cross:
                canvas.line(stroke, 3.6, rng)
            for stroke in cross:
                canvas.line(stroke, 1.8, rng, ACCENT)
    if 'hearts' in extras:
        for hx, hy, s in ((16, 30, 4.2), (112, 22, 3.4)):
            canvas.paint(OUTLINE, canvas.mask(heart(hx, hy, s + .9)))
            canvas.paint(HEART, canvas.mask(heart(hx, hy, s)))
    if 'sweat' in extras:
        drop = [(104, 44), (101, 51), (102, 55), (106, 55), (107, 51)]
        canvas.paint(OUTLINE, canvas.mask(scale(drop, (104, 51), 1.35, 1.25)))
        canvas.paint(SWEAT, canvas.mask(drop))
    if 'boing' in extras:
        for side in (-1, 1):
            for k, dy in ((0, 0), (1, -7)):
                x = 64 + side * (50 - k * 2)
                canvas.line([(x, 96 + dy), (x + side * 5, 92 + dy)], 1.8, rng)
    return canvas.downsample()


NEUTRAL = pose()


def rise_back(start, steps, knot=0, **face):
    """A slow-rise foam recovery: each step closes most of the remaining squash and lingers longer."""
    frames = []
    sx, sy = start
    for i in range(steps):
        sx, sy = 1 + (sx - 1) * .55, 1 + (sy - 1) * .55
        knot = -knot * .6
        frames.append((pose(sx=round(sx, 3), sy=round(sy, 3), knot=round(knot, 1), **face), 150 + 70 * i))
    return frames


ANIMATIONS = {
    'idle': ('loop', [
        (NEUTRAL, 900),
        (pose(sx=1.02, sy=.98, twinkle=1), 500), (pose(sx=1.035, sy=.965, twinkle=1), 600),
        (pose(sx=1.02, sy=.98), 500), (NEUTRAL, 700),
        (pose(eyes='blink'), 120), (pose(look=-2), 700), (pose(look=2, twinkle=1), 700),
        (pose(sx=1.08, sy=.92, knot=-8, eyes='happy'), 160),
        *rise_back((1.08, .92), 3, knot=-8, eyes='happy'),
        (NEUTRAL, 600),
    ]),
    'working': ('loop', [
        (pose(sx=1.12, sy=.88, knot=-10, eyes='dot', mouth='wobbly', steam=0), 160),
        (pose(sx=1.06, sy=.94, knot=6, eyes='dot', mouth='wobbly', steam=.5), 200),
        (pose(sx=1.03, sy=.97, knot=-3, eyes='dot', mouth='wobbly', steam=1, twinkle=1), 240),
        (pose(sx=1.01, sy=.99, knot=1, eyes='dot', mouth='wobbly', steam=1.5), 260),
    ]),
    'finished': ('once', [
        (pose(sx=1.14, sy=.82, eyes='squeeze'), 180),
        (pose(lift=1, rise=8, sx=.88, sy=1.12, knot=-12, eyes='happy', mouth='open'), 90),
        (pose(lift=1, rise=18, sx=.97, sy=1.03, knot=8, eyes='happy', mouth='open', twinkle=1, extras=('sparkle',)), 200),
        (pose(lift=1, rise=8, sx=.91, sy=1.09, knot=14, eyes='happy', mouth='open'), 90),
        (pose(sx=1.15, sy=.8, knot=-10, eyes='happy', mouth='open', extras=()), 140),
        *rise_back((1.15, .8), 4, knot=-10, eyes='happy', extras=('blush',)),
        (pose(eyes='happy', twinkle=1, extras=('blush', 'hearts')), 600),
    ]),
    'needs-you': ('hold', [
        (pose(sx=1.1, sy=.9, eyes='wide', mouth='o'), 100),
        (pose(lift=1, rise=8, sx=.94, sy=1.06, knot=-10, eyes='wide', mouth='open', extras=('bang',)), 160),
        (pose(sx=1.08, sy=.92, knot=8, eyes='wide', mouth='open', extras=('bang',)), 120),
        (pose(lift=1, rise=6, sx=.96, sy=1.04, knot=-6, tilt=4, eyes='wide', mouth='open', extras=('bang',)), 160),
        (pose(sx=1.05, sy=.95, knot=4, eyes='wide', mouth='open', extras=('bang',)), 120),
        (pose(eyes='wide', mouth='o', tilt=-5, knot=4, extras=('bang', 'sweat')), 600),
    ]),
    'resting': ('hold', [
        (pose(sx=1.16, sy=.8, knot=-14, eyes='closed', mouth='smile', extras=('zzz',)), 1000),
    ]),
    'hover': ('loop', [
        (pose(sx=1.15, sy=.8, knot=-10, eyes='squeeze', mouth='o', extras=('blush',)), 160),
        *rise_back((1.15, .8), 4, knot=-10, eyes='happy', mouth='open', extras=('blush',)),
        (pose(eyes='happy', mouth='open', twinkle=1, extras=('blush', 'hearts')), 500),
    ]),
}
