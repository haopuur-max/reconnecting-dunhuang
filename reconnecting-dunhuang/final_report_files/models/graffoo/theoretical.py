"""Theoretical model: 16 entities, 19 canonical relations, 5 narrative layers, with authority records and subjects.

One body, two outputs: theoretical_web.svg (body + compact legend, for the web page) and theoretical_full.svg
(same body + the full legend and notes, for the PDF). Every relation, authority source, subject and evidence
definition is read from the TEI file and checked before saving."""
import sys, copy
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import TEI as TEI_PATH, out
from svglib import SVG, tw, INK, MONO
from lxml import etree

TEI = "{http://www.tei-c.org/ns/1.0}"
XID = "{http://www.w3.org/XML/1998/namespace}id"
T = etree.parse(str(TEI_PATH))
REC = {e.get(XID): e for e in T.find(f".//{TEI}standOff").iter(TEI + "person", TEI + "place", TEI + "org", TEI + "object")}
SRC = {"wikidata": "Wikidata", "viaf": "VIAF", "lc": "LC", "lcsh": "LCSH", "fast": "FAST", "worldcat-entity": "WorldCat",
       "bl-shelfmark": "BL shelfmark"}
EVDEF = {c.get(XID).split("-")[-1]: " ".join("".join(c.find(TEI + "catDesc").itertext()).split())
         for c in T.find(f".//{TEI}taxonomy[@{XID}='evidence']").iter(TEI + "category")}
CANON = {r.get(XID): (r.get("name"), r.get("active").lstrip("#"), r.get("passive").lstrip("#"), r.get("ana").split("-")[-1])
         for r in T.iter(TEI + "relation") if r.getparent().get("type") == "canonical"}
FORMALISED = {r.get("corresp").lstrip("#") for r in T.iter(TEI + "relation") if r.getparent().get("type") == "conceptual"}
SUBJ = [(c.findtext(f"{TEI}desc"), [e.get("uri").rsplit("/", 1)[-1] for e in c.iter(TEI + "equiv")])
        for c in T.find(f".//{TEI}taxonomy[@{XID}='concepts']").iter(TEI + "category")]
SUBJ_REL = [r.get("passive").lstrip("#") for r in T.iter(TEI + "relation") if r.getparent().get("type") == "subject"]


def idnos(xid):
    return [(i.get("type"), i.text.strip()) for i in REC[xid].iter(TEI + "idno")]


def sources(xid):
    out = []
    for t, _ in idnos(xid):
        if t in SRC and SRC[t] not in out:
            out.append(SRC[t])
    return out


# type sizes (px at full canvas width)
F_NAME, F_TYPE, F_CHIP, F_ID, F_REL, F_NOTE, F_NUM = 23, 16, 14.5, 14, 17.5, 16, 16
W = 1720
d = SVG(W, 100, "Reconnecting Dunhuang - theoretical model",
        "Theoretical model of Reconnecting Dunhuang: 16 entities and 19 relations in natural language across five narrative layers, "
        "with the authority records of each entity and the subject classification of the corpus, as recorded in the TEI file.")
TYPE = {"item": ("#9A6A12", "#FFFBEF"), "corpus": ("#B7791F", "#FFF6E0"), "place": ("#2F7D4F", "#EEF7F0"), "network": ("#6B5FB5", "#F2F0FB"),
        "person": ("#7A4E9C", "#F6F0FA"), "inst": ("#1F7A7A", "#EAF6F6"), "digital": ("#8E44AD", "#F5EEFA")}
DRAWN, BOX = [], {}
GREY = "#5B6470"


def chips(x, y, labels, size=F_CHIP):
    for lab in labels:
        w = tw(lab, size, 600) + 16
        d.rect(x, y, w, size + 10, fill="#FFFFFF", stroke="#9AA3AE", sw=1, rx=(size + 10) / 2)
        d.text(x + w / 2, y + size + 2.5, lab, size, 600, fill="#3F4956", anchor="middle")
        x += w + 6
    return x


