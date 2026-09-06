# Reconnecting Dunhuang TEI XML to RDF Transformation

## Purpose

This document describes the final XML to RDF transformation method for the Reconnecting Dunhuang project. It explains how the locked TEI standOff model is converted into Turtle and RDF/XML without changing the underlying entities, relations, evidence status, authority identifiers, or ontology mappings.

## Final Input XML

The sole transformation input is:

`../tei_xml/reconnecting_dunhuang.xml`

The XML contains the frozen source text, the TEI annotations, entity and authority registers, canonical relations R1-R16, conceptual edges cr1-cr30, event nodes, and time-span nodes.

## Namespaces

- `crm:` `http://www.cidoc-crm.org/cidoc-crm/`
- `crmsci:` `http://www.cidoc-crm.org/extensions/crmsci/`
- `crmdig:` `http://www.cidoc-crm.org/extensions/crmdig/`
- `dm:` `https://haopuur-max.github.io/reconnecting-dunhuang/ontology/`
- `resource:` `https://haopuur-max.github.io/reconnecting-dunhuang/resource/`

The `dm:` namespace is used only for the four project-specific properties documented in the TEI header:

- `dm:partOfNetwork`
- `dm:locatedNear`
- `dm:providesDigitalAccessTo`
- `dm:virtuallyBringsTogether`

## Mapping Strategy

The RDF conversion reads TEI standOff data and produces four RDF layers:

1. Entity typing and labels from TEI entity, event, digital-object, and time-span registers.
2. Authority reconciliation using CIDOC CRM identifier modelling.
3. Core conceptual assertions from the 30 conceptual relation elements.
4. Statement provenance using RDF reification and evidence-status metadata.

The 16 canonical relations are not emitted as domain predicates. They are preserved as human-readable provenance labels connected to the corresponding conceptual-edge statements.

## Authority Reconciliation

Authority identifiers are modelled with the CIDOC CRM identifier pattern:

`entity -> crm:P1_is_identified_by -> E42_Identifier`

Each identifier node stores its literal identifier value with `crm:P190_has_symbolic_content` and links to an identifier scheme node with `crm:P2_has_type`.

No `owl:sameAs` statements are used.

## Canonical to Conceptual to RDF Strategy

The canonical layer records normalized project relations R1-R16. The conceptual layer expresses those relations as formal ontology edges using CIDOC CRM, CRMsci, CRMdig, and the four documented `dm:` properties.

Only conceptual edges cr1-cr30 become core RDF assertions. Their `@corresp` links preserve the connection back to R1-R16, and their `@ana` values preserve Direct or Enriched evidence status.

R1-R15 are Direct. R16 is Enriched. R16 is not Direct evidence from the frozen Wikipedia revision; it is an Enriched project interpretation supported by an additional authoritative source: International Dunhuang Programme, "About - International Dunhuang Programme", The British Library, <https://idp.bl.uk/about/>. The page's "Our Mission" section states that the programme links the collections of over 35 partner institutions worldwide, forming a growing network of libraries, museums and research institutes, providing the additional authoritative basis for R16 as an Enriched project interpretation.

## RDF Reification and Provenance Design

Each conceptual edge receives one `rdf:Statement` node under `resource:statement/`.

Each statement records:

- `rdf:subject`
- `rdf:predicate`
- `rdf:object`
- `dcterms:relation` pointing to the corresponding canonical relation resource
- `dcterms:type` pointing to `resource:evidence/direct` or `resource:evidence/enriched`

This provenance layer describes the 30 conceptual assertions. It does not add extra core conceptual assertions.

## R2 Symmetry Handling

The TEI keeps cr2 as one relation encoded with `@mutual="#mogao-caves #dunhuang"`. The RDF conversion emits one core assertion:

`Mogao Caves -> dm:locatedNear -> Dunhuang`

The transformation also declares:

`dm:locatedNear rdf:type owl:SymmetricProperty`

This preserves the property semantics without adding a second reverse core triple.

## How to Run

From the extracted package root, run:

```bash
python3 output/final_report_files/xml_to_rdf/transform_tei_to_rdf.py
```

The script uses package-relative defaults and writes:

- `output/final_report_files/xml_to_rdf/reconnecting_dunhuang.ttl`
- `output/final_report_files/xml_to_rdf/reconnecting_dunhuang.rdf`
- `output/final_report_files/xml_to_rdf/rdf_qa_report.txt`
- `output/view_turtle.html` (regenerated automatically)
- `output/view_rdfxml.html` (regenerated automatically)

Dependencies: `lxml` and `rdflib`.

## Outputs

- `reconnecting_dunhuang.ttl` - Turtle serialization.
- `reconnecting_dunhuang.rdf` - RDF/XML serialization.
- `rdf_qa_report.txt` - RDF conversion and post-generation QA report.
- `view_turtle.html` - browser-readable wrapper for Turtle, regenerated from the `.ttl` file every run.
- `view_rdfxml.html` - browser-readable wrapper for RDF/XML, regenerated from the `.rdf` file every run.

## Viewer Regeneration (v2.4)

RDF/XML serialization order is not guaranteed to be stable across runs, so a hand-authored viewer file can silently go stale relative to the raw `.rdf` file the next time the script is rerun. `transform_tei_to_rdf.py` closes this gap: immediately after writing `reconnecting_dunhuang.ttl` and `reconnecting_dunhuang.rdf`, it regenerates `view_turtle.html` and `view_rdfxml.html` directly from those same two files. Each viewer applies only HTML escaping to the raw text for safe display inside `<pre><code>`; no RDF content is reinterpreted, reordered, or altered, and the header's "Back to Web Report" link and the raw-file download link are preserved unchanged. This guarantees the viewer text and the raw file text can never drift apart, byte-for-byte after removing only the HTML-escaping/wrapper markup.

## Final QA Numbers

- Core conceptual assertions: 30 / 30.
- Authority identifiers converted: 41.
- Identifier schemes: 7.
- Statement provenance nodes: 30.
- Total RDF triples: 459.
- Turtle graph: 459 triples.
- RDF/XML graph: 459 triples.
- Turtle and RDF/XML graphs: isomorphic.
- Post-generation validation: PASS.

## Final Validation Method

After serialization, the script re-parses the generated Turtle and RDF/XML files, independently rebuilds the expected graph from the TEI/XML, and compares the expected and actual graphs by exact triple-set equality and graph isomorphism.

The validation checks the full graph: entity typing and labels, core conceptual assertions, authority reconciliation, statement provenance, evidence labels, canonical-relation labels, and the `dm:locatedNear` symmetric-property declaration.

## Known Modelling Limitation

The locked aggregate model represents `Dunhuang Manuscripts` as `crm:E78_Curated_Holding`. The transfer model uses `crm:P25_moved` from the transfer event to that aggregate manuscript collection. CIDOC CRM has a narrower physical-object range expectation for `crm:P25_moved`, so this creates a known range tension.

This package documents the issue as a retained modelling limitation. It does not introduce a new `crm:E19_Physical_Object` subset node, does not change `crm:E78_Curated_Holding`, does not change `crm:P25_moved`, and does not alter the locked 30-edge conceptual model. Any strict semantic restructuring would require a separate semantic review across the theoretical model, conceptual model, Graffoo diagram, TEI/XML, RDF serializations, and QA counts.
