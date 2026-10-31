#!/usr/bin/env python3
"""
Reconnecting Dunhuang - TEI/XML to RDF transformation (v3.1, review round 1: language-tagged labels).

Input : tei_xml/reconnecting_dunhuang.xml   (the single source for everything below)
        ontology/dm-ontology.ttl            (definitions of the three dm: properties)
Output: reconnecting_dunhuang.ttl / .rdf    (the same graph in Turtle and RDF/XML)
        rdf_qa_report.txt                   (counts + validation results)

What the script does, in order
  1. read_entities()      every standOff record that has <note type="conceptualClass">
                          becomes one resource with rdf:type and rdfs:label (@en); name elements
                          with @xml:lang (zh, ja) become further rdfs:label in that language.
  2. add_concepts()       the project taxonomy "concepts" becomes a skos:ConceptScheme;
                          <equiv @uri> becomes skos:exactMatch.
  3. add_identifiers()    every <idno> becomes a crm:E42_Identifier node (CIDOC CRM pattern)
                          and, where the scheme has a URI form, an external link chosen by
                          the authority linking policy (owl:sameAs only for actors on Wikidata).
  4. add_time_bounds()    <date @when/@notBefore/@notAfter> on time-span records becomes
                          crm:P82a_begin_of_the_begin / crm:P82b_end_of_the_end (xsd:dateTime).
  5. add_relations()      listRelation[@type='conceptual'] -> one triple per <relation>
                          listRelation[@type='subject']    -> dcterms:subject triples
  6. add_provenance()     each conceptual relation also gets an rdf:Statement node recording
                          which theoretical relation (R1-R19) it comes from and its evidence
                          status (Direct / Enriched). This layer is kept for traceability only.
                          R1-R19 are typed crm:E89_Propositional_Object: propositions of the
                          theoretical model, not RDF triples (an rdf:Statement restates one
                          triple; several statements can refer to the same proposition).
                          The TEI taxonomy "evidence" becomes a second skos:ConceptScheme whose
                          two concepts carry their TEI catDesc as skos:definition.
     Enriched relations carry relation/@source -> listBibl "enrichment-sources"; each pointer
                          becomes dcterms:source (the bibl's URL) on the rdf:Statement.
  7. validate()           reference integrity, CIDOC CRM domain/range, dm: declarations,
                          round-trip of both serializations, presence of every TEI relation.

Nothing is invented: every value in the graph comes from an attribute or element of the TEI
file, or from the fixed tables below (namespaces, link policy, class/property signatures).
"""

import sys
from datetime import date
from pathlib import Path

from lxml import etree
from rdflib import Graph, Literal, Namespace, URIRef, RDF, RDFS, OWL, compare
from rdflib.namespace import DCTERMS, SKOS, XSD

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
REPORT_FILES = SCRIPT_DIR.parent
DEFAULT_XML = REPORT_FILES / "tei_xml" / "reconnecting_dunhuang.xml"
DEFAULT_ONTOLOGY = REPORT_FILES / "ontology" / "dm-ontology.ttl"
DEFAULT_TTL = SCRIPT_DIR / "reconnecting_dunhuang.ttl"
DEFAULT_RDF = SCRIPT_DIR / "reconnecting_dunhuang.rdf"
DEFAULT_QA = SCRIPT_DIR / "rdf_qa_report.txt"

# ---------------------------------------------------------------------------
# Namespaces
# ---------------------------------------------------------------------------
BASE = "https://haopuur-max.github.io/reconnecting-dunhuang/"
DM = Namespace(BASE + "ontology/")
RES = Namespace(BASE + "resource/")
CRM = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
CRMSCI = Namespace("http://www.cidoc-crm.org/extensions/crmsci/")
CRMDIG = Namespace("http://www.cidoc-crm.org/extensions/crmdig/")
PREFIXES = {"crm": CRM, "crmsci": CRMSCI, "crmdig": CRMDIG, "dm": DM,
            "dcterms": DCTERMS, "skos": SKOS}

TEI = "http://www.tei-c.org/ns/1.0"
NS = {"tei": TEI}
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"