def entity(key, xid, n, name, kind, typ, cx, cy, ids=None, minw=0):
    srcs = sources(xid)
    cw = sum(tw(s, F_CHIP, 600) + 22 for s in srcs)
    lines = [" · ".join(f"{SRC[t]} {v}" for t, v in idnos(xid) if t in grp) for grp in (ids or [])]
    pad = 58
    w = max(minw, tw(name, F_NAME, 600) + pad + 20, tw(typ, F_TYPE) + pad + 20, cw + pad + 14,
            *[tw(l, F_ID, 400, True) + pad + 20 for l in lines])
    h = 116 + 21 * len(lines)
    x, y = cx - w / 2, cy - h / 2
    col, fill = TYPE[kind]
    d.rect(x, y, w, h, fill=fill, stroke=col, sw=2, rx=10, dash="7 5" if kind == "network" else None)
    d.raw(f'<circle cx="{x+28:.1f}" cy="{y+30:.1f}" r="16" fill="#FFFFFF" stroke="{col}" stroke-width="1.8"/>')
    d.text(x + 28, y + 30 + F_NUM * .36, str(n), F_NUM, 600, fill=col, anchor="middle")
    d.text(x + pad, y + 38, name, F_NAME, 600)
    d.text(x + pad, y + 62, typ, F_TYPE, fill=GREY)
    chips(x + pad, y + 76, srcs)
    for i, l in enumerate(lines):
        d.text(x + pad, y + 126 + 21 * i, l, F_ID, fam=MONO, fill="#2F3944")
    BOX[key] = (x, y, w, h)
    return BOX[key]


def P(key, side, t=.5):
    x, y, w, h = BOX[key]
    return {"n": (x + w * t, y), "s": (x + w * t, y + h), "w": (x, y + h * t), "e": (x + w, y + h * t)}[side]


def rel(rid, pts, lpos, anchor="middle", two=False):
    name, a, b, ev = CANON[rid]
    enr = ev == "enriched"
    col = "#7C3AED" if enr else INK
    dash = ' stroke-dasharray="9 6"' if enr else ""
    path = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    d.mid.append(f'<path d="{path}" fill="none" stroke="{col}" stroke-width="2.2"{dash}/>')
    d._arrow(pts[-2], pts[-1], col, filled=True, L=15, W=7)
    tag = f"{rid.upper()}{'★' if enr else ''}"
    if two:
        d.text(lpos[0], lpos[1] - F_REL - 3, tag, F_REL, 600, fill=col, anchor=anchor, halo=True)
        d.text(lpos[0], lpos[1], name, F_REL, 600, fill=col, anchor=anchor, halo=True)
    elif rid not in FORMALISED:   # theoretical relation kept, no RDF statement formalises it: label + diamond
        lab = f"{tag}  {name}"; wl = tw(lab, F_REL, 600); wd = tw(" ◇", F_REL, 600) + 4
        x0 = lpos[0] - (wl + wd) / 2
        d.text(x0, lpos[1], lab, F_REL, 600, fill=col, halo=True)
        d.text(x0 + wl + 4, lpos[1], "◇", F_REL + 2, 600, fill="#B4410E", halo=True)
    else:
        d.text(lpos[0], lpos[1], f"{tag}  {name}", F_REL, 600, fill=col, anchor=anchor, halo=True)
    DRAWN.append((rid, a, b, pts[0], pts[-1]))


# ---- header ---------------------------------------------------------------------------------------
d.text(40, 58, "Theoretical model", 36, 600)
d.text(40, 92, "16 entities · 19 relations in natural language · 5 narrative layers · authority records and subjects from the TEI file",
       18, fill="#4B5563")
d.text(40, 124, "Together  →  Discovered  →  Dispersed  →  Institutionally separated  →  Digitally reconnected", 18, 600, fill="#2F3E50")

# ---- layers (title in a band header) ------------------------------------------------------------------
LAY = [("I", "Original context", "historical and spatial context", 150, 760, "#F4F7FC"),
       ("II", "Discovery", "rediscovery in 1900", 930, 230, "#FFFBF0"),
       ("III", "Dispersal", "early 20th-century dispersal", 1180, 560, "#FDF4F3"),
       ("IV", "Collections", "institutional separation", 1760, 900, "#F0F8F8"),
       ("V", "Digital reconnection", "contemporary virtual reunion", 2680, 350, "#F6F2FB")]
for num, title, sub, y, h, fill in LAY:
    d.rect(20, y, W - 40, h, fill=fill, stroke="#D5DCE5", sw=1.2, rx=16, layer="back")
    d.text(44, y + 36, f"{num}", 24, 600, fill="#1F4E79", layer="back")
    d.text(44 + tw(num, 24, 600) + 14, y + 36, title.upper(), 18, 600, fill="#1F4E79", layer="back")
    d.text(44 + tw(num, 24, 600) + 14 + tw(title.upper(), 18, 600) + 14, y + 36, sub, 16, fill="#6B7280", italic=True, layer="back")

