"""Graffoo diagram 1 - conceptual model, core (classes and properties of the historical narrative).

Every usage arc is checked against usage.py (class-level usage in the final RDF) before saving."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import out
import svglib, conformance
from svglib import SVG, tw, INK, MONO
import usage
svglib.SIZES.update(cls=19.5, lab=17)

W, H = 1900, 1760
d = SVG(W, H, "Reconnecting Dunhuang - conceptual model, core (Graffoo)",
        "Graffoo diagram of the core of the Reconnecting Dunhuang conceptual model: CIDOC CRM 7.1.3, CRMsci 3.2 and "
        "CRMdig 5.0 classes, the reused properties used between them (dotted: property facility), the three dm: "
        "properties with their declared domain and range (solid), and the direct subclass axioms between the classes shown.")
DRAWN, NAME = [], {}
S = d.side
DIRCHECK = []
F = dict(facility=True)


def C(k, x, y, label):
    m = d.mark(); NAME[k] = label; d.cls(k, x, y, label); d.tag_since(m, f"node n-{k}")


def DT(k, x, y, label):
    m = d.mark(); NAME[k] = label; d.datatype(k, x, y, label); d.tag_since(m, f"node n-{k}")


def use(sk, p, ok):
    DRAWN.append((NAME[sk], p, NAME[ok]))
    pts = d.last_arc   # direction check: dot on the domain class, arrowhead on the range class
    assert d.on_box(sk, pts[0]) and d.on_box(ok, pts[-1]), (sk, p, ok, pts[0], pts[-1])
    DIRCHECK.append(p)
    d.tag_since(d.arc_mark, f"edge e-{sk}")   # the arc, its markers and its label, by domain class


def mid(a, b):
    return (a + b) / 2


# ---- header ------------------------------------------------------------------------
d.text(40, 54, "Conceptual model — core (Graffoo)", 34, 600)
d.text(40, 88, "How existing ontologies are used in this project: CIDOC CRM 7.1.3, CRMsci 3.2 and CRMdig 5.0 classes and properties as used by the data,", 18, fill="#444")
d.text(40, 114, "plus three project properties (dm:). An application profile — not a redefinition of CIDOC CRM.", 18, fill="#444")

# ---- classes -------------------------------------------------------------------------
X0, X1, X2, X3, XR = 215, 730, 1190, 1610, 1845
C("S19", X1, 200, "crmsci:S19_Encounter_Event")
C("E96", X1, 410, "crm:E96_Purchase")
C("E9",  X1, 640, "crm:E9_Move")
C("E7",  X1, 860, "crm:E7_Activity")
C("D2",  X1, 1070, "crmdig:D2_Digitization_Process")
C("E21", X2, 300, "crm:E21_Person")
C("E19", X2 - 30, 525, "crm:E19_Physical_Object")   # 30 px left: room for the P46i label
C("E53", X2, 760, "crm:E53_Place")
C("D1",  X2, 1070, "crmdig:D1_Digital_Object")
C("E39", X3, 150, "crm:E39_Actor")
C("E18", X3, 525, "crm:E18_Physical_Thing")
C("E74", X3, 1070, "crm:E74_Group")
C("E52", X0, 525, "crm:E52_Time-Span")
DT("dt",  X0, 245, "xsd:dateTime")
DT("str", X2 - 30, 640, "xsd:string")
L = {k: d.boxes[k][:4] for k in d.boxes}             # x, y, w, h
right = lambda k: L[k][0] + L[k][2]
left = lambda k: L[k][0]
top = lambda k: L[k][1]
bot = lambda k: L[k][1] + L[k][3]

def axiom(sk, ok, what):  # same direction check for the subclass axioms and the dm: properties
    pts = d.last_arc
    assert d.on_box(sk, pts[0]) and d.on_box(ok, pts[-1]), (sk, ok, what)
    DIRCHECK.append(what)
    d.tag_since(d.arc_mark, f"edge e-{sk}")


# ---- subclass axioms: only direct ones, both classes on the diagram ------------------
a = S("E21", "n", .75)
d.arc([a, (a[0], 150), S("E39", "w")], "sub", "rdfs:subClassOf", lpos=(a[0] + 10, 252), lanchor="start"); axiom("E21", "E39", "E21 subClassOf E39")
a = S("E74", "e", .5)
d.arc([a, (XR, a[1]), (XR, 150), S("E39", "e")], "sub", "rdfs:subClassOf", lpos=(XR - 7, 640), lrot=-90); axiom("E74", "E39", "E74 subClassOf E39")
a = S("E19", "e", .3)
d.arc([a, (left("E18"), a[1])], "sub", "rdfs:subClassOf", lpos=(mid(right("E19"), left("E18")), a[1] - 8)); axiom("E19", "E18", "E19 subClassOf E18")

# ---- dm: properties: declared in dm-ontology.ttl, solid, at their declared domain/range --
d.arc([S("E39", "s"), S("E18", "n")], "obj", "dm:virtuallyBringsTogether", lpos=(X3 + 12, 335), lanchor="start"); axiom("E39", "E18", "dm:virtuallyBringsTogether")
x0, y0, w0, h0 = L["E53"]; r = x0 + w0
d.arc([(r, y0 + 12), (r + 70, y0 + 12), (r + 70, y0 - 32), (r - 26, y0 - 32), (r - 26, y0)], "obj", "dm:partOfNetwork",
      lpos=(r + 78, y0 - 8), lanchor="start"); axiom("E53", "E53", "dm:partOfNetwork")
d.arc([(r, y0 + h0 - 12), (r + 70, y0 + h0 - 12), (r + 70, y0 + h0 + 32), (r - 26, y0 + h0 + 32), (r - 26, y0 + h0)], "obj", "dm:locatedNear",
      lpos=(r + 78, y0 + h0 + 22), lanchor="start"); axiom("E53", "E53", "dm:locatedNear")

# ---- reused properties used here (property facility: dotted, no domain/range asserted) ----
# discovery
a = S("S19", "e", .3); x = S("E21", "n", .3)[0]
d.arc([a, (x, a[1]), (x, top("E21"))], "obj", "crm:P14_carried_out_by", lpos=(mid(a[0], x), a[1] - 8), **F); use("S19", "crm:P14_carried_out_by", "E21")
a = S("S19", "e", .75); lx = S("E18", "n", .12)[0]
d.arc([a, (lx, a[1]), (lx, top("E18"))], "obj", "crmsci:O19_encountered_object",
      lpos=(mid(S("E21", "n", .75)[0], lx) + 10, a[1] - 8), **F); use("S19", "crmsci:O19_encountered_object", "E18")
# purchase
a = S("E96", "e", .2); x = S("E21", "s", .4)[0]
d.arc([a, (x, a[1]), (x, bot("E21"))], "obj", "crm:P23_transferred_title_from", lpos=(a[0] + 12, a[1] - 9), lanchor="start", **F); use("E96", "crm:P23_transferred_title_from", "E21")
a = S("E96", "e", .8); x = S("E21", "s", .75)[0]
d.arc([a, (x, a[1]), (x, bot("E21"))], "obj", "crm:P22_transferred_title_to", lpos=(a[0] + 12, a[1] + 21), lanchor="start", **F); use("E96", "crm:P22_transferred_title_to", "E21")
a = S("E96", "s", .5); b = S("E19", "w", .3)
d.arc([a, (a[0], b[1]), b], "obj", "crm:P24_transferred_title_of", lpos=(mid(a[0], b[0]), b[1] - 9), **F); use("E96", "crm:P24_transferred_title_of", "E19")
# transfer
a = S("E9", "e", .25); b = S("E19", "w", .75); lx = X1 + 210
d.arc([a, (lx, a[1]), (lx, b[1]), b], "obj", "crm:P25_moved", lpos=(lx - 8, mid(a[1], b[1]) + 5), lanchor="end", **F); use("E9", "crm:P25_moved", "E19")
a = S("E9", "e", .75); b = S("E53", "w", .72); lx = left("E53") - 95
d.arc([a, (lx, a[1]), (lx, b[1]), b], "obj", "crm:P26_moved_to", lpos=(mid(a[0], lx), a[1] + 21), **F); use("E9", "crm:P26_moved_to", "E53")
a = S("E9", "w", .25); lx = X1 - 110; b = S("E21", "w", .5)
d.arc([a, (lx, a[1]), (lx, b[1]), b], "obj", "crm:P15_was_influenced_by", lpos=(mid(lx, b[0]), b[1] - 9), **F); use("E9", "crm:P15_was_influenced_by", "E21")
# sealing
a = S("E7", "e", .3); x = S("E53", "s", .3)[0]
d.arc([a, (x, a[1]), (x, bot("E53"))], "obj", "crm:P7_took_place_at", lpos=(mid(a[0], x), a[1] - 8), **F); use("E7", "crm:P7_took_place_at", "E53")
a = S("E7", "e", .75); x = left("E18") + 22
d.arc([a, (x, a[1]), (x, bot("E18"))], "obj", "crm:P12_occurred_in_the_presence_of", lpos=(mid(a[0], x), a[1] + 21), **F); use("E7", "crm:P12_occurred_in_the_presence_of", "E18")
# time-spans, to the left
for k, lane, t, ts in [("S19", 345, .2, .5), ("E96", 395, .4, .5), ("E9", 395, .6, .75), ("E7", 345, .8, .5)]:
    a = S(k, "w", ts); b = S("E52", "e", t)
    d.arc([a, (lane, a[1]), (lane, b[1]), b], "obj", "crm:P4_has_time-span", lpos=(mid(a[0], lane), a[1] + (22 if k == "E9" else -8)), lsize=16.5, **F)
    use(k, "crm:P4_has_time-span", "E52")
# digitization
a = S("D2", "e", .5); b = S("D1", "w", .5)
d.arc([a, b], "obj", "crmdig:L11_had_output", lpos=(mid(a[0], b[0]), a[1] - 9), lsize=15.5, **F); use("D2", "crmdig:L11_had_output", "D1")
a = S("D2", "n", .8); x = left("E18") + 62; yl = top("D2") - 72
d.arc([a, (a[0], yl), (x, yl), (x, bot("E18"))], "obj", "crmdig:L1_digitized", lpos=(mid(a[0], x), yl - 8), **F); use("D2", "crmdig:L1_digitized", "E18")
a = S("D2", "s", .5); yl = bot("D2") + 52
d.arc([a, (a[0], yl), (X3, yl), S("E74", "s")], "obj", "crm:P14_carried_out_by", lpos=(mid(a[0], X3), yl - 8), **F); use("D2", "crm:P14_carried_out_by", "E74")
a = S("D1", "e", .5); b = S("E74", "w", .5)
d.arc([a, b], "obj", "dcterms:publisher", lpos=(mid(a[0], b[0]), a[1] - 9), **F); use("D1", "dcterms:publisher", "E74")
# physical things
a = S("E19", "e", .75)
d.arc([a, (left("E18"), a[1])], "obj", "crm:P46i_forms_part_of", lpos=(mid(right("E19"), left("E18")), a[1] + 21), lsize=16, **F); use("E19", "crm:P46i_forms_part_of", "E18")
a = S("E19", "s", .9); yl = bot("E19") + 42; lx = X3 + 150
d.arc([a, (a[0], yl), (lx, yl), (lx, top("E74") - 38), (S("E74", "n", .7)[0], top("E74") - 38), S("E74", "n", .7)], "obj",
      "crm:P50_has_current_keeper", lpos=(lx - 7, 800), lrot=-90, **F); use("E19", "crm:P50_has_current_keeper", "E74")
x0, y0, w0, h0 = L["E53"]
d.arc([(x0 + 26, y0), (x0 + 26, y0 - 32), (x0 - 46, y0 - 32), (x0 - 46, y0 + 12), (x0, y0 + 12)], "obj", "crm:P89_falls_within",
      lpos=(x0 - 10, y0 - 40), **F); use("E53", "crm:P89_falls_within", "E53")
# data properties
a = S("E19", "s", .35)
d.arc([a, (a[0], top("str"))], "data", "crm:P3_has_note", lpos=(a[0] - 9, mid(bot("E19"), top("str")) + 5), lanchor="end", **F); use("E19", "crm:P3_has_note", "str")
for t, p in [(.3, "crm:P82a_begin_of_the_begin"), (.7, "crm:P82b_end_of_the_end")]:
    a = S("E52", "n", t)
    d.arc([a, (a[0], bot("dt"))], "data", p, lpos=(a[0] - 7, mid(top("E52"), bot("dt"))), lanchor="middle", lsize=16, lrot=-90, **F)
    use("E52", p, "dt")

# ---- bottom: compact legend (web) or full panels (PDF) ---------------------------------------
def e96_note(x, y):
    lines = conformance.E96_LINES
    w, h = 296, 52 + 22 * len(lines)
    d.rect(x, y, w, h, fill="#FFFBEB", stroke="#D9A441", sw=1.4, rx=6)
    d.text(x + 16, y + 30, "Why an event?", 17, 600)
    for i, l in enumerate(lines):
        d.text(x + 16, y + 56 + 22 * i, l, 15, fill="#2A2A2A")


def compact_legend(Y):
    d.rect(30, Y, W - 60, 128, fill="#FFFFFF", stroke="#9A9A9A", sw=1)
    d.cls("lg_c", 110, Y + 40, "Class", minw=110, size=15); d.datatype("lg_d", 110, Y + 92, "Datatype", size=15)
    items = [("obj", False, "declared here (dm:): domain and range as in dm-ontology.ttl"),
             ("obj", True, "existing property (CIDOC CRM, CRMsci, CRMdig, DCTerms) used between these classes;"),
             ("data", True, "existing data property used here"),
             ("sub", False, "rdfs:subClassOf, direct only")]
    for i, (k, fac, lab) in enumerate(items):
        y = Y + 30 + 26 * i
        d.arc([(210, y), (300, y)], k, None, facility=fac); d.text(314, y + 5, lab, 15)
    d.text(314 + tw("existing property (CIDOC CRM, CRMsci, CRMdig, DCTerms) used between these classes; ", 15), Y + 61, "no domain or range asserted", 15, 600)
    d.text(1240, Y + 35, "● domain end   ▶ range end", 15, fill="#333")
    d.text(1240, Y + 62, "Declared domain/range of every existing property and", 15, fill="#333")
    d.text(1240, Y + 84, "the inheritance that makes each use valid: see the", 15, fill="#333")
    d.text(1240, Y + 106, "table that accompanies this figure, and the full PDF.", 15, fill="#333")
    return Y + 128


def full_panels(Y):
    d.ontology_box(30, Y, 620, 262, "Reconnecting Dunhuang project ontology 2.1", "https://haopuur-max.github.io/reconnecting-dunhuang/ontology/")
    d.axioms_box(48, Y + 66, [
        "ObjectProperty: dm:partOfNetwork",
        "  Domain: crm:E53_Place   Range: crm:E53_Place",
        "ObjectProperty: dm:locatedNear",
        "  Characteristics: Symmetric",
        "  Domain: crm:E53_Place   Range: crm:E53_Place",
        "ObjectProperty: dm:virtuallyBringsTogether",
        "  Domain: crm:E39_Actor   Range: crm:E18_Physical_Thing"], title="Additional axioms (dm-ontology.ttl)", size=13.5, w=584)
    px, py = 30, Y + 282
    d.rect(px, py, 620, 200, fill="#FFFFFF", stroke=INK, sw=1.3)
    d.raw(f'<rect x="{px+0.7}" y="{py+0.7}" width="618.6" height="34" fill="#EDEDED"/>')
    d.text(px + 14, py + 23, "Prefixes", 15, 600)
    for i, (p, iri) in enumerate([("crm:", "http://www.cidoc-crm.org/cidoc-crm/   (7.1.3)"), ("crmsci:", "http://www.cidoc-crm.org/extensions/crmsci/   (3.2)"),
                                  ("crmdig:", "http://www.cidoc-crm.org/extensions/crmdig/   (5.0)"), ("dcterms:", "http://purl.org/dc/terms/"),
                                  ("dm:", "https://haopuur-max.github.io/reconnecting-dunhuang/ontology/"), ("xsd:", "http://www.w3.org/2001/XMLSchema#")]):
        d.text(px + 14, py + 58 + 23 * i, p, 13.5, fam=MONO, fill="#1F5FBF")
        d.text(px + 100, py + 58 + 23 * i, iri, 13.5, fam=MONO)

    lx, ly, lw, lh = 672, Y, 300, 482
    d.rect(lx, ly, lw, lh, fill="#FFFFFF", stroke="#9A9A9A", sw=1)
    d.text(lx + 16, ly + 30, "Graffoo notation", 15, 600)
    yy = ly + 66
    d.cls("lg_c", lx + 72, yy, "Class", minw=100, size=14); d.text(lx + 140, yy + 5, "class", 13.5)
    yy += 54; d.datatype("lg_d", lx + 72, yy, "Datatype"); d.text(lx + 140, yy + 5, "datatype", 13.5)
    def lgarc(y, kind, fac):
        d.arc([(lx + 20, y), (lx + 126, y)], kind, None, facility=fac)
    yy += 56; lgarc(yy, "obj", False); d.text(lx + 140, yy - 4, "object property", 13.5); d.text(lx + 140, yy + 14, "declared here", 13.5)
    yy += 58; lgarc(yy, "obj", True); d.text(lx + 140, yy - 4, "object property", 13.5); d.text(lx + 140, yy + 14, "used here (facility)", 13.5)
    yy += 58; lgarc(yy, "data", True); d.text(lx + 140, yy - 4, "data property", 13.5); d.text(lx + 140, yy + 14, "used here (facility)", 13.5)
    yy += 56; lgarc(yy, "sub", False); d.text(lx + 140, yy + 5, "rdfs:subClassOf", 13.5)
    yy += 44; d.text(lx + 16, yy, "● domain end   ▶ range end", 13, fill="#444")
    yy += 22; d.text(lx + 16, yy, "Dotted arcs assert no domain or range;", 13, fill="#444")
    yy += 19; d.text(lx + 16, yy, "they show where an existing property is", 13, fill="#444")
    yy += 19; d.text(lx + 16, yy, "used. Its declared signature is on the right.", 13, fill="#444")

    cx, cw = 994, 876
    rows = conformance.ROWS
    nl = sum(len(r[3]) for r in rows)
    ch = 92 + 20.5 * nl + 10
    d.rect(cx, Y, cw, max(ch, 482), fill="#FFFFFF", stroke="#9A9A9A", sw=1)
    d.text(cx + 16, Y + 30, "Why each reused property fits the classes it links", 15, 600)
    d.text(cx + 16, Y + 51, "Declared domain → range in CIDOC CRM 7.1.3, CRMsci 3.2, CRMdig 5.0, DCMI Terms 2020.  ⊑ : subclass of", 13, fill="#555")
    cols = [cx + 16, cx + 300, cx + 420, cx + 572]
    hy = Y + 78
    for xx, h in zip(cols, ["Property", "Declared", "Used here", "Valid because"]):
        d.text(xx, hy, h, 13, 600, fill="#444")
    d.raw(f'<line x1="{cx+16}" y1="{hy+7}" x2="{cx+cw-16}" y2="{hy+7}" stroke="#BBB" stroke-width="1"/>')
    y = hy + 27
    for p, dec, uw, inh in rows:
        d.text(cols[0], y, p, 12.5, fam=MONO); d.text(cols[1], y, dec, 12.5); d.text(cols[2], y, uw, 12.5)
        for j, line in enumerate(inh):
            d.text(cols[3], y + 20.5 * j, line, 12.5)
        y += 20.5 * len(inh)

    return Y + max(ch, 482)


# ---- every usage arc drawn == every class-level use in the data -------------------------
CORE = {"crm:P4_has_time-span", "crm:P7_took_place_at", "crm:P12_occurred_in_the_presence_of", "crm:P14_carried_out_by",
        "crm:P15_was_influenced_by", "crm:P22_transferred_title_to", "crm:P23_transferred_title_from", "crm:P24_transferred_title_of",
        "crm:P25_moved", "crm:P26_moved_to", "crm:P46i_forms_part_of", "crm:P50_has_current_keeper", "crm:P89_falls_within",
        "crm:P3_has_note", "crm:P82a_begin_of_the_begin", "crm:P82b_end_of_the_end", "crmsci:O19_encountered_object",
        "crmdig:L1_digitized", "crmdig:L11_had_output", "dcterms:publisher"}
data = {k for k in usage.usage() if k[1] in CORE}
assert set(DRAWN) == data, (sorted(data - set(DRAWN)), sorted(set(DRAWN) - data))
print(f"core: {len(DRAWN)} usage arcs = data; {len(DIRCHECK)} arcs start on the domain class and end on the range class; height {d.h}")
e96_note(30, 610)
BODY = 1200
for mode in ("web", "full"):
    keep = (list(d.back), list(d.mid), list(d.front), dict(d.boxes))
    end = compact_legend(BODY) if mode == "web" else full_panels(BODY)
    d.h = int(end + 50)
    d.text(40, d.h - 20, f"Generated from reconnecting_dunhuang.ttl ({len(usage.G)} triples) and dm-ontology.ttl. Labels, identifiers, subjects and "
           "provenance: second diagram.", 15, fill="#666")
    d.save(out("core", mode))
    d.back, d.mid, d.front, d.boxes = keep
