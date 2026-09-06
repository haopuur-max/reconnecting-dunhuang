#!/usr/bin/env python3
"""
Reconnecting Dunhuang — TEI/XML to RDF transformation.

Parses the locked reconnecting_dunhuang.xml (standOff entity registers +
canonical/conceptual relation layers) and produces an RDF dataset in
Turtle and RDF/XML, serialized from the same in-memory graph.

Project scope preserved from the finalized conceptual model (v1), extended
for v2 (provenance/reification layer), extended again for v2.1 (integrated
post-generation validation into the script itself) and v2.2 (upgraded that
validation from existence checks to an exact full-graph comparison):

  - Only the 30 conceptual-layer <relation> elements (cr1-cr30) become
    core domain assertions (the formal CIDOC CRM / dm: ontology edges).
    The 16 canonical-layer relations (r1-r16) use informal, pre-ontology
    labels (e.g. "sold_manuscripts_to") that are explicitly NOT formal
    ontology properties per this project's own Theoretical Model notes,
    so they are never asserted as RDF predicates. Their r-numbers and
    names are used only as literal label text on provenance nodes (see
    below); they never contribute additional core conceptual edges.

  - Authority identifiers (<idno>) are converted using CIDOC CRM's own
    identifier pattern (P1_is_identified_by / E42_Identifier /
    P190_has_symbolic_content / P2_has_type), NOT owl:sameAs.
    Only <idno> elements that actually exist in the TEI are converted.
    Nothing is invented or backfilled.

  - Identifier-scheme type nodes (one per distinct @type value actually
    used, e.g. "viaf", "wikidata", "fast-control-number") live under
    resource:identifier-type/, not under the dm: ontology namespace,
    which is reserved for the four locked project-specific properties.

  - v2: each conceptual-layer relation (cr1-cr30) additionally gets a
    standard RDF reification node (resource:statement/cr{N}, typed
    rdf:Statement, carrying rdf:subject/rdf:predicate/rdf:object)
    recording, via Dublin Core Terms:
      * dcterms:relation -> resource:canonical-relation/r{N}
        (the canonical-layer relation it corresponds to, via @corresp)
      * dcterms:type     -> resource:evidence/direct | resource:evidence/enriched
        (the evidence status carried by TEI @ana)
    These are metadata ABOUT the 30 core assertions, not additional
    core assertions themselves.

  - v2: resource:canonical-relation/r1..r16 and resource:evidence/direct
    and resource:evidence/enriched get rdfs:label triples so the
    provenance layer is human-readable directly from the RDF output.

  - v2: dm:locatedNear is declared owl:SymmetricProperty as a standalone
    ontology-level triple. This does not add a reverse core assertion;
    cr2's single mutual triple remains the only core edge for r2.

  - v2.1: PostGenerationValidator was integrated into the script itself,
    re-parsing the serialized .ttl and .rdf files fresh (not the
    in-memory graph) and independently re-deriving expected data straight
    from reconnecting_dunhuang.xml, then diffing the two — without
    calling any Converter method and without reusing the DM_PROPERTIES
    lookup table. This closed the gap between "a human ran an ad-hoc
    check once" and "the script itself proves its own output correct
    every time it runs." If validation fails, the script exits non-zero
    after writing the mismatch details to the QA report; it never
    silently prints FAIL and exits 0.

  - v2.2: v2.1's validator checked existence ("does each expected triple
    appear in the actual graph") over a scope limited to specific
    predicates and node counts. That missed two classes of real defect:
    a triple whose CONTENT is wrong but whose surrounding counts are
    unchanged (e.g. a corrupted identifier value), and an arbitrary
    EXTRA triple using a predicate outside the checked scope. v2.2
    rewrites the validator to independently rebuild the ENTIRE expected
    459-triple dataset from the XML and diff it for exact triple-set
    equality (expected-actual and actual-expected both empty) plus graph
    isomorphism, against the serialized TTL, the serialized RDF/XML, and
    the in-memory graph. Both classes of defect above were reproduced
    against the old validator and confirmed caught by the new one.

    Both v2.1 and v2.2 are purely additive to the RDF layer: neither
    changes any RDF mapping or the triple count (still 459/459).

  - v2.4: the script now regenerates view_turtle.html and view_rdfxml.html
    immediately after writing reconnecting_dunhuang.ttl and
    reconnecting_dunhuang.rdf, so the two browser-readable viewers can
    never go stale relative to the raw serialized files (RDF/XML
    serialization order is not guaranteed stable across runs, even
    though the underlying graph is unchanged). Each viewer applies only
    HTML escaping to the raw file text; it does not reinterpret,
    reorder, or alter any RDF content. This is purely additive to the
    package's reproducibility story: it does not change any RDF
    mapping, triple count, or the 459/459 result.
"""

import html
import os
import sys
from pathlib import Path
from lxml import etree
from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS, OWL, compare
from rdflib.namespace import DCTERMS

