# Reconnecting Dunhuang

**A dispersed manuscript corpus, reconnected through data.**

HAOPU YIN · Digital Humanities and Digital Knowledge (DHDK), University of Bologna\
Final LODLAM project for *Information Science and Cultural Heritage*, a.y. 2025–2026

> ### ▶ [Open the project website](https://haopuur-max.github.io/reconnecting-dunhuang/)
> https://haopuur-max.github.io/reconnecting-dunhuang/
>
> Final submission (v1.0): [download `Reconnecting_Dunhuang_HP_YIN_FINAL.zip`](https://github.com/haopuur-max/reconnecting-dunhuang/releases/tag/v1.0)
> · Source: English Wikipedia, [*Dunhuang manuscripts*, revision 1347007263](https://en.wikipedia.org/w/index.php?title=Dunhuang_manuscripts&oldid=1347007263), frozen for this project

---

## 1. The project in brief

**The case.** Most of the Dunhuang manuscripts were sealed together in the Library Cave of the Mogao Caves in the early
11th century and found in 1900. From 1907 they were sold and moved, and today they are held by institutions in several
countries. The International Dunhuang Programme brings them together again online.

**The research question.** *How can a dispersed manuscript corpus be reconnected through structured and linked data?*
The project reconnects information about the corpus — who found, sold, moved and holds which manuscripts — not the
manuscripts themselves.

**The approach**, from one frozen Wikipedia article to linked data:

| Step | What was done | Result |
|---|---|---|
| 1. Domain | read the article as people, places, institutions, manuscripts and events | 28 entity records in the TEI standOff |
| 2. Theoretical model | the story as natural-language relations in five narrative layers, from *Together* to *Digitally reconnected* | 16 entities, 19 relations (R1–R19) |
| 3. Conceptual model | the relations formalized with CIDOC CRM 7.1.3, CRMsci 3.2, CRMdig 5.0, SKOS and DCTerms, plus three project properties; drawn in Graffoo | 38 conceptual relations |
| 4. TEI encoding | the article in TEI P5, names marked in the text and described once in a standOff layer, linked to authority files | 65 entity annotations; 45 identifiers (Wikidata, VIAF, LC, LCSH, FAST, WorldCat, BL shelfmark) |
| 5. Transformations | XSLT → an HTML Wiki View; Python and rdflib → RDF in Turtle and RDF/XML | 683 RDF triples |

Each step counts something different: annotations are not records, and the 683 triples also hold labels, identifiers,
time-spans and the provenance of each statement, not only the modelled relations.

**Key modelling decisions**

- **Events at the centre.** A sale is modelled as an event (`crm:E96_Purchase`) that links seller, buyer, object and
  time, not as a direct line between two people.
- **Every relation states its evidence.** *Direct*: stated in the frozen article. *Enriched* (R16–R19): needs another
  source, named in the TEI and recorded as `dcterms:source` in the RDF.
- **What the source does not say stays out of the data.** The article says the British Library and the Tokyo National
  Museum hold manuscripts, but not which ones, so R9 and R12 stay in the theoretical model (◇) with no holding triple.
- **One documented item.** The printed Diamond Sutra of 868 (British Library, Or.8210/P.2) is part of the corpus
  (`P46i`), was bought by Stein (`P24`) and is kept by the British Library (`P50`, custody, not ownership).

## 2. Reading the website

The report is a website of eight pages. Read them in this order, or go straight to the question you need:

| Page | Question it answers |
|---|---|
| [Home](https://haopuur-max.github.io/reconnecting-dunhuang/) | What is the project about, and what did it produce? |
| [01 Domain](https://haopuur-max.github.io/reconnecting-dunhuang/domain.html) | What does the article tell, and which entities does it name? |
| [02 Models](https://haopuur-max.github.io/reconnecting-dunhuang/models.html) | How does the story become a formal model? (theoretical model, two Graffoo diagrams, modelling decisions) |
| [03 TEI](https://haopuur-max.github.io/reconnecting-dunhuang/tei.html) | How is the article encoded? (annotations, standOff records, relations) |
| [04 Transformations](https://haopuur-max.github.io/reconnecting-dunhuang/transformations.html) | How were the HTML and RDF outputs produced? |
| [05 RDF](https://haopuur-max.github.io/reconnecting-dunhuang/rdf.html) | What does the data say? (triples, authority links, URIs) |
| [Wiki View](https://haopuur-max.github.io/reconnecting-dunhuang/wiki-view.html) | The TEI file rendered as an article by the XSLT |
| [Files](https://haopuur-max.github.io/reconnecting-dunhuang/files.html) | Every file, the validation results and the credits |

**One relation followed through the whole project** — R6, "Wang Yuanlu sold manuscripts to Aurel Stein": the article
sentence → the theoretical relation R6 in the TEI → its formalisation as a CIDOC CRM purchase event (relation `cr10`) →
the Python line that writes each triple → the purchase in the Turtle file. Shown with real code on the [home page](https://haopuur-max.github.io/reconnecting-dunhuang/#h-results); the model diagrams can be
enlarged full screen on the [Models page](https://haopuur-max.github.io/reconnecting-dunhuang/models.html#theoretical).

## 3. Main files

| What | File |
|---|---|
| TEI/XML document | [`reconnecting_dunhuang.xml`](reconnecting-dunhuang/final_report_files/tei_xml/reconnecting_dunhuang.xml) |
| RDF dataset | [`reconnecting_dunhuang.ttl`](reconnecting-dunhuang/final_report_files/xml_to_rdf/reconnecting_dunhuang.ttl) (Turtle), [`reconnecting_dunhuang.rdf`](reconnecting-dunhuang/final_report_files/xml_to_rdf/reconnecting_dunhuang.rdf) (RDF/XML) |
| Project ontology | [`dm-ontology.ttl`](reconnecting-dunhuang/final_report_files/ontology/dm-ontology.ttl) |
| XML → HTML | [`tei_to_html.xsl`](reconnecting-dunhuang/final_report_files/xml_to_html/tei_to_html.xsl), [`transform_tei_to_html.py`](reconnecting-dunhuang/final_report_files/xml_to_html/transform_tei_to_html.py) |
| XML → RDF | [`transform_tei_to_rdf.py`](reconnecting-dunhuang/final_report_files/xml_to_rdf/transform_tei_to_rdf.py) |
| Model diagrams (PDF) | [theoretical model](reconnecting-dunhuang/final_report_files/models/Reconnecting_Dunhuang_Theoretical_Model_FINAL.pdf), [Graffoo: core](reconnecting-dunhuang/final_report_files/models/conceptual_model_core_graffoo.pdf), [Graffoo: subjects, identifiers and evidence](reconnecting-dunhuang/final_report_files/models/conceptual_model_subjects_identifiers_evidence_graffoo.pdf) |
| Quality report | [`QA_REPORT.md`](QA_REPORT.md) |

## 4. Status

Final, frozen on 31 October 2026. TEI valid against TEI P5; RDF checks V1–V7 pass; Turtle and RDF/XML hold the same
683-triple graph; the website's 405 links and 19 code excerpts are checked against the files; the build is
reproducible with one command (section 8). Details: [`QA_REPORT.md`](QA_REPORT.md).

## 5. Repository and package contents

```
Reconnecting_Dunhuang_HP_YIN/        (the repository root; the same files as the v1.0 ZIP)
├── README.md                    this guide
├── CHANGELOG_FINAL.md           changes of the final technical round
├── QA_REPORT.md                 final quality check of this package
├── MANIFEST.txt                 every file with its size and hash
├── reconnecting-dunhuang/       the website (web report) with all project files
    ├── index.html               home page: the entry point of the report and of the oral presentation
    ├── domain.html  models.html  tei.html  transformations.html  rdf.html  files.html
    ├── wiki-view.html           the TEI file rendered by the XSLT stylesheet
    ├── README.md                technical notes on rebuilding the web report
    ├── assets/                  styles, scripts, fonts, images, diagrams
    └── final_report_files/      data, models, schemas, scripts and reports
└── .github/workflows/static.yml publishes reconnecting-dunhuang/ with GitHub Pages (repository only)
```

## 6. Opening the project offline

The website also works offline from the ZIP: all paths are relative and no external resource is loaded. Unzip it first;
pages opened from inside the archive preview may not load their images and styles.

Open `reconnecting-dunhuang/index.html`. The navigation leads to every part of the report: Domain, Models, TEI,
Transformations, RDF, Wiki View and Files. The website itself is used for the oral presentation; there is no separate
slide deck.

## 7. Where each course requirement is

Website links open the published pages; file paths are inside `reconnecting-dunhuang/`.

| Course requirement | On the website | Files |
|---|---|---|
| Study of the domain: idea and at least 10 entities | [domain.html](https://haopuur-max.github.io/reconnecting-dunhuang/domain.html) | 16 entities in the theoretical model; 28 entity records in the TEI standOff (persons, places, organisations, manuscripts, events) |
| Theoretical model | [models.html#theoretical](https://haopuur-max.github.io/reconnecting-dunhuang/models.html#theoretical) | `final_report_files/models/Reconnecting_Dunhuang_Theoretical_Model_FINAL.svg` (web) / `_full.svg` / `.pdf` (full version with notes) |
| Conceptual model (Graffoo) and reused ontologies | [models.html#conceptual](https://haopuur-max.github.io/reconnecting-dunhuang/models.html#conceptual), `#ontologies` | two Graffoo diagrams, each as web SVG, full SVG and PDF: `models/conceptual_model_core_graffoo.*` and `models/conceptual_model_subjects_identifiers_evidence_graffoo.*`; also `models/core_conceptual_model.*` and `models/conceptual_model_instance_graph.*` (website colours) |
| Project ontology terms | [models.html#properties](https://haopuur-max.github.io/reconnecting-dunhuang/models.html#properties) | `final_report_files/ontology/dm-ontology.ttl` (three properties, used with CIDOC CRM 7.1.3, CRMsci, CRMdig, DCTerms, SKOS) |
| Authority links and subjects | [rdf.html#linking](https://haopuur-max.github.io/reconnecting-dunhuang/rdf.html#linking); [models.html](https://haopuur-max.github.io/reconnecting-dunhuang/models.html) | `models/authority_linking_table.md`; TEI `idno` and `equiv`; RDF `owl:sameAs` / `rdfs:seeAlso` / `skos:exactMatch` (Wikidata, VIAF, LC, LCSH, FAST, WorldCat) |
| TEI/XML document | [tei.html](https://haopuur-max.github.io/reconnecting-dunhuang/tei.html) | `final_report_files/tei_xml/reconnecting_dunhuang.xml` (TEI P5, valid against `schemas/tei_all.rng`) |
| XML → HTML transformation and output | [transformations.html#x1](https://haopuur-max.github.io/reconnecting-dunhuang/transformations.html#x1), [wiki-view.html](https://haopuur-max.github.io/reconnecting-dunhuang/wiki-view.html) | `final_report_files/xml_to_html/tei_to_html.xsl`, `transform_tei_to_html.py`, output `reconnecting_dunhuang.html` |
| XML/TEI → RDF transformation (Python) and dataset | [transformations.html#p1](https://haopuur-max.github.io/reconnecting-dunhuang/transformations.html#p1), [rdf.html](https://haopuur-max.github.io/reconnecting-dunhuang/rdf.html) | `final_report_files/xml_to_rdf/transform_tei_to_rdf.py`; output `reconnecting_dunhuang.ttl` and `reconnecting_dunhuang.rdf` (683 triples) |
| Report with all files | [files.html](https://haopuur-max.github.io/reconnecting-dunhuang/files.html) | every deliverable listed with its size |

## 8. Rebuilding everything

**One command** (from inside `reconnecting-dunhuang/`): it runs every step below in order, writes all QA reports
(the TEI validation report included) and stops at the first step that fails.

```bash
python3 final_report_files/run_all.py
```

The same steps one by one, from inside `reconnecting-dunhuang/`, in this order:

```bash
# 1. validate the TEI file
xmllint --noout --relaxng final_report_files/schemas/tei_all.rng final_report_files/tei_xml/reconnecting_dunhuang.xml

# 2. TEI -> RDF (Turtle and RDF/XML) with its checks V1-V7
python3 final_report_files/xml_to_rdf/transform_tei_to_rdf.py

# 3. TEI -> HTML with the XSLT stylesheet, and the HTML checks
python3 final_report_files/xml_to_html/transform_tei_to_html.py

# 4. model diagrams from the RDF dataset (instance graph, core classes, case diagrams), then the theoretical
#    model and the two Graffoo diagrams, web and full versions, with their PDFs
python3 final_report_files/models/generate_model_diagrams.py
python3 final_report_files/models/graffoo/build_model_diagrams.py

# 5. website pages, then the full-site check
python3 final_report_files/site_build/build_site_snippets.py
python3 final_report_files/site_build/check_site.py
```

Requirements, and how to install them (macOS with Homebrew shown; on Linux use `apt install graphviz libxml2-utils`):

```bash
pip install lxml "rdflib>=7" pillow playwright
python3 -m playwright install chromium     # the browser that renders the diagram PDFs (step 4b)
brew install graphviz libxml2              # Graphviz `dot` (step 4a); xmllint is optional, see below
```

- `run_all.py` first checks every tool and, if one is missing, stops before building anything and names the command to
  install it.
- **TEI validation**: with `xmllint` if it is installed; otherwise with `lxml`, which runs the same libxml2 RELAX NG
  validator on the same schema (`schemas/tei_all.rng`). Both give the same result: checked on the TEI file and on three
  deliberately invalid copies (QA_REPORT section 8). The report names the validator used.
- **Chromium**: Playwright's own browser, or an installed Chromium/Chrome given in the environment variable
  `RD_CHROMIUM` (path to the executable). Rendering is offline (local files, fonts embedded in the SVGs); any web
  request is blocked and reported as an error.
- `--skip-diagrams` leaves steps 4a and 4b out (no Graphviz, Pillow or Chromium needed); the summary then marks them
  NOT RUN.

Re-running gives the same data. Some outputs can differ byte by byte without any change of content: the
RDF/XML serialiser may order statements differently (the graph stays isomorphic, and `rdf.html`, which prints
that file, follows its order), the PDFs carry their creation time, and Graphviz spaces the model diagrams slightly
differently when the Source Sans 3 font is not installed. Report files carry the date of the run.

## 9. How the content is kept honest

- The RDF is generated from the TEI file only; no output file is edited by hand.
- Every relation has an evidence type. Direct relations come from the frozen Wikipedia revision. Enriched relations
  (R16–R19) point to their own sources in the TEI (`relation/@source`, `listBibl` "enrichment-sources"), and the
  RDF records each of them as `dcterms:source` on the `rdf:Statement`; check V7 enforces this.
- Code on the website is cut from the final files and shows their real line numbers; `check_site.py` compares every
  excerpt with its file.
- The three main model diagrams are drawn from the TEI file and the RDF dataset by `models/graffoo/`; each build
  stops if a drawn arc, its direction, an example fact or a count differs from the data. On the Models page the
  diagrams are shown at reading size (wider than the text column on desktop; on narrow screens the panel scrolls
  sideways, with "Fit to width" and "Enlarge" views); the PDFs carry the complete notes, legend, prefixes and tables.

## 10. Status of the URIs and of the online version

The RDF dataset names its resources `https://haopuur-max.github.io/reconnecting-dunhuang/resource/{id}` and the
project properties `.../ontology/{name}`. These are stable identifiers in a namespace the project controls, but they
are **not dereferenceable**: a static host would need one page per resource, and none is generated (a resource URI
returns 404, checked on 31 October 2026).

**Online version.** The website is published with GitHub Pages at https://haopuur-max.github.io/reconnecting-dunhuang/ (repository
`haopuur-max/reconnecting-dunhuang`, release v1.0). Checked online on 31 October 2026: the 8 pages load; every local
link, file and anchor (58 distinct targets) resolves; key files are byte-identical to this package (QA_REPORT section 8.F).

## 11. Credits

- Photographs and the manuscript image: public domain according to their Wikimedia Commons file pages, checked on
  29 October 2026 (the 1907 Cave 16 photograph: public domain in the United States); the home-page fragments are cut
  from Pelliot chinois 2778 (Bibliothèque nationale de France). Details and open points:
  `reconnecting-dunhuang/assets/img/IMAGE_CREDITS.md`.
- Sources of the Enriched relations: International Dunhuang Programme (idp.bl.uk), listed in the TEI `listBibl`
  "enrichment-sources".
- Fonts: Source Serif 4, Source Sans 3, Source Code Pro (SIL Open Font License 1.1, in `assets/fonts/`).
  Syntax highlighting: Prism (MIT, `assets/js/PRISM-LICENSE.txt`).
