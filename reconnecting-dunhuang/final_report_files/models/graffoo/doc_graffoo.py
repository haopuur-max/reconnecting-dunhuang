"""Graffoo diagram 2 - conceptual model: subjects, identifiers and evidence.

Two versions from the same code and the same checks:
  web  - every class, property, example individual and fact; short notes only (the long notes go into the HTML of the
         Models page)
  full - the same diagram plus the complete notes, both evidence definitions, the Graffoo legend and the prefixes (PDF)

Class level on the left of each band (checked against usage.py), one real example from the data on the right (checked
against the Turtle file). Evidence definitions are read from the Turtle file, not typed here."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import TTL, out
import svglib
from svglib import SVG, tw, INK, MONO, C_OBJ, C_DATA
import usage
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL, SKOS, DCTERMS

svglib.SIZES.update(cls=19.5, lab=17, sub=15, ind=16.5, indsub=14)
F_NOTE, F_BAND, F_BSUB = 16, 24, 17

G = Graph().parse(TTL)
RES = "https://haopuur-max.github.io/reconnecting-dunhuang/resource/"
CRM = "http://www.cidoc-crm.org/cidoc-crm/"
WD = "http://www.wikidata.org/entity/"
DEF = {k: str(G.value(URIRef(RES + "evidence/" + k), SKOS.definition)) for k in ("direct", "enriched")}
N_EV = {k: len(set(G.subjects(DCTERMS.type, URIRef(RES + "evidence/" + k)))) for k in ("direct", "enriched")}
N_STMT = len(set(G.subjects(RDF.type, RDF.Statement)))
N_PROP = len(set(G.subjects(RDF.type, URIRef(CRM + "E89_Propositional_Object"))))
assert (N_STMT, N_PROP, N_EV["direct"], N_EV["enriched"], len(G)) == (38, 19, 34, 4, 683)
_ids = set(G.subjects(RDF.type, URIRef(CRM + "E42_Identifier")))
N_IDS, N_SCHEMES = len(_ids), len({G.value(i, URIRef(CRM + "P2_has_type")) for i in _ids})
N_SAME, N_SEE = len(list(G.triples((None, OWL.sameAs, None)))), len(list(G.triples((None, RDFS.seeAlso, None))))
assert (N_IDS, N_SCHEMES, N_SAME, N_SEE) == (45, 8, 10, 30)
N_SRC = len(list(G.triples((None, DCTERMS.source, None))))
assert N_SRC == 6 and {G.value(x, DCTERMS.type) for x in G.subjects(DCTERMS.source, None)} == {URIRef(RES + "evidence/enriched")}
assert {str(G.value(x, RDF.type)) for x in G.subjects(OWL.sameAs, None)} == {CRM + "E21_Person", CRM + "E74_Group"}
N_SUBJ = len(set(G.objects(URIRef(RES + "dunhuang-manuscripts"), DCTERMS.subject)))
N_WD = len([o for o in G.objects(None, SKOS.exactMatch) if str(o).startswith(WD)])
N_LCSH = len([o for o in G.objects(None, SKOS.exactMatch) if "id.loc.gov/authorities/subjects/" in str(o)])
assert (N_SUBJ, N_WD, N_LCSH) == (6, 6, 5)
assert URIRef("http://id.loc.gov/authorities/names/n82045000") in set(G.objects(URIRef(RES + "aurel-stein"), RDFS.seeAlso))
assert len(set(G.subjects(RDF.type, SKOS.Concept))) == 6 + 2   # 6 subjects + 2 evidence types
W = 1900


def build(FULL):
    H = 3020 if FULL else 2560
    d = SVG(W, H, "Reconnecting Dunhuang - conceptual model: subjects, identifiers and evidence (Graffoo)",
            "Graffoo diagram of the documentation layer of the Reconnecting Dunhuang dataset: crm:E42 identifiers and authority "
            "links (owl:sameAs, rdfs:seeAlso), subject concepts in SKOS, and the evidence layer, in which the conceptual-relation "
            "triples are restated as rdf:Statement nodes that point to the propositions of the theoretical model (crm:E89), to "
            "their evidence type and, for Enriched statements, to their sources.")
    DRAWN, NAME, FACTS, EXCHECK = [], {}, [], []
    S = d.side
    F = dict(facility=True)

    def fact(s, p, o):
        FACTS.append((s, p, o))

    def C(k, x, y, label, sub=None, minw=0):
        NAME[k] = label; d.cls(k, x, y, label, sub=sub, minw=minw)

    def use(sk, p, ok):
        DRAWN.append((NAME[sk], p, NAME[ok]))
        pts = d.last_arc   # direction check: dot on the domain class, arrowhead on the range class
        assert d.on_box(sk, pts[0]) and d.on_box(ok, pts[-1]), (sk, p, ok, pts[0], pts[-1])

    def ex(sk, ok):        # same check for an example arc between two individuals
        pts = d.last_arc
        assert d.on_box(sk, pts[0]) and d.on_box(ok, pts[-1]), (sk, ok, pts[0], pts[-1])
        EXCHECK.append((sk, ok))

    def ind(k, x, y, label, sub=None):
        d.individual(k, x, y, label, sub=sub)

    def iri(k, x, y, text, size=16):
        w = tw(text, size, 400, True) + 24
        d.rect(x - w / 2, y - 19, w, 38, fill="#FFFFFF", stroke="#555", sw=1.2, rx=4)
        d.text(x, y + 6, text, size, fam=MONO, anchor="middle")
        d.boxes[k] = (x - w / 2, y - 19, w, 38)

    def lit(k, x, y, text, size=16):
        w = tw(text, size, 400, True) + 22
        d.rect(x - w / 2, y - 18, w, 36, fill="#F4F4F4", stroke="#2E8B3E", sw=1.1, rx=2)
        d.text(x, y + 6, text, size, fam=MONO, anchor="middle")
        d.boxes[k] = (x - w / 2, y - 18, w, 36)

    def note(x, y, w, lines, title=None, size=F_NOTE, fill="#FAFAF7", lh=None):
        lh = lh or round(size * 1.4)
        h = 20 + (28 if title else 0) + lh * len(lines)
        d.rect(x, y, w, h, fill=fill, stroke="#B5B5B5", sw=1, rx=4)
        yy = y + 14 + size
        if title:
            d.text(x + 16, yy, title, size + 1, 600); yy += 28
        for l in lines:
            bold = l.startswith("**")
            d.text(x + 16, yy, l.strip("*"), size, 600 if bold else 400, fill="#2A2A2A"); yy += lh
        assert max(tw(l.strip("*"), size, 600 if l.startswith("**") else 400) for l in lines) + 32 <= w, (lines, w)
        return h

    def band(y, h, n, title, subtitle, dend=None):
        d.rect(20, y, W - 40, h, fill="#FBFBFD", stroke="#D3D8E0", sw=1, rx=10, layer="back")
        d.text(44, y + 38, f"{n}  {title}", F_BAND, 600, layer="back")
        d.text(44, y + 66, subtitle, F_BSUB, fill="#555", layer="back")
        d.raw(f'<line x1="960" y1="{y+88}" x2="960" y2="{dend or y+h-20}" stroke="#D3D8E0" stroke-width="1" stroke-dasharray="4 4"/>', layer="back")
        d.text(48, y + 110, "CLASS LEVEL", 14, 600, fill="#7A7A7A", layer="back")
        d.text(984, y + 110, "EXAMPLE FROM THE DATA", 14, 600, fill="#7A7A7A", layer="back")

    def zone(x, y, w, h, n, label, fill, dx=14):
        d.rect(x, y, w, h, fill=fill, stroke="#C9CED6", sw=1, rx=8, layer="back")
        d.text(x + dx, y + 26, f"{n}  {label}", 16, 600, fill="#3A3A3A", layer="back")

    def mid(a, b):
        return (a + b) / 2

    # ---- header ---------------------------------------------------------------------------
    d.text(40, 54, "Conceptual model — subjects, identifiers and evidence (Graffoo)", 32, 600)
    d.text(40, 86, "The layer that documents the core model: who or what an entity is elsewhere, what the corpus is about, "
           "and where each conceptual relation comes from.", 17, fill="#555")

    # =====================================================================================
    # A. identifiers and authority links
    # =====================================================================================
    YA = 112
    HA = 760 if FULL else 690
    band(YA, HA, "A", "Identifiers and authority links",
         "CIDOC CRM identifier pattern for every authority number; external links chosen by what they claim")
    d.restriction("anchorA", 200, YA + 250, ["crm:E18_Physical_Thing", "or crm:E19_Physical_Object", "or crm:E21_Person", "or crm:E53_Place", "or crm:E74_Group"], size=16.5)
    NAME["anchorA"] = "anchors"
    C("E42", 700, YA + 250, "crm:E42_Identifier")
    C("E55", 700, YA + 450, "crm:E55_Type")
    d.datatype("strA", 700, YA + 580, "xsd:string"); NAME["strA"] = "xsd:string"
    a = S("anchorA", "e", .5); b = S("E42", "w", .5)
    d.arc([a, b], "obj", "crm:P1_is_identified_by", lpos=(mid(a[0], b[0]), a[1] - 10), **F)
    ex("anchorA", "E42")
    a = S("E42", "s", .35); d.arc([a, S("E55", "n", .35)], "obj", "crm:P2_has_type", lpos=(a[0] - 10, YA + 360), lanchor="end", **F)
    ex("E42", "E55")
    a = S("E42", "e", .5); x = 880
    d.arc([a, (x, a[1]), (x, YA + 580), S("strA", "e", .5)], "data", "crm:P190_has_symbolic_content",
          lpos=(x + 22, YA + 420), lrot=-90, **F)
    ex("E42", "strA")
    d.text(200, YA + 350, "classes of the core diagram that", 15, anchor="middle", fill="#555")
    d.text(200, YA + 370, "carry authority identifiers", 15, anchor="middle", fill="#555")
    note(48, YA + 430, 470, [f"{N_IDS} identifiers in {N_SCHEMES} schemes: Wikidata,", "VIAF, LC names, LCSH, FAST, FAST",
                             "control number, WorldCat Entity,", "British Library shelfmark."]
         + (["Every number is kept as data, whatever", "external link is added (or not) for", "the same scheme."] if FULL else []))
    # example
    ind("stein", 1100, YA + 260, "aurel-stein", sub="crm:E21_Person")
    ind("steinviaf", 1470, YA + 260, "aurel-stein-viaf", sub="crm:E42_Identifier")
    ind("tviaf", 1470, YA + 480, "identifier-type/viaf", sub="crm:E55_Type")
    lit("v", 1770, YA + 480, '"88967071"')
    ind("wdstein", 1100, YA + 480, "wd:Q313061", sub="Wikidata item")
    iri("viafrec", 1470, YA + 150, "viaf:88967071")
    a = S("stein", "e"); b = S("steinviaf", "w")
    d.arc([a, b], "obj", "crm:P1_is_identified_by", lpos=(mid(a[0], b[0]), a[1] - 10), lsize=16)
    ex("stein", "steinviaf")
    fact("aurel-stein", CRM + "P1_is_identified_by", "aurel-stein-viaf")
    a = S("steinviaf", "s"); b = S("tviaf", "n")
    d.arc([a, b], "obj", "crm:P2_has_type", lpos=(a[0] - 10, mid(a[1], b[1]) + 6), lanchor="end")
    ex("steinviaf", "tviaf")
    fact("aurel-stein-viaf", CRM + "P2_has_type", "identifier-type/viaf")
    a = S("steinviaf", "e"); b = S("v", "n")
    d.arc([a, (b[0], a[1]), b], "data", "crm:P190_has_symbolic_content", lpos=(a[0] + 12, a[1] - 10), lanchor="start", lsize=16)
    ex("steinviaf", "v")
    fact("aurel-stein-viaf", CRM + "P190_has_symbolic_content", Literal("88967071"))
    a = S("stein", "s"); b = S("wdstein", "n")
    d.raw(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#1D1D1F" stroke-width="2.2"/>', layer="mid")
    d.text(a[0] + 12, mid(a[1], b[1]) + 6, "owl:sameAs", 17, 600, halo=True)
    fact("aurel-stein", str(OWL.sameAs), WD + "Q313061")
    a = S("stein", "n"); b = S("viafrec", "w")
    d.arc([a, (a[0], b[1]), b], "ann", "rdfs:seeAlso", lpos=(mid(a[0], b[0]) + 30, b[1] - 10))
    ex("stein", "viafrec")
    fact("aurel-stein", str(RDFS.seeAlso), "http://viaf.org/viaf/88967071")
    note(990, YA + 590, 880, ["**owl:sameAs — the same individual (persons and groups): 10 links",
                              f"**rdfs:seeAlso — a description elsewhere, no identity claim: {N_SEE} links"]
         + (["Aurel Stein also has rdfs:seeAlso to LC n82045000 and WorldCat; the corpus and",
             "the places link to Wikidata with rdfs:seeAlso, not owl:sameAs."] if FULL else []))

    # =====================================================================================
    # B. subjects
    # =====================================================================================
    YB = YA + HA + 30
    HB = 700 if FULL else 660
    band(YB, HB, "B", "Subjects",
         "The religious and philosophical traditions in the source as a SKOS concept scheme, aligned to Wikidata and LCSH")
    C("E18b", 200, YB + 250, "crm:E18_Physical_Thing", sub="class of the core diagram")
    C("Concept", 660, YB + 250, "skos:Concept")
    C("Scheme", 560, YB + 480, "skos:ConceptScheme")
    d.datatype("lang", 840, YB + 480, "rdf:langString"); NAME["lang"] = "rdf:langString"
    a = S("E18b", "e", .5); b = S("Concept", "w", .5)
    d.arc([a, b], "obj", "dcterms:subject", lpos=(mid(a[0], b[0]), a[1] - 10), **F); use("E18b", "dcterms:subject", "Concept")
    cx0, cy0, cw0, ch0 = d.boxes["Concept"]
    a = S("Concept", "s", .15); d.arc([a, (a[0], S("Scheme", "n")[1])], "obj", "skos:inScheme", lpos=(a[0] - 10, YB + 350), lanchor="end", **F)
    use("Concept", "skos:inScheme", "Scheme")
    r = cx0 + cw0
    d.arc([(r - 34, cy0), (r - 34, cy0 - 44), (r + 56, cy0 - 44), (r + 56, cy0 + 14), (r, cy0 + 14)], "obj", "skos:exactMatch",
          lpos=(r + 10, cy0 - 54), **F)
    ex("Concept", "Concept")
    d.text(r + 10, cy0 - 78, "(objects: Wikidata items, LCSH headings)", 15, fill="#555", anchor="middle")
    lx0, ly0, lw0, lh0 = d.boxes["lang"][:4]
    a = S("Concept", "e", .75); xb = lx0 + lw0 * .62
    d.arc([a, (xb, a[1]), (xb, ly0)], "ann", "skos:prefLabel", lpos=(xb - 10, YB + 345), lanchor="end", **F)
    ex("Concept", "lang")
    a = S("Concept", "s", .8)
    d.arc([a, (a[0], ly0 + lh0 / 2), (lx0 + 7, ly0 + lh0 / 2)], "ann", "skos:definition", lpos=(a[0] + 10, YB + 405), lanchor="start", **F)
    ex("Concept", "lang")
    d.text(a[0] + 10, YB + 426, "(evidence types)", 15, fill="#555")
    # example
    ind("corpus", 1100, YB + 250, "dunhuang-manuscripts", sub="crm:E18_Physical_Thing")
    ind("buddhism", 1460, YB + 250, "concept-buddhism", sub="skos:Concept")
    ind("wdb", 1775, YB + 250, "wd:Q748", sub="Wikidata item")
    ind("rt", 1460, YB + 490, "religious-traditions", sub="skos:ConceptScheme")
    a = S("corpus", "e"); b = S("buddhism", "w")
    d.arc([a, b], "obj", "dcterms:subject", lpos=(mid(a[0], b[0]), a[1] - 10))
    ex("corpus", "buddhism")
    fact("dunhuang-manuscripts", str(DCTERMS.subject), "concept-buddhism")
    a = S("buddhism", "e"); b = S("wdb", "w")
    d.arc([a, b], "obj", "skos:exactMatch", lpos=(mid(a[0], b[0]), a[1] - 10))
    ex("buddhism", "wdb")
    fact("concept-buddhism", str(SKOS.exactMatch), WD + "Q748")
    a = S("buddhism", "s"); b = S("rt", "n")
    d.arc([a, b], "obj", "skos:inScheme", lpos=(a[0] + 12, mid(a[1], b[1]) + 6), lanchor="start")
    ex("buddhism", "rt")
    fact("concept-buddhism", str(SKOS.inScheme), "concept-scheme/religious-traditions")
    note(48, YB + 560, 880, [f"{N_SUBJ} subjects: Buddhism, Daoism, Confucianism, Nestorian Christianity, Manichaeism, Judaism.",
                             f"skos:exactMatch: {N_WD} to Wikidata, {N_LCSH} to LCSH (none found for Nestorian Christianity)."])
    note(1600, YB + 400, 270, ["**skos:exactMatch aligns", "**two concepts.", "It is not an identity", "claim about real-world", "things."]
         + (["Nor does it say that", "the corpus is Buddhism."] if FULL else []))

    # =====================================================================================
    # C. evidence
    # =====================================================================================
    YC = YB + HB + 30
    HC = 1340 if FULL else 1115
    band(YC, HC, "C", "Evidence: from the theoretical model to the triples",
         f"Only the {N_STMT} conceptual-relation triples (the formalisations of R1–R{N_PROP}) are restated as rdf:Statement — "
         f"not all {len(G)} triples of the dataset", dend=YC + 1000)
    C("Stmt", 230, YC + 300, "rdf:Statement", minw=230)
    C("E89", 730, YC + 210, "crm:E89_Propositional_Object")
    C("Concept2", 730, YC + 400, "skos:Concept", sub="same class as in B")
    C("Scheme2", 730, YC + 590, "skos:ConceptScheme", sub="same class as in B")
    C("Res", 230, YC + 600, "rdfs:Resource", minw=230)
    lx = 410
    a = S("Stmt", "e", .3); b = S("E89", "w", .5)
    d.arc([a, (lx, a[1]), (lx, b[1]), b], "obj", "dcterms:relation", lpos=(lx + 10, b[1] - 10), lanchor="start", **F)
    ex("Stmt", "E89")
    use("Stmt", "dcterms:relation", "E89")
    a = S("Stmt", "e", .7); b = S("Concept2", "w", .5)
    d.arc([a, (lx, a[1]), (lx, b[1]), b], "obj", "dcterms:type", lpos=(lx + 10, b[1] - 10), lanchor="start", **F)
    ex("Stmt", "Concept2")
    use("Stmt", "dcterms:type", "Concept2")
    a = S("Concept2", "s", .5); d.arc([a, S("Scheme2", "n", .5)], "obj", "skos:inScheme", lpos=(a[0] + 12, mid(a[1], S("Scheme2", "n")[1]) + 6),
                                       lanchor="start", **F)
    ex("Concept2", "Scheme2")
    for t in (.12, .5, .88):
        a = S("Stmt", "s", t); b = S("Res", "n", t)
        d.arc([a, b], "obj", None, **F)
        ex("Stmt", "Res")
    ym = mid(S("Stmt", "s")[1], S("Res", "n")[1])
    d.text(S("Stmt", "s", .12)[0] - 10, ym - 14, "rdf:subject", 17, 600, fill=C_OBJ, anchor="end", halo=True)
    d.text(S("Stmt", "s", .5)[0], ym + 28, "rdf:predicate", 17, 600, fill=C_OBJ, anchor="middle", halo=True)
    d.text(S("Stmt", "s", .88)[0] + 10, ym - 14, "rdf:object", 17, 600, fill=C_OBJ, halo=True)
    note(48, YC + 140, 340, [f"{N_PROP} propositions R1–R{N_PROP}", f"{N_STMT} statements · 2 evidence types"])
    iri("Src", 730, YC + 780, "ex:IRI"); NAME["Src"] = "(external IRI)"
    ls = 375
    a = S("Stmt", "e", .9); b = S("Src", "w", .5)
    d.arc([a, (ls, a[1]), (ls, b[1]), b], "obj", "dcterms:source", lpos=(ls + 12, b[1] - 10), lanchor="start", **F)
    use("Stmt", "dcterms:source", "Src")
    d.text(730, YC + 745, f"source pages: {N_SRC} links, Enriched statements only", 15, fill="#555", anchor="middle")
    note(48, YC + 830, 880, ["rdf:subject, rdf:object: resources of the core diagram; rdf:predicate: the",
                             "property of the restated triple. A proposition can be restated by several",
                             "statements (R6: 5) or by none (R9, R12)."])

    # example, in three zones: the historical event as data / its restatement / proposition and evidence type
    zone(984, YC + 130, 886, 200, "1", "Historical event, as data: one triple of the dataset", "#FFF7E8")
    d.rect(984, YC + 345, 886, 200, fill="#EEF4FB", stroke="#C9CED6", sw=1, rx=8, layer="back")
    d.text(1150, YC + 371, "2  Restatement of that triple (rdf:Statement, not an event)", 16, 600, fill="#3A3A3A", layer="back")
    zone(984, YC + 560, 430, 440, "3", "Proposition of the theoretical model", "#F3EFFA")
    zone(1428, YC + 560, 442, 440, "4", "Evidence type", "#EEF7EF", dx=50)
    ind("ps", 1130, YC + 235, "purchase-stein", sub="crm:E96_Purchase")
    ind("as", 1720, YC + 235, "aurel-stein", sub="crm:E21_Person")
    a = S("ps", "e"); b = S("as", "w")
    d.arc([a, b], "obj", "crm:P22_transferred_title_to", lpos=(mid(a[0], b[0]), a[1] - 10))
    ex("ps", "as")
    ind("cr10", 1430, YC + 468, "statement/cr10", sub="rdf:Statement")
    a = S("cr10", "w", .35); b = S("ps", "s", .62)
    d.arc([a, (b[0], a[1]), b], "obj", "rdf:subject", lpos=(b[0] + 12, a[1] - 10), lanchor="start")
    ex("cr10", "ps")
    a = S("cr10", "e", .3); b = S("as", "s", .38)
    d.arc([a, (b[0], a[1]), b], "obj", "rdf:object", lpos=(b[0] - 12, a[1] - 10), lanchor="end")
    ex("cr10", "as")
    a = S("cr10", "e", .75)
    iri("p22", 1730, a[1], "crm:P22_transferred_title_to", size=15)
    b = S("p22", "w", .5)
    d.arc([a, b], "obj", "rdf:predicate", lpos=(a[0] + 6, a[1] + 32), lanchor="start", lsize=16)
    ex("cr10", "p22")
    ind("r6", 1090, YC + 720, "R6", sub="crm:E89")
    ind("r9", 1300, YC + 720, "R9", sub="crm:E89")
    a = S("cr10", "s", .75); b = S("r6", "n", .7)
    d.arc([a, (a[0], YC + 640), (b[0], YC + 640), b], "obj", "dcterms:relation", lpos=(mid(a[0], b[0]) + 30, YC + 630))
    ex("cr10", "r6")
    ind("direct", 1580, YC + 715, "evidence/direct", sub="skos:Concept")
    ind("et", 1580, YC + 905, "evidence-types", sub="skos:ConceptScheme")
    a = S("cr10", "s", .25); b = S("direct", "n")
    d.arc([a, (a[0], YC + 640), (b[0], YC + 640), b], "obj", "dcterms:type", lpos=(b[0] + 12, YC + 630), lanchor="start")
    ex("cr10", "direct")
    a = S("direct", "s"); b = S("et", "n")
    d.arc([a, b], "obj", "skos:inScheme", lpos=(a[0] + 12, mid(a[1], b[1]) + 6), lanchor="start")
    ex("direct", "et")
    note(1000, YC + 810, 400, ["R6 is restated by 5 statements:", "cr9, cr10, cr11, cr31, cr36.", "R9, R12 (held_by): none."])
    for s_, p_, o_ in [("purchase-stein", CRM + "P22_transferred_title_to", "aurel-stein"), ("statement/cr10", str(RDF.subject), "purchase-stein"),
                       ("statement/cr10", str(RDF.predicate), CRM + "P22_transferred_title_to"), ("statement/cr10", str(RDF.object), "aurel-stein"),
                       ("statement/cr10", str(DCTERMS.relation), "canonical-relation/r6"), ("statement/cr10", str(DCTERMS.type), "evidence/direct"),
                       ("evidence/direct", str(SKOS.inScheme), "concept-scheme/evidence-types")]:
        fact(s_, p_, o_)
    for st in ["cr9", "cr11", "cr31", "cr36"]:
        fact("statement/" + st, str(DCTERMS.relation), "canonical-relation/r6")
    # definitions and the three layers
    yd = YC + 1035
    d.text(48, yd, f"skos:definition of evidence/direct ({N_EV['direct']} statements):", 16, 600)
    d.text(48, yd + 26, f"“{DEF['direct']}”", 16, fill="#2A2A2A")
    if FULL:
        d.text(48, yd + 60, f"skos:definition of evidence/enriched ({N_EV['enriched']} statements, R16–R19):", 16, 600)
        lines, cur = [], ""
        for word in f"“{DEF['enriched']}”".split(" "):          # wrap to the band width
            if tw((cur + " " + word).strip(), 16) > W - 120:
                lines.append(cur); cur = word
            else:
                cur = (cur + " " + word).strip()
        lines.append(cur)
        for i, line in enumerate(lines):
            d.text(48, yd + 86 + 24 * i, line, 16, fill="#2A2A2A")
        note(48, yd + 86 + 24 * len(lines) - 2, 1822, ["**Three layers, three kinds of resource",
                                  "1  purchase-stein (crm:E96_Purchase) stands for the historical sale; the triple purchase-stein P22 aurel-stein is a fact of the dataset.",
                                  "2  statement/cr10 (rdf:Statement) restates that one triple so that it can be annotated. It is not the sale and it is not the proposition.",
                                  "3  R6 (crm:E89_Propositional_Object) is a proposition of the theoretical model, in natural language (“sold manuscripts to”); "
                                  "statements point to it with dcterms:relation."],
             fill="#FFF8E6")
    else:
        d.text(48, yd + 56, f"Definition of “Enriched” ({N_EV['enriched']} statements, R16–R19), and the difference between the event, the statement and the "
               "proposition: see the text that accompanies this figure, and the PDF.", 15.5, fill="#555")

    # ---- legend (and prefixes in the full version) ------------------------------------------------
    YL = YC + HC + 24
    if FULL:
        d.rect(20, YL, 1040, 210, fill="#FFFFFF", stroke="#9A9A9A", sw=1)
        d.text(40, YL + 30, "Graffoo notation", 17, 600)
        d.cls("lg1", 110, YL + 76, "Class", minw=120, size=16); d.text(186, YL + 82, "class", 15.5)
        d.restriction("lg2", 110, YL + 148, ["A or B"], size=15); d.text(186, YL + 154, "class expression", 15.5)
        d.individual("lg3", 345, YL + 76, "i", r=22); d.text(378, YL + 82, "individual", 15.5)
        d.datatype("lg4", 360, YL + 148, "Datatype", size=15); d.text(440, YL + 154, "datatype", 15.5)
        lit("lg5", 570, YL + 76, '"literal"', size=15); iri("lg6", 570, YL + 148, "ex:IRI", size=15)
        d.text(640, YL + 82, "literal value", 15.5); d.text(640, YL + 154, "external IRI", 15.5)

        def lg(y, x, kind, fac, label):
            d.arc([(x, y), (x + 80, y)], kind, None, facility=fac); d.text(x + 92, y + 5, label, 15)
        lg(YL + 62, 770, "obj", True, "object property used")
        lg(YL + 97, 770, "obj", False, "fact between individuals")
        lg(YL + 132, 770, "ann", True, "annotation property used")
        d.raw(f'<line x1="770" y1="{YL+167}" x2="850" y2="{YL+167}" stroke="#1D1D1F" stroke-width="2.2"/>')
        d.text(862, YL + 172, "owl:sameAs", 15)
        d.text(40, YL + 198, "Dotted arcs: properties defined in CIDOC CRM, SKOS, DCTerms or RDF, used here; they assert no domain or range.",
               14, fill="#555")
        px = 1080
        d.rect(px, YL, 800, 210, fill="#FFFFFF", stroke=INK, sw=1.3)
        d.raw(f'<rect x="{px+0.7}" y="{YL+0.7}" width="798.6" height="36" fill="#EDEDED"/>')
        d.text(px + 14, YL + 25, "Prefixes", 17, 600)
        PX = [("crm:", "http://www.cidoc-crm.org/cidoc-crm/ (7.1.3)"), ("skos:", "http://www.w3.org/2004/02/skos/core#"),
              ("dcterms:", "http://purl.org/dc/terms/"), ("rdf: rdfs: owl:", "W3C RDF, RDF Schema, OWL"),
              ("wd: viaf:", "http://www.wikidata.org/entity/ · http://viaf.org/viaf/"),
              ("(none)", "https://haopuur-max.github.io/reconnecting-dunhuang/resource/")]
        for i, (p, u) in enumerate(PX):
            d.text(px + 14, YL + 62 + 24 * i, p, 14.5, fam=MONO, fill="#1F5FBF"); d.text(px + 175, YL + 62 + 24 * i, u, 14.5, fam=MONO)
        YE = YL + 210
    else:
        d.rect(20, YL, W - 40, 96, fill="#FFFFFF", stroke="#9A9A9A", sw=1)
        d.cls("lg1", 90, YL + 48, "Class", minw=100, size=16)
        d.restriction("lg2", 222, YL + 48, ["A or B"], size=15)
        d.datatype("lg4", 355, YL + 48, "Datatype", size=15)
        d.individual("lg3", 460, YL + 48, "i", r=20)
        d.text(488, YL + 54, "individual", 15)
        lit("lg5", 630, YL + 48, '"literal"', size=15); iri("lg6", 745, YL + 48, "ex:IRI", size=15)

        def lg(y, x, kind, fac, label):
            d.arc([(x, y), (x + 70, y)], kind, None, facility=fac); d.text(x + 82, y + 5, label, 15)
        lg(YL + 32, 830, "obj", True, "object property used (no domain or range asserted)")
        lg(YL + 66, 830, "obj", False, "fact between individuals")
        lg(YL + 32, 1440, "ann", True, "annotation property used")
        d.raw(f'<line x1="1440" y1="{YL+66}" x2="1510" y2="{YL+66}" stroke="#1D1D1F" stroke-width="2.2"/>')
        d.text(1522, YL + 71, "owl:sameAs (same individual)", 15)
        YE = YL + 96
    d.text(40, YE + 34, f"Generated from reconnecting_dunhuang.ttl ({len(G)} triples). rdfs:label on every resource is not drawn."
           + ("" if FULL else " Prefixes and full notes: PDF version."), 15, fill="#666")
    Hreal = YE + 56

    # ---- checks ------------------------------------------------------------------------------
    DOC = {"dcterms:subject", "skos:inScheme", "dcterms:relation", "dcterms:type", "dcterms:source"}
    U = usage.usage()
    data = {k for k in U if k[1] in DOC}
    assert set(DRAWN) == data, (sorted(data - set(DRAWN)), sorted(set(DRAWN) - data))
    assert {c for (c, p, o) in U if p == "crm:P1_is_identified_by"} == {"crm:E18_Physical_Thing", "crm:E19_Physical_Object", "crm:E21_Person", "crm:E53_Place", "crm:E74_Group"}
    assert ("crm:E42_Identifier", "crm:P2_has_type", "crm:E55_Type") in U and ("crm:E42_Identifier", "crm:P190_has_symbolic_content", "xsd:string") in U
    assert ("skos:Concept", "skos:exactMatch", "(external IRI)") in U and ("skos:Concept", "skos:prefLabel", "rdf:langString") in U
    assert ("skos:Concept", "skos:definition", "rdf:langString") in U
    assert {p for (c, p, o) in U if c == "rdf:Statement"} == {"rdf:subject", "rdf:predicate", "rdf:object", "dcterms:relation", "dcterms:type", "dcterms:source"}
    for s_, p_, o_ in FACTS:
        su = URIRef(s_ if s_.startswith("http") else RES + s_)
        ob = o_ if isinstance(o_, Literal) else URIRef(o_ if o_.startswith("http") else RES + o_)
        assert (su, URIRef(p_), ob) in G, (s_, p_, o_)
    for k, cls in [("aurel-stein", CRM + "E21_Person"), ("aurel-stein-viaf", CRM + "E42_Identifier"), ("identifier-type/viaf", CRM + "E55_Type"),
                   ("dunhuang-manuscripts", CRM + "E18_Physical_Thing"), ("concept-buddhism", str(SKOS.Concept)),
                   ("concept-scheme/religious-traditions", str(SKOS.ConceptScheme)), ("statement/cr10", str(RDF.Statement)),
                   ("purchase-stein", CRM + "E96_Purchase"), ("canonical-relation/r6", CRM + "E89_Propositional_Object"),
                   ("canonical-relation/r9", CRM + "E89_Propositional_Object"), ("evidence/direct", str(SKOS.Concept)),
                   ("concept-scheme/evidence-types", str(SKOS.ConceptScheme))]:
        assert (URIRef(RES + k), RDF.type, URIRef(cls)) in G, k
    for r_ in ("r9", "r12"):
        assert not list(G.subjects(DCTERMS.relation, URIRef(RES + "canonical-relation/" + r_)))
    assert len(set(G.subjects(DCTERMS.relation, URIRef(RES + "canonical-relation/r6")))) == 5
    assert str(G.value(URIRef(RES + "canonical-relation/r9"), RDFS.label)).endswith("held_by")
    assert str(G.value(URIRef(RES + "canonical-relation/r12"), RDFS.label)).endswith("held_by")
    # every circle, box and zone inside the canvas
    for k, b in d.boxes.items():
        assert b[0] >= 20 and b[0] + b[2] <= W - 20 and b[1] + b[3] <= Hreal, (k, b)
    d.h = Hreal
    out_path = out("doc", "full" if FULL else "web")
    d.save(out_path)
    print(f"doc {'full' if FULL else 'web'}: {len(DRAWN)} class-level arcs = data; {len(FACTS)} example facts in the Turtle file; {len(EXCHECK)} arcs checked for direction; height {Hreal}")


for FULL in (False, True):
    build(FULL)
