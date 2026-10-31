"""Small SVG toolkit for the Reconnecting Dunhuang model diagrams.

Graffoo notation (essepuntato.it/graffoo/specification):
  class            yellow rectangle, solid black border
  datatype         green rhomboid, solid black border
  individual       pink circle, solid black border
  class restriction light-yellow rectangle with a Manchester expression
  object property  blue line: filled circle at the domain end, filled arrow at the range end
  data property    green line: empty circle at the domain end, empty arrow at the range end
  annotation prop. orange line: backslash at the domain end, open arrow at the range end
  property facility (property defined elsewhere, only used here): the same line drawn dotted
  class axiom      solid black labelled arrow (rdfs:subClassOf)
  ontology         transparent box, dotted border, light-blue heading with the ontology IRI
  additional axioms light-blue box with a folded corner
"""
import base64, math, html, hashlib, re
from pathlib import Path
from PIL import ImageFont

from paths import TTF as FD, WOFF2 as SITE_FONTS
_FONTS = {}


def font(weight=400, size=16, mono=False):
    key = (weight, size, mono)
    if key not in _FONTS:
        f = "source-code-pro-latin-400-normal.ttf" if mono else f"source-sans-3-latin-{weight}-normal.ttf"
        _FONTS[key] = ImageFont.truetype(str(FD / f), size)
    return _FONTS[key]


def tw(text, size=16, weight=400, mono=False):
    """Text width in px, measured with the real font."""
    return font(weight, size, mono).getlength(text)


def esc(t):
    return html.escape(t, quote=True)


def font_face_css():
    faces = []
    for fam, wt, files in [("Source Sans 3", 400, ["source-sans-3-latin-400-normal", "source-sans-3-latin-ext-400-normal"]),
                           ("Source Sans 3", 600, ["source-sans-3-latin-600-normal", "source-sans-3-latin-ext-600-normal"]),
                           ("Source Code Pro", 400, ["source-code-pro-latin-400-normal", "source-code-pro-latin-ext-400-normal"]),
                           ("Source Serif 4", 600, ["source-serif-4-latin-600-normal"]),
                           ("Source Serif 4", 400, ["source-serif-4-latin-400-italic"])]:
        for f in files:
            data = base64.b64encode((SITE_FONTS / f"{f}.woff2").read_bytes()).decode()
            style = "italic" if "italic" in f else "normal"
            rng = "U+0100-024F,U+1E00-1EFF" if "ext" in f else "U+0000-00FF,U+2000-206F,U+2190-21FF,U+2200-22FF,U+2605"
            faces.append(f"@font-face{{font-family:'{fam}';font-style:{style};font-weight:{wt};"
                         f"src:url(data:font/woff2;base64,{data}) format('woff2');unicode-range:{rng}}}")
    return "\n".join(faces)


SANS = "'Source Sans 3','Helvetica Neue',Arial,sans-serif"
MONO = "'Source Code Pro',Menlo,monospace"
SERIF = "'Source Serif 4',Georgia,serif"

# Graffoo palette
C_CLASS, C_CLASS_R = "#FFF4A3", "#FFFBDA"
C_DT = "#CDEBC0"
C_IND = "#F8C9DA"
C_OBJ, C_DATA, C_ANN = "#1F5FBF", "#2E8B3E", "#D97706"
C_AX = "#DCEBFA"
INK = "#1D1D1F"


SIZES = {"cls": 17, "lab": 14.5, "sub": 13.5, "ind": 14, "indsub": 12}   # default class-name and arc-label sizes; scripts may change them


