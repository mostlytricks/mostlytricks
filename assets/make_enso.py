"""A personal avatar: gravity's mark drawn as an ensō (a Zen brush circle) in sumi ink on hanji.

Same geometry as gravity's mark (brand/make_mark.py MASTER): a mass at the centre, a band winding ~295 degrees,
thin at its tail and heavy at its head, ending in a round body. Read as a brush: the body is where the brush
landed and pooled, the band is the sweep, the tail is where it lifted off and went dry.
"""
import math
import random
import sys

A0, SWEEP = -0.95, 5.15
CX, CY = 50.0, 52.0
R0, R1, W0, W1, WEXP = 33.0, 24.0, 1.4, 9.6, 0.9
CENTRE, HEAD = 11.5, 7.5

INK = "#1A1815"
PAPER_TOP, PAPER_BOTTOM = "#F3EEE4", "#E8E0D1"


def n(v):
    s = f"{v:.2f}"
    return s.rstrip("0").rstrip(".") if "." in s else s


def at(u):
    return A0 - SWEEP * u, R0 + (R1 - R0) * u


def width(u):
    return W0 + (W1 - W0) * (u ** WEXP)


def xy(a, r):
    return CX + r * math.cos(a), CY + r * math.sin(a)


def bristles(rng, count=34, steps=220):
    """The band as many bristle strands; toward the tail they break into the dry brush's gaps (kasure)."""
    out = []
    for k in range(count):
        f = -1 + 2 * (k + 0.5) / count               # where across the band this bristle runs (-1 .. 1)
        edge = abs(f)
        # outer bristles lose the paper first: each has a u below which it carries little ink
        dry_from = 0.12 + 0.42 * edge ** 1.6 + rng.uniform(-0.05, 0.05)
        seg, segs = [], []
        on = True
        for i in range(steps + 1):
            u = i / steps
            dryness = max(0.0, (dry_from - u) / max(dry_from, 1e-6))   # 0 where wet, toward 1 at the tail
            p_off = 0.0008 + 0.30 * dryness
            p_on = 0.35 - 0.30 * dryness
            on = (rng.random() > p_off) if on else (rng.random() < p_on)
            if on:
                seg.append(u)
            elif seg:
                segs.append(seg)
                seg = []
        if seg:
            segs.append(seg)
        for s in segs:
            if len(s) < 2:
                continue
            outer, inner = [], []
            for u in s:
                a, r = at(u)
                w = width(u) / 2
                mid = r + f * w
                half = w / count * 1.9               # strands overlap so the wet part reads solid
                outer.append(xy(a, mid + half))
                inner.append(xy(a, mid - half))
            d = "M" + "L".join(f"{n(x)} {n(y)}" for x, y in outer + inner[::-1]) + "Z"
            op = 0.9 + 0.1 * rng.random()
            out.append(f'<path d="{d}" fill-opacity="{n(op)}"/>')
    return out


def svg(size_px=1024, seed=7):
    rng = random.Random(seed)
    side = 104.0
    vx, vy = 49.66 - side / 2, 50.49 - side / 2
    hx, hy = xy(*at(1.0))
    strands = "\n".join(bristles(rng))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="{n(vx)} {n(vy)} {n(side)} {n(side)}" width="{size_px}" height="{size_px}">
<defs>
  <linearGradient id="paper" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{PAPER_TOP}"/><stop offset="1" stop-color="{PAPER_BOTTOM}"/>
  </linearGradient>
  <radialGradient id="vignette" cx="50%" cy="48%" r="70%">
    <stop offset="0.55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#3A2E1E" stop-opacity="0.05"/>
  </radialGradient>
  <filter id="fibre" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="0.75" numOctaves="4" seed="3" result="t"/>
    <feColorMatrix in="t" type="matrix" values="0 0 0 0 0.35  0 0 0 0 0.28  0 0 0 0 0.18  0 0 0 0.07 0"/>
  </filter>
  <filter id="brush" x="-10%" y="-10%" width="120%" height="120%">
    <feTurbulence type="fractalNoise" baseFrequency="0.22" numOctaves="3" seed="11" result="n"/>
    <feDisplacementMap in="SourceGraphic" in2="n" scale="1.6" xChannelSelector="R" yChannelSelector="G" result="d"/>
    <feTurbulence type="fractalNoise" baseFrequency="0.09" numOctaves="2" seed="5" result="grain"/>
    <feColorMatrix in="grain" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  -0.3 0 0 0 1.08" result="mask"/>
    <feComposite in="d" in2="mask" operator="in"/>
  </filter>
  <filter id="dot" x="-20%" y="-20%" width="140%" height="140%">
    <feTurbulence type="fractalNoise" baseFrequency="0.24" numOctaves="3" seed="23" result="n"/>
    <feDisplacementMap in="SourceGraphic" in2="n" scale="1.3" xChannelSelector="R" yChannelSelector="G"/>
  </filter>
  <filter id="bleed" x="-30%" y="-30%" width="160%" height="160%">
    <feGaussianBlur stdDeviation="0.9"/>
  </filter>
</defs>
<rect x="{n(vx)}" y="{n(vy)}" width="{n(side)}" height="{n(side)}" fill="url(#paper)"/>
<rect x="{n(vx)}" y="{n(vy)}" width="{n(side)}" height="{n(side)}" filter="url(#fibre)"/>
<rect x="{n(vx)}" y="{n(vy)}" width="{n(side)}" height="{n(side)}" fill="url(#vignette)"/>
<g fill="{INK}" opacity="0.10" filter="url(#bleed)">
  <circle cx="{n(CX)}" cy="{n(CY)}" r="{n(CENTRE + 0.5)}"/><circle cx="{n(hx)}" cy="{n(hy)}" r="{n(HEAD + 0.4)}"/>
</g>
<g fill="{INK}" filter="url(#brush)">
{strands}
  <g filter="url(#dot)"><circle cx="{n(CX)}" cy="{n(CY)}" r="{n(CENTRE)}"/><circle cx="{n(hx)}" cy="{n(hy)}" r="{n(HEAD)}"/></g>
</g>
</svg>
'''


if __name__ == "__main__":
    out = sys.argv[1]
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 7
    if len(sys.argv) > 3:
        HEAD = float(sys.argv[3])      # the body at the band's head (the mark's own: 7.5)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(svg(seed=seed))
