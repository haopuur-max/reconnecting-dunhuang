# Reconnecting Dunhuang — TEI/XML to RDF transformation

Script: `transform_tei_to_rdf.py` (Python 3, lxml, rdflib 7.x) · Input: `../tei_xml/reconnecting_dunhuang.xml`
(the single source) and `../ontology/dm-ontology.ttl` · Output: `reconnecting_dunhuang.ttl` and
`reconnecting_dunhuang.rdf` (the same graph in Turtle and RDF/XML) and `rdf_qa_report.txt`.
Every number below is read from `rdf_qa_report.txt` of the last run.

## Vocabularies

| Prefix | Vocabulary and version | Namespace |
|---|---|---|
| `crm:` | [CIDOC CRM 7.1.3](http://www.cidoc-crm.org/cidoc-crm/7.1.3/) | `http://www.cidoc-crm.org/cidoc-crm/` |
| `crmsci:` | [CRMsci 3.2](http://www.cidoc-crm.org/extensions/crmsci/3.2/) | `http://www.cidoc-crm.org/extensions/crmsci/` |
| `crmdig:` | [CRMdig 5.0](https://cidoc-crm.org/crmdig/ModelVersion/crmdig-v5.0) | `http://www.cidoc-crm.org/extensions/crmdig/` |
| `skos:` | SKOS (W3C Recommendation 2009) | `http://www.w3.org/2004/02/skos/core#` |
| `dcterms:` | DCMI Metadata Terms (2020) | `http://purl.org/dc/terms/` |
| `owl:` `rdfs:` `rdf:` | OWL 2, RDF Schema 1.1 | |
| `dm:` | project ontology, `dm-ontology.ttl` (three properties) | `https://haopuur-max.github.io/reconnecting-dunhuang/ontology/` |
| `resource:` | project resources | `https://haopuur-max.github.io/reconnecting-dunhuang/resource/` |

## What the script produces, layer by layer

1. **Entities.** Every standOff record with `<note type="conceptualClass">` becomes a resource with that
   `rdf:type` and an English `rdfs:label` (`@en`); a second name element with `@xml:lang` becomes a further
   `rdfs:label` in that language (11 labels: `@zh` for Chinese persons, places and the National Library of China,
   `@ja` for Ōtani Kōzui and the Tokyo National Museum): 34 records (persons, places, institutions, the corpus and its four
   physical subsets, one documented manuscript, the digital surrogate, events and time-spans). `<note type="sourceWording">`
   and `<note type="description">` become `crm:P3_has_note`.
2. **Subject concepts.** The TEI taxonomy `concepts` becomes a `skos:ConceptScheme` with 6 `skos:Concept`s;
   each `<equiv>` becomes `skos:exactMatch` (11: 6 to Wikidata, 5 to the Library of Congress Subject Headings).
3. **Identifiers and authority links.** Every `<idno>` becomes a `crm:E42_Identifier` (`crm:P1_is_identified_by`,
   `crm:P190_has_symbolic_content`, `crm:P2_has_type` → identifier type): 45 identifiers in 8 schemes (the British Library shelfmark included). Where the
   scheme has a URI form, one external link is added:
   `owl:sameAs` only for Wikidata items of actors (persons and groups, institutions included), which denote the
   same individual (10); `rdfs:seeAlso` for all other authority records, subject headings and Wikidata items of
   places, of the corpus and of the Diamond Sutra (30). FAST control numbers and the British Library shelfmark have no
   URI form and stay identifiers only.
4. **Time-spans.** `@when`, `@notBefore`, `@notAfter` become `crm:P82a_begin_of_the_begin` /
   `crm:P82b_end_of_the_end` (`xsd:dateTime`).
5. **Relations.** Each `<relation>` of the conceptual layer becomes one triple (38); each subject relation becomes
   `dcterms:subject` (6). `dm:locatedNear` (R2, encoded with `@mutual`) is emitted once; its symmetry is declared in
   `dm-ontology.ttl` (`owl:SymmetricProperty`).
6. **Provenance.** Each conceptual triple is also restated as an `rdf:Statement` (38) with
   `rdf:subject / rdf:predicate / rdf:object`, `dcterms:relation` → the theoretical relation it formalises, and
   `dcterms:type` → its evidence type; an Enriched statement also has `dcterms:source` → each page that supports it
   (6 links, read from `relation/@source` and the TEI `listBibl` "enrichment-sources").
   - The 19 theoretical relations R1–R19 are typed `crm:E89_Propositional_Object`: they are propositions of the
     theoretical model, not RDF triples. Several statements can formalise one proposition (R6 → cr9, cr10, cr11,
     cr31, cr36). R9 and R12 are propositions with no formal statement, because the source does not say which
     manuscripts the British Library and the Tokyo National Museum hold. R19 (the British Library holds the Diamond Sutra) is
     one documented case of R9, not its formalisation.
   - The TEI taxonomy `evidence` becomes a second `skos:ConceptScheme`, "Evidence types", with two `skos:Concept`s
     whose `skos:definition` is the TEI `catDesc`: *Direct* — evidence from the frozen Wikipedia revision (R1–R15);
     *Enriched* — a relation supported by an additional authoritative source (R16, the project's interpretation of the
     International Dunhuang Programme's description of itself; R17–R19, the printed Diamond Sutra of 868 from the IDP
     catalogue and research articles).

Total: 683 triples.

## Validation (run after every serialisation)

- V1 every TEI pointer resolves to a standOff record.
- V2 domain and range of every CRM-family and `dm:` relation, against CIDOC CRM 7.1.3, CRMsci 3.2, CRMdig 5.0 and
  `dm-ontology.ttl`.
- V3 every `dm:` property used is declared; the retired property is unused.
- V4 the Turtle and RDF/XML files are re-parsed and are isomorphic to the in-memory graph.
- V5 every conceptual and subject relation of the TEI is present in the Turtle file.
- V6 every project resource is typed.
- V7 every Enriched relation has its own sources with a URL, Direct relations have none, and every source of a
  conceptual relation is a `dcterms:source` of its `rdf:Statement` in the Turtle file.

The RDF/XML serialiser may order statements differently between runs; the graph stays isomorphic.

## How to run

From the website root (`reconnecting-dunhuang/`):

```bash
python3 final_report_files/xml_to_rdf/transform_tei_to_rdf.py
```