# ---------------------------------------------------------------------------
# Authority linking policy
#   All identifiers are always kept as crm:E42_Identifier nodes (no identity claim).
#   In addition, an external link is added when the scheme has a URI form:
#     - owl:sameAs  only for Wikidata items of actors (persons and groups, institutions included),
#                   where the Wikidata item and our resource denote the same individual;
#     - rdfs:seeAlso for everything else: authority records (VIAF clusters, LC name
#                   authorities), subject headings (LCSH, FAST), and Wikidata items of
#                   places and of the corpus, whose Wikidata class differs from our
#                   CIDOC CRM class (e.g. E53 Place is a spatial extent, not a city).
#   FAST control numbers have no URI form and stay as identifiers only.
#   Concepts use skos:exactMatch (see add_concepts).
# ---------------------------------------------------------------------------
AUTHORITY_URI = {
    "wikidata": "http://www.wikidata.org/entity/{}",
    "viaf": "http://viaf.org/viaf/{}",
    "lc": "http://id.loc.gov/authorities/names/{}",
    "lcsh": "http://id.loc.gov/authorities/subjects/{}",
    "fast": "http://id.worldcat.org/fast/{}",
    "worldcat-entity": "https://id.oclc.org/worldcat/entity/{}",
}
SCHEME_LABELS = {
    "wikidata": "Wikidata",
    "viaf": "VIAF",
    "lc": "Library of Congress Name Authority File",
    "lcsh": "Library of Congress Subject Headings",
    "fast": "FAST (OCLC)",
    "fast-control-number": "FAST control number (OCLC)",
    "worldcat-entity": "WorldCat Entity",
    "bl-shelfmark": "British Library shelfmark",
}