# ---- the corpus: one column through all layers ---------------------------------------------------------
CX, CW = 645, 250
cy0, cy1 = 200, 2808
CL, CR = CX - CW / 2, CX + CW / 2
d.rect(CL, cy0, CW, cy1 - cy0, fill="#FFF6E0", stroke="#B7791F", sw=2.2, rx=14)
d.raw(f'<circle cx="{CL+28}" cy="{cy0+30}" r="16" fill="#FFFFFF" stroke="#B7791F" stroke-width="1.8"/>')
d.text(CL + 28, cy0 + 30 + F_NUM * .36, "1", F_NUM, 600, fill="#B7791F", anchor="middle")
d.text(CX, cy0 + 82, "DUNHUANG", 25, 600, anchor="middle")
d.text(CX, cy0 + 112, "MANUSCRIPTS", 25, 600, anchor="middle")
d.text(CX, cy0 + 138, "Historical manuscript corpus", F_TYPE, fill=GREY, anchor="middle")
srcs = sources("dunhuang-manuscripts")
chips(CX - (sum(tw(s, F_CHIP, 600) + 22 for s in srcs) - 6) / 2, cy0 + 152, srcs)
ids = {t: v for t, v in idnos("dunhuang-manuscripts")}
for i, l in enumerate([f"Wikidata {ids['wikidata']}", f"VIAF {ids['viaf']}", f"LC {ids['lc']}", f"FAST {ids['fast']}"]):
    d.text(CX, cy0 + 208 + 21 * i, l, F_ID, fam=MONO, fill="#2F3944", anchor="middle")
d.raw(f'<line x1="{CX}" y1="{cy0+300}" x2="{CX}" y2="{cy1-24}" stroke="#E2B45A" stroke-width="3" stroke-dasharray="2 8" stroke-linecap="round"/>')

# ---- I. original context ------------------------------------------------------------------------------
XL = 262
entity("silk", "silk-road", 9, "Silk Road", "network", "Historical / cultural network", XL, 270)
entity("dh", "dunhuang", 4, "Dunhuang", "place", "Place", XL, 445)
entity("mg", "mogao-caves", 3, "Mogao Caves", "place", "Place (heritage site)", XL, 640, ids=[["wikidata"], ["lcsh", "fast"]])
entity("lc", "library-cave", 2, "Library Cave (Cave 17)", "place", "Place (heritage site)", XL, 835)
for rid, lo, hi in [("r1", "dh", "silk"), ("r2", "mg", "dh"), ("r3", "lc", "mg")]:
    a, b = P(lo, "n"), P(hi, "s")
    rel(rid, [a, b], (XL + 12, (a[1] + b[1]) / 2 + 6), anchor="start")
rel("r4", [(CL, 835), P("lc", "e")], ((CL + P("lc", "e")[0]) / 2, 823), two=True)
sx, sy = CR + 120, 205
sw_, sh = W - 40 - sx - 14, 112 + 62 * len(SUBJ)
d.rect(sx, sy, sw_, sh, fill="#FFFFFF", stroke="#94A3B8", sw=1.5, rx=12)
d.text(sx + 24, sy + 40, "Subjects of the corpus", 21, 600)
d.text(sx + 24, sy + 66, "traditions named in the source", F_TYPE, fill=GREY)
for i, (name, eq) in enumerate(SUBJ):
    yy = sy + 112 + 62 * i
    d.rect(sx + 24, yy - 25, 300, 46, fill="#F1F5F9", stroke="#94A3B8", sw=1.2, rx=23)
    d.text(sx + 46, yy + 6, name, 18, 600)
    if eq:
        chips(sx + 340, yy - 12, [("Wikidata " if q.startswith("Q") else "LCSH ") + q for q in eq])
    else:
        d.text(sx + 342, yy + 6, "no authority link", 15, fill="#8A94A3", italic=True)
ay = sy + 112 + 62 * 2
d.mid.append(f'<path d="M{CR:.1f},{ay:.1f} L{sx:.1f},{ay:.1f}" fill="none" stroke="#64748B" stroke-width="2.2" stroke-dasharray="3 5"/>')
d._arrow((CR, ay), (sx, ay), "#64748B", L=14, W=6.5)
d.text((CR + sx) / 2, ay - 12, "has subject", 16, 600, fill="#475569", anchor="middle", halo=True)
d.text((CR + sx) / 2, ay + 26, f"× {len(SUBJ)}", 16, 600, fill="#475569", anchor="middle", halo=True)