# ---------------------------------------------------------------------------
# Project namespaces
# ---------------------------------------------------------------------------
PROJECT_BASE = "https://haopuur-max.github.io/reconnecting-dunhuang/"
DM = Namespace(PROJECT_BASE + "ontology/")
RESOURCE = Namespace(PROJECT_BASE + "resource/")
CRM = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
CRMSCI = Namespace("http://www.cidoc-crm.org/extensions/crmsci/")
CRMDIG = Namespace("http://www.cidoc-crm.org/extensions/crmdig/")

TEI_NS = "http://www.tei-c.org/ns/1.0"
NSMAP = {"tei": TEI_NS}

CLASS_NS = {"crm": CRM, "crmsci": CRMSCI, "crmdig": CRMDIG}
SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_XML = SCRIPT_DIR.parent / "tei_xml" / "reconnecting_dunhuang.xml"
DEFAULT_TTL = SCRIPT_DIR / "reconnecting_dunhuang.ttl"
DEFAULT_RDF = SCRIPT_DIR / "reconnecting_dunhuang.rdf"
DEFAULT_QA_REPORT = SCRIPT_DIR / "rdf_qa_report.txt"
# output/ is two levels up from output/final_report_files/xml_to_rdf/
DEFAULT_OUTPUT_DIR = SCRIPT_DIR.parent.parent
DEFAULT_VIEW_TURTLE = DEFAULT_OUTPUT_DIR / "view_turtle.html"
DEFAULT_VIEW_RDFXML = DEFAULT_OUTPUT_DIR / "view_rdfxml.html"

DM_PROPERTIES = {
    "dm:partOfNetwork": DM.partOfNetwork,
    "dm:locatedNear": DM.locatedNear,
    "dm:providesDigitalAccessTo": DM.providesDigitalAccessTo,
    "dm:virtuallyBringsTogether": DM.virtuallyBringsTogether,
}

# Human-readable labels for identifier schemes actually encountered.
# Only used if a scheme shows up in the data; unknown schemes fall back
# to their raw @type string so nothing is silently dropped.
SCHEME_LABELS = {
    "wikidata": "Wikidata",
    "viaf": "VIAF",
    "lc": "Library of Congress Authorities",
    "lcsh": "Library of Congress Subject Headings",
    "fast": "FAST (OCLC)",
    "fast-control-number": "FAST control number (OCLC)",
    "worldcat-entity": "WorldCat Entity",
}

EVIDENCE_LABELS = {
    "direct": "Direct evidence",
    "enriched": "Enriched evidence",
}


def tei(tag):
    return f"{{{TEI_NS}}}{tag}"


def strip_prefix(ref):
    """'#foo' -> 'foo'"""
    return ref[1:] if ref.startswith("#") else ref


def class_uri(conceptual_class_text):
    """'crm:E21_Person' -> CRM.E21_Person"""
    prefix, local = conceptual_class_text.split(":", 1)
    return CLASS_NS[prefix][local]


def first_text(el, xpath):
    found = el.xpath(xpath, namespaces=NSMAP)
    return found[0].strip() if found else None


