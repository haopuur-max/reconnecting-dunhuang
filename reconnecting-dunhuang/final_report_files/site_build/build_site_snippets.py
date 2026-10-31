#!/usr/bin/env python3
"""
Build the Web Report pages from templates.

Every code snippet on the site is cut from the final project files by ANCHOR (an xml:id, a
resource URI, a function name), never retyped, and carries its real line numbers. Tables that
describe the model (theoretical relations, project properties) are read from the TEI file and
from dm-ontology.ttl. Diagrams are inlined from the SVG files generated from the RDF.

Run after transform_tei_to_rdf.py and generate_model_diagrams.py:
    python3 final_report_files/site_build/build_site_snippets.py

Template directives
    {{snippet:ID}}      code card for a snippet listed in SNIPPETS
    {{svg:path}}        inline SVG file (ids prefixed so several SVGs can share a page)
    {{table:canonical}} theoretical relations R1-R19 from the TEI canonical layer
    {{table:dm}}        project properties from dm-ontology.ttl
    {{legend:instance}} / {{legend:class}}  colour key for generated diagrams
    {{models:NAME}}     text beside the model diagrams (models/graffoo/model_text.py: evidence, conformance, ...)
    {{size:path}}       natural width and height of an SVG, for <img width=".." height="..">
"""

import html
import re
from pathlib import Path

from lxml import etree
from rdflib import Graph, RDF, RDFS, OWL
from rdflib.namespace import SKOS

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TEMPLATES = HERE / "templates"
TEI_FILE = ROOT / "final_report_files" / "tei_xml" / "reconnecting_dunhuang.xml"
TTL_FILE = ROOT / "final_report_files" / "xml_to_rdf" / "reconnecting_dunhuang.ttl"
DM_FILE = ROOT / "final_report_files" / "ontology" / "dm-ontology.ttl"
NS = {"tei": "http://www.tei-c.org/ns/1.0"}

PAGES = [  # file, navigation label, title
    ("index.html", "Home", "Reconnecting Dunhuang"),
    ("domain.html", "Domain", "Domain"),
    ("models.html", "Models", "Models"),
    ("tei.html", "TEI", "TEI encoding"),
    ("transformations.html", "Transformations", "Transformations"),
    ("rdf.html", "RDF", "RDF"),
    ("wiki-view.html", "Wiki View", "Wiki View"),
    ("files.html", "Files", "Files"),
]

# Snippets: id -> (file relative to ROOT, kind, anchor, lines to highlight (substring), note)
TEI_PATH = "final_report_files/tei_xml/reconnecting_dunhuang.xml"
SNIPPETS = {
    "M1": ("final_report_files/xml_to_rdf/reconnecting_dunhuang.ttl", "turtle-resource",
           "resource:transfer-beijing", ["crm:P25_moved"],
           "The move as it appears in the RDF dataset. Line numbers are those of the Turtle file; "
           "the highlighted line is the property whose range requires a physical object."),
    "T1": (TEI_PATH, "xml-element", "sourceDesc", ["wikipedia-oldid", "Permanent revision URL"],
           "The highlighted lines fix the exact revision: its identifier and its permanent URL."),
    "T2": (TEI_PATH, "xml-first-line", "<p>|after:<body>", [],
           ""),
    "T3": (TEI_PATH, "xml-id", "aurel-stein", ["<idno"],
           ""),
    "T4": (TEI_PATH, "xml-ids", "r6 cr9 cr10 cr11 cr31 cr36", ['xml:id="r6"'],
           ""),
    "T5": (TEI_PATH, "xml-first-line", "<cit>", [],
           "Stein's own description of the Library Cave: a quotation inside a citation, with its footnote reference. "
           "Long lines wrap here for reading."),
}
TTL_PATH = "final_report_files/xml_to_rdf/reconnecting_dunhuang.ttl"
RDFXML_PATH = "final_report_files/xml_to_rdf/reconnecting_dunhuang.rdf"
SNIPPETS.update({
    "R1": (TTL_PATH, "turtle-resource", "resource:purchase-stein",
           ["crm:P22_transferred_title_to"],
           ""),
    "R1x": (RDFXML_PATH, "rdfxml-about", "resource/purchase-stein", ["P22_transferred_title_to"],
            "The same six triples in this generated RDF/XML file: resource IRIs in rdf:about and rdf:resource, predicate names abbreviated with namespace prefixes."),
    "R2": (TTL_PATH, "turtle-resource", "resource:stein-portion", ["crm:P46i_forms_part_of"],
           "The subset Stein acquired: an E19 physical object that forms part of the corpus, with the source's own wording kept as a note."),
    "R3": (TTL_PATH, "turtle-resources", "resource:aurel-stein resource:aurel-stein-viaf", ["owl:sameAs", "rdfs:seeAlso"],
           "Two parts of the file, in file order. First, one of the four identifier nodes, as CIDOC CRM models identifiers. Second, the person, with one identity link and three reference links (highlighted)."),
    "R4": (TTL_PATH, "turtle-resources", "resource:timespan-purchase-stein resource:timespan-sealing", ["P82a_begin_of_the_begin"],
           "Two time-spans. The first has a lower bound only (highlighted); the second, the sealing of the Library Cave, keeps the source's wording and no numeric bounds."),
    "R5": (TTL_PATH, "turtle-resource", "<https://haopuur-max.github.io/reconnecting-dunhuang/resource/statement/cr11>", [],
           "A statement about a statement: the triple purchase-stein P24 stein-portion, its theoretical relation R6 and its evidence type."),
})
PY_RDF = "final_report_files/xml_to_rdf/transform_tei_to_rdf.py"
SNIPPETS.update({
    "X1": ("final_report_files/xml_to_html/tei_to_html.xsl", "xsl-template", "tei:persName[@ref]", ["href", "data-ref"],
           ""),
    "X2": ("final_report_files/xml_to_html/transform_tei_to_html.py", "python-def", "transform", ["etree.XSLT"],
           "The Python function that runs the stylesheet with lxml and writes the HTML file."),
    "P1": (PY_RDF, "python-def", "add_relations", ["self.g.add"],
           ""),
    "P2": (PY_RDF, "python-defs", "date_bound add_time_bounds", ["P82a_begin_of_the_begin", "P82b_end_of_the_end"],
           "Two parts of the script, in file order: the helper that turns a TEI date value into an xsd:dateTime, and the step that adds the bounds."),
    "C1": ("README.md", "readme-code", "bash", [],
           "The commands as they appear in the project README. Each script exits with an error if one of its checks fails."),
})
WRAP = {"T1", "T2", "T4", "T5", "R1x"}
LANG = {"turtle-resource": "turtle", "turtle-resources": "turtle", "rdfxml-about": "markup",
        "xml-id": "markup", "xml-ids": "markup", "xml-element": "markup",
        "xml-first-line": "markup", "python-def": "python", "python-defs": "python",
        "xsl-template": "markup", "readme-code": "bash"}