# ---- II. discovery -------------------------------------------------------------------------------------
entity("wy1", "wang-yuanlu", 5, "Wang Yuanlu", "person", "Person", XL, 1055)
rel("r5", [P("wy1", "e"), (CL, 1055)], ((P("wy1", "e")[0] + CL) / 2, 1043))
d.rect(CR + 40, 1035, 170, 38, fill="#FFFFFF", stroke="#C9CED6", sw=1.1, rx=6, dash="3 3")
d.text(CR + 125, 1060, "25 June 1900", F_TYPE, anchor="middle", fill="#374151")
d.text(CR + 220, 1060, "date of the discovery", 15, fill=GREY, italic=True)

# ---- III. dispersal ------------------------------------------------------------------------------------
XW, XB = CR + 160, W - 205
entity("wy2", "wang-yuanlu", 5, "Wang Yuanlu", "person", "Person (as in layer II)", XW, 1500)
entity("st", "aurel-stein", 6, "Aurel Stein", "person", "Person", XB, 1330, ids=[["wikidata"], ["viaf", "lc"]], minw=330)
entity("pe", "paul-pelliot", 7, "Paul Pelliot", "person", "Person", XB, 1500, minw=330)
entity("ot", "otani-kozui", 8, "Ōtani Kōzui", "person", "Person", XB, 1655, minw=330)
lane = P("wy2", "e")[0] + 34
for rid, t, tgt in [("r6", .22, "st"), ("r7", .5, "pe"), ("r8", .78, "ot")]:
    a = P("wy2", "e", t); b = P(tgt, "w")
    pts = [a, b] if rid == "r7" else [a, (lane, a[1]), (lane, b[1]), b]
    rel(rid, pts, ((lane + b[0]) / 2 + 8, b[1] - 12))
entity("luo", "luo-zhenyu", 10, "Luo Zhenyu", "person", "Person", XL - 82, 1350)   # left of XL: room for the R13 label
rel("r13", [P("luo", "e"), (CL, 1350)], ((P("luo", "e")[0] + CL) / 2, 1338), two=True)
d.rect(XL - 210, 1435, 420, 66, fill="#FFFFFF", stroke="#C9CED6", sw=1.1, rx=6, dash="3 3")
d.text(XL - 192, 1462, "Scope: most of the remaining Chinese", F_TYPE, fill="#374151")
d.text(XL - 192, 1486, "manuscripts; to Beijing, 1910", F_TYPE, fill="#374151")

# ---- IV. collections ------------------------------------------------------------------------------------
XN = W - 300
entity("tnm", "tokyo-national-museum", 14, "Tokyo National Museum", "inst", "Institution", XL - 50, 1880, minw=320)
entity("nlc", "nlc", 13, "National Library of China", "inst", "Institution", XN, 1880, minw=430)
entity("bnf", "bnf", 12, "Bibliothèque nationale de France", "inst", "Institution", XN, 2035, minw=430)
entity("bl", "british-library", 11, "British Library", "inst", "Institution", XN, 2190, minw=430)
for rid, k, y, side in [("r12", "tnm", 1880, "L"), ("r11", "nlc", 1880, "R"), ("r10", "bnf", 2035, "R"), ("r9", "bl", 2190, "R")]:
    if side == "L":
        b = P(k, "e"); rel(rid, [(CL, y), b], ((CL + b[0]) / 2, y - 12))
    else:
        b = P(k, "w"); rel(rid, [(CR, y), b], ((CR + b[0]) / 2, y - 12))
# one documented item (Enriched, review round 2a): the printed Diamond Sutra of 868, under the British Library
entity("ds", "diamond-sutra-868", 16, "Diamond Sutra, printed copy of 868", "item", "Manuscript item (woodblock print)", XN, 2375,
       ids=[["bl-shelfmark", "wikidata"]], minw=430)