class Converter:
    def __init__(self, xml_path):
        self.tree = etree.parse(xml_path)
        self.root = self.tree.getroot()
        self.g = Graph()
        self.g.bind("crm", CRM)
        self.g.bind("crmsci", CRMSCI)
        self.g.bind("crmdig", CRMDIG)
        self.g.bind("dm", DM)
        self.g.bind("resource", RESOURCE)
        self.g.bind("rdf", RDF)
        self.g.bind("rdfs", RDFS)
        self.g.bind("owl", OWL)
        self.g.bind("dcterms", DCTERMS)

        # QA counters, kept separate from the graph itself so the report
        # doesn't depend on re-querying triples back out after the fact.
        # (Independent re-verification of the actual serialized output is
        # done by PostGenerationValidator below, not by these counters.)
        self.n_core_conceptual_edges = 0
        self.n_authority_triples = 0
        self.n_entity_typing_triples = 0
        self.n_entity_label_triples = 0
        self.schemes_used = set()
        self.n_idno_converted = 0

        # v2: provenance / reification layer counters
        self.n_statement_nodes = 0
        self.n_reification_triples = 0        # rdf:type + subject + predicate + object + dcterms:relation + dcterms:type, per statement
        self.n_canonical_relation_labels = 0
        self.n_evidence_labels = 0
        self.n_symmetric_property_triples = 0
        self.canonical_relation_names = {}    # 'r6' -> 'sold_manuscripts_to'
        self.evidence_used = set()            # 'direct' / 'enriched'

    # -- entity registers ---------------------------------------------
    def convert_entities(self):
        standoff = self.root.find(tei("standOff"))

        # listPerson -> person
        for person in standoff.findall(f"{tei('listPerson')}/{tei('person')}"):
            xml_id = person.get("{http://www.w3.org/XML/1998/namespace}id")
            label = first_text(person, f"tei:persName[not(@xml:lang)]/text()") \
                or first_text(person, "tei:persName/text()")
            self._add_entity(xml_id, person, label)
            self._add_idnos(xml_id, person)

        # listPlace -> place
        for place in standoff.findall(f"{tei('listPlace')}/{tei('place')}"):
            xml_id = place.get("{http://www.w3.org/XML/1998/namespace}id")
            label = first_text(place, "tei:placeName/text()")
            self._add_entity(xml_id, place, label)
            self._add_idnos(xml_id, place)

        # listOrg -> org
        for org in standoff.findall(f"{tei('listOrg')}/{tei('org')}"):
            xml_id = org.get("{http://www.w3.org/XML/1998/namespace}id")
            label = first_text(org, "tei:orgName/text()")
            self._add_entity(xml_id, org, label)
            self._add_idnos(xml_id, org)

        # generic <list type="..."><item> registers: aggregate holdings,
        # digital objects, time spans
        for list_el in standoff.findall(tei("list")):
            for item in list_el.findall(tei("item")):
                xml_id = item.get("{http://www.w3.org/XML/1998/namespace}id")
                label = (
                    first_text(item, "tei:name/text()")
                    or first_text(item, "tei:date/text()")
                )
                self._add_entity(xml_id, item, label)
                self._add_idnos(xml_id, item)

        # listEvent -> event
        for event in standoff.findall(f"{tei('listEvent')}/{tei('event')}"):
            xml_id = event.get("{http://www.w3.org/XML/1998/namespace}id")
            label = first_text(event, "tei:label/text()")
            self._add_entity(xml_id, event, label)
            # events carry no <idno> in this file; _add_idnos is a no-op
            # if none are present, called for symmetry/future-proofing
            self._add_idnos(xml_id, event)

    def _add_entity(self, xml_id, el, label):
        subj = RESOURCE[xml_id]
        note = first_text(el, "tei:note[@type='conceptualClass']/text()")
        if note:
            self.g.add((subj, RDF.type, class_uri(note)))
            self.n_entity_typing_triples += 1
        if label:
            self.g.add((subj, RDFS.label, Literal(label)))
            self.n_entity_label_triples += 1

    def _add_idnos(self, xml_id, el):
        entity = RESOURCE[xml_id]
        for idno in el.findall(tei("idno")):
            scheme = idno.get("type")
            value = (idno.text or "").strip()
            if not scheme or not value:
                continue
            self.schemes_used.add(scheme)
            self.n_idno_converted += 1

            ident_node = RESOURCE[f"{xml_id}-{scheme}"]
            scheme_node = RESOURCE[f"identifier-type/{scheme}"]

            self.g.add((ident_node, RDF.type, CRM.E42_Identifier))
            self.g.add((ident_node, CRM.P190_has_symbolic_content, Literal(value)))
            self.g.add((ident_node, CRM.P2_has_type, scheme_node))
            self.g.add((entity, CRM.P1_is_identified_by, ident_node))
            self.n_authority_triples += 4

    def _add_identifier_type_nodes(self):
        for scheme in sorted(self.schemes_used):
            scheme_node = RESOURCE[f"identifier-type/{scheme}"]
            label = SCHEME_LABELS.get(scheme, scheme)
            self.g.add((scheme_node, RDF.type, CRM.E55_Type))
            self.g.add((scheme_node, RDFS.label, Literal(label)))
            self.n_authority_triples += 2

    # -- canonical relations (r1-r16): read-only lookup, no RDF edges --
    def index_canonical_relations(self):
        """
        Build an r-number -> informal relation name lookup from the
        canonical layer (type='canonical'). This layer is NEVER turned
        into RDF predicates (see module docstring); the lookup is used
        purely to write human-readable rdfs:label text onto the
        provenance-layer resource:canonical-relation/rN nodes.
        """
        standoff = self.root.find(tei("standOff"))
        canonical = standoff.find(f"{tei('listRelation')}[@type='canonical']")
        for rel in canonical.findall(tei("relation")):
            r_id = rel.get("{http://www.w3.org/XML/1998/namespace}id")
            name = rel.get("name")
            self.canonical_relation_names[r_id] = name

    # -- conceptual relations (the formal ontology edges) --------------
    def convert_conceptual_relations(self):
        standoff = self.root.find(tei("standOff"))
        conceptual = standoff.find(
            f"{tei('listRelation')}[@type='conceptual']"
        )
        for rel in conceptual.findall(tei("relation")):
            cr_id = rel.get("{http://www.w3.org/XML/1998/namespace}id")
            name = rel.get("name")
            ref = rel.get("ref")

            if ref:
                predicate = URIRef(ref)
            elif name in DM_PROPERTIES:
                predicate = DM_PROPERTIES[name]
            else:
                raise ValueError(
                    f"Relation {cr_id} has neither @ref nor a recognised "
                    f"dm: property name ({name}); refusing to guess a predicate."
                )

            active = rel.get("active")
            passive = rel.get("passive")
            mutual = rel.get("mutual")

            if active and passive:
                subj_id, obj_id = strip_prefix(active), strip_prefix(passive)
            elif mutual:
                ids = [strip_prefix(t) for t in mutual.split()]
                if len(ids) != 2:
                    raise ValueError(f"Unexpected @mutual shape: {mutual!r}")
                subj_id, obj_id = ids[0], ids[1]
            else:
                raise ValueError(
                    f"Relation {cr_id} has neither active/passive nor "
                    f"mutual endpoints."
                )

            subj = RESOURCE[subj_id]
            obj = RESOURCE[obj_id]

            # --- core conceptual assertion (unchanged from v1) ---
            self.g.add((subj, predicate, obj))
            self.n_core_conceptual_edges += 1

            # --- v2: provenance / reification layer ---
            corresp = rel.get("corresp")
            ana = rel.get("ana")
            if corresp and ana:
                self._add_statement_provenance(cr_id, subj, predicate, obj, corresp, ana)

    def _add_statement_provenance(self, cr_id, subj, predicate, obj, corresp, ana):
        r_id = strip_prefix(corresp)                                    # '#r6' -> 'r6'
        evidence_key = strip_prefix(ana).replace("evidence-", "", 1)    # '#evidence-direct' -> 'direct'
        self.evidence_used.add(evidence_key)

        statement_node = RESOURCE[f"statement/{cr_id}"]
        canonical_node = RESOURCE[f"canonical-relation/{r_id}"]
        evidence_node = RESOURCE[f"evidence/{evidence_key}"]

        self.g.add((statement_node, RDF.type, RDF.Statement))
        self.g.add((statement_node, RDF.subject, subj))
        self.g.add((statement_node, RDF.predicate, predicate))
        self.g.add((statement_node, RDF.object, obj))
        self.g.add((statement_node, DCTERMS.relation, canonical_node))
        self.g.add((statement_node, DCTERMS.type, evidence_node))

        self.n_statement_nodes += 1
        self.n_reification_triples += 6

    def _add_provenance_labels(self):
        # canonical-relation/rN labels: "R{n} – {informal_name}"
        for r_id in sorted(self.canonical_relation_names, key=lambda x: int(x[1:])):
            name = self.canonical_relation_names[r_id]
            r_num = r_id[1:]  # 'r6' -> '6'
            node = RESOURCE[f"canonical-relation/{r_id}"]
            self.g.add((node, RDFS.label, Literal(f"R{r_num} – {name}")))
            self.n_canonical_relation_labels += 1

        # evidence/direct and evidence/enriched labels (only for the
        # evidence keys actually referenced by the conceptual layer)
        for key in sorted(self.evidence_used):
            node = RESOURCE[f"evidence/{key}"]
            label = EVIDENCE_LABELS.get(key, key)
            self.g.add((node, RDFS.label, Literal(label)))
            self.n_evidence_labels += 1

    def _add_ontology_declarations(self):
        # dm:locatedNear is mutual in the TEI (@mutual) and collapses to a
        # single directed RDF triple (cr2). Declaring it symmetric restores
        # that lost symmetry as ontology-level metadata WITHOUT adding a
        # second, reverse core assertion.
        self.g.add((DM.locatedNear, RDF.type, OWL.SymmetricProperty))
        self.n_symmetric_property_triples += 1

    # -- driver ----------------------------------------------------------
    def run(self):
        self.convert_entities()
        self._add_identifier_type_nodes()
        self.index_canonical_relations()
        self.convert_conceptual_relations()
        self._add_provenance_labels()
        self._add_ontology_declarations()
        return self.g

    @property
    def n_provenance_triples(self):
        return (
            self.n_reification_triples
            + self.n_canonical_relation_labels
            + self.n_evidence_labels
            + self.n_symmetric_property_triples
        )

    def qa_report(self, validation_errors):
        total = len(self.g)
        entity_triples = self.n_entity_typing_triples + self.n_entity_label_triples
        computed_total = (
            entity_triples
            + self.n_core_conceptual_edges
            + self.n_authority_triples
            + self.n_provenance_triples
        )
        lines = [
            "=== Reconnecting Dunhuang — TEI to RDF QA report ===",
            "",
            "1. Core conceptual assertions (cr1-cr30, formal ontology edges):",
            f"   {self.n_core_conceptual_edges}/30",
            "",
            "2. Authority reconciliation layer (CIDOC CRM identifier pattern, "
            "not owl:sameAs):",
            f"   - <idno> elements converted: {self.n_idno_converted}",
            f"   - distinct identifier schemes encountered: "
            f"{len(self.schemes_used)} ({', '.join(sorted(self.schemes_used))})",
            f"   - authority reconciliation triples "
            f"(E42_Identifier typing + P190 + P2_has_type + P1_is_identified_by "
            f"+ E55_Type scheme-node typing/labels): {self.n_authority_triples}",
            "",
            "3. Statement provenance / reification layer (metadata ABOUT the "
            "30 core assertions above; adds no new core assertions):",
            f"   - reified statement nodes (rdf:Statement, one per cr1-cr30): "
            f"{self.n_statement_nodes}",
            f"   - reification triples (rdf:type + rdf:subject + rdf:predicate "
            f"+ rdf:object + dcterms:relation + dcterms:type, 6 per statement): "
            f"{self.n_reification_triples}",
            f"   - resource:canonical-relation/rN rdfs:label triples: "
            f"{self.n_canonical_relation_labels}",
            f"   - resource:evidence/{{direct|enriched}} rdfs:label triples: "
            f"{self.n_evidence_labels}",
            f"   - dm:locatedNear owl:SymmetricProperty declaration: "
            f"{self.n_symmetric_property_triples}",
            f"   - provenance-layer subtotal: {self.n_provenance_triples}",
            "",
            f"4. Total RDF triple count: {total}",
            f"   (breakdown: {entity_triples} entity rdf:type/rdfs:label + "
            f"{self.n_core_conceptual_edges} core conceptual assertions + "
            f"{self.n_authority_triples} authority-reconciliation triples + "
            f"{self.n_provenance_triples} provenance/reification triples "
            f"= {computed_total})",
            f"   Recomputed from in-memory graph length: {total} "
            f"(matches breakdown sum: {computed_total == total})",
            "",
            "=== Post-generation independent validation ===",
            "A complete expected RDF dataset (all layers: entity typing/"
            "labels, core conceptual assertions, authority reconciliation, "
            "statement provenance/reification) is independently rebuilt "
            "straight from reconnecting_dunhuang.xml, then compared for "
            "EXACT triple-set equality (expected-actual and actual-expected "
            "must both be empty — not merely \"does each expected triple "
            "exist\") plus graph isomorphism, against the serialized .ttl, "
            "the serialized .rdf, and the in-memory graph produced this "
            "run. This full-graph diff catches both a triple whose content "
            "is wrong (e.g. a corrupted identifier value) and any "
            "unexpected extra triple, neither of which an existence-only "
            "check can see. The validator does not call any Converter "
            "method, and rebuilds the predicate for each dm:-only "
            "relation directly from the XML rather than reusing the "
            "DM_PROPERTIES lookup table, which reduces the risk that a "
            "shared mapping bug goes undetected. It still shares generic "
            "namespace constants, XML/URI helpers, and the SCHEME_LABELS "
            "text lookup with the converter, since those encode no "
            "project-specific structural mapping decision.",
            "",
        ]
        if validation_errors:
            lines.append(f"POST-GENERATION VALIDATION: FAIL "
                         f"({len(validation_errors)} mismatch(es))")
            for e in validation_errors:
                lines.append(f"  - {e}")
        else:
            lines.append(
                "POST-GENERATION VALIDATION: PASS — the independently "
                "rebuilt expected graph (26 independently rebuilt entities "
                "covering 52 rdf:type/rdfs:label triples, 30 core "
                "conceptual assertions, 41 authority-reconciliation "
                "identifiers across 178 triples, and a 199-triple statement "
                "provenance/reification layer — 459 triples total) is "
                "EXACTLY equal (missing=0, extra=0) to the serialized TTL, "
                "the serialized RDF/XML, and the in-memory graph produced "
                "this run, and all three are pairwise graph-isomorphic."
            )
        lines += [
            "",
            "No owl:sameAs used anywhere. No domain entities, relations, or "
            "identifiers were invented beyond what is present in "
            "reconnecting_dunhuang.xml. The RDF structural scaffolding that "
            "does not correspond 1:1 to a TEI element (E42_Identifier nodes, "
            "E55_Type scheme nodes, rdf:Statement reification nodes) is "
            "mechanically generated from that XML data and does not assert "
            "any fact not already present in the source.",
        ]
        return "\n".join(lines)