# ---------------------------------------------------------------------------
# Snippet extraction by anchor
# ---------------------------------------------------------------------------
def extract(path, kind, anchor):
    lines = (ROOT / path).read_text(encoding="utf-8").split("\n")
    if kind == "turtle-resource":
        start = next(i for i, l in enumerate(lines) if l.startswith(f"{anchor} a "))
        end = next(i for i in range(start, len(lines)) if lines[i].rstrip().endswith(" ."))
    elif kind == "xml-id":
        start = next(i for i, l in enumerate(lines) if f'xml:id="{anchor}"' in l)
        tag = re.match(r"\s*<([\w:]+)", lines[start]).group(1)
        if lines[start].rstrip().endswith("/>") or f"</{tag}>" in lines[start]:
            end = start
        else:
            end = next(i for i in range(start, len(lines)) if f"</{tag}>" in lines[i])
    elif kind == "rdfxml-about":
        start = next(i for i, l in enumerate(lines) if "rdf:Description" in l and f'{anchor}"' in l)
        end = next(i for i in range(start, len(lines)) if "</rdf:Description>" in lines[i])
    elif kind == "xml-element":
        start = next(i for i, l in enumerate(lines) if re.search(rf"<{anchor}[\s>]", l))
        end = next(i for i in range(start, len(lines)) if f"</{anchor}>" in lines[i])
    elif kind == "xml-first-line":
        needle, _, after = anchor.partition("|after:")
        begin = next(i for i, l in enumerate(lines) if after in l) if after else 0
        start = end = next(i for i in range(begin, len(lines)) if needle in lines[i])
    elif kind == "xsl-template":
        start = next(i for i, l in enumerate(lines) if f'<xsl:template match="{anchor}"' in l)
        end = next(i for i in range(start, len(lines)) if "</xsl:template>" in lines[i])
    elif kind == "readme-code":
        start = next(i for i, l in enumerate(lines) if l.strip() == f"```{anchor}") + 1
        end = next(i for i in range(start, len(lines)) if lines[i].strip() == "```") - 1
    elif kind == "python-def":
        def_line = next(i for i, l in enumerate(lines) if re.match(rf"\s*def {anchor}\(", l))
        start = def_line
        while start > 0 and lines[start - 1].strip().startswith("@"):   # keep decorators
            start -= 1
        indent = len(lines[def_line]) - len(lines[def_line].lstrip())
        end = def_line
        for i in range(def_line + 1, len(lines)):
            if lines[i].strip() and len(lines[i]) - len(lines[i].lstrip()) <= indent:
                break
            if lines[i].strip():
                end = i
    else:
        raise ValueError(kind)
    return start + 1, lines[start:end + 1]


def ALL_LINES(path):
    return (ROOT / path).read_text(encoding="utf-8").split("\n")


def code_text(lines):
    """Escape code for HTML; braces become entities so code can never be read as a template directive."""
    return html.escape("\n".join(lines)).replace("{", "&#123;").replace("}", "&#125;")


def segments(path, kind, anchor):
    """One (first line, lines) pair per contiguous block; xml-ids merges adjacent records."""
    if kind not in ("xml-ids", "turtle-resources", "python-defs"):
        return [extract(path, kind, anchor)]
    single = {"xml-ids": "xml-id", "turtle-resources": "turtle-resource", "python-defs": "python-def"}[kind]
    blocks = sorted(extract(path, single, a) for a in anchor.split())
    merged = []
    for first, body in blocks:
        prev_end = merged[-1][0] + len(merged[-1][1]) if merged else None
        gap = ALL_LINES(path)[prev_end - 1:first - 1] if merged else None
        if merged and first >= prev_end and all(not l.strip() for l in gap):
            merged[-1] = (merged[-1][0], merged[-1][1] + gap + body)   # join blocks separated only by blank lines
        else:
            merged.append((first, body))
    return merged


def pre_block(first, body, lang, marks, wrap):
    hl, carry = [], False
    for i, l in enumerate(body):
        if any(m in l for m in marks) or carry:
            hl.append(str(first + i))
            # Turtle object lists continue after a comma: keep the continuation lines highlighted
            carry = lang == "turtle" and l.rstrip().endswith(",")
        else:
            carry = False
    data_line = f' data-line="{",".join(hl)}"' if hl else ""
    cls = f"line-numbers language-{lang}" + (" code-wrap" if wrap else "")
    return (f'<pre class="{cls}" data-start="{first}" data-line-offset="{first - 1}"{data_line}>'
            f'<code class="language-{lang}">{code_text(body)}</code></pre>')


def code_card(sid):
    path, kind, anchor, marks, note = SNIPPETS[sid]
    lang = LANG.get(kind, "markup")
    segs = segments(path, kind, anchor)
    if kind in ("xml-ids", "turtle-resources"):
        where = ", ".join(anchor.split())
    elif kind in ("python-defs", "python-def"):
        where = ", ".join(a + "()" for a in anchor.split())
    elif kind == "turtle-resource" and anchor.startswith("<"):
        where = anchor.rsplit("/", 1)[-1].rstrip(">")
    else:
        where = anchor.split("|")[0]
    ranges = ", ".join(f"{f}" if len(b) == 1 else f"{f}–{f + len(b) - 1}" for f, b in segs)
    blocks = "\n  ".join(pre_block(f, b, lang, marks, sid in WRAP) for f, b in segs)
    return (f'<div class="code-card{" code-card--multi" if len(segs) > 1 else ""}" id="snippet-{sid}">\n'
            f'  <div class="code-card__bar"><span class="code-card__path">{html.escape(path)}</span>'
            f'<span>{html.escape(where)}, line{"s" if "–" in ranges or "," in ranges else ""} {ranges}</span>'
            f'<a href="{path}">Open the full file</a></div>\n'
            f'  {blocks}\n'
            + (f'  <p class="code-card__note">{html.escape(note)}</p>\n' if note else "") + '</div>')


# ---------------------------------------------------------------------------
# Inline SVG
# ---------------------------------------------------------------------------
def svg_dims(rel):
    """'W" height="H' from the SVG viewBox, for an <img> of a model diagram (its natural size)."""
    vb = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', (ROOT / rel).read_text(encoding="utf-8"))
    return f'{float(vb.group(1)):g}" height="{float(vb.group(2)):g}'


def inline_svg(rel):
    svg = (ROOT / rel).read_text(encoding="utf-8")
    prefix = Path(rel).stem.replace("_", "-") + "-"
    svg = re.sub(r'\bid="([^"]+)"', lambda m: f'id="{prefix}{m.group(1)}"', svg)
    svg = re.sub(r'url\(#([^)]+)\)', lambda m: f'url(#{prefix}{m.group(1)})', svg)
    svg = re.sub(r'href="#([^"]+)"', lambda m: f'href="#{prefix}{m.group(1)}"', svg)
    # never scale a diagram above its natural size, so text keeps one size across figures
    vb = re.search(r'viewBox="[\d.]+ [\d.]+ ([\d.]+) [\d.]+"', svg)
    if vb:
        natural = round(float(vb.group(1)) * 96 / 72)
        svg = svg.replace("<svg ", f'<svg style="max-width:{natural}px;margin:0 auto" ', 1)
    return svg.strip()


# ---------------------------------------------------------------------------
# Generated tables
# ---------------------------------------------------------------------------
def tei_label(root, ref):
    el = root.xpath(f"//*[@xml:id='{ref.lstrip('#')}']", namespaces=NS)[0]
    for xp in ("tei:persName[not(@xml:lang)]", "tei:placeName", "tei:orgName",
               "tei:objectIdentifier/tei:objectName", "tei:name"):
        found = el.xpath(xp, namespaces=NS)
        if found:
            return " ".join("".join(found[0].itertext()).split())
    return ref


def table_canonical():
    root = etree.parse(str(TEI_FILE)).getroot()
    rows = []
    for rel in root.xpath("//tei:listRelation[@type='canonical']/tei:relation", namespaces=NS):
        rid = rel.get("xml:id") or rel.get("{http://www.w3.org/XML/1998/namespace}id")
        if rel.get("mutual"):
            a, b = rel.get("mutual").split()
        else:
            a, b = rel.get("active"), rel.get("passive")
        enriched = rel.get("ana") == "#evidence-enriched"
        tag = '<span class="tag tag--enriched">Enriched</span>' if enriched else '<span class="tag tag--direct">Direct</span>'
        rows.append(f"<tr><td class=\"nowrap\">R{rid[1:]}</td><td>{html.escape(tei_label(root, a))}</td>"
                    f"<td><em>{html.escape(rel.get('name'))}</em></td><td>{html.escape(tei_label(root, b))}</td><td>{tag}</td></tr>")
    return ('<div class="table-wrap"><table><thead><tr><th>ID</th><th>Subject</th><th>Relation</th>'
            '<th>Object</th><th>Evidence</th></tr></thead><tbody>\n' + "\n".join(rows) + "\n</tbody></table></div>")


def curie(g, uri):
    try:
        return g.namespace_manager.normalizeUri(uri)
    except Exception:
        return str(uri)