# ---------------------------------------------------------------------------
# Class hierarchy and property signatures used for the domain/range check.
# Transcribed from CIDOC CRM 7.1.3, CRMsci 3.2 (O19 range E18; S19 < S27 < I1),
# CRMinf 1.2.1 (I1 < E7) and CRMdig 5.0 (L1 D2 -> E18; L11 D7 -> D1; D7 < E11, E65).
# Only the classes and properties this dataset uses are listed; anything else
# is reported so the table cannot silently fall behind the data.
# ---------------------------------------------------------------------------
SUPERCLASSES = {
    "crm:E1_CRM_Entity": [],
    "crm:E77_Persistent_Item": ["crm:E1_CRM_Entity"],
    "crm:E70_Thing": ["crm:E77_Persistent_Item"],
    "crm:E72_Legal_Object": ["crm:E70_Thing"],
    "crm:E71_Human-Made_Thing": ["crm:E70_Thing"],
    "crm:E18_Physical_Thing": ["crm:E72_Legal_Object"],
    "crm:E19_Physical_Object": ["crm:E18_Physical_Thing"],
    "crm:E24_Physical_Human-Made_Thing": ["crm:E18_Physical_Thing", "crm:E71_Human-Made_Thing"],
    "crm:E78_Curated_Holding": ["crm:E24_Physical_Human-Made_Thing"],
    "crm:E20_Biological_Object": ["crm:E19_Physical_Object"],
    "crm:E39_Actor": ["crm:E77_Persistent_Item"],
    "crm:E21_Person": ["crm:E20_Biological_Object", "crm:E39_Actor"],
    "crm:E74_Group": ["crm:E39_Actor"],
    "crm:E53_Place": ["crm:E1_CRM_Entity"],
    "crm:E52_Time-Span": ["crm:E1_CRM_Entity"],
    "crm:E2_Temporal_Entity": ["crm:E1_CRM_Entity"],
    "crm:E92_Spacetime_Volume": ["crm:E1_CRM_Entity"],
    "crm:E4_Period": ["crm:E2_Temporal_Entity", "crm:E92_Spacetime_Volume"],
    "crm:E5_Event": ["crm:E4_Period"],
    "crm:E7_Activity": ["crm:E5_Event"],
    "crm:E8_Acquisition": ["crm:E7_Activity"],
    "crm:E96_Purchase": ["crm:E8_Acquisition"],
    "crm:E9_Move": ["crm:E7_Activity"],
    "crm:E63_Beginning_of_Existence": ["crm:E5_Event"],
    "crm:E65_Creation": ["crm:E7_Activity", "crm:E63_Beginning_of_Existence"],
    "crm:E28_Conceptual_Object": ["crm:E71_Human-Made_Thing"],
    "crm:E89_Propositional_Object": ["crm:E28_Conceptual_Object"],
    "crm:E90_Symbolic_Object": ["crm:E28_Conceptual_Object", "crm:E72_Legal_Object"],
    "crm:E73_Information_Object": ["crm:E89_Propositional_Object", "crm:E90_Symbolic_Object"],
    "crminf:I1_Argumentation": ["crm:E7_Activity"],
    "crmsci:S27_Observation": ["crminf:I1_Argumentation"],
    "crmsci:S19_Encounter_Event": ["crmsci:S27_Observation"],
    "crm:E11_Modification": ["crm:E7_Activity"],
    "crmsci:S21_Measurement": ["crmsci:S27_Observation"],
    "crmdig:D7_Digital_Machine_Event": ["crm:E11_Modification", "crm:E65_Creation"],
    "crmdig:D11_Digital_Measurement_Event": ["crmdig:D7_Digital_Machine_Event", "crmsci:S21_Measurement"],
    "crmdig:D2_Digitization_Process": ["crmdig:D11_Digital_Measurement_Event"],
    "crmdig:D1_Digital_Object": ["crm:E73_Information_Object"],
}
SIGNATURES = {  # property -> (domain, range)
    "crm:P4_has_time-span": ("crm:E2_Temporal_Entity", "crm:E52_Time-Span"),
    "crm:P7_took_place_at": ("crm:E4_Period", "crm:E53_Place"),
    "crm:P12_occurred_in_the_presence_of": ("crm:E5_Event", "crm:E77_Persistent_Item"),
    "crm:P14_carried_out_by": ("crm:E7_Activity", "crm:E39_Actor"),
    "crm:P15_was_influenced_by": ("crm:E7_Activity", "crm:E1_CRM_Entity"),
    "crm:P22_transferred_title_to": ("crm:E8_Acquisition", "crm:E39_Actor"),
    "crm:P23_transferred_title_from": ("crm:E8_Acquisition", "crm:E39_Actor"),
    "crm:P24_transferred_title_of": ("crm:E8_Acquisition", "crm:E18_Physical_Thing"),
    "crm:P25_moved": ("crm:E9_Move", "crm:E19_Physical_Object"),
    "crm:P26_moved_to": ("crm:E9_Move", "crm:E53_Place"),
    "crm:P46i_forms_part_of": ("crm:E18_Physical_Thing", "crm:E18_Physical_Thing"),
    "crm:P50_has_current_keeper": ("crm:E18_Physical_Thing", "crm:E39_Actor"),
    "crm:P89_falls_within": ("crm:E53_Place", "crm:E53_Place"),
    "crmsci:O19_encountered_object": ("crmsci:S19_Encounter_Event", "crm:E18_Physical_Thing"),
    "crmdig:L1_digitized": ("crmdig:D2_Digitization_Process", "crm:E18_Physical_Thing"),
    "crmdig:L11_had_output": ("crmdig:D7_Digital_Machine_Event", "crmdig:D1_Digital_Object"),
}

EVIDENCE_LABELS = {"direct": "Direct evidence (frozen Wikipedia revision)",
                   "enriched": "Enriched evidence (additional authoritative source)"}


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------
def curie_to_uri(curie):
    """'crm:E21_Person' -> URIRef"""
    prefix, local = curie.split(":", 1)
    return PREFIXES[prefix][local]


def uri_to_curie(uri):
    for prefix, ns in PREFIXES.items():
        if str(uri).startswith(str(ns)):
            return f"{prefix}:{str(uri)[len(str(ns)):]}"
    return str(uri)


def local_id(ref):
    """'#aurel-stein' -> 'aurel-stein'"""
    return ref[1:] if ref.startswith("#") else ref


def ancestors(cls):
    """cls and all its superclasses (transitively)."""
    seen, todo = set(), [cls]
    while todo:
        c = todo.pop()
        if c not in seen:
            seen.add(c)
            todo.extend(SUPERCLASSES.get(c, []))
    return seen


def is_a(cls, target):
    return target in ancestors(cls)


