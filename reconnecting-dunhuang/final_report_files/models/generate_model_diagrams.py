#!/usr/bin/env python3
"""
Generate every model diagram directly from the final RDF (and, for the one theoretical
example, from the TEI canonical relations), so no picture can disagree with the data.

Outputs in final_report_files/models/
  conceptual_model_instance_graph.svg/.pdf  ABox: all individuals and the properties linking
                                            them (identifiers, provenance, concepts left out).
                                            Website palette.
  core_conceptual_model.svg/.pdf            TBox subset used by the four modelling cases and
                                            the core-resource decision. Website palette.
  authority_linking_table.md                every identifier and the link predicate chosen.

The three main model diagrams (theoretical model and the two Graffoo diagrams of the conceptual
model) are drawn by graffoo/build_model_diagrams.py.

Outputs in assets/diagrams/ (website figures, website palette)
  case_theory_r6.svg        theoretical relation r6, as written in the TEI canonical layer
  case_core_resource.svg    corpus (E18), subsets (E19), keepers, digital surrogate (D1)
  case_discovery.svg / case_purchase.svg / case_transfer.svg / case_digitization.svg

A case diagram contains only triples that exist in reconnecting_dunhuang.ttl; the selection
is a list of (subject, predicate) pairs below, so no entity, relation or term can be added.

Requires Graphviz (`dot`) and the Source Sans 3 font installed locally for text metrics.
Run after transform_tei_to_rdf.py.
"""

import re
import subprocess
import textwrap
from pathlib import Path

from lxml import etree
from rdflib import Graph, RDF, RDFS, OWL, URIRef, Namespace
from rdflib.namespace import SKOS, DCTERMS

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TTL = HERE.parent / "xml_to_rdf" / "reconnecting_dunhuang.ttl"
TEI_FILE = HERE.parent / "tei_xml" / "reconnecting_dunhuang.xml"
SITE_DIAGRAMS = ROOT / "assets" / "diagrams"

BASE = "https://haopuur-max.github.io/reconnecting-dunhuang/"
RES, DM = Namespace(BASE + "resource/"), BASE + "ontology/"
PREFIXES = {
    "http://www.cidoc-crm.org/cidoc-crm/": "crm:",
    "http://www.cidoc-crm.org/extensions/crmsci/": "crmsci:",
    "http://www.cidoc-crm.org/extensions/crmdig/": "crmdig:",
    DM: "dm:",
    str(DCTERMS): "dcterms:",
    str(SKOS): "skos:",
}
FONT_STACK = "'Source Sans 3', 'Helvetica Neue', Arial, sans-serif"

# Website palette (Final Specification 13.1)
INK, MUTED, RULE = "#2B2622", "#5C534A", "#B9AC95"
AZURITE, AZ_TINT, CINNABAR = "#1F4E79", "#E2E9F0", "#A63A24"
MALACHITE, MAL_TINT, OCHRE = "#2F6B4F", "#E4EEE8", "#8A5A1F"
EVENT_CLASSES = {"crm:E7_Activity", "crm:E96_Purchase", "crm:E9_Move",
                 "crmsci:S19_Encounter_Event", "crmdig:D2_Digitization_Process"}
ACTOR_CLASSES = {"crm:E21_Person", "crm:E74_Group"}


def node_style(cls):
    if cls in EVENT_CLASSES:
        return dict(shape="ellipse", style="filled", fillcolor=AZ_TINT, color=AZURITE)
    if cls in ACTOR_CLASSES:
        return dict(shape="box", style="filled,rounded", fillcolor="#FBF8F1", color=MUTED)
    if cls == "crm:E53_Place":
        return dict(shape="box", style="filled,rounded", fillcolor=MAL_TINT, color=MALACHITE)
    if cls == "crm:E18_Physical_Thing":
        return dict(shape="box", style="filled,rounded", fillcolor="#F2E6D2", color=OCHRE, penwidth="2")
    if cls == "crm:E19_Physical_Object":
        return dict(shape="box", style="filled,rounded", fillcolor="#F8F0E2", color=OCHRE)
    if cls == "crm:E52_Time-Span":
        return dict(shape="note", style="filled", fillcolor="#F6F1E7", color=RULE)
    if cls == "crmdig:D1_Digital_Object":
        return dict(shape="box", style="filled,rounded,dashed", fillcolor="#FFFFFF", color=AZURITE)
    return dict(shape="box", style="filled,rounded", fillcolor="#FFFFFF", color=MUTED)


def curie(uri):
    for ns, p in PREFIXES.items():
        if str(uri).startswith(ns):
            return p + str(uri)[len(ns):]
    return str(uri)