def table_dm():
    g = Graph().parse(DM_FILE)
    rows = []
    for p in sorted(set(g.subjects(RDF.type, OWL.ObjectProperty))):
        name = curie(g, p)
        sym = " (symmetric)" if (p, RDF.type, OWL.SymmetricProperty) in g else ""
        rows.append("<tr>"
                    f"<td class=\"nowrap\"><code>{html.escape(name)}</code>{sym}</td>"
                    f"<td>{html.escape(str(g.value(p, SKOS.definition)))}</td>"
                    f"<td><code>{html.escape(curie(g, g.value(p, RDFS.domain)))}</code> → "
                    f"<code>{html.escape(curie(g, g.value(p, RDFS.range)))}</code></td>"
                    f"<td>{html.escape(str(g.value(p, SKOS.editorialNote)))}</td></tr>")
    return ('<div class="table-wrap"><table><thead><tr><th>Property</th><th>Definition</th>'
            '<th>Domain → range</th><th>Existing properties considered</th></tr></thead><tbody>\n'
            + "\n".join(rows) + "\n</tbody></table></div>")


# What each part of the TEI file does (explanatory text; element names and lines come from the file)
FILEMAP_ROLES = {
    "fileDesc": "Title, responsibility and the frozen Wikipedia source",
    "encodingDesc": "Project description and the two taxonomies: concepts and evidence",
    "profileDesc": "Languages used in the text",
    "revisionDesc": "Change history of the file",
    "listPerson": "People, with authority identifiers",
    "listPlace": "Places",
    "listOrg": "Institutions and the International Dunhuang Project",
    "listObject": "The manuscript corpus and its physical subsets",
    "list/digitalObjects": "The digital surrogate",
    "list/timeSpans": "Time-spans, with machine-readable dates where the source gives them",
    "listEvent": "Events: sealing, discovery, purchases, transfer, digitization",
    "listRelation/canonical": "Theoretical relations R1–R19, in natural language",
    "listRelation/conceptual": "The same relations formalized with CIDOC CRM properties",
    "listRelation/subject": "Subjects of the corpus (dcterms:subject)",
    "body": "The article, with inline markup that points to standOff",
    "back": "See also, references and further reading",
}
PART_ROLES = {
    "teiHeader": "Describes the file and its source",
    "standOff": "Holds the model: entities, events and relations",
    "text": "The Wikipedia article itself",
}


def filemap():
    root = etree.parse(str(TEI_FILE)).getroot()
    n_lines = len(TEI_FILE.read_text(encoding="utf-8").split("\n"))
    parts = [e for e in root if isinstance(e.tag, str)]
    cols = []
    for i, part in enumerate(parts):
        name = etree.QName(part).localname
        end = (parts[i + 1].sourceline - 1) if i + 1 < len(parts) else n_lines - 1
        rows = []
        kids = [c for c in part if isinstance(c.tag, str)]
        for c in kids:
            cname = etree.QName(c).localname
            key = f"{cname}/{c.get('type')}" if c.get("type") else cname
            label = f'&lt;{cname}{" type=&quot;" + c.get("type") + "&quot;" if c.get("type") else ""}&gt;'
            rows.append(f'<li><code>{label}</code><span class="filemap__line">line {c.sourceline}</span>'
                        f'<span class="filemap__role">{html.escape(FILEMAP_ROLES.get(key, ""))}</span></li>')
        cols.append(f'<div class="filemap__part"><p class="filemap__head"><code>&lt;{name}&gt;</code>'
                    f'<span class="filemap__line">lines {part.sourceline}–{end}</span></p>'
                    f'<p class="filemap__desc">{html.escape(PART_ROLES.get(name, ""))}</p><ul>{"".join(rows)}</ul></div>')
    return f'<div class="filemap wide" aria-label="Structure of reconnecting_dunhuang.xml">{"".join(cols)}</div>'


def fullfile(rel):
    text = (ROOT / rel).read_text(encoding="utf-8").rstrip("\n")
    lang = "markup" if rel.endswith((".xml", ".xsl", ".rdf", ".html")) else ("python" if rel.endswith(".py") else "turtle")
    return (f'<details class="fullfile">\n  <summary>Show the complete file: {html.escape(Path(rel).name)}</summary>\n'
            f'  <div class="code-card"><div class="code-card__bar"><span class="code-card__path">{html.escape(rel)}</span>'
            f'<a href="{rel}" download>Download</a></div>\n'
            f'  <pre class="line-numbers language-{lang} fullfile__pre" data-start="1"><code class="language-{lang}">'
            f'{code_text(text.split(chr(10)))}</code></pre></div>\n</details>')


def triple_card(spec):
    """{{triple:resource:purchase-stein crm:P22_transferred_title_to}} - checked against the Turtle file."""
    g = Graph().parse(TTL_FILE)
    s_c, p_c = spec.split()
    s, p = g.namespace_manager.expand_curie(s_c), g.namespace_manager.expand_curie(p_c)
    objs = list(g.objects(s, p))
    if len(objs) != 1:
        raise SystemExit(f"triple card: expected one object for {spec}, found {len(objs)}")
    o = objs[0]
    o_c = g.namespace_manager.normalizeUri(o)
    def part(role, cur, full, note):
        return (f'<div class="triple__part"><span class="triple__role">{role}</span>'
                f'<code class="triple__curie">{html.escape(cur)}</code>'
                f'<span class="triple__full">{html.escape(str(full))}</span>'
                f'<span class="triple__note">{note}</span></div>')
    return ('<div class="triple wide" role="group" aria-label="One RDF triple">'
            + part("Subject", s_c, s, "an IRI or a blank node")
            + part("Predicate", p_c, p, "always an IRI, here from an ontology")
            + part("Object", o_c, o, "an IRI, a literal or a blank node")
            + '</div>')


def table_authority():
    g = Graph().parse(TTL_FILE)
    P1 = g.namespace_manager.expand_curie("crm:P1_is_identified_by")
    P2 = g.namespace_manager.expand_curie("crm:P2_has_type")
    P190 = g.namespace_manager.expand_curie("crm:P190_has_symbolic_content")
    rows = []
    for ent, _, ident in sorted(g.triples((None, P1, None)), key=lambda t: (str(g.value(t[0], RDFS.label)), str(t[2]))):
        scheme = str(g.value(g.value(ident, P2), RDFS.label))
        value = str(g.value(ident, P190))
        link = "Identifier only"
        for pred, name in ((OWL.sameAs, "owl:sameAs"), (RDFS.seeAlso, "rdfs:seeAlso")):
            for target in g.objects(ent, pred):
                if value in str(target):
                    link = f"<code>{name}</code>"
        rows.append(f"<tr><td>{html.escape(str(g.value(ent, RDFS.label)))}</td>"
                    f"<td><code>{html.escape(g.namespace_manager.normalizeUri(g.value(ent, RDF.type)))}</code></td>"
                    f"<td>{html.escape(scheme)}</td><td><code>{html.escape(value)}</code></td><td>{link}</td></tr>")
    return ('<div class="table-wrap"><table><thead><tr><th>Entity</th><th>Class</th><th>Scheme</th>'
            '<th>Identifier</th><th>External link</th></tr></thead><tbody>\n' + "\n".join(rows) + "\n</tbody></table></div>")


def table_conceptual():
    root = etree.parse(str(TEI_FILE)).getroot()
    rows = []
    for rel in root.xpath("//tei:listRelation[@type='conceptual']/tei:relation", namespaces=NS):
        rid = rel.get("{http://www.w3.org/XML/1998/namespace}id")
        if rel.get("mutual"):
            a, b = rel.get("mutual").split()
        else:
            a, b = rel.get("active"), rel.get("passive")
        enriched = rel.get("ana") == "#evidence-enriched"
        tag = ' <span class="tag tag--enriched">Enriched</span>' if enriched else ""
        rows.append(f"<tr><td>{html.escape(tei_label(root, a))}</td><td><code>{html.escape(rel.get('name'))}</code></td>"
                    f"<td>{html.escape(tei_label(root, b))}</td>"
                    f"<td class=\"nowrap\">R{rel.get('corresp')[2:]}{tag}</td></tr>")
    return ('<div class="table-wrap"><table><thead><tr><th>Subject</th><th>Property</th><th>Object</th>'
            '<th>From</th></tr></thead><tbody>\n' + "\n".join(rows) + "\n</tbody></table></div>")