def date_bound(value, end):
    """TEI date value ('1907' or '1900-06-25') -> xsd:dateTime literal for P82a/P82b."""
    parts = value.split("-")
    if len(parts) == 1:
        year = int(parts[0])
        text = f"{year:04d}-12-31T23:59:59" if end else f"{year:04d}-01-01T00:00:00"
    elif len(parts) == 3:
        text = f"{value}T23:59:59" if end else f"{value}T00:00:00"
    else:
        raise ValueError(f"Unsupported TEI date value: {value!r}")
    return Literal(text, datatype=XSD.dateTime)


# ---------------------------------------------------------------------------
# Transformation
# ---------------------------------------------------------------------------
class Transformer:
    def __init__(self, xml_path):
        self.root = etree.parse(str(xml_path)).getroot()
        self.standoff = self.root.find(f"{{{TEI}}}standOff")
        self.g = Graph()
        for prefix, ns in PREFIXES.items():
            self.g.bind(prefix, ns)
        self.g.bind("resource", RES)
        self.g.bind("owl", OWL)
        self.entity_class = {}          # xml:id -> 'crm:E21_Person'
        self.stats = {}

    # 1 -- entities ------------------------------------------------------
    @staticmethod
    def label_of(el):
        for xp in ("tei:persName[not(@xml:lang)]", "tei:placeName[not(@xml:lang)]", "tei:orgName[not(@xml:lang)]",
                   "tei:objectIdentifier/tei:objectName[not(@xml:lang)]", "tei:name", "tei:label", "tei:date"):
            found = el.xpath(xp, namespaces=NS)
            if found:
                return " ".join("".join(found[0].itertext()).split())
        return None

    @staticmethod
    def native_names(el):
        """Second name elements in the entity's own language: [(lang, text), ...]."""
        found = el.xpath("tei:persName[@xml:lang] | tei:placeName[@xml:lang] | tei:orgName[@xml:lang]"
                         " | tei:objectIdentifier/tei:objectName[@xml:lang]", namespaces=NS)
        return [(n.get("{http://www.w3.org/XML/1998/namespace}lang"), " ".join("".join(n.itertext()).split()))
                for n in found]

    def read_entities(self):
        records = self.standoff.xpath(".//*[@xml:id][tei:note[@type='conceptualClass']]", namespaces=NS)
        for el in records:
            xml_id = el.get(XML_ID)
            cls = el.xpath("string(tei:note[@type='conceptualClass'])", namespaces=NS).strip()
            node = RES[xml_id]
            self.entity_class[xml_id] = cls
            self.g.add((node, RDF.type, curie_to_uri(cls)))
            label = self.label_of(el)
            if label:
                self.g.add((node, RDFS.label, Literal(label, lang="en")))
            for lang, text in self.native_names(el):     # e.g. "王圆箓"@zh, "東京国立博物館"@ja
                self.g.add((node, RDFS.label, Literal(text, lang=lang)))
                self.stats["native_labels"] = self.stats.get("native_labels", 0) + 1
            for note in el.xpath("tei:note[@type='sourceWording' or @type='description']", namespaces=NS):
                self.g.add((node, CRM.P3_has_note, Literal(" ".join("".join(note.itertext()).split()))))
        self.stats["entities"] = len(records)

    # 2 -- concepts ----------------------------------------------------------
    def add_concepts(self):
        taxonomy = self.root.xpath("//tei:taxonomy[@xml:id='concepts']", namespaces=NS)[0]
        scheme = RES["concept-scheme/religious-traditions"]
        self.g.add((scheme, RDF.type, SKOS.ConceptScheme))
        self.g.add((scheme, RDFS.label, Literal("Religious and philosophical traditions (project taxonomy)")))
        n, n_match = 0, 0
        for cat in taxonomy.findall(f"{{{TEI}}}category"):
            xml_id = cat.get(XML_ID)
            node = RES[xml_id]
            self.entity_class[xml_id] = "skos:Concept"
            self.g.add((node, RDF.type, SKOS.Concept))
            self.g.add((node, SKOS.prefLabel, Literal(cat.findtext(f"{{{TEI}}}desc").strip(), lang="en")))
            self.g.add((node, SKOS.inScheme, scheme))
            n += 1
            for equiv in cat.findall(f"{{{TEI}}}equiv"):
                self.g.add((node, SKOS.exactMatch, URIRef(equiv.get("uri"))))
                n_match += 1
        self.stats.update(concepts=n, exactMatch=n_match)

    # 3 -- identifiers and external links --------------------------------
    def link_predicate(self, scheme, cls):
        if scheme not in AUTHORITY_URI:
            return None
        if scheme == "wikidata" and cls in SUPERCLASSES and is_a(cls, "crm:E39_Actor"):
            return OWL.sameAs
        return RDFS.seeAlso

    def add_identifiers(self):
        schemes, n_ids, n_same, n_see = set(), 0, 0, 0
        for idno in self.standoff.xpath(".//tei:idno[@type]", namespaces=NS):
            owner = idno.xpath("ancestor::*[@xml:id][1]", namespaces=NS)[0]
            xml_id, scheme, value = owner.get(XML_ID), idno.get("type"), (idno.text or "").strip()
            entity = RES[xml_id]
            ident = RES[f"{xml_id}-{scheme}"]
            scheme_node = RES[f"identifier-type/{scheme}"]
            self.g.add((entity, CRM.P1_is_identified_by, ident))
            self.g.add((ident, RDF.type, CRM.E42_Identifier))
            self.g.add((ident, CRM.P190_has_symbolic_content, Literal(value)))
            self.g.add((ident, CRM.P2_has_type, scheme_node))
            schemes.add(scheme)
            n_ids += 1
            pred = self.link_predicate(scheme, self.entity_class[xml_id])
            if pred is not None:
                self.g.add((entity, pred, URIRef(AUTHORITY_URI[scheme].format(value))))
                n_same += pred == OWL.sameAs
                n_see += pred == RDFS.seeAlso
        for scheme in sorted(schemes):
            node = RES[f"identifier-type/{scheme}"]
            self.g.add((node, RDF.type, CRM.E55_Type))
            self.g.add((node, RDFS.label, Literal(SCHEME_LABELS.get(scheme, scheme))))
        self.stats.update(identifiers=n_ids, schemes=len(schemes), sameAs=n_same, seeAlso=n_see)

    # 4 -- time bounds -----------------------------------------------------
    def add_time_bounds(self):
        n = 0
        spans = self.standoff.xpath(
            ".//*[@xml:id][tei:note[@type='conceptualClass']='crm:E52_Time-Span']", namespaces=NS)
        for item in spans:
            node, d = RES[item.get(XML_ID)], item.find(f"{{{TEI}}}date")
            begin = d.get("when") or d.get("notBefore")
            end = d.get("when") or d.get("notAfter")
            if begin:
                self.g.add((node, CRM.P82a_begin_of_the_begin, date_bound(begin, end=False)))
                n += 1
            if end:
                self.g.add((node, CRM.P82b_end_of_the_end, date_bound(end, end=True)))
                n += 1
        self.stats.update(time_spans=len(spans), time_bounds=n)

    # 5 -- relations -----------------------------------------------------------
    @staticmethod
    def endpoints(rel):
        if rel.get("active") and rel.get("passive"):
            return local_id(rel.get("active")), local_id(rel.get("passive"))
        a, b = [local_id(t) for t in rel.get("mutual").split()]
        return a, b

    @staticmethod
    def predicate_of(rel):
        if rel.get("ref"):
            return URIRef(rel.get("ref"))
        return curie_to_uri(rel.get("name"))          # dm: properties carry no @ref

    def relations(self, kind):
        return self.standoff.xpath(f"tei:listRelation[@type='{kind}']/tei:relation", namespaces=NS)

    def add_relations(self):
        for kind in ("conceptual", "subject"):
            for rel in self.relations(kind):
                s, o = self.endpoints(rel)
                self.g.add((RES[s], self.predicate_of(rel), RES[o]))
        self.stats["conceptual_edges"] = len(self.relations("conceptual"))
        self.stats["subject_edges"] = len(self.relations("subject"))

    # 6 -- provenance (kept for traceability, not the main narrative) ----------
    def add_provenance(self):
        names = {r.get(XML_ID): r.get("name") for r in self.relations("canonical")}
        used_evidence = set()
        for rel in self.relations("conceptual"):
            s, o = self.endpoints(rel)
            r_id = local_id(rel.get("corresp"))
            evidence = local_id(rel.get("ana")).replace("evidence-", "")
            st = RES[f"statement/{rel.get(XML_ID)}"]
            self.g.add((st, RDF.type, RDF.Statement))
            self.g.add((st, RDF.subject, RES[s]))
            self.g.add((st, RDF.predicate, self.predicate_of(rel)))
            self.g.add((st, RDF.object, RES[o]))
            self.g.add((st, DCTERMS.relation, RES[f"canonical-relation/{r_id}"]))
            self.g.add((st, DCTERMS.type, RES[f"evidence/{evidence}"]))
            for token in (rel.get("source") or "").split():      # Enriched: the sources of this assertion
                self.g.add((st, DCTERMS.source, URIRef(self.source_urls()[local_id(token)])))
                self.stats["sources"] = self.stats.get("sources", 0) + 1
            used_evidence.add(evidence)
        for r_id, name in names.items():
            self.g.add((RES[f"canonical-relation/{r_id}"], RDF.type, CRM.E89_Propositional_Object))
            self.g.add((RES[f"canonical-relation/{r_id}"], RDFS.label, Literal(f"R{r_id[1:]} - {name}")))
        scheme = RES["concept-scheme/evidence-types"]
        self.g.add((scheme, RDF.type, SKOS.ConceptScheme))
        self.g.add((scheme, RDFS.label, Literal("Evidence types (project taxonomy)")))
        taxonomy = self.root.xpath("//tei:taxonomy[@xml:id='evidence']", namespaces=NS)[0]
        for ev in sorted(used_evidence):
            node = RES[f"evidence/{ev}"]
            cat = taxonomy.xpath(f"tei:category[@xml:id='evidence-{ev}']", namespaces=NS)[0]
            self.g.add((node, RDF.type, SKOS.Concept))
            self.g.add((node, RDFS.label, Literal(EVIDENCE_LABELS[ev])))
            self.g.add((node, SKOS.inScheme, scheme))
            self.g.add((node, SKOS.definition, Literal(" ".join("".join(cat.find(f"{{{TEI}}}catDesc").itertext()).split()), lang="en")))
        self.stats["statements"] = len(self.relations("conceptual"))
        self.stats["propositions"] = len(names)
        self.stats["evidence_types"] = len(used_evidence)

    def source_urls(self):
        """listBibl enrichment-sources: bibl/@xml:id -> the URL of its ref."""
        return {b.get(XML_ID): b.xpath("string(tei:ref/@target)", namespaces=NS)
                for b in self.standoff.xpath("tei:listBibl[@xml:id='enrichment-sources']/tei:bibl", namespaces=NS)}

    def run(self):
        self.read_entities()
        self.add_concepts()
        self.add_identifiers()
        self.add_time_bounds()
        self.add_relations()
        self.add_provenance()
        return self.g


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------
def validate(t, ttl_path, rdf_path, ontology_path):
    errors, checks = [], []

    # V1 reference integrity: every pointer in listRelation resolves to a record
    known = set(t.entity_class)
    known |= {r.get(XML_ID) for r in t.relations("canonical")}
    known |= {c.get(XML_ID) for c in t.root.xpath("//tei:category", namespaces=NS)}
    known |= set(t.source_urls())
    bad = []
    for rel in t.standoff.xpath("tei:listRelation/tei:relation", namespaces=NS):
        for attr in ("active", "passive", "corresp", "ana"):
            if rel.get(attr) and local_id(rel.get(attr)) not in known:
                bad.append(f"{rel.get(XML_ID)}/@{attr}={rel.get(attr)}")
        for token in (rel.get("mutual") or "").split() + (rel.get("source") or "").split():
            if local_id(token) not in known:
                bad.append(f"{rel.get(XML_ID)}/@mutual={token}")
    errors += [f"Unresolved TEI pointer: {b}" for b in bad]
    checks.append(f"V1 TEI pointers resolve to standOff records: {'PASS' if not bad else 'FAIL'}")

    # V2 domain/range of every conceptual relation (CIDOC CRM family + dm:)
    dm_graph = Graph().parse(ontology_path)
    dm_sig = {uri_to_curie(p): (uri_to_curie(dm_graph.value(p, RDFS.domain)),
                                uri_to_curie(dm_graph.value(p, RDFS.range)))
              for p in set(dm_graph.subjects(RDF.type, OWL.ObjectProperty))}
    signatures = {**SIGNATURES, **dm_sig}
    table_rows, violations, unchecked = [], [], []
    for rel in t.relations("conceptual"):
        s, o = t.endpoints(rel)
        prop = uri_to_curie(t.predicate_of(rel))
        cs, co = t.entity_class[s], t.entity_class[o]
        if prop not in signatures:
            unchecked.append(f"{rel.get(XML_ID):>4}  {prop}  {cs} -> {co}")
            continue
        for cls in (cs, co):
            if cls not in SUPERCLASSES:
                violations.append(f"{rel.get(XML_ID)}: class {cls} not in hierarchy table")
        dom, rng = signatures[prop]
        ok_d, ok_r = is_a(cs, dom), is_a(co, rng)
        table_rows.append(f"  {rel.get(XML_ID):>4}  {prop:<38} {cs} -> {co}  "
                          f"[domain {'ok' if ok_d else 'VIOLATION'}, range {'ok' if ok_r else 'VIOLATION'}]")
        if not ok_d:
            violations.append(f"{rel.get(XML_ID)}: {cs} is not a {dom} (domain of {prop})")
        if not ok_r:
            violations.append(f"{rel.get(XML_ID)}: {co} is not a {rng} (range of {prop})")
    errors += violations
    checks.append(f"V2 domain/range of {len(table_rows)} CRM-family and dm: relations: "
                  f"{'PASS' if not violations else 'FAIL'}")

    # V3 every dm: property used is declared; the retired one is not used
    used_dm = {uri_to_curie(p) for p in t.g.predicates() if str(p).startswith(str(DM))}
    undeclared = used_dm - set(dm_sig)
    retired = "dm:providesDigitalAccessTo" in used_dm
    errors += [f"dm: property used but not declared in dm-ontology.ttl: {p}" for p in sorted(undeclared)]
    if retired:
        errors.append("Retired property dm:providesDigitalAccessTo is still used")
    checks.append(f"V3 dm: properties used ({', '.join(sorted(used_dm))}) are declared; "
                  f"retired property unused: {'PASS' if not undeclared and not retired else 'FAIL'}")

    # V4 both serializations re-parse to the same graph as the one in memory
    g_ttl = Graph().parse(ttl_path, format="turtle")
    g_rdf = Graph().parse(rdf_path, format="xml")
    iso = compare.isomorphic(g_ttl, t.g) and compare.isomorphic(g_rdf, t.g)
    if not iso:
        errors.append("Serialized Turtle / RDF/XML are not isomorphic to the in-memory graph")
    checks.append(f"V4 Turtle ({len(g_ttl)} triples) and RDF/XML ({len(g_rdf)} triples) are "
                  f"isomorphic to the in-memory graph ({len(t.g)}): {'PASS' if iso else 'FAIL'}")

    # V5 every TEI relation appears as a triple in the serialized Turtle
    missing = []
    for kind in ("conceptual", "subject"):
        for rel in t.relations(kind):
            s, o = t.endpoints(rel)
            if (RES[s], t.predicate_of(rel), RES[o]) not in g_ttl:
                missing.append(rel.get(XML_ID))
    errors += [f"TEI relation missing from Turtle: {m}" for m in missing]
    checks.append(f"V5 all {t.stats['conceptual_edges']} conceptual and {t.stats['subject_edges']} subject "
                  f"relations present in the Turtle file: {'PASS' if not missing else 'FAIL'}")

    # V6 every project resource used as a subject is typed (theoretical propositions and
    #    evidence types included)
    untyped = sorted({str(s) for s in t.g.subjects() if str(s).startswith(str(RES))
                      and (s, RDF.type, None) not in t.g})
    errors += [f"Untyped resource: {u}" for u in untyped]
    checks.append(f"V6 every project resource is typed: {'PASS' if not untyped else 'FAIL'}")

    # V7 every Enriched relation (canonical and conceptual) points to at least one source with a URL,
    #    every Direct relation has none, and every source pointer of a conceptual relation is a
    #    dcterms:source of its rdf:Statement in the Turtle file
    urls, src_problems = t.source_urls(), []
    for rel in t.standoff.xpath("tei:listRelation[@type='canonical' or @type='conceptual']/tei:relation", namespaces=NS):
        enriched = rel.get("ana") == "#evidence-enriched"
        tokens = (rel.get("source") or "").split()
        if enriched and not tokens:
            src_problems.append(f"{rel.get(XML_ID)}: Enriched relation without @source")
        if not enriched and tokens:
            src_problems.append(f"{rel.get(XML_ID)}: Direct relation with @source")
        for tok in tokens:
            if not urls.get(local_id(tok), "").startswith("http"):
                src_problems.append(f"{rel.get(XML_ID)}: source {tok} has no URL")
        if rel.getparent().get("type") == "conceptual":
            st = RES[f"statement/{rel.get(XML_ID)}"]
            for tok in tokens:
                if (st, DCTERMS.source, URIRef(urls.get(local_id(tok), ""))) not in g_ttl:
                    src_problems.append(f"{rel.get(XML_ID)}: dcterms:source {tok} missing in Turtle")
    errors += src_problems
    n_enr = len(t.root.xpath("//tei:listRelation[@type='conceptual']/tei:relation[@ana='#evidence-enriched']", namespaces=NS))
    checks.append(f"V7 every Enriched relation has its own sources ({n_enr} conceptual, {len(urls)} sources), "
                  f"Direct relations have none, and each source is a dcterms:source in the Turtle file: "
                  f"{'PASS' if not src_problems else 'FAIL'}")

    return errors, checks, table_rows, unchecked