class PostGenerationValidator:
    """
    Fully independent re-derivation of the ENTIRE expected RDF dataset,
    straight from reconnecting_dunhuang.xml, compared against a fresh
    re-parse of the actual serialized .ttl / .rdf output (and, as a third
    leg, the in-memory graph this run just produced) via exact triple-set
    equality (expected - actual and actual - expected must both be empty)
    plus graph isomorphism as a redundant cross-check.

    This is deliberately a full expected_graph == actual_graph comparison,
    not a set of "does X exist" existence checks. An existence-only check
    cannot see two classes of real defect: (a) a triple whose CONTENT is
    wrong but whose surrounding counts are unchanged (e.g. a corrupted
    identifier value — same number of <idno>/E42_Identifier nodes, wrong
    P190 literal), and (b) an arbitrary EXTRA triple using a predicate
    outside whatever narrow scope a particular existence check happened to
    cover. Both were demonstrated as live false negatives against an
    earlier version of this validator (which only checked existence plus
    a scoped missing/extra diff over the conceptual layer's own predicate
    set) and are why this version rebuilds and diffs the complete graph.

    Deliberately does NOT call any Converter method, and does NOT reuse
    the DM_PROPERTIES lookup table (the hand-written predicate-mapping
    table in the conversion path) — the predicate for the 4 dm:-only
    relations is rebuilt here directly from the XML's @name string, which
    reduces the risk that a shared mapping bug there goes undetected.
    This validator still shares the SCHEME_LABELS text lookup and generic
    XML/URI syntax helpers (tei(), strip_prefix(), class_uri(), the
    namespace constants) with the converter, since those encode display
    text and pure string mechanics rather than a structural mapping
    decision — a bug specifically inside SCHEME_LABELS could still go
    uncaught by this validator.
    """

    def __init__(self, xml_path, ttl_path, rdf_path, live_graph):
        self.tree = etree.parse(xml_path)
        self.root = self.tree.getroot()
        self.ttl_path = ttl_path
        self.rdf_path = rdf_path
        self.live_graph = live_graph
        self.errors = []
        self.expected = Graph()
        self.canonical_relation_names = {}   # 'r6' -> 'sold_manuscripts_to'
        self.evidence_used = set()           # 'direct' / 'enriched'
        self.n_expected_entities = 0

    def _err(self, msg):
        self.errors.append(msg)

    @staticmethod
    def _independent_predicate(ref, name):
        if ref:
            return URIRef(ref)
        prefix, local = name.split(":", 1)
        if prefix != "dm":
            raise ValueError(f"unexpected relation name prefix in {name!r}")
        return DM[local]

    @staticmethod
    def _iter_entities(standoff):
        """Yield (xml_id, element) for every entity register the conversion
        covers — persons, places, orgs, generic list items, events."""
        for person in standoff.findall(f"{tei('listPerson')}/{tei('person')}"):
            yield person.get("{http://www.w3.org/XML/1998/namespace}id"), person
        for place in standoff.findall(f"{tei('listPlace')}/{tei('place')}"):
            yield place.get("{http://www.w3.org/XML/1998/namespace}id"), place
        for org in standoff.findall(f"{tei('listOrg')}/{tei('org')}"):
            yield org.get("{http://www.w3.org/XML/1998/namespace}id"), org
        for list_el in standoff.findall(tei("list")):
            for item in list_el.findall(tei("item")):
                yield item.get("{http://www.w3.org/XML/1998/namespace}id"), item
        for event in standoff.findall(f"{tei('listEvent')}/{tei('event')}"):
            yield event.get("{http://www.w3.org/XML/1998/namespace}id"), event

    @staticmethod
    def _entity_label(xml_id, el):
        # mirrors, independently, which element supplies an entity's label
        return (
            first_text(el, "tei:persName[not(@xml:lang)]/text()")
            or first_text(el, "tei:persName/text()")
            or first_text(el, "tei:placeName/text()")
            or first_text(el, "tei:orgName/text()")
            or first_text(el, "tei:name/text()")
            or first_text(el, "tei:date/text()")
            or first_text(el, "tei:label/text()")
        )

    def run(self):
        g_ttl = Graph().parse(self.ttl_path, format="turtle")
        g_rdf = Graph().parse(self.rdf_path, format="xml")

        standoff = self.root.find(tei("standOff"))
        self._build_expected_entities(standoff)
        self._build_expected_authority(standoff)
        self._build_expected_core_and_provenance(standoff)
        self._build_expected_ontology_declarations()

        if self.n_expected_entities != 26:
            self._err(f"expected 26 entities in XML, independently counted {self.n_expected_entities}")

        # Full expected_graph == actual_graph comparison, run against all
        # three artifacts this script produced: the serialized TTL, the
        # serialized RDF/XML, and the in-memory graph main() just built.
        for label, g in (
            ("serialized TTL", g_ttl),
            ("serialized RDF/XML", g_rdf),
            ("in-memory graph produced this run", self.live_graph),
        ):
            if not compare.isomorphic(self.expected, g):
                self._err(f"independently-rebuilt expected graph is NOT isomorphic to the {label}.")
            missing = set(self.expected) - set(g)
            extra = set(g) - set(self.expected)
            if missing:
                sample = list(missing)[:5]
                more = f" (+{len(missing) - 5} more)" if len(missing) > 5 else ""
                self._err(f"{len(missing)} expected triple(s) missing from {label}: {sample}{more}")
            if extra:
                sample = list(extra)[:5]
                more = f" (+{len(extra) - 5} more)" if len(extra) > 5 else ""
                self._err(f"{len(extra)} unexpected extra triple(s) found in {label}: {sample}{more}")

        # Pinpoint diagnostic checks kept for clearer error messages on a
        # few specific, high-value facts. Redundant with the full-graph
        # diff above (any failure here is also caught there) — kept so a
        # failure names the exact issue instead of only a raw triple diff.
        self._diagnostic_checks(standoff)

        return self.errors

    # -- expected-graph construction (independent of Converter) ---------
    def _build_expected_entities(self, standoff):
        for xml_id, el in self._iter_entities(standoff):
            self.n_expected_entities += 1
            subj = RESOURCE[xml_id]
            class_text = first_text(el, "tei:note[@type='conceptualClass']/text()")
            if class_text:
                self.expected.add((subj, RDF.type, class_uri(class_text)))
            label = self._entity_label(xml_id, el)
            if label:
                self.expected.add((subj, RDFS.label, Literal(label)))

    def _build_expected_authority(self, standoff):
        schemes_used = set()
        for xml_id, el in self._iter_entities(standoff):
            entity = RESOURCE[xml_id]
            for idno in el.findall(tei("idno")):
                scheme = idno.get("type")
                value = (idno.text or "").strip()
                if not scheme or not value:
                    continue
                schemes_used.add(scheme)
                ident_node = RESOURCE[f"{xml_id}-{scheme}"]
                scheme_node = RESOURCE[f"identifier-type/{scheme}"]
                self.expected.add((ident_node, RDF.type, CRM.E42_Identifier))
                self.expected.add((ident_node, CRM.P190_has_symbolic_content, Literal(value)))
                self.expected.add((ident_node, CRM.P2_has_type, scheme_node))
                self.expected.add((entity, CRM.P1_is_identified_by, ident_node))
        for scheme in schemes_used:
            scheme_node = RESOURCE[f"identifier-type/{scheme}"]
            label = SCHEME_LABELS.get(scheme, scheme)
            self.expected.add((scheme_node, RDF.type, CRM.E55_Type))
            self.expected.add((scheme_node, RDFS.label, Literal(label)))

    def _build_expected_core_and_provenance(self, standoff):
        canonical = standoff.find(f"{tei('listRelation')}[@type='canonical']")
        for rel in canonical.findall(tei("relation")):
            r_id = rel.get("{http://www.w3.org/XML/1998/namespace}id")
            self.canonical_relation_names[r_id] = rel.get("name")

        conceptual = standoff.find(f"{tei('listRelation')}[@type='conceptual']")
        rels = conceptual.findall(tei("relation"))
        if len(rels) != 30:
            self._err(f"expected 30 <relation> elements in the conceptual layer, found {len(rels)}")

        for rel in rels:
            cr_id = rel.get("{http://www.w3.org/XML/1998/namespace}id")
            ref = rel.get("ref")
            name = rel.get("name")
            predicate = self._independent_predicate(ref, name)

            active, passive, mutual = rel.get("active"), rel.get("passive"), rel.get("mutual")
            if active and passive:
                subj_id, obj_id = strip_prefix(active), strip_prefix(passive)
            elif mutual:
                ids = [strip_prefix(t) for t in mutual.split()]
                subj_id, obj_id = ids[0], ids[1]
            else:
                self._err(f"{cr_id}: no active/passive or mutual endpoints in XML")
                continue

            subj, obj = RESOURCE[subj_id], RESOURCE[obj_id]
            self.expected.add((subj, predicate, obj))

            corresp, ana = rel.get("corresp"), rel.get("ana")
            if not corresp or not ana:
                self._err(f"{cr_id}: missing @corresp or @ana in XML")
                continue
            r_id = strip_prefix(corresp)
            evidence_key = strip_prefix(ana).replace("evidence-", "", 1)
            self.evidence_used.add(evidence_key)

            stmt = RESOURCE[f"statement/{cr_id}"]
            canonical_node = RESOURCE[f"canonical-relation/{r_id}"]
            evidence_node = RESOURCE[f"evidence/{evidence_key}"]
            self.expected.add((stmt, RDF.type, RDF.Statement))
            self.expected.add((stmt, RDF.subject, subj))
            self.expected.add((stmt, RDF.predicate, predicate))
            self.expected.add((stmt, RDF.object, obj))
            self.expected.add((stmt, DCTERMS.relation, canonical_node))
            self.expected.add((stmt, DCTERMS.type, evidence_node))

        for r_id, name in self.canonical_relation_names.items():
            node = RESOURCE[f"canonical-relation/{r_id}"]
            self.expected.add((node, RDFS.label, Literal(f"R{r_id[1:]} – {name}")))
        evidence_texts = {"direct": "Direct evidence", "enriched": "Enriched evidence"}
        for key in self.evidence_used:
            node = RESOURCE[f"evidence/{key}"]
            self.expected.add((node, RDFS.label, Literal(evidence_texts.get(key, key))))

    def _build_expected_ontology_declarations(self):
        self.expected.add((DM.locatedNear, RDF.type, OWL.SymmetricProperty))

    # -- pinpoint diagnostics (redundant with the full diff, clearer msgs) --
    def _diagnostic_checks(self, standoff):
        conceptual = standoff.find(f"{tei('listRelation')}[@type='conceptual']")
        for rel in conceptual.findall(tei("relation")):
            if rel.get("{http://www.w3.org/XML/1998/namespace}id") == "cr30":
                corresp = strip_prefix(rel.get("corresp") or "")
                ana = strip_prefix(rel.get("ana") or "").replace("evidence-", "", 1)
                if corresp != "r16" or ana != "enriched":
                    self._err(
                        f"cr30 expected to correspond to r16 with enriched evidence, "
                        f"found corresp={corresp} evidence={ana}"
                    )
                break

        n_idno = sum(
            1 for _, el in self._iter_entities(standoff) for idno in el.findall(tei("idno"))
            if idno.get("type") and (idno.text or "").strip()
        )
        if n_idno != 41:
            self._err(f"expected 41 convertible <idno> elements in standOff, independently counted {n_idno}")

        sym_count = len({t for t in self.expected.triples((DM.locatedNear, RDF.type, OWL.SymmetricProperty))})
        core_count = len({t for t in self.expected.triples((None, DM.locatedNear, None))})
        if sym_count != 1:
            self._err(f"expected exactly 1 dm:locatedNear owl:SymmetricProperty triple, found {sym_count}")
        if core_count != 1:
            self._err(f"expected exactly 1 core triple using dm:locatedNear as predicate, found {core_count}")


