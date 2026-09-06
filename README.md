# Reconnecting Dunhuang Final Web Report

## Start Here

Open `output/index.html` after extracting the complete ZIP package. This is the main Web Report for reviewing the project narrative, model diagrams, TEI/XML, Technical HTML, RDF outputs, and QA reports.

The report is designed to open locally from the extracted folder. All images, diagrams, PDFs, viewers, and downloads are referenced with paths relative to `output/`, so the `output/` folder is self-contained and `output/index.html` can be opened directly by double-clicking it, with no local server required.

## Package Structure

- `output/index.html` - main Web Report entry point.
- `output/view_turtle.html` - browser-readable wrapper for the Turtle serialization.
- `output/view_rdfxml.html` - browser-readable wrapper for the RDF/XML serialization.
- `output/final_package_qa_report.txt` - final package QA report.
- `output/final_package_changelog.txt` - final package changelog.
- `output/final_report_files/tei_xml/reconnecting_dunhuang.xml` - final encoded TEI/XML used as the common input for both transformation branches (XML to HTML and XML to RDF).
- `output/final_report_files/xml_to_html/` - XML to HTML stylesheet, script, generated Technical HTML, and HTML QA report.
- `output/final_report_files/xml_to_rdf/` - XML to RDF script, Turtle, RDF/XML, RDF QA report, and transformation documentation.
- `output/final_report_files/models/` - final theoretical, conceptual, Graffoo, and authority-control model files.
- `output/final_report_files/source_snapshot/` - local PDF snapshot of the frozen Wikipedia source.
- `output/final_report_files/validation/` - TEI validation and project QA reports.
- `output/assets/Reconnecting_Dunhuang_Showcase_Assets_FINAL/` - images, diagrams, icons, and asset documentation used by the Web Report.

## Frozen Source

The project source text is the frozen English Wikipedia article `Dunhuang manuscripts`, revision `oldid=1347007263`, timestamped `03:43, 4 April 2026`.

The Web Report links both the online frozen revision and a local PDF snapshot. The TEI/XML encodes the frozen source text and the locked project annotations.

## Running XML to HTML

From the extracted package, run:

```bash
python3 output/final_report_files/xml_to_html/transform_tei_to_html.py
```

The script uses package-relative defaults:

- input TEI/XML: `output/final_report_files/tei_xml/reconnecting_dunhuang.xml`
- stylesheet: `output/final_report_files/xml_to_html/tei_to_html.xsl`
- output HTML: `output/final_report_files/xml_to_html/reconnecting_dunhuang.html`
- QA report: `output/final_report_files/xml_to_html/html_qa_report.txt`

Dependency: `lxml`.

## Running XML to RDF

From the extracted package, run:

```bash
python3 output/final_report_files/xml_to_rdf/transform_tei_to_rdf.py
```

The script uses package-relative defaults:

- input TEI/XML: `output/final_report_files/tei_xml/reconnecting_dunhuang.xml`
- Turtle output: `output/final_report_files/xml_to_rdf/reconnecting_dunhuang.ttl`
- RDF/XML output: `output/final_report_files/xml_to_rdf/reconnecting_dunhuang.rdf`
- RDF QA report: `output/final_report_files/xml_to_rdf/rdf_qa_report.txt`
- Turtle viewer: `output/view_turtle.html`
- RDF/XML viewer: `output/view_rdfxml.html`

Dependencies: `lxml` and `rdflib`.

## Automatic Viewer Regeneration

`transform_tei_to_rdf.py` regenerates `output/view_turtle.html` and `output/view_rdfxml.html` automatically every time it runs, immediately after writing the `.ttl` and `.rdf` files. Each viewer is only a browser-safe wrapper: its content is the exact text of the corresponding raw file with HTML escaping applied for safe display, with no RDF content reinterpreted, reordered, or altered. This guarantees the viewers can never go stale relative to the raw files, even though RDF/XML serialization order is not guaranteed to be stable across runs.

## RDF Viewers and Downloads

Use `output/view_turtle.html` and `output/view_rdfxml.html` for browser-readable inspection. These viewer files wrap the exact Turtle and RDF/XML source text so it can be read conveniently in a browser.

Use the download links for the original machine-readable files:

- `output/final_report_files/xml_to_rdf/reconnecting_dunhuang.ttl`
- `output/final_report_files/xml_to_rdf/reconnecting_dunhuang.rdf`

## Expected Counts

- Canonical relations: 16 / 16.
- Conceptual edges: 30 / 30.
- Events: 7.
- Time-spans: 2.
- Evidence status: R1-R15 Direct; R16 Enriched.
- RDF triples: 459 in Turtle and 459 in RDF/XML.
- Authority identifiers: 41.
- Identifier schemes: 7.
- RDF validation: PASS.

R16 is not Direct evidence from the frozen Wikipedia revision. It is an Enriched project interpretation supported by an additional authoritative source: International Dunhuang Programme, "About - International Dunhuang Programme", The British Library, https://idp.bl.uk/about/.

## Known Modelling Limitation

The RDF technical documentation records one retained modelling limitation: the locked aggregate model uses `crm:E78_Curated_Holding` for the Dunhuang Manuscripts while `crm:P25_moved` has a narrower physical-object range expectation. This is documented intentionally and not changed in this package; the locked 30-edge model is preserved.