def esc(text):
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def attrs(d):
    return ", ".join(f'{k}="{v}"' for k, v in d.items())


def cls_of(g, node):
    return curie(g.value(node, RDF.type))


def enriched_triples(g):
    """(s, p, o) whose provenance statement is typed as Enriched evidence."""
    out = set()
    for st in g.subjects(RDF.type, RDF.Statement):
        if str(g.value(st, DCTERMS.type)).endswith("/evidence/enriched"):
            out.add((g.value(st, RDF.subject), g.value(st, RDF.predicate), g.value(st, RDF.object)))
    return out


def core_triples(g):
    """Object-property triples between typed project individuals, without identifiers,
    provenance nodes or concepts."""
    for s, p, o in g:
        if not (str(s).startswith(str(RES)) and str(o).startswith(str(RES))):
            continue
        if any(x in str(s) + str(o) for x in ("/statement/", "identifier-type", "/canonical-relation/",
                                               "/evidence/", "concept-")):
            continue
        if p == RDF.type or (s, RDF.type, None) not in g or (o, RDF.type, None) not in g:
            continue
        if curie(p) in ("crm:P1_is_identified_by", "dcterms:subject"):
            continue
        yield s, p, o


# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------
def postprocess_svg(path, label):
    """Scalable, accessible SVG that uses the website font stack."""
    svg = path.read_text(encoding="utf-8")
    svg = re.sub(r"<\?xml[^>]*>\s*", "", svg)
    svg = re.sub(r"<!DOCTYPE[^>]*>\s*", "", svg, flags=re.S)
    svg = re.sub(r"<!--.*?-->\s*", "", svg, flags=re.S)
    svg = re.sub(r"<title>[^<]*</title>\s*", "", svg)
    svg = re.sub(r'<svg width="[^"]*" height="[^"]*"', f'<svg role="img" aria-label="{esc(label)}"', svg, count=1)
    svg = svg.replace('font-family="Source Sans 3"', f'font-family="{FONT_STACK}"')
    svg = svg.replace('<polygon fill="white" stroke="none"', '<polygon fill="none" stroke="none"', 1)
    path.write_text(svg, encoding="utf-8")


def render(dot_text, out_dir, stem, label, pdf=False):
    out_dir.mkdir(parents=True, exist_ok=True)
    dot_path = out_dir / f"{stem}.dot"
    dot_path.write_text(dot_text, encoding="utf-8")
    subprocess.run(["dot", "-Tsvg", str(dot_path), "-o", str(out_dir / f"{stem}.svg")], check=True)
    if pdf:
        subprocess.run(["dot", "-Tpdf", str(dot_path), "-o", str(out_dir / f"{stem}.pdf")], check=True)
    dot_path.unlink()
    postprocess_svg(out_dir / f"{stem}.svg", label)


GRAPH_HEAD = [
    '  graph [rankdir=LR, bgcolor="transparent", fontname="Source Sans 3", nodesep=0.3, ranksep=0.55, pad=0.2];',
    f'  node [fontname="Source Sans 3", fontsize=13, fontcolor="{INK}", margin="0.14,0.07"];',
    f'  edge [fontname="Source Sans 3", fontsize=11, color="{MUTED}", fontcolor="{MUTED}", arrowsize=0.7];',
]


def instance_dot(g, triples, name, rankdir="LR"):
    enriched = enriched_triples(g)
    lines = [f"digraph {name} {{", *GRAPH_HEAD, f"  graph [rankdir={rankdir}];"]
    nodes = {n for s, _, o in triples for n in (s, o)}
    for n in sorted(nodes):
        c = cls_of(g, n)
        label = g.value(n, RDFS.label) or n.split("/")[-1]
        name = "<br/>".join(esc(line) for line in textwrap.wrap(str(label), 26))
        html = f'<<b>{name}</b><br/><font point-size="10.5" color="{MUTED}">{esc(c)}</font>>'
        lines.append(f'  "{n}" [{attrs(node_style(c))}, label={html}];')
    for s, p, o in sorted(triples):
        pc = curie(p)
        if (s, p, o) in enriched:
            style = dict(color=CINNABAR, fontcolor=CINNABAR, style="dashed", penwidth="1.4")
            text = f"{pc} (Enriched)"
        elif pc.startswith("dm:"):
            style = dict(color=AZURITE, fontcolor=AZURITE, penwidth="1.6")
            text = pc
        elif pc.startswith("dcterms:"):
            style = dict(style="dashed")
            text = pc
        else:
            style, text = {}, pc
        extra = (", " + attrs(style)) if style else ""
        lines.append(f'  "{s}" -> "{o}" [label="{esc(text)}"{extra}];')
    lines.append("}")
    return "\n".join(lines)