def relmap(rel_id):
    """How one TEI <relation> becomes one triple: values read from the TEI file, triple checked in the Turtle."""
    root = etree.parse(str(TEI_FILE)).getroot()
    rel = root.xpath(f"//tei:relation[@xml:id='{rel_id}']", namespaces=NS)[0]
    g = Graph().parse(TTL_FILE)
    base = "https://haopuur-max.github.io/reconnecting-dunhuang/resource/"
    s_iri, o_iri = base + rel.get("active")[1:], base + rel.get("passive")[1:]
    from rdflib import URIRef
    if (URIRef(s_iri), URIRef(rel.get("ref")), URIRef(o_iri)) not in g:
        raise SystemExit(f"relmap: triple for {rel_id} not found in the Turtle file")
    nm = g.namespace_manager
    rows = [("@active", rel.get("active"), "Subject", nm.normalizeUri(URIRef(s_iri))),
            ("@ref", rel.get("ref"), "Predicate", nm.normalizeUri(URIRef(rel.get("ref")))),
            ("@passive", rel.get("passive"), "Object", nm.normalizeUri(URIRef(o_iri)))]
    body = "".join(f"<tr><td><code>{html.escape(a)}</code></td><td><code>{html.escape(v)}</code></td>"
                   f"<td>{r}</td><td><code>{html.escape(t)}</code></td></tr>" for a, v, r, t in rows)
    return ('<div class="table-wrap"><table><thead><tr><th>TEI attribute</th><th>Value in the file</th>'
            '<th>Part of the triple</th><th>In the Turtle file</th></tr></thead><tbody>' + body + "</tbody></table></div>")


# ---------------------------------------------------------------------------
# Domain page: natural-language layer only (no ontology class names)
# ---------------------------------------------------------------------------
CATEGORY = {  # conceptual class -> plain words shown on the Domain page
    "crm:E21_Person": ("People", "Person"),
    "crm:E53_Place": ("Places", "Place"),
    "crm:E74_Group": ("Institutions", "International project"),
    "crm:E18_Physical_Thing": ("Manuscripts", "The manuscript corpus"),
    "crm:E19_Physical_Object": ("Manuscripts", "Group of manuscripts"),
    "crmdig:D1_Digital_Object": ("Manuscripts", "Digital copy"),
}
EVENT_KIND = {"sealing-event": "Sealing", "discovery-event": "Discovery", "purchase-stein": "Purchase",
              "purchase-pelliot": "Purchase", "purchase-otani": "Purchase", "transfer-beijing": "Transfer",
              "digitization-event": "Digitization"}
ROLES = {  # one sentence per entity, paraphrasing the frozen Wikipedia revision
    "wang-yuanlu": "Daoist monk who discovered the documents in the cave on 25 June 1900 and from 1907 sold them to Western explorers.",
    "aurel-stein": "Explorer who bought around 7,000 complete manuscripts and 6,000 fragments from Wang and took them to Europe.",
    "paul-pelliot": "Explorer who bought almost 10,000 documents from Wang; the manuscripts he took are stored in the Bibliothèque nationale de France.",
    "otani-kozui": "Bought hundreds more of the manuscripts from Wang.",
    "luo-zhenyu": "Scholar and antiquarian whose efforts brought most of the remaining Chinese manuscripts to Beijing in 1910.",
    "library-cave": "The cave (Cave 17) in which the documents were sealed in the early 11th century.",
    "mogao-caves": "The cave complex near Sachu (Dunhuang) where the manuscripts were found.",
    "dunhuang": "Sachu, modern-day Dunhuang: a regional centre of manuscript production on the Silk Road.",
    "silk-road": "The network of routes of which Sachu formed part.",
    "beijing": "Where the remaining Chinese manuscripts were taken in 1910.",
    "british-library": "Named in the source among the institutions that hold manuscripts acquired by Western and Japanese scholars.",
    "bnf": "Holds the manuscripts that Pelliot took.",
    "nlc": "Holds the remaining Chinese manuscripts taken to Beijing in 1910.",
    "tokyo-national-museum": "Named in the source among the institutions that hold manuscripts acquired by Western and Japanese scholars.",
    "idp": "Is digitizing all the manuscript collections and makes them freely accessible online.",
    "dunhuang-manuscripts": "Religious and secular texts, mainly handwritten on hemp, silk and paper, discovered at the Mogao Caves in 1900 and now dispersed.",
    "stein-portion": "The manuscripts Stein acquired: around 7,000 complete manuscripts and 6,000 fragments.",
    "pelliot-portion": "The manuscripts Pelliot acquired: almost 10,000 documents.",
    "otani-portion": "The manuscripts sold to Ōtani Kōzui: hundreds more, in the source's words.",
    "remaining-chinese-manuscripts": "Most of the Chinese manuscripts still at Dunhuang, taken to Beijing in 1910.",
    "digital-surrogate": "The digitized manuscript collections, freely accessible online.",
    "diamond-sutra-868": "Not named in the page; added from the International Dunhuang Programme: a printed scroll dated 868, "
                         "one documented item of the corpus, bought by Stein in 1907 and now in the British Library (Or.8210/P.2).",
    "sealing-event": "The documents were sealed in the Library Cave.",
    "discovery-event": "Wang Yuanlu discovered the documents in the cave.",
    "purchase-stein": "Wang sold manuscripts to Aurel Stein.",
    "purchase-pelliot": "Wang sold manuscripts to Paul Pelliot.",
    "purchase-otani": "Wang sold hundreds more manuscripts to Ōtani Kōzui.",
    "transfer-beijing": "Most of the remaining Chinese manuscripts were taken to Beijing.",
    "digitization-event": "The International Dunhuang Project is digitizing the manuscript collections.",
}
AUTH_LINK = {"wikidata": ("Wikidata", "https://www.wikidata.org/wiki/{}"), "viaf": ("VIAF", "https://viaf.org/viaf/{}"),
             "lc": ("Library of Congress", "https://id.loc.gov/authorities/names/{}.html"),
             "lcsh": ("LCSH", "https://id.loc.gov/authorities/subjects/{}.html"),
             "fast": ("FAST", "https://id.worldcat.org/fast/{}"),
             "worldcat-entity": ("WorldCat", "https://id.oclc.org/worldcat/entity/{}")}
TABS = ["People", "Places", "Institutions", "Manuscripts", "Events"]


def tei_root():
    return etree.parse(str(TEI_FILE)).getroot()


def records(root):
    so = root.find("{http://www.tei-c.org/ns/1.0}standOff")
    out = []
    for el in so.xpath(".//*[@xml:id][tei:note[@type='conceptualClass']]", namespaces=NS):
        out.append((el.get("{http://www.w3.org/XML/1998/namespace}id"),
                    el.xpath("string(tei:note[@type='conceptualClass'])", namespaces=NS).strip(), el))
    return out


def event_dates(root):
    """event id -> date wording of its time-span (via the P4 relations), or None."""
    dates = {}
    for rel in root.xpath("//tei:listRelation[@type='conceptual']/tei:relation[@name='crm:P4_has_time-span']", namespaces=NS):
        span = root.xpath(f"//*[@xml:id='{rel.get('passive')[1:]}']/tei:date", namespaces=NS)[0]
        dates[rel.get("active")[1:]] = " ".join("".join(span.itertext()).split())
    return dates


