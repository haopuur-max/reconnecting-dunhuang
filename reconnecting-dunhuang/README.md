# Reconnecting Dunhuang - Web Report and data package

This folder is the website root: the same files are served by GitHub Pages and browsed offline
from the ZIP (open `index.html`; all paths are relative and no external resource is loaded).

Status: final (data and model frozen after review round 2a, 29 October 2026). All eight pages are built from the
project files; the full-site
acceptance check is in `final_report_files/validation/site_acceptance_report.txt`.

## Structure

- `index.html` ... `files.html` - the eight pages of the Web Report (generated, do not edit by hand; `index.html` is
  the one hand-maintained page).
- `assets/` - `css/` (design system, syntax theme, print), `js/` (menu, figure enlargement, Prism),
  `fonts/` (Source Serif 4, Source Sans 3, Source Code Pro, SIL OFL 1.1), `img/` (public-domain
  historical photographs, see `IMAGE_CREDITS.md`), `diagrams/` (figures generated from the data),
  `ornaments/` (original SVG line ornaments).
- `final_report_files/` - the project data and scripts:
  `tei_xml/`, `ontology/dm-ontology.ttl`, `xml_to_rdf/`, `xml_to_html/`, `models/`, `validation/`,
  `source_snapshot/`, `schemas/tei_all.rng`, `site_build/` (page templates, build script, the full-site check, and
  `make_fragments.py`, which cuts the torn manuscript fragments of the home page from Pelliot chinois 2778).
  `models/graffoo/` draws the theoretical model and the two Graffoo diagrams of the conceptual model (web and full
  versions, PDFs) and checks every arc, direction and example against the TEI file and the RDF dataset.

## Rebuilding everything (from this folder, in this order)

One command runs all the steps below with their checks and stops at the first failure:
`python3 final_report_files/run_all.py`. Step by step:

```bash
xmllint --noout --relaxng final_report_files/schemas/tei_all.rng final_report_files/tei_xml/reconnecting_dunhuang.xml
python3 final_report_files/xml_to_rdf/transform_tei_to_rdf.py
python3 final_report_files/xml_to_html/transform_tei_to_html.py
python3 final_report_files/models/generate_model_diagrams.py
python3 final_report_files/models/graffoo/build_model_diagrams.py
python3 final_report_files/site_build/build_site_snippets.py
python3 final_report_files/site_build/check_site.py
```

Dependencies: `lxml`, `rdflib` 7.x, Graphviz `dot` (with Source Sans 3 installed for text metrics); for the three
main model diagrams (`models/graffoo/`) also Pillow and Playwright with Chromium (`python3 -m playwright install
chromium`, or an installed Chromium given in `RD_CHROMIUM`). `xmllint` is optional: without it the TEI is validated
with lxml against the same RELAX NG schema. `run_all.py` checks all of these before it builds anything.
Code on the website is cut from the final files by anchor and shows their real line numbers;
diagrams and model tables are generated from the TEI file, the RDF dataset and dm-ontology.ttl.

## Status of the URIs

Resources and project properties use `https://haopuur-max.github.io/reconnecting-dunhuang/resource/{id}` and
`.../ontology/{name}`. These are identifiers in a namespace the project controls; they are not dereferenceable: on a
static host each resource would need its own page (a resource URI returns 404). The website itself is published at
https://haopuur-max.github.io/reconnecting-dunhuang/ (GitHub Pages; checked online on 31 October 2026).