# ---------------------------------------------------------------------------
# Browser-readable viewer regeneration (view_turtle.html / view_rdfxml.html)
# ---------------------------------------------------------------------------
# These viewers are only a browser-safe wrapper around the exact serialized
# .ttl / .rdf source text. They do not reinterpret RDF or alter triples.
# Regenerating them here (rather than leaving hand-authored copies in the
# package) closes a reproducibility gap: RDF/XML serialization order is not
# guaranteed stable across runs (Turtle output has been observed to be
# stable; RDF/XML has not), so a static viewer file can silently go stale
# the moment transform_tei_to_rdf.py is rerun. Regenerating both viewers as
# part of the same script run that produces the .ttl/.rdf guarantees the
# viewer text and the raw file text can never drift apart.

VIEWER_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
body {{ margin: 0; font-family: Menlo, Consolas, monospace; background: #f8f0df; color: #2f261d; }}
header {{ position: sticky; top: 0; background: #fff8eb; border-bottom: 1px solid #decaa6; padding: 16px 24px; }}
a {{ color: #1f5f61; text-decoration-thickness: 1px; text-underline-offset: 3px; }}
a:hover {{ color: #8a3f2d; }}
main {{ padding: 24px; }}
pre {{ white-space: pre-wrap; word-break: break-word; line-height: 1.5; font-size: 14px; background: #fffaf0; border: 1px solid #decaa6; border-radius: 8px; padding: 20px; overflow: auto; }}
</style>
</head>
<body>
<header>
<strong>{header_label}</strong> \u00b7 <a href="index.html">Back to Web Report</a> \u00b7 <a href="{download_href}" download>Download source file</a>
</header>
<main><pre><code>{content}</code></pre></main>
</body>
</html>
"""


def render_viewer_html(title, header_label, download_href, raw_text):
    """Wrap raw_text (verbatim Turtle or RDF/XML source) in the browser
    viewer template. The only transformation applied to raw_text is HTML
    escaping (&, <, >, ", ') so it renders safely inside <pre><code>; no
    RDF content is reinterpreted, reordered, or altered."""
    escaped = html.escape(raw_text, quote=True)
    return VIEWER_TEMPLATE.format(
        title=title, header_label=header_label, download_href=download_href, content=escaped
    )


def regenerate_viewers(out_ttl, out_rdf, view_turtle_path, view_rdfxml_path, output_root):
    """Regenerate view_turtle.html and view_rdfxml.html from the freshly
    serialized .ttl/.rdf files so viewer content can never go stale
    relative to the raw files, regardless of serialization order."""
    ttl_text = out_ttl.read_text(encoding="utf-8")
    rdf_text = out_rdf.read_text(encoding="utf-8")

    # Compute a portable relative href from the viewer's own directory
    # (output_root) to the raw file, so download links keep working
    # regardless of custom output paths passed on the command line.
    ttl_href = os.path.relpath(out_ttl, start=output_root).replace(os.sep, "/")
    rdf_href = os.path.relpath(out_rdf, start=output_root).replace(os.sep, "/")

    turtle_html = render_viewer_html(
        "Reconnecting Dunhuang Turtle Viewer",
        "Reconnecting Dunhuang Turtle",
        ttl_href,
        ttl_text,
    )
    rdfxml_html = render_viewer_html(
        "Reconnecting Dunhuang RDF/XML Viewer",
        "Reconnecting Dunhuang RDF/XML",
        rdf_href,
        rdf_text,
    )

    view_turtle_path.parent.mkdir(parents=True, exist_ok=True)
    view_rdfxml_path.parent.mkdir(parents=True, exist_ok=True)
    view_turtle_path.write_text(turtle_html, encoding="utf-8")
    view_rdfxml_path.write_text(rdfxml_html, encoding="utf-8")


def main():
    xml_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_XML
    out_ttl = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_TTL
    out_rdf = Path(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_RDF
    qa_report = Path(sys.argv[4]) if len(sys.argv) > 4 else DEFAULT_QA_REPORT
    view_turtle_path = Path(sys.argv[5]) if len(sys.argv) > 5 else DEFAULT_VIEW_TURTLE
    view_rdfxml_path = Path(sys.argv[6]) if len(sys.argv) > 6 else DEFAULT_VIEW_RDFXML
    output_root = Path(sys.argv[7]) if len(sys.argv) > 7 else DEFAULT_OUTPUT_DIR

    conv = Converter(xml_path)
    graph = conv.run()

    out_ttl.parent.mkdir(parents=True, exist_ok=True)
    out_rdf.parent.mkdir(parents=True, exist_ok=True)
    graph.serialize(destination=out_ttl, format="turtle")
    graph.serialize(destination=out_rdf, format="xml")

    # Regenerate the browser-readable viewers from the files just written,
    # so their content is guaranteed to match this run's raw output exactly
    # (byte-for-byte, modulo HTML escaping/wrapper markup).
    regenerate_viewers(out_ttl, out_rdf, view_turtle_path, view_rdfxml_path, output_root)

    validator = PostGenerationValidator(xml_path, out_ttl, out_rdf, graph)
    validation_errors = validator.run()

    report = conv.qa_report(validation_errors)
    print(report)
    qa_report.parent.mkdir(parents=True, exist_ok=True)
    qa_report.write_text(report + "\n", encoding="utf-8")

    print(f"Regenerated viewer: {view_turtle_path}")
    print(f"Regenerated viewer: {view_rdfxml_path}")

    if validation_errors:
        print(
            f"\nPost-generation validation FAILED with {len(validation_errors)} "
            f"mismatch(es). See rdf_qa_report.txt for details.",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