def domain_source():
    root = tei_root()
    bibl = root.xpath("//tei:sourceDesc/tei:bibl", namespaces=NS)[0]
    oldid = bibl.xpath("string(tei:idno[@type='wikipedia-oldid'])", namespaces=NS)
    when = bibl.xpath("string(tei:date)", namespaces=NS)
    url = bibl.xpath("string(tei:ref/@target)", namespaces=NS)
    title = bibl.xpath("string(tei:title)", namespaces=NS)
    pdf = "final_report_files/source_snapshot/Wikipedia_Dunhuang_manuscripts_oldid_1347007263.pdf"
    if not (ROOT / pdf).exists():
        raise SystemExit("source snapshot PDF missing")
    return (f'<dl class="source-card wide"><dt>Article</dt><dd>English Wikipedia, “{html.escape(title)}”</dd>'
            f'<dt>Revision</dt><dd>{html.escape(oldid)}, saved {html.escape(when)} (UTC)</dd>'
            f'<dt>Online</dt><dd><a href="{html.escape(url)}">Permanent link to this revision</a></dd>'
            f'<dt>Offline</dt><dd><a href="{pdf}">PDF snapshot of the revision</a></dd></dl>')


def domain_timeline():
    root = tei_root()
    dates = event_dates(root)
    items = []
    for xml_id, cls, el in records(root):
        if xml_id not in EVENT_KIND:
            continue
        label = " ".join("".join(el.xpath("tei:label", namespaces=NS)[0].itertext()).split())
        date = dates.get(xml_id)
        date_html = html.escape(date) if date else '<span class="timeline__nodate">No date in the source</span>'
        items.append(f'<li class="timeline__item"><p class="timeline__date">{date_html}</p>'
                     f'<div class="timeline__body"><p class="timeline__kind">{EVENT_KIND[xml_id]}</p>'
                     f'<p class="timeline__label">{html.escape(label)}</p><p class="timeline__text">{html.escape(ROLES[xml_id])}</p></div></li>')
    return f'<ol class="timeline wide" aria-label="Events of the story, in the order of the TEI file">{"".join(items)}</ol>'


def authority_links(el):
    links = []
    for idno in el.iter("{http://www.tei-c.org/ns/1.0}idno"):
        scheme = idno.get("type")
        if scheme in AUTH_LINK:
            name, pattern = AUTH_LINK[scheme]
            links.append(f'<a href="{pattern.format(idno.text.strip())}">{name}</a>')
    return ", ".join(links) or '<span class="muted">None</span>'


def domain_entities():
    root = tei_root()
    dates = event_dates(root)
    groups = {t: [] for t in TABS}
    for xml_id, cls, el in records(root):
        if cls == "crm:E52_Time-Span":
            continue
        if xml_id not in ROLES:
            raise SystemExit(f"Domain page: no role sentence for {xml_id}")
        if xml_id in EVENT_KIND:
            label = " ".join("".join(el.xpath("tei:label", namespaces=NS)[0].itertext()).split())
            date = dates.get(xml_id) or "No date in the source"
            groups["Events"].append(f"<tr><td>{html.escape(label)}</td><td>{EVENT_KIND[xml_id]}</td>"
                                    f"<td>{html.escape(ROLES[xml_id])}</td><td>{html.escape(date)}</td></tr>")
            continue
        tab, category = CATEGORY[cls]
        if cls == "crm:E19_Physical_Object" and el.get("type") == "item":   # one documented manuscript, not a group
            category = "Single manuscript"
        if cls == "crm:E74_Group":  # institutions and the IDP share E74 Group; TEI org/@type tells them apart
            category = {"institution": "Institution", "project": "International project"}[el.get("type")]
        groups[tab].append(f"<tr><td>{html.escape(tei_label(root, '#' + xml_id))}</td><td>{category}</td>"
                           f"<td>{html.escape(ROLES[xml_id])}</td><td>{authority_links(el)}</td></tr>")
    tabs, panels = [], []
    for i, t in enumerate(TABS):
        sel = "true" if i == 0 else "false"
        tabs.append(f'<button type="button" role="tab" id="tab-{t.lower()}" aria-controls="panel-{t.lower()}" aria-selected="{sel}"'
                    f'{"" if i == 0 else " tabindex=\"-1\""}>{t}</button>')
        last = "Date" if t == "Events" else "Authority records"
        second = "Kind of event" if t == "Events" else "Category"
        panels.append(f'<div class="tabs__panel" role="tabpanel" id="panel-{t.lower()}" aria-labelledby="tab-{t.lower()}"{"" if i == 0 else " hidden"}>'
                      f'<h3 class="tabs__fallback">{t}</h3><div class="table-wrap"><table><thead><tr><th>Name</th><th>{second}</th>'
                      f'<th>Role in the source</th><th>{last}</th></tr></thead><tbody>{"".join(groups[t])}</tbody></table></div></div>')
    return f'<div class="tabs wide" data-tabs><div class="tabs__list" role="tablist" aria-label="Entities by kind">{"".join(tabs)}</div>{"".join(panels)}</div>'


# ---------------------------------------------------------------------------
# Files page: every file, the QA results read from the reports, and credits
# ---------------------------------------------------------------------------
FR = "final_report_files/"
FILE_GROUPS = [
    ("Source", [
        (FR + "source_snapshot/Wikipedia_Dunhuang_manuscripts_oldid_1347007263.pdf", "PDF snapshot of the frozen Wikipedia revision"),
    ]),
    ("TEI", [
        (FR + "tei_xml/reconnecting_dunhuang.xml", "The TEI P5 file: header, standOff model and the encoded article"),
        (FR + "schemas/tei_all.rng", "The TEI P5 schema used for validation (RELAX NG, release 4.12.0)"),
    ]),
    ("Ontology", [
        (FR + "ontology/dm-ontology.ttl", "Definitions of the three project properties"),
    ]),
    ("Data", [
        (FR + "xml_to_rdf/reconnecting_dunhuang.ttl", "The RDF dataset in Turtle"),
        (FR + "xml_to_rdf/reconnecting_dunhuang.rdf", "The same dataset in RDF/XML"),
    ]),
    ("Scripts", [
        (FR + "run_all.py", "Runs the whole chain below with every check, in one command, and stops at the first failure"),
        (FR + "xml_to_html/tei_to_html.xsl", "XSLT stylesheet: TEI to HTML"),
        (FR + "xml_to_html/transform_tei_to_html.py", "Runs the stylesheet and checks the HTML"),
        (FR + "xml_to_rdf/transform_tei_to_rdf.py", "TEI to RDF transformation and its checks"),
        (FR + "models/generate_model_diagrams.py", "Draws the instance graph, the core classes and the case diagrams from the RDF dataset"),
        (FR + "models/graffoo/build_model_diagrams.py", "Draws the theoretical model and the two Graffoo diagrams, web and full versions, and checks them against the data"),
        (FR + "site_build/build_site_snippets.py", "Builds these pages and cuts the code excerpts from the files"),
        (FR + "site_build/make_fragments.py", "Cuts the torn manuscript fragments of the home page from Pelliot chinois 2778 (crops with a generated edge)"),
    ]),
    ("Models", [
        (FR + "models/Reconnecting_Dunhuang_Theoretical_Model_FINAL.svg", "Theoretical model (SVG, web version)"),
        (FR + "models/Reconnecting_Dunhuang_Theoretical_Model_FINAL_full.svg", "Theoretical model (SVG, full version)"),
        (FR + "models/Reconnecting_Dunhuang_Theoretical_Model_FINAL.pdf", "Theoretical model (PDF, full version)"),
        (FR + "models/conceptual_model_core_graffoo.svg", "Conceptual model, core, Graffoo (SVG, web version)"),
        (FR + "models/conceptual_model_core_graffoo_full.svg", "Conceptual model, core, Graffoo (SVG, full version)"),
        (FR + "models/conceptual_model_core_graffoo.pdf", "Conceptual model, core, Graffoo (PDF, full version)"),
        (FR + "models/conceptual_model_subjects_identifiers_evidence_graffoo.svg", "Conceptual model, subjects, identifiers and evidence, Graffoo (SVG, web version)"),
        (FR + "models/conceptual_model_subjects_identifiers_evidence_graffoo_full.svg", "Conceptual model, subjects, identifiers and evidence, Graffoo (SVG, full version)"),
        (FR + "models/conceptual_model_subjects_identifiers_evidence_graffoo.pdf", "Conceptual model, subjects, identifiers and evidence, Graffoo (PDF, full version)"),
        (FR + "models/conceptual_model_instance_graph.svg", "Instance graph (SVG)"),
        (FR + "models/conceptual_model_instance_graph.pdf", "Instance graph (PDF)"),
        (FR + "models/core_conceptual_model.svg", "Core classes, website colours (SVG)"),
        (FR + "models/core_conceptual_model.pdf", "Core classes, website colours (PDF)"),
        (FR + "models/authority_linking_table.md", "Every identifier and the link it received"),
    ]),
    ("Outputs", [
        ("wiki-view.html", "The Wiki View: the TEI file rendered as an article"),
        (FR + "xml_to_html/reconnecting_dunhuang.html", "The HTML produced by the XSLT stylesheet"),
    ]),
    ("Reports", [
        (FR + "validation/tei_validation_report.txt", "TEI validation"),
        (FR + "xml_to_rdf/rdf_qa_report.txt", "RDF checks and counts"),
        (FR + "xml_to_html/html_qa_report.txt", "HTML checks"),
        (FR + "validation/site_acceptance_report.txt", "Full-site check: links, code excerpts, Wiki View, file list, reports"),
        ("README.md", "How to rebuild everything"),
    ]),
]
IMAGE_SECTIONS = {"hero_cave16_manuscripts.jpg": 1, "history_pelliot_cave17.jpg": 2, "entity_wang_yuanlu.jpg": 3,
                  "manuscript_pelliot_chinois_2778.jpg": 4, "context_donor_portrait_cave17.jpg": 5}