entity("st2", "aurel-stein", 6, "Aurel Stein", "person", "Person (as in layer III)", XN, 2560, minw=430)
rel("r19", [P("ds", "n"), P("bl", "s")], (XN + 14, (P("ds", "n")[1] + P("bl", "s")[1]) / 2 + 6), anchor="start")
rel("r17", [P("ds", "w"), (CR, P("ds", "w")[1])], ((CR + P("ds", "w")[0]) / 2, P("ds", "w")[1] - 12))
rel("r18", [P("ds", "s"), P("st2", "n")], (XN + 14, (P("ds", "s")[1] + P("st2", "n")[1]) / 2 + 6), anchor="start")
nx, ny = CR + 36, 2470
d.rect(nx, ny, 340, 118, fill="#FFFFFF", stroke="#C9CED6", sw=1.1, rx=6, dash="3 3")
for i, line in enumerate(["R19 is one documented case of R9:", "the British Library holds this item.",
                          "R9 itself stays a general relation (◇):", "the page does not say which items."]):
    d.text(nx + 16, ny + 28 + 24 * i, line, 15.5, fill="#374151")

# ---- V. digital ------------------------------------------------------------------------------------------
entity("idp", "idp", 15, "International Dunhuang Project (IDP)", "digital", "Digital heritage project", CX, 2938, ids=[["wikidata"]])
ix, iy, iw, ih = BOX["idp"]
yin = cy1 - 70
lw, le = ix - 40, ix + iw + 40
rel("r14", [(ix, iy + ih * .4), (lw, iy + ih * .4), (lw, yin), (CL, yin)], (lw - 12, iy + ih * .4 - 40), anchor="end")
rel("r15", [(CX, iy), (CX, cy1)], (CX + 12, (iy + cy1) / 2 + 6), anchor="start")
rel("r16", [(ix + iw, iy + ih * .4), (le, iy + ih * .4), (le, yin), (CR, yin)], (le + 12, iy + ih * .4 - 40), anchor="start")
BODY_H = 3045

# ---- checks ------------------------------------------------------------------------------------------------
KEY = {"silk": "silk-road", "dh": "dunhuang", "mg": "mogao-caves", "lc": "library-cave", "wy1": "wang-yuanlu", "wy2": "wang-yuanlu",
       "st": "aurel-stein", "pe": "paul-pelliot", "ot": "otani-kozui", "luo": "luo-zhenyu", "bl": "british-library", "bnf": "bnf",
       "nlc": "nlc", "tnm": "tokyo-national-museum", "idp": "idp", "ds": "diamond-sutra-868", "st2": "aurel-stein"}
assert sorted(r[0] for r in DRAWN) == sorted(CANON)
COL = (CL, cy0, CW, cy1 - cy0)
def owner(pt):
    hits = [k for k, (x, y, w, h) in list(BOX.items()) + [("corpus", COL)] if x - 1 <= pt[0] <= x + w + 1 and y - 1 <= pt[1] <= y + h + 1]
    return {KEY.get(k, "dunhuang-manuscripts") for k in hits}
for rid, a, b, p0, p1 in DRAWN:
    assert a in owner(p0) and b in owner(p1), (rid, a, b, owner(p0), owner(p1))
assert len(set(KEY.values()) | {"dunhuang-manuscripts"}) == 16
assert SUBJ_REL == [c.get(XID) for c in T.find(f".//{TEI}taxonomy[@{XID}='concepts']").iter(TEI + "category")]
assert sorted(set(CANON) - FORMALISED) == ["r12", "r9"]
for k, (x, y, w, h) in BOX.items():
    assert 20 < x and x + w < W - 20, ("box outside the canvas", k)