def select(g, pairs):
    """Triples for (subject id, predicate curie) pairs; fails loudly if one does not exist."""
    out = []
    for sid, pc in pairs:
        found = [(s, p, o) for s, p, o in core_triples(g) if s == RES[sid] and curie(p) == pc]
        if not found:
            raise SystemExit(f"Case diagram asks for a triple that is not in the data: {sid} {pc}")
        out += found
    return out


CASES = {
    "case_core_resource": ("The corpus (E18), its physical subsets (E19), keepers named in the source, and the digital surrogate (D1)", [
        ("stein-portion", "crm:P46i_forms_part_of"), ("pelliot-portion", "crm:P46i_forms_part_of"),
        ("otani-portion", "crm:P46i_forms_part_of"), ("remaining-chinese-manuscripts", "crm:P46i_forms_part_of"),
        ("pelliot-portion", "crm:P50_has_current_keeper"), ("remaining-chinese-manuscripts", "crm:P50_has_current_keeper"),
        ("digitization-event", "crmdig:L1_digitized"), ("digitization-event", "crmdig:L11_had_output")]),
    "case_discovery": ("Discovery modelled as a CRMsci encounter event", [
        ("discovery-event", "crm:P14_carried_out_by"), ("discovery-event", "crmsci:O19_encountered_object"),
        ("discovery-event", "crm:P4_has_time-span")]),
    "case_purchase": ("The purchase involving Aurel Stein as a CIDOC CRM purchase event", [
        ("purchase-stein", "crm:P23_transferred_title_from"), ("purchase-stein", "crm:P22_transferred_title_to"),
        ("purchase-stein", "crm:P24_transferred_title_of"), ("purchase-stein", "crm:P4_has_time-span"),
        ("stein-portion", "crm:P46i_forms_part_of")]),
    "case_transfer": ("The 1910 transfer to Beijing as a move of a physical subset", [
        ("transfer-beijing", "crm:P25_moved"), ("transfer-beijing", "crm:P26_moved_to"),
        ("transfer-beijing", "crm:P15_was_influenced_by"), ("transfer-beijing", "crm:P4_has_time-span"),
        ("remaining-chinese-manuscripts", "crm:P46i_forms_part_of"),
        ("remaining-chinese-manuscripts", "crm:P50_has_current_keeper")]),
    "case_digitization": ("Digitization with CRMdig, publication with DCTerms and the enriched project interpretation", [
        ("digitization-event", "crm:P14_carried_out_by"), ("digitization-event", "crmdig:L1_digitized"),
        ("digitization-event", "crmdig:L11_had_output"), ("digital-surrogate", "dcterms:publisher"),
        ("idp", "dm:virtuallyBringsTogether")]),
}

VERTICAL_CASES = {"case_digitization"}


def theory_r6():
    """Theoretical relation r6 exactly as written in the TEI canonical layer."""
    ns = {"tei": "http://www.tei-c.org/ns/1.0"}
    root = etree.parse(str(TEI_FILE)).getroot()
    rel = root.xpath("//tei:listRelation[@type='canonical']/tei:relation[@xml:id='r6']", namespaces=ns)[0]
    def name(ref):
        el = root.xpath(f"//*[@xml:id='{ref[1:]}']", namespaces=ns)[0]
        return " ".join("".join(el.xpath("tei:persName[not(@xml:lang)]", namespaces=ns)[0].itertext()).split())
    a, b, label = name(rel.get("active")), name(rel.get("passive")), rel.get("name")
    node = f'shape=box, style="filled,rounded", fillcolor="#FBF8F1", color="{MUTED}"'
    dot = "\n".join(["digraph theory {", *GRAPH_HEAD,
                     f'  "a" [{node}, label=<<b>{esc(a)}</b>>];', f'  "b" [{node}, label=<<b>{esc(b)}</b>>];',
                     f'  "a" -> "b" [label="{esc(label)}  (R6)", color="{INK}", fontcolor="{INK}", fontsize=12];', "}"])
    render(dot, SITE_DIAGRAMS, "case_theory_r6", f"Theoretical relation R6: {a} {label} {b}")


def short(p):
    """Compact edge label for the core model: 'crm:P24_transferred_title_of' -> 'P24 transferred title of'.
    CIDOC CRM, CRMsci and CRMdig lose their prefix; dm: and dcterms: keep theirs."""
    if p.startswith(("crm:", "crmsci:", "crmdig:")):
        return p.split(":", 1)[1].replace("_", " ")
    return p