def human_size(n):
    return f"{n / 1024 / 1024:.1f} MB" if n >= 1024 * 1024 else f"{max(1, round(n / 1024))} KB"


def files_groups():
    out = []
    for group, items in FILE_GROUPS:
        rows = []
        for path, desc in items:
            if not (ROOT / path).exists():
                raise SystemExit(f"Files page lists a missing file: {path}")
            size = human_size((ROOT / path).stat().st_size)
            rows.append(f'<li><a href="{path}">{html.escape(Path(path).name)}</a>'
                        f'<span class="filelist__desc">{html.escape(desc)}</span><span class="filelist__size">{size}</span></li>')
        out.append(f'<div class="filelist__group"><h3>{group}</h3><ul>{"".join(rows)}</ul></div>')
    return f'<div class="filelist wide">{"".join(out)}</div>'


def qa_summary():
    rdf = (ROOT / FR / "xml_to_rdf/rdf_qa_report.txt").read_text(encoding="utf-8")
    htm = (ROOT / FR / "xml_to_html/html_qa_report.txt").read_text(encoding="utf-8")
    tei = (ROOT / FR / "validation/tei_validation_report.txt").read_text(encoding="utf-8")
    def tag(ok):
        return '<span class="result result--pass">Pass</span>' if ok else '<span class="result result--fail">Fail</span>'
    checks = [("TEI validation", "The TEI file is valid against the TEI P5 schema tei_all", "Relax NG validation: PASS" in tei)]
    for line in re.findall(r"^  (V\d .+)$", rdf, flags=re.M):
        text, _, result = line.rpartition(": ")
        desc = text.split(" ", 1)[1]
        checks.append(("RDF " + text.split(" ", 1)[0], desc[:1].upper() + desc[1:], result.strip() == "PASS"))
    checks.append(("HTML checks", "Every standOff record, relation, section, figure caption and reference of the TEI file appears in the HTML; the TEI file is unchanged", htm.strip().endswith("HTML QA PASS")))
    if not all(c[2] for c in checks):
        raise SystemExit("Files page: a QA report does not pass")
    rows = "".join(f"<tr><td class=\"nowrap\">{html.escape(a)}</td><td>{html.escape(b)}</td><td>{tag(c)}</td></tr>" for a, b, c in checks)
    counts = re.search(r"^Counts\n(.*?)\n\n", rdf, flags=re.M | re.S).group(1)
    crow = []
    for line in counts.splitlines():
        name, _, value = line.strip().partition(" ..")
        name = name.strip()
        crow.append(f"<tr><td>{html.escape(name[:1].upper() + name[1:])}</td><td>{html.escape(value.strip(' .'))}</td></tr>")
    date = re.search(r"Generated: (\S+)", rdf).group(1)
    return (f'<div class="table-wrap"><table><thead><tr><th>Check</th><th>What it verifies</th><th>Result</th></tr></thead><tbody>{rows}</tbody></table></div>'
            f'<h3>The dataset in numbers</h3><p>Read from the RDF report of {html.escape(date)}.</p>'
            f'<div class="table-wrap"><table><thead><tr><th>Item</th><th>Count</th></tr></thead><tbody>{"".join(crow)}</tbody></table></div>')


def credits():
    used = set()
    for f in ROOT.glob("*.html"):
        used |= set(re.findall(r"assets/img/([\w.-]+\.jpg)", f.read_text(encoding="utf-8")))
        if "assets/img/fragments/" in f.read_text(encoding="utf-8"):   # the fragments are cut from item 4
            used.add("manuscript_pelliot_chinois_2778.jpg")
    text = (ROOT / "assets/img/IMAGE_CREDITS.md").read_text(encoding="utf-8")
    sections = {int(m.group(1)): m.group(0) for m in re.finditer(r"^## (\d+)\..*?(?=^## |\Z)", text, flags=re.M | re.S)}
    items = []
    for name in sorted(used):
        sec = sections[IMAGE_SECTIONS[name]]
        title = re.search(r"^## \d+\. (.+)$", sec, flags=re.M).group(1)
        field = lambda k: (re.search(rf"\*\*{k}:\*\* (.+)", sec) or [None, ""])[1]
        who = ", ".join(x for x in (field("Author"), field("Date")) if x)
        items.append(f'<li><b>{html.escape(title)}.</b> {html.escape(who)}. {html.escape(field("Rights"))}. '
                     f'<a href="{html.escape(field("Source page"))}">Wikimedia Commons</a></li>')
    return f'<ul class="credits">{"".join(items)}</ul>'


def wiki_view():
    """The Wiki View is the XSLT output: the same stylesheet is run with base='' (images relative to the website
    root) and its #wiki-root element is placed in the site shell. Apart from that path prefix it must be identical
    to the deliverable xml_to_html/reconnecting_dunhuang.html, which is checked here."""
    xsl = etree.XSLT(etree.parse(str(ROOT / FR / "xml_to_html/tei_to_html.xsl")))
    result = xsl(etree.parse(str(TEI_FILE)), base="''")
    # serialized exactly as transform_tei_to_html.py writes the deliverable (method html, pretty_print)
    root = etree.fromstring(etree.tostring(result, method="html", encoding="UTF-8", pretty_print=True), etree.HTMLParser())
    view = root.xpath("//div[@id='wiki-root']")[0]
    view_html = etree.tostring(view, method="html", encoding="unicode")
    deliverable = etree.parse(str(ROOT / FR / "xml_to_html/reconnecting_dunhuang.html"), etree.HTMLParser())
    deliv_html = etree.tostring(deliverable.xpath("//div[@id='wiki-root']")[0], method="html", encoding="unicode")
    if deliv_html.replace('src="../../', 'src="') != view_html:
        raise SystemExit("Wiki View differs from the XSLT deliverable; run transform_tei_to_html.py first")
    for src in view.xpath("//img/@src"):
        if not (ROOT / src).exists():
            raise SystemExit(f"Wiki View image missing: {src}")
    return view_html


HOME_LABELS = ["dunhuang-manuscripts", "library-cave", "wang-yuanlu", "aurel-stein", "idp"]