# ---- legends: compact (web) and full (PDF) -------------------------------------------------------------------
def legend(full):
    y0 = BODY_H + 10
    h = 362 if not full else 632
    d.rect(20, y0, W - 40, h, fill="#FFFFFF", stroke="#D5DCE5", sw=1.2, rx=12)
    d.text(44, y0 + 38, "Entity types", 17, 600)
    for i, (k, lab) in enumerate([("corpus", "Manuscript corpus"), ("place", "Place / heritage site"), ("network", "Cultural network"),
                                  ("person", "Person"), ("inst", "Institution"), ("digital", "Digital project"), ("item", "Manuscript item")]):
        col, fill = TYPE[k]
        xx, yy = 44 + (i % 2) * 250, y0 + 60 + (i // 2) * 40
        d.rect(xx, yy, 40, 24, fill=fill, stroke=col, sw=1.8, rx=5, dash="6 4" if k == "network" else None)
        d.text(xx + 52, yy + 18, lab, F_TYPE)
    X = 590
    d.text(X, y0 + 38, "Relations and evidence", 17, 600)
    def lg(y, col, dash, lab, sub=None):
        d.mid.append(f'<path d="M{X},{y} L{X+80},{y}" stroke="{col}" stroke-width="2.2" fill="none"{dash}/>')
        d._arrow((X, y), (X + 80, y), col, L=14, W=6.5)
        d.text(X + 96, y + 6, lab, F_TYPE)
        if sub:
            d.text(X + 96, y + 28, sub, 15, fill=GREY)
    lg(y0 + 72, INK, "", "R1–R15  Direct: extracted or modelled directly from the frozen Wikipedia revision",
       "(no independent historical verification implied)")
    lg(y0 + 132, "#7C3AED", ' stroke-dasharray="9 6"', "R16–R19★  Enriched: supported by an additional authoritative source",
       "(R16: a project interpretation; R17–R19: one documented item, IDP)")
    lg(y0 + 192, "#64748B", ' stroke-dasharray="3 5"', "has subject: the corpus classified by tradition")
    d.text(X + 30, y0 + 248, "◇", 19, 600, fill="#B4410E", anchor="middle")
    d.text(X + 96, y0 + 248, "not formalised — R9, R12: theoretical relations kept; no holding triple is asserted in the RDF", F_TYPE)
    d.text(X + 96, y0 + 272, "(the source does not say which manuscripts these institutions hold)", 15, fill=GREY)
    # repeated boxes: a small box with the same number marker, as drawn in the body
    d.rect(X + 6, y0 + 300, 68, 30, fill="#F6F0FA", stroke=TYPE["person"][0], sw=1.6, rx=6)
    d.raw(f'<circle cx="{X+24}" cy="{y0+315}" r="10" fill="#FFFFFF" stroke="{TYPE["person"][0]}" stroke-width="1.4"/>')
    d.text(X + 24, y0 + 320, "6", 13, 600, fill=TYPE["person"][0], anchor="middle")
    d.text(X + 96, y0 + 322, "Repeated box (same number, “as in layer …”) = the same entity drawn again, not an additional entity",
           F_TYPE)
    d.text(44, y0 + 226, "Authority records", 17, 600)
    xe = chips(44, y0 + 240, ["Wikidata", "VIAF", "LC", "LCSH", "FAST", "WorldCat"])
    chips(44, y0 + 270, ["BL shelfmark"])
    d.text(44 + tw("BL shelfmark", F_CHIP, 600) + 30, y0 + 286, "identifiers recorded in the TEI standOff", 15, fill=GREY)
    if full:
        yy = y0 + 362
        d.raw(f'<line x1="44" y1="{yy-14}" x2="{W-44}" y2="{yy-14}" stroke="#E2E8F0"/>')
        d.text(44, yy + 10, "Evidence types (TEI taxonomy, also skos:definition in the RDF)", 17, 600)
        d.text(44, yy + 40, f"Direct — {EVDEF['direct']}", F_TYPE)
        enr = EVDEF["enriched"]
        lines, cur = [], ""
        for word in f"Enriched — {enr}".split(" "):          # wrap to the legend width
            if tw((cur + " " + word).strip(), F_TYPE) > W - 100:
                lines.append(cur); cur = word
            else:
                cur = (cur + " " + word).strip()
        lines.append(cur)
        for i, line in enumerate(lines):
            d.text(44 + (tw("Enriched — ", F_TYPE) if i else 0), yy + 66 + 24 * i, line, F_TYPE)
        yy += 24 * (len(lines) - 2)
        d.text(44, yy + 154, "Natural-language layer: these entity types and relations are refactored into ontology classes and properties "
               "in the conceptual model.", F_TYPE)
        d.text(44, yy + 180, "Full authority numbers are printed for five entities; every record is in models/authority_linking_table.md.",
               F_TYPE)
        n_conc = sum(1 for r in T.iter(TEI + "relation") if r.getparent().get("type") == "conceptual")
        assert sorted(FORMALISED, key=lambda r: int(r[1:])) == [f"r{i}" for i in (*range(1, 9), 10, 11, *range(13, 20))]
        d.text(44, yy + 206, f"Relations formalised in the RDF: R1–R8, R10, R11, R13–R19 ({n_conc} conceptual triples); R9 and R12 are not.", F_TYPE)
    return y0 + h + 30


for mode in ("web", "full"):
    keep = (list(d.back), list(d.mid), list(d.front))
    d.h = legend(mode == "full")
    d.save(out("theoretical", mode))
    d.back, d.mid, d.front = keep
print(f"theoretical: {len(CANON)} relations, 16 entities; not formalised:", sorted(set(CANON) - FORMALISED))