def core_conceptual_model(g):
    """Class-level view of the triples used by the cases, in the website palette."""
    triples = {t for _, pairs in CASES.values() for t in select(g, pairs)}
    edges = {(cls_of(g, s), curie(p), cls_of(g, o)) for s, p, o in triples}
    spans = {cls_of(g, s) for s, p, o in triples if cls_of(g, o) == "crm:E52_Time-Span"}
    if spans:
        edges.add(("crm:E52_Time-Span", "crm:P82a_begin_of_the_begin", "xsd:dateTime"))
        edges.add(("crm:E52_Time-Span", "crm:P82b_end_of_the_end", "xsd:dateTime"))
    classes = {c for e in edges for c in (e[0], e[2]) if not c.startswith("xsd:")}
    lines = ["digraph core {", *GRAPH_HEAD, "  graph [rankdir=LR, ranksep=0.3, nodesep=0.3];", "  edge [fontsize=12];"]
    for c in sorted(classes):
        st = dict(node_style(c))
        st.pop("shape", None)
        shape = "ellipse" if c in EVENT_CLASSES else "box"
        lines.append(f'  "{c}" [shape={shape}, {attrs(st)}, label=<<b>{esc(c.replace("_", " "))}</b>>];')
    lines.append(f'  "xsd:dateTime" [shape=box, style="rounded,dashed", color="{MALACHITE}", fontcolor="{MALACHITE}", label="xsd:dateTime"];')
    for s, p, o in sorted(edges):
        if o.startswith("xsd:"):
            style = f', color="{MALACHITE}", fontcolor="{MALACHITE}"'
        elif p.startswith("dm:"):
            style = f', color="{AZURITE}", fontcolor="{AZURITE}", penwidth="1.6", constraint=false'
        elif p.startswith("dcterms:"):
            style = ', style="dashed", constraint=false'
        else:
            style = ""
        lines.append(f'  "{s}" -> "{o}" [label="{esc(short(p))}"{style}];')
    lines.append("}")
    render("\n".join(lines), HERE, "core_conceptual_model",
           "Core conceptual model: the classes and properties used by the modelling cases", pdf=True)
    return len(classes), len(edges)


def authority_table(g):
    P1 = URIRef("http://www.cidoc-crm.org/cidoc-crm/P1_is_identified_by")
    P2 = URIRef("http://www.cidoc-crm.org/cidoc-crm/P2_has_type")
    P190 = URIRef("http://www.cidoc-crm.org/cidoc-crm/P190_has_symbolic_content")
    rows = ["# Authority linking table (generated from reconnecting_dunhuang.ttl)", "",
            "Every identifier is kept as a `crm:E42_Identifier`. The last column shows the extra external link, "
            "chosen by the linking policy in `transform_tei_to_rdf.py`.", "",
            "| Entity | Class | Scheme | Identifier | External link |", "| --- | --- | --- | --- | --- |"]
    for ent, _, ident in sorted(g.triples((None, P1, None))):
        scheme = str(g.value(g.value(ident, P2), RDFS.label))
        value = str(g.value(ident, P190))
        link = "identifier only"
        for pred, name in ((OWL.sameAs, "owl:sameAs"), (RDFS.seeAlso, "rdfs:seeAlso")):
            for target in g.objects(ent, pred):
                if value in str(target):
                    link = f"{name} <{target}>"
        rows.append(f"| {g.value(ent, RDFS.label)} | {cls_of(g, ent)} | {scheme} | {value} | {link} |")
    rows += ["", "Concepts (skos:exactMatch):", ""]
    for c, _, t in sorted(g.triples((None, SKOS.exactMatch, None))):
        rows.append(f"- {g.value(c, SKOS.prefLabel)} -> <{t}>")
    (HERE / "authority_linking_table.md").write_text("\n".join(rows) + "\n", encoding="utf-8")


def main():
    g = Graph().parse(TTL)
    full = list(core_triples(g))
    render(instance_dot(g, full, "abox"), HERE, "conceptual_model_instance_graph",
           "Instance graph: every individual in the dataset and the properties linking them", pdf=True)
    for stem, (label, pairs) in CASES.items():
        rankdir = "TB" if stem in VERTICAL_CASES else "LR"
        render(instance_dot(g, select(g, pairs), stem.replace("-", "_"), rankdir), SITE_DIAGRAMS, stem, label)
    theory_r6()
    n_core = core_conceptual_model(g)
    authority_table(g)
    print(f"Instance graph: {len({n for s, _, o in full for n in (s, o)})} individuals, {len(full)} edges")
    print(f"Case diagrams: {len(CASES)} + theoretical R6")
    print(f"Core conceptual model: {n_core[0]} classes, {n_core[1]} class-level property uses")


if __name__ == "__main__":
    main()