def home_overlay():
    """The theoretical relations R1-R16 drawn over the hero photograph. Nodes and edges are read from the
    TEI canonical layer; their positions come from a Graphviz (neato) layout, so nothing is placed by hand."""
    import subprocess
    root = tei_root()
    edges = []
    for rel in root.xpath("//tei:listRelation[@type='canonical']/tei:relation", namespaces=NS):
        a, b = (rel.get("mutual").split() if rel.get("mutual") else (rel.get("active"), rel.get("passive")))
        edges.append((a[1:], b[1:]))
    nodes = sorted({n for e in edges for n in e})
    dot = "graph g { graph [layout=neato, overlap=false, start=7, sep=0.4]; node [shape=point];\n"
    dot += "\n".join(f'"{a}" -- "{b}";' for a, b in edges) + "\n}"
    plain = subprocess.run(["dot", "-Tplain"], input=dot, capture_output=True, text=True, check=True).stdout
    pos = {}
    for line in plain.splitlines():
        parts = line.split()
        if parts and parts[0] == "node":
            pos[parts[1].strip('"')] = (float(parts[2]), float(parts[3]))
    xs, ys = [p[0] for p in pos.values()], [p[1] for p in pos.values()]
    W, H, M = 550, 386, 48
    def place(n):
        x, y = pos[n]
        return (M + (x - min(xs)) / ((max(xs) - min(xs)) or 1) * (W - 2 * M),
                M + (max(ys) - y) / ((max(ys) - min(ys)) or 1) * (H - 2 * M))
    out = [f'<svg class="hero__overlay" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice" aria-hidden="true">']
    for a, b in edges:
        (x1, y1), (x2, y2) = place(a), place(b)
        out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"/>')
    for n in nodes:
        x, y = place(n)
        cls = "hero__node hero__node--core" if n == "dunhuang-manuscripts" else "hero__node"
        out.append(f'<circle class="{cls}" cx="{x:.1f}" cy="{y:.1f}" r="{6 if n == "dunhuang-manuscripts" else 4}"><title>{html.escape(tei_label(root, "#" + n))}</title></circle>')
    for n in HOME_LABELS:
        x, y = place(n)
        label = html.escape(tei_label(root, "#" + n))
        w = 7.2 * len(label) + 14
        lx = min(max(x - w / 2, 4), W - w - 4)
        ly = y + 10 if y < H - 30 else y - 30
        out.append(f'<g class="hero__label"><rect x="{lx:.1f}" y="{ly:.1f}" width="{w:.1f}" height="20" rx="3"/>'
                   f'<text x="{lx + w / 2:.1f}" y="{ly + 14:.1f}" text-anchor="middle">{label}</text></g>')
    out.append("</svg>")
    return "".join(out)


def table_dm_short():
    g = Graph().parse(DM_FILE)
    rows = []
    for p in sorted(set(g.subjects(RDF.type, OWL.ObjectProperty))):
        rows.append(f"<tr><td class=\"nowrap\"><code>{html.escape(curie(g, p))}</code></td>"
                    f"<td>{html.escape(str(g.value(p, SKOS.definition)))}</td>"
                    f"<td><code>{html.escape(curie(g, g.value(p, RDFS.domain)))}</code> → "
                    f"<code>{html.escape(curie(g, g.value(p, RDFS.range)))}</code></td></tr>")
    return ('<div class="table-wrap"><table><thead><tr><th>Property</th><th>Definition</th>'
            '<th>Domain → range</th></tr></thead><tbody>' + "".join(rows) + "</tbody></table></div>")


def uri_list():
    """Namespaces and example IRIs, each checked in the Turtle and dm-ontology files."""
    from rdflib import URIRef
    g = Graph().parse(TTL_FILE)
    dm = Graph().parse(DM_FILE)
    base = "https://haopuur-max.github.io/reconnecting-dunhuang/"
    examples = [(base + "resource/dunhuang-manuscripts", g), (base + "resource/aurel-stein", g),
                (base + "resource/purchase-stein", g), (base + "resource/timespan-purchase-stein", g),
                (base + "ontology/virtuallyBringsTogether", dm)]
    rows = []
    for iri, graph in examples:
        if (URIRef(iri), None, None) not in graph:
            raise SystemExit(f"URI example not in the data: {iri}")
        rows.append(f"<li><code>{html.escape(iri)}</code></li>")
    return ('<dl class="source-card wide"><dt>Resources</dt><dd><code>' + base + 'resource/{id}</code></dd>'
            '<dt>Properties</dt><dd><code>' + base + 'ontology/{name}</code> (prefix <code>dm:</code>)</dd></dl>'
            '<ul class="uri-list">' + "".join(rows) + "</ul>")


LEGENDS = {
    "instance": [
        ("swatch swatch--event", "Event"), ("swatch swatch--actor", "Person or institution"),
        ("swatch swatch--place", "Place"), ("swatch swatch--thing", "The corpus (E18)"),
        ("swatch swatch--object", "Physical subset (E19)"), ("swatch swatch--time", "Time-span"),
        ("swatch swatch--digital", "Digital object"), ("line-key line-key--dm", "Project property (dm:)"),
        ("line-key line-key--dcterms", "DCTerms property"), ("line-key line-key--enriched", "Enriched relation"),
    ],
    "class": [
        ("swatch swatch--event", "Event classes"), ("swatch swatch--actor", "Actor classes"),
        ("swatch swatch--place", "Place"), ("swatch swatch--thing", "E18 Physical Thing"),
        ("swatch swatch--object", "E19 Physical Object"), ("swatch swatch--time", "E52 Time-Span"),
        ("swatch swatch--digital", "D1 Digital Object"), ("line-key line-key--dm", "Project property (dm:)"),
        ("line-key line-key--dcterms", "DCTerms property"),
    ],
}


def legend(kind):
    items = "".join(f'<span class="legend__item"><span class="{c}" aria-hidden="true"></span>{html.escape(t)}</span>'
                    for c, t in LEGENDS[kind])
    return f'<p class="legend" aria-label="Colour key">{items}</p>'


# ---------------------------------------------------------------------------
# Page shell
# ---------------------------------------------------------------------------
SHELL = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<meta name="author" content="{author}">
<link rel="icon" href="assets/ornaments/mark.svg" type="image/svg+xml">
<link rel="stylesheet" href="assets/css/site.css">
<link rel="stylesheet" href="assets/css/prism-editorial.css">
<link rel="stylesheet" href="assets/css/print.css">
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header">
  <div class="site-header__inner">
    <a class="wordmark" href="index.html">Reconnecting Dunhuang</a>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav">Menu</button>
    <nav class="site-nav" id="site-nav" aria-label="Main">
      <ul>
{nav}
      </ul>
    </nav>
  </div>
</header>
<main id="main" class="page">
{content}
</main>
<footer class="site-footer">
  <div class="site-footer__inner">
    <nav class="pager" aria-label="Previous and next page">
{pager}
    </nav>
    <p class="site-footer__meta"><img src="assets/ornaments/mark.svg" alt="" width="36" height="36">
      <span>{author} · A project for Information Science and Cultural Heritage, University of Bologna, 2025–2026. Source: English Wikipedia, “Dunhuang manuscripts”, revision 1347007263.</span></p>
  </div>
</footer>
<script src="assets/js/prism.js"></script>
<script src="assets/js/site.js"></script>
</body>
</html>
"""

DESCRIPTIONS = {
    "wiki-view.html": "The TEI-derived Wiki View: the Dunhuang manuscripts article as encoded in TEI, rendered by XSLT with a contents list, an infobox and links to the standOff entities.",
    "files.html": "Every file of the Reconnecting Dunhuang project, the results of its checks, and credits for images, fonts and software.",
    "index.html": "Reconnecting Dunhuang: the Dunhuang manuscripts, from one Wikipedia article to a TEI edition, a CIDOC CRM model and an RDF dataset.",
    "domain.html": "The source and the story behind Reconnecting Dunhuang: a frozen Wikipedia revision, the events from the sealing of the Library Cave to digitization, and the people, places, institutions and manuscripts involved.",
    "transformations.html": "How one TEI file produces both outputs of the Reconnecting Dunhuang project: XSLT for the HTML Wiki View, Python and rdflib for the RDF dataset.",
    "rdf.html": "How to read the Reconnecting Dunhuang RDF dataset: triples, Turtle and RDF/XML, physical subsets, dates and links to external authorities.",
    "tei.html": "How the Wikipedia article and the Reconnecting Dunhuang model are encoded in one TEI P5 file: header, standOff and text.",
    "models.html": "How the Reconnecting Dunhuang project moves from a natural-language theoretical model to a conceptual model built on CIDOC CRM, CRMsci and CRMdig.",
}

PENDING = """<header class="page-head">
  <h1>{title}</h1>
  <p class="pending">This page is built in the next stage of the project, after the Models page has been reviewed.</p>