class SVG:
    def __init__(self, w, h, title, desc):
        self.w, self.h, self.title, self.desc = w, h, title, desc
        self.back, self.mid, self.front = [], [], []
        self.boxes = {}

    # ---- tagging: CSS classes on everything drawn since a mark (used by the presentation to highlight) ----
    def mark(self):
        return (len(self.back), len(self.mid), len(self.front))

    def tag_since(self, m, cls):
        for L, k in zip((self.back, self.mid, self.front), m):
            for i in range(k, len(L)):
                L[i] = re.sub(r'<(rect|text|path|polygon|polyline|circle|line)(?=[\s/>])', rf'<\1 class="{cls}"', L[i])

    # ---- primitives -------------------------------------------------------
    def text(self, x, y, s, size=16, weight=400, fill=INK, anchor="start", fam=SANS, italic=False, layer="front", halo=False, rot=0):
        st = ' font-style="italic"' if italic else ""
        if rot:
            st += f' transform="rotate({rot} {x:.1f} {y:.1f})"'
        h = ' paint-order="stroke" stroke="#FFFFFF" stroke-width="5" stroke-linejoin="round"' if halo else ""
        getattr(self, layer).append(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" font-size="{size}" font-weight="{weight}"'
                                    f' fill="{fill}" text-anchor="{anchor}"{st}{h}>{esc(s)}</text>')

    def rect(self, x, y, w, h, fill="none", stroke=INK, sw=1.4, rx=0, dash=None, layer="mid"):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        getattr(self, layer).append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def raw(self, s, layer="front"):
        getattr(self, layer).append(s)

    # ---- Graffoo widgets -----------------------------------------------------
    def cls(self, key, cx, cy, label, sub=None, minw=0, restriction=False, size=None):
        size = size or SIZES["cls"]
        w = max(minw, tw(label, size, 600) + 34, tw(sub or "", SIZES["sub"]) + 30)
        h = round(size * 2.7) if not sub else round(size * 3.5)
        x, y = cx - w / 2, cy - h / 2
        self.rect(x, y, w, h, fill=C_CLASS_R if restriction else C_CLASS, sw=1.5)
        if sub:
            self.text(cx, y + h * .45, label, size, 600, anchor="middle")
            self.text(cx, y + h * .8, sub, SIZES["sub"], 400, fill="#5B5B5B", anchor="middle")
        else:
            self.text(cx, cy + size * 0.36, label, size, 600, anchor="middle")
        self.boxes[key] = (x, y, w, h)
        return self.boxes[key]

    def restriction(self, key, cx, cy, lines, size=15):
        w = max(tw(l, size, 400, True) for l in lines) + 30
        h = 18 + 22 * len(lines)
        x, y = cx - w / 2, cy - h / 2
        self.rect(x, y, w, h, fill=C_CLASS_R, sw=1.5)
        for i, l in enumerate(lines):
            self.text(cx, y + 30 + 22 * i, l, size, 400, anchor="middle", fam=MONO)
        self.boxes[key] = (x, y, w, h)

    def datatype(self, key, cx, cy, label, size=None):
        size = size or SIZES["lab"]
        w, h, sk = tw(label, size, 600) + 44, 40, 14
        x, y = cx - w / 2, cy - h / 2
        pts = f"{x+sk:.1f},{y:.1f} {x+w:.1f},{y:.1f} {x+w-sk:.1f},{y+h:.1f} {x:.1f},{y+h:.1f}"
        self.mid.append(f'<polygon points="{pts}" fill="{C_DT}" stroke="{INK}" stroke-width="1.5"/>')
        self.text(cx, cy + size * 0.36, label, size, 600, anchor="middle")
        self.boxes[key] = (x, y, w, h, "rhomboid", sk)

    def individual(self, key, cx, cy, label, r=None, size=None, sub=None):
        size = size or SIZES["ind"]; ss = SIZES["indsub"]
        r = r or max(34, tw(label, size, 600) / 2 + 12, (tw(sub, ss) / 2 + 12) if sub else 0)
        self.mid.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{C_IND}" stroke="{INK}" stroke-width="1.5"/>')
        if sub:
            self.text(cx, cy - size * 0.12, label, size, 600, anchor="middle")
            self.text(cx, cy + size * 0.12 + ss * 1.05, sub, ss, 400, fill="#5B5B5B", anchor="middle")
        else:
            self.text(cx, cy + size * 0.36, label, size, 600, anchor="middle")
        self.boxes[key] = (cx - r, cy - r, 2 * r, 2 * r, "circle")

    def ontology_box(self, x, y, w, h, title, iri, size=15):
        self.rect(x, y, w, h, fill="none", stroke="#3B3B3B", sw=1.3, dash="2 4", layer="back")
        hh = 50
        self.back.append(f'<rect x="{x+0.7:.1f}" y="{y+0.7:.1f}" width="{w-1.4:.1f}" height="{hh}" fill="#CFE6F8"/>')
        self.text(x + 14, y + 22, title, size, 600, layer="back")
        self.text(x + 14, y + 41, iri, 13, 400, fam=MONO, fill="#3B4A57", layer="back")

    def axioms_box(self, x, y, lines, title="Additional axioms", size=14, w=None):
        w = w or max(tw(l, size, 400, True) for l in lines + [title]) + 34
        h = 40 + 21 * len(lines)
        f = 16
        pts = f"{x:.1f},{y:.1f} {x+w-f:.1f},{y:.1f} {x+w:.1f},{y+f:.1f} {x+w:.1f},{y+h:.1f} {x:.1f},{y+h:.1f}"
        self.mid.append(f'<polygon points="{pts}" fill="{C_AX}" stroke="{INK}" stroke-width="1.3"/>')
        self.mid.append(f'<polyline points="{x+w-f:.1f},{y:.1f} {x+w-f:.1f},{y+f:.1f} {x+w:.1f},{y+f:.1f}" fill="none" stroke="{INK}" stroke-width="1.3"/>')
        self.text(x + 14, y + 24, title, 14, 600)
        for i, l in enumerate(lines):
            self.text(x + 14, y + 47 + 21 * i, l, size, 400, fam=MONO)
        return (x, y, w, h)

    # ---- arcs ------------------------------------------------------------------
    def arc(self, pts, kind="obj", label=None, facility=False, lpos=None, lanchor="middle", lsize=14.5,
            lcolor=None, lseg=None, curve=False, loffset=(0, -7), lrot=0):
        lsize = SIZES["lab"] if lsize == 14.5 else lsize
        self.last_arc = list(pts)
        self.arc_mark = self.mark()
        """pts: list of (x, y). kind: obj | data | ann | sub."""
        col = {"obj": C_OBJ, "data": C_DATA, "ann": C_ANN, "sub": INK}[kind]
        dash = ' stroke-dasharray="1.5 4.5" stroke-linecap="round"' if facility else ""
        sw = 2.0 if facility else 1.7
        if curve and len(pts) == 4:
            d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f} C{pts[1][0]:.1f},{pts[1][1]:.1f} {pts[2][0]:.1f},{pts[2][1]:.1f} {pts[3][0]:.1f},{pts[3][1]:.1f}"
        else:
            d = _rounded(pts, 10)
        # shorten the line at the range end so it does not run through the arrowhead
        self.mid.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{sw}"{dash}/>')
        a, b = (pts[-2], pts[-1])
        s0, s1 = pts[1], pts[0]
        if kind == "sub":
            self._arrow(a, b, INK, filled=True)
        elif kind == "obj":
            self._dot(pts[0], col, filled=True); self._arrow(a, b, col, filled=True)
        elif kind == "data":
            self._dot(pts[0], col, filled=False); self._arrow(a, b, col, filled=False)
        elif kind == "ann":
            self._slash(s0, s1, col); self._arrow(a, b, col, filled=False, open_=True)
        if label:
            if lpos is None:
                i = lseg if lseg is not None else (len(pts) - 2) // 2
                (x1, y1), (x2, y2) = pts[i], pts[i + 1]
                lpos = ((x1 + x2) / 2 + loffset[0], (y1 + y2) / 2 + loffset[1])
            self.text(lpos[0], lpos[1], label, lsize, 600 if kind != "sub" else 400, fill=lcolor or (col if kind != "sub" else INK),
                      anchor=lanchor, halo=True, rot=lrot)

    def _dot(self, p, col, filled):
        self.front.append(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="5" fill="{col if filled else "#FFFFFF"}" stroke="{col}" stroke-width="1.8"/>')

    def _arrow(self, a, b, col, filled=True, open_=False, L=14, W=6.5):
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        p1 = (b[0] - L * math.cos(ang) + W * math.sin(ang), b[1] - L * math.sin(ang) - W * math.cos(ang))
        p2 = (b[0] - L * math.cos(ang) - W * math.sin(ang), b[1] - L * math.sin(ang) + W * math.cos(ang))
        if open_:
            self.front.append(f'<polyline points="{p1[0]:.1f},{p1[1]:.1f} {b[0]:.1f},{b[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}" fill="none" stroke="{col}" stroke-width="1.9"/>')
        else:
            fill = col if filled else "#FFFFFF"
            self.front.append(f'<polygon points="{b[0]:.1f},{b[1]:.1f} {p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}" fill="{fill}" stroke="{col}" stroke-width="1.6" stroke-linejoin="round"/>')

    def _slash(self, a, b, col):
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        c = (b[0] - 7 * math.cos(ang), b[1] - 7 * math.sin(ang))
        d = 7
        p1 = (c[0] + d * math.cos(ang + 2.2), c[1] + d * math.sin(ang + 2.2))
        p2 = (c[0] - d * math.cos(ang + 2.2), c[1] - d * math.sin(ang + 2.2))
        self.front.append(f'<line x1="{p1[0]:.1f}" y1="{p1[1]:.1f}" x2="{p2[0]:.1f}" y2="{p2[1]:.1f}" stroke="{col}" stroke-width="2"/>')

    # ---- anchor helpers ------------------------------------------------------
    def on_box(self, key, p, tol=2.5):
        """True if point p lies on the outline of box/circle key (used to check that each arc starts at its domain
        class and ends, with the arrowhead, at its range class)."""
        b = self.boxes[key]
        x, y, w, h = b[:4]
        if len(b) > 4 and b[4] == "circle":
            return abs(math.hypot(p[0] - (x + w / 2), p[1] - (y + h / 2)) - w / 2) <= tol
        if len(b) > 4 and b[4] == "rhomboid":
            sk = b[5]
            P = [(x + sk, y), (x + w, y), (x + w - sk, y + h), (x, y + h)]
            def dseg(a, c):
                vx, vy = c[0] - a[0], c[1] - a[1]
                t = max(0, min(1, ((p[0] - a[0]) * vx + (p[1] - a[1]) * vy) / (vx * vx + vy * vy)))
                return math.hypot(p[0] - a[0] - t * vx, p[1] - a[1] - t * vy)
            return min(dseg(P[i], P[(i + 1) % 4]) for i in range(4)) <= tol
        inside = x - tol <= p[0] <= x + w + tol and y - tol <= p[1] <= y + h + tol
        edge = min(abs(p[0] - x), abs(p[0] - x - w), abs(p[1] - y), abs(p[1] - y - h)) <= tol
        return inside and edge

    def side(self, key, s, t=0.5):
        """Point on side s (n,s,e,w) of a box, at fraction t along it."""
        b = self.boxes[key]
        x, y, w, h = b[:4]
        if len(b) > 4 and b[4] == "circle":
            cx, cy, r = x + w / 2, y + h / 2, w / 2
            ang = {"n": -90, "s": 90, "e": 0, "w": 180}[s] + (t - 0.5) * 80
            return (cx + r * math.cos(math.radians(ang)), cy + r * math.sin(math.radians(ang)))
        if len(b) > 4 and b[4] == "rhomboid":  # points on the slanted outline, not on the bounding box
            k = b[5]
            return {"n": (x + k + (w - k) * t, y), "s": (x + (w - k) * t, y + h), "w": (x + k * (1 - t), y + h * t),
                    "e": (x + w - k * t, y + h * t)}[s]
        return {"n": (x + w * t, y), "s": (x + w * t, y + h), "w": (x, y + h * t), "e": (x + w, y + h * t)}[s]

    def save(self, path):
        body = "\n".join(self.back + self.mid + self.front)
        uid = "g" + hashlib.sha1(self.title.encode()).hexdigest()[:6]   # unique ids, so two diagrams can share a page
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" height="{self.h}" '
               f'role="img" aria-labelledby="{uid}-t {uid}-d">'
               f'<title id="{uid}-t">{esc(self.title)}</title><desc id="{uid}-d">{esc(self.desc)}</desc>'
               f'<style>{font_face_css()}</style>'
               f'<rect width="{self.w}" height="{self.h}" fill="#FFFFFF"/>\n{body}\n</svg>')
        Path(path).write_text(svg, encoding="utf-8")
        return path


def _rounded(pts, r):
    if len(pts) == 2:
        return f"M{pts[0][0]:.1f},{pts[0][1]:.1f} L{pts[1][0]:.1f},{pts[1][1]:.1f}"
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(1, len(pts) - 1):
        p0, p1, p2 = pts[i - 1], pts[i], pts[i + 1]
        v1 = (p1[0] - p0[0], p1[1] - p0[1]); v2 = (p2[0] - p1[0], p2[1] - p1[1])
        l1 = math.hypot(*v1) or 1; l2 = math.hypot(*v2) or 1
        rr = min(r, l1 / 2, l2 / 2)
        a = (p1[0] - v1[0] / l1 * rr, p1[1] - v1[1] / l1 * rr)
        b = (p1[0] + v2[0] / l2 * rr, p1[1] + v2[1] / l2 * rr)
        d += f" L{a[0]:.1f},{a[1]:.1f} Q{p1[0]:.1f},{p1[1]:.1f} {b[0]:.1f},{b[1]:.1f}"
    d += f" L{pts[-1][0]:.1f},{pts[-1][1]:.1f}"
    return d
