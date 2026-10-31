"""HTML text placed beside the model diagrams on the Models page (directives {{models:...}} in the template).

Every number and definition is read from the Turtle file, and the table rows come from conformance.py, the module the
full (PDF) version of the core diagram prints from, so the page text, the web diagrams and the PDFs cannot disagree."""
import html
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import TTL
import conformance
from rdflib import Graph, URIRef
from rdflib.namespace import RDF, RDFS, OWL, SKOS, DCTERMS

G = Graph().parse(TTL)
RES = "https://haopuur-max.github.io/reconnecting-dunhuang/resource/"
CRM = "http://www.cidoc-crm.org/cidoc-crm/"
DEF = {k: str(G.value(URIRef(RES + "evidence/" + k), SKOS.definition)) for k in ("direct", "enriched")}
NEV = {k: len(set(G.subjects(DCTERMS.type, URIRef(RES + "evidence/" + k)))) for k in ("direct", "enriched")}
NST = len(set(G.subjects(RDF.type, RDF.Statement)))
NSAME = len(list(G.triples((None, OWL.sameAs, None))))
NSEE = len(list(G.triples((None, RDFS.seeAlso, None))))
NR6 = len(set(G.subjects(DCTERMS.relation, URIRef(RES + "canonical-relation/r6"))))
NONE = sorted(r for r in ("r9", "r12") if not list(G.subjects(DCTERMS.relation, URIRef(RES + "canonical-relation/" + r))))
assert (len(G), NST, NEV["direct"], NEV["enriched"], NSAME, NSEE, NR6, NONE) == (683, 38, 34, 4, 10, 30, 5, ["r12", "r9"])
e = html.escape


def evidence():
    return (f'<dl class="defs">\n'
            f'  <div><dt>Direct</dt><dd>{e(DEF["direct"])} <span class="defs__n">{NEV["direct"]} restated triples</span></dd></div>\n'
            f'  <div><dt>Enriched</dt><dd>{e(DEF["enriched"])} <span class="defs__n">{NEV["enriched"]} restated triples (R16–R19)</span></dd></div>\n'
            f'</dl>')


def conformance_table():
    rows = "\n".join(
        f"<tr><td><code>{e(p)}</code></td><td>{e(dec)}</td><td>{e(used)}</td><td>{'<br>'.join(e(x) for x in why)}</td></tr>"
        for p, dec, used, why in conformance.ROWS)
    return ('<div class="table-wrap">\n<table class="table--compact">\n'
            '<thead><tr><th>Property</th><th>Declared</th><th>Used here</th><th>Valid because</th></tr></thead>\n'
            f'<tbody>\n{rows}\n</tbody></table>\n</div>')


def e96():
    return e(" ".join(conformance.E96_LINES))


def identity():
    return (f'<code>owl:sameAs</code> ({NSAME} links) only where the external record is the same individual (persons and groups); '
            f'<code>rdfs:seeAlso</code> ({NSEE} links) for a description elsewhere, with no identity claim (the corpus and the '
            f'places link to Wikidata this way).')


def statements():
    return (f'Only the {NST} conceptual-relation triples (the formalisations of R1–R19) are restated as <code>rdf:Statement</code>, '
            f'not all {len(G)} triples of the dataset.')


def r6_count():
    return str(NR6)


DIRECTIVES = {"evidence": evidence, "conformance": conformance_table, "e96": e96, "identity": identity,
              "statements": statements, "r6-count": r6_count}