</header>
"""


NAV = ["domain.html", "models.html", "tei.html", "transformations.html", "rdf.html", "files.html"]
FROZEN = {"index.html"}   # not rewritten by this script


def nav_html(current):
    labels = {f: l for f, l, _ in PAGES}
    items = []
    for file in NAV:
        cur = ' aria-current="page"' if file == current else ""
        cls = ' class="nav-secondary"' if file == "files.html" else ""
        items.append(f'        <li{cls}><a href="{file}"{cur}>{labels[file]}</a></li>')
    return "\n".join(items)


def pager_html(current):
    labels = {f: l for f, l, _ in PAGES}
    if current not in NAV:
        return f'      <a class="pager__prev" href="transformations.html"><span class="pager__dir">Back to</span><span class="pager__name">Transformations</span></a>'
    order = [(f, labels[f], None) for f in NAV]
    idx = NAV.index(current)
    out = []
    if idx > 0:
        f, l, _ = order[idx - 1]
        out.append(f'      <a class="pager__prev" href="{f}"><span class="pager__dir">Previous</span><span class="pager__name">{l}</span></a>')
    if idx < len(order) - 1:
        f, l, _ = order[idx + 1]
        out.append(f'      <a class="pager__next" href="{f}"><span class="pager__dir">Next</span><span class="pager__name">{l}</span></a>')
    return "\n".join(out)


def label_table_cells(text):
    """Give every <td> a data-label taken from its column header, so narrow screens can show
    each row as a stacked card (see site.css, max-width 600px)."""
    def one_table(m):
        table = m.group(0)
        heads = [re.sub(r"<[^>]+>", "", h).strip() for h in re.findall(r"<th[^>]*>(.*?)</th>", table, flags=re.S)]
        def one_row(r):
            cells = iter(heads)
            return re.sub(r"<td(?![^>]*data-label)", lambda c: f'<td data-label="{html.escape(next(cells, ""))}"', r.group(0))
        return re.sub(r"<tr>.*?</tr>", one_row, table, flags=re.S)
    return re.sub(r"<table>.*?</table>", one_table, text, flags=re.S)


def render_directives(text):
    text = re.sub(r"\{\{snippet:(\w+)\}\}", lambda m: code_card(m.group(1)), text)
    text = re.sub(r"\{\{svg:([^}]+)\}\}", lambda m: inline_svg(m.group(1)), text)
    text = text.replace("{{table:canonical}}", table_canonical())
    text = text.replace("{{table:dm}}", table_dm())
    text = text.replace("{{table:dm-short}}", table_dm_short())
    text = text.replace("{{rdf:uris}}", uri_list())
    text = re.sub(r"\{\{triple:([^}]+)\}\}", lambda m: triple_card(m.group(1)), text)
    text = re.sub(r"\{\{relmap:([\w-]+)\}\}", lambda m: relmap(m.group(1)), text)
    if "{{files:" in text:
        text = text.replace("{{files:groups}}", files_groups()).replace("{{files:qa}}", qa_summary())
    if "{{home:overlay}}" in text:
        text = text.replace("{{home:overlay}}", home_overlay())
    if "{{home:revision}}" in text:
        url = tei_root().xpath("string(//tei:sourceDesc/tei:bibl/tei:ref/@target)", namespaces=NS)
        text = text.replace("{{home:revision}}", html.escape(url))
    if "{{domain:" in text:
        text = text.replace("{{domain:source}}", domain_source()).replace("{{domain:timeline}}", domain_timeline())
        text = text.replace("{{domain:entities}}", domain_entities())
    if "{{table:authority}}" in text:
        text = text.replace("{{table:authority}}", table_authority())
    if "{{table:conceptual}}" in text:
        text = text.replace("{{table:conceptual}}", table_conceptual())
    text = re.sub(r"\{\{legend:(\w+)\}\}", lambda m: legend(m.group(1)), text)
    if "{{models:" in text:
        import sys
        sys.path.insert(0, str(ROOT / "final_report_files" / "models" / "graffoo"))
        import model_text
        text = re.sub(r"\{\{models:([\w-]+)\}\}", lambda m: model_text.DIRECTIVES[m.group(1)](), text)
    text = re.sub(r"\{\{size:([^}]+)\}\}", lambda m: svg_dims(m.group(1)), text)
    text = text.replace("{{filemap:tei}}", filemap())
    tei_lines = TEI_FILE.read_text(encoding="utf-8").split("\n")
    text = re.sub(r"\{\{teiline:(.+?)\}\}",
                  lambda m: str(next(i + 1 for i, l in enumerate(tei_lines) if html.unescape(m.group(1)) in l)), text)
    text = re.sub(r"\{\{fullfile:([^}]+)\}\}", lambda m: fullfile(m.group(1)), text)
    text = label_table_cells(text)
    if "{{wiki:view}}" in text:   # inserted after table labelling: the XSLT output is kept exactly as produced
        text = text.replace("{{wiki:view}}", wiki_view())
    left = re.findall(r"\{\{[^}]*\}\}", text)
    if left:
        raise SystemExit(f"Unresolved template directives: {left}")
    return text


def author_name():
    """The author as recorded in the TEI titleStmt (the one place the name is written)."""
    pn = tei_root().xpath("//tei:titleStmt/tei:author/tei:persName", namespaces=NS)[0]
    return " ".join("".join(pn.itertext()).split())


def update_frozen_footer(file):
    """index.html is not rebuilt; only its author meta tag and footer line are brought in line with the other pages."""
    path = ROOT / file
    text = path.read_text(encoding="utf-8")
    name = html.escape(author_name())
    text = re.sub(r'\n<meta name="author" content="[^"]*">', "", text)
    text = re.sub(r'(<meta name="description" content="[^"]*">)', rf'\1\n<meta name="author" content="{name}">', text, count=1)
    text = re.sub(r"<span>(?:[^<·]* · )?A project for Information Science", f"<span>{name} · A project for Information Science", text, count=1)
    path.write_text(text, encoding="utf-8")


def main():
    built = []
    # files.html is built last, so that its image credits can see which images the other pages use
    build_order = sorted(PAGES, key=lambda p: p[0] == "files.html")
    for file, label, title in build_order:
        if file in FROZEN:
            continue
        template = TEMPLATES / file
        if template.exists():
            content = template.read_text(encoding="utf-8")
            if "{{files:credits}}" in content:
                content = content.replace("{{files:credits}}", credits())
            content = render_directives(content)
            if file == "domain.html":
                leak = re.findall(r"\b(?:crm|crmsci|crmdig):\w+|\b[EDS]\d{1,3}_[A-Z]\w*", content)
                if leak:
                    raise SystemExit(f"Domain page must stay in natural language; found ontology terms: {sorted(set(leak))}")
            built.append(file)
        else:
            content = PENDING.format(title=html.escape(title))
        full_title = title if title == "Reconnecting Dunhuang" else f"{title} · Reconnecting Dunhuang"
        page = SHELL.format(title=html.escape(full_title), description=html.escape(DESCRIPTIONS.get(file, "Reconnecting Dunhuang - Web Report")),
                            nav=nav_html(file), content=content, pager=pager_html(file), author=html.escape(author_name()))
        (ROOT / file).write_text(page, encoding="utf-8")
    print("Built from templates:", ", ".join(built) or "none")
    for file in sorted(FROZEN):
        update_frozen_footer(file)
    print("Not rebuilt (frozen):", ", ".join(sorted(FROZEN)), "- author meta tag and footer line updated")


if __name__ == "__main__":
    main()