# ---------------------------------------------------------------------------
# QA report
# ---------------------------------------------------------------------------
def qa_report(t, errors, checks, table_rows, unchecked):
    s = t.stats
    lines = [
        "=== Reconnecting Dunhuang - TEI to RDF QA report (v3.2, review round 2a) ===",
        f"Generated: {date.today().isoformat()}",
        "",
        "Counts",
        f"  entities with a conceptual class ......... {s['entities']}",
        f"  native-script labels (@zh, @ja) .......... {s.get('native_labels', 0)}",
        f"  time-spans / P82a-P82b bounds ............ {s['time_spans']} / {s['time_bounds']}",
        f"  subject concepts (skos:Concept) .......... {s['concepts']} (skos:exactMatch: {s['exactMatch']})",
        f"  conceptual relations ..................... {s['conceptual_edges']}",
        f"  subject relations (dcterms:subject) ...... {s['subject_edges']}",
        f"  identifiers (crm:E42_Identifier) ......... {s['identifiers']} in {s['schemes']} schemes",
        f"  external links ........................... owl:sameAs {s['sameAs']}, rdfs:seeAlso {s['seeAlso']}",
        f"  provenance statements (rdf:Statement) .... {s['statements']}",
        f"  sources of Enriched statements ........... {s.get('sources', 0)} dcterms:source",
        f"  theoretical propositions (crm:E89) ....... {s['propositions']}",
        f"  evidence types (skos:Concept) ............ {s['evidence_types']}",
        f"  total triples ............................ {len(t.g)}",
        "",
        "Validation",
        *[f"  {c}" for c in checks],
        "",
        "Domain/range table (checked against CIDOC CRM 7.1.3, CRMsci 3.2, CRMdig 5.0, dm-ontology.ttl)",
        *table_rows,
        "",
        "Relations using vocabularies outside the CRM family (no domain/range declared to check)",
        *[f"  {u}" for u in unchecked],
        "",
    ]
    lines += (["RESULT: FAIL", *[f"  - {e}" for e in errors]] if errors else ["RESULT: PASS"])
    return "\n".join(lines) + "\n"


def main():
    t = Transformer(DEFAULT_XML)
    g = t.run()
    g.serialize(destination=DEFAULT_TTL, format="turtle")
    g.serialize(destination=DEFAULT_RDF, format="xml")

    errors, checks, rows, unchecked = validate(t, DEFAULT_TTL, DEFAULT_RDF, DEFAULT_ONTOLOGY)
    report = qa_report(t, errors, checks, rows, unchecked)
    DEFAULT_QA.write_text(report, encoding="utf-8")
    print(report)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
