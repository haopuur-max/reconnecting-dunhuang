# Final QA report

Package: `Reconnecting_Dunhuang_HP_YIN`, final version of 31 October 2026 (final technical round: section 8; changes in `CHANGELOG_FINAL.md`), with the **visual upgrade of the website (section 7)**.
**Frozen for submission.** No further design changes; data, model and diagrams unchanged since review round 2a.
**Status: data and model frozen.** After review round 2a no entity, relation or ontology term is added; only real
semantic errors, data inconsistencies or omissions against the course guidelines would still be corrected.

The oral presentation uses the website itself (`reconnecting-dunhuang/index.html`). The separate presentation page
and its 17-page PDF backup were removed from the package (see section 5).

| | |
|---|---|
| TEI | `final_report_files/tei_xml/reconnecting_dunhuang.xml`, 550 lines, valid TEI P5 (RELAX NG, release 4.12.0) |
| RDF | **683 triples**, Turtle and RDF/XML isomorphic; checks V1–V7 pass |
| Theoretical model | 16 entities, R1–R19 (R1–R15 Direct; R16–R19 Enriched); R9 and R12 not formalised (◇) |
| Conceptual layer | 38 conceptual relations, 6 subject relations, 45 identifiers in 8 schemes |
| Website | 8 pages, 405 local links, images and anchors, 0 broken; 19 code excerpts identical to their files; 0 external requests offline |

## 1. Changes of the review (28–29 October 2026)

### Round 1: names, subjects, one-command run (613 → 636 triples)

- **Native-script names** (`@xml:lang`): 敦煌文献, 藏经洞, 莫高窟, 敦煌, 丝绸之路, 北京, 中国国家图书馆 (`zh`) and
  東京国立博物館 (`ja`), in addition to the three persons. Western institutions and the IDP keep their own-language name.
  The names were checked against the Chinese and Japanese Wikipedia articles. In the RDF, English labels are `@en`
  and these names are further `rdfs:label`s.
- **Subjects**: new concept Judaism (two mentions annotated, subject relation s6); Wikidata alignments for Nestorian
  Christianity (Q168414) and Manichaeism (Q131165); LCSH alignments for Buddhism (sh85017454), Taoism (sh85132392),
  Confucianism (sh85031069), Manichaeism (sh85080542) and Judaism (sh85070835). No LCSH heading was found for
  Nestorian Christianity.
- **`final_report_files/run_all.py`**: the whole chain with every check, in one command.
- Triples: +23, all accounted for: +11 language labels, +8 `skos:exactMatch`, +4 for Judaism; 33 existing English labels
  re-tagged `@en` (no label lost).

### Round 2a: one documented item, the printed Diamond Sutra of 868 (636 → 683 triples)

The page mentions copies of the Diamond Sutra only in general. The project adds one documented item from the
International Dunhuang Programme (IDP), with Enriched evidence and its own sources.

**Theoretical and conceptual mapping**

| Theoretical relation | Conceptual relation (RDF) | Evidence | Sources (`dcterms:source`) |
|---|---|---|---|
| R17 Diamond Sutra *part_of* Dunhuang Manuscripts | cr38 `diamond-sutra-868 crm:P46i_forms_part_of dunhuang-manuscripts` | Enriched | IDP, *Shaping the Stein collection's Dunhuang corpus (2)*; IDP, *The Diamond Sutra* |
| R18 Diamond Sutra *acquired_by* Aurel Stein | cr39 `purchase-stein crm:P24_transferred_title_of diamond-sutra-868` | Enriched | IDP, *Shaping the Stein collection's Dunhuang corpus (2)*; IDP, *Discovering Cave 17* |
| R19 Diamond Sutra *held_by* British Library | cr40 `diamond-sutra-868 crm:P50_has_current_keeper british-library` | Enriched | IDP catalogue, Or.8210/P.2 |
| R16 IDP *virtually_brings_together* Dunhuang Manuscripts (existing) | cr30 `idp dm:virtuallyBringsTogether dunhuang-manuscripts` | Enriched | IDP, *About* |

What each source supports (recorded in the TEI `listBibl` "enrichment-sources", `note type="supports"`):
- *About* (idp.bl.uk/about/): the IDP links "the collections of over 35 partner institutions worldwide" and makes them
  freely available. `dm:virtuallyBringsTogether` is the project's reading of this description, not a term of the IDP.
- *Shaping the Stein collection's Dunhuang corpus (2)*: the printed Diamond Sutra of 868 (Or.8210/P.2, Ch.ciii.014)
  was among the items of Cave 17's "miscellaneous" bundles, handed over to Stein in the first transaction,
  21 May – 6 June 1907.
- *The Diamond Sutra*: made in AD 868, found in a hidden cave at the Mogao site.
- *Discovering Cave 17*: in 1907 "Stein managed to purchase 12 cases of material for small fee".
- IDP catalogue, Or.8210/P.2: British Library; Stein number Ch.ciii.014; Mogao Caves; 868.

**Modelling decisions** (TEI `projectDesc` and the Models page):
- *P46i (R17)*: a historical physical part-whole relation. The corpus (`crm:E18_Physical_Thing`) is the physical
  aggregate sealed in the Library Cave (R4). CIDOC CRM 7.1.3 states that P46 "does not specify when and for how long a
  component element resided in the respective whole": the triple does not say that the corpus is still kept together,
  nor when the scroll left it. It is not a classification (what the texts are about is `dcterms:subject`).
  The scope note was checked in the official RDFS of CIDOC CRM 7.1.3 (FORTH, February 2024).
- *P24 (R18)*: based on the IDP's research on Stein's acquisition of 1907, not on an item-by-item list of the
  transaction. It records the transfer as these sources describe it and makes no judgement on its legitimacy.
  It is consistent with the existing `purchase-stein` (seller Wang Yuanlu, buyer Aurel Stein, "from 1907 onwards").
- *P50 (R19)*: custody, not ownership (`crm:P52_has_current_owner` is not used).
- *R9 unchanged*: R19 is one documented case of R9, explained in the theoretical model and on the Models page; there
  is no RDF link between them, and R9 keeps its ◇.

**Entity record**: `diamond-sutra-868`, `crm:E19_Physical_Object`, label "Diamond Sutra, printed copy of 868",
British Library shelfmark Or.8210/P.2 (identifier scheme added: "British Library shelfmark", no URI form),
Wikidata Q28097186 (`rdfs:seeAlso`), description as `crm:P3_has_note`.

**Triples: +48, −1 (636 → 683)**, compared triple by triple with the round 1 graph:
- entity: type, label, note, two `P1_is_identified_by`, `rdfs:seeAlso` (6);
- two identifiers × 3 triples, and the new identifier type with its label (8);
- three conceptual relations (3);
- three `rdf:Statement`s with their sources: cr38 and cr39 have two sources (8 triples each), cr40 one (7) — 23 in all;
  and one `dcterms:source` on the existing R16 statement (1);
- three propositions R17–R19 × 2 (6);
- the Enriched definition replaced by the generalised one (+1, −1).

**New check V7**: every Enriched relation (canonical and conceptual) has at least one source with a URL; Direct
relations have none; every source of a conceptual relation is a `dcterms:source` of its `rdf:Statement` in the Turtle
file. Result: 4 Enriched conceptual relations, 5 sources, 6 `dcterms:source` triples: PASS.

## 2. Automatic checks (29 October 2026, `python3 final_report_files/run_all.py`)

| # | Check | Result |
|---|---|---|
| 1 | TEI P5 validation (RELAX NG) | PASS |
| 2 | RDF V1–V7: pointers, domain/range of 37 CRM-family and `dm:` relations, `dm:` declarations, Turtle = RDF/XML (683 = 683), every relation present, every resource typed, sources of Enriched relations | PASS |
| 3 | HTML QA: XML unchanged by the transformation; 34/34 entity cards; 65 entity anchors; 34/34 bibliography entries | PASS |
| 4 | Model diagrams against the data: theoretical model (19 relations drawn once, direction checked; R9 and R12 the only unformalised relations); core Graffoo (24 usage arcs = data, 30 arcs on domain and range); second Graffoo (5 class-level arcs = data, 19 example facts in the Turtle file, 26 arcs checked for direction) | PASS |
| 5 | Full-site check: 374 local links, images and anchors, 0 broken; 15 code blocks identical to their files; Wiki View equals the XSLT output; 34 listed files exist with current sizes; QA reports pass; Domain page free of ontology terms | PASS |
| 6 | Offline: the 8 pages opened in Chromium with every network request blocked: 0 external requests, 0 failed loads, 0 broken images, 0 page errors | PASS |
| 7 | Reproducibility: the whole chain run twice; identical outputs except the PDFs (creation time), RDF/XML statement order (graph isomorphic, 683 triples) and `rdf.html`, which prints that file | PASS |
| 8 | No output edited by hand: the RDF, the Wiki View, the diagrams and the pages (except `index.html`) are regenerated by `run_all.py` | PASS |

## 3. Model diagrams: what changed

| Diagram | Change |
|---|---|
| Theoretical model | Layer IV: the right column now reads National Library of China, BnF, British Library, Diamond Sutra (16), Aurel Stein (drawn again "as in layer III"); R17 (to the corpus), R18 (to Aurel Stein), R19 (to the British Library), all Enriched; a note: R19 is one documented case of R9, which stays ◇. Layer IV is taller and layer V moved down. Luo Zhenyu's box moved left so that the R13 label no longer touches the boxes. Header: 16 entities, 19 relations. Legend: "Manuscript item", "R16–R19 Enriched", BL shelfmark; full Enriched definition wrapped |
| Conceptual model, core (Graffoo) | **Unchanged** (the three new relations use class-level arcs already drawn: E19 → E18, E96 → E19, E19 → E74). Only the footer count reads 683 triples |
| Conceptual model, subjects, identifiers and evidence (Graffoo) | Band A: `crm:E19_Physical_Object` among the classes with identifiers; 45 identifiers in 8 schemes; 30 `rdfs:seeAlso`. Band B (round 1): 6 subjects, 6 Wikidata and 5 LCSH alignments. Band C: new arc `rdf:Statement dcterms:source ex:IRI` (6 links, Enriched only); R1–R19; 38 statements; Enriched: 4 statements |
| Instance graph, core classes, purchase case (generated) | Show the Diamond Sutra and its three Enriched arcs |

### Final visual acceptance of the three model diagrams (29 October 2026)

The five-layer theoretical model and the two Graffoo diagrams are the final diagrams; no layout was redesigned.

- **Automatic overlap scan** (Chromium, every label of the web and full SVGs measured): labels crossing a box edge,
  theoretical model 4 → **0**; core Graffoo 0; second Graffoo 0. The only remaining text-on-text hits are the
  two-line labels whose lines touch by design (DUNHUANG / MANUSCRIPTS, R4 / sealed_in, R13 / facilitated_transfer_of)
  and the name and class written inside each individual of the Graffoo examples.
- **Two real issues found and fixed** (theoretical model only): the label "R10 held_by" lay on the border of the BnF
  box (caused in round 2a, when BnF was moved to the narrow left side), and "facilitated_transfer_of" (R13) touched the
  Luo Zhenyu box and the corpus column. Fix: BnF back on the right side above the British Library; Luo Zhenyu's box
  moved 82 px to the left. No relation, label text or data changed.
- **Desktop width**: at 1440 px the three diagrams are shown 1334 px wide without sideways scrolling; at 1280 px the
  panel scrolls sideways and the page does not overflow.
- **Enlarge view**: each diagram opens at its natural size (1720 or 1900 px).
- **PDF at actual size** (96 dpi): legends, prefixes, the wrapped Enriched definition and the `dcterms:source` arc are
  readable, with nothing clipped.
- **Semantics by eye**: R17–R19 dashed purple with ★, arrows from the Diamond Sutra to the corpus, to Aurel Stein and to
  the British Library; R9 and R12 keep ◇; the R9 note matches the Models page; the core Graffoo is unchanged; band A
  lists E19 (a subclass of E18, shown because the data uses it); `dcterms:source` goes from `rdf:Statement` to an
  external IRI, Enriched statements only.
- The radial sketch of the theoretical model is not part of the submission (kept outside the package).
- **Repeated boxes explained** (text only): Wang Yuanlu (5) and Aurel Stein (6) are drawn in two layers each. The Models
  page now says that a repeated box keeps the same number, refers to the same entity and is not an additional one,
  and that the model has 16 distinct entities; the legend of the theoretical model (web and PDF) has the line
  "Repeated box (same number, "as in layer …") = the same entity drawn again, not an additional entity". The count is
  enforced by the build (the boxes map to 16 distinct TEI records) and reads 16 in the diagram header, the Models page,
  the README and this report. No entity, relation, number or arrow changed.

## 4. Website

Pages updated from the data: Domain (the Diamond Sutra as "Single manuscript", with the note that the page does not
name it), Models (R1–R19; R17–R19 paragraph; three rows in "Modelling decisions"; evidence counts), TEI, RDF,
Transformations, Wiki View, Files (`run_all.py` listed). The visual design was then upgraded; see section 7.

## 5. Presentation removed

Removed from the package, because the website is used for the oral presentation and these files would no longer
match the data: `presentation.html`, `assets/css/presentation.css`, `assets/js/presentation.js`, `assets/img/fragments/`,
`assets/img/presentation/`, `site_build/build_presentation.py`, `site_build/make_fragments.py`,
`site_build/make_wiki_detail.py`, `validation/presentation_provenance.txt` and `Reconnecting_Dunhuang_Presentation_2_Backup.pdf`.
The Presentation entry on the home page and the presentation step of the build were removed. No remaining page,
script or stylesheet refers to them (checked). The old files are kept in a separate backup archive, outside the
submission package. The visual upgrade (section 7) brought back only the five fragment images and `make_fragments.py`,
which regenerates them pixel for pixel from `manuscript_pelliot_chinois_2778.jpg`. The model PDFs, the Wikipedia source PDF and every other deliverable are kept.

## 6. Remaining limitations

1. **Project URIs not dereferenceable; online version not verified.** The site is not yet published at
   `https://haopuur-max.github.io/reconnecting-dunhuang/`; all checks are local.
2. **The home-page overlay** draws the sixteen relations of the original model (R1–R16); its caption says so.
3. **Below about 1360 px the diagrams scroll sideways** on the Models page ("Fit to width" and "Enlarge" are offered).
   On A4 paper they are small; the diagram PDFs are meant for zooming.
4. **The 868 date** of the Diamond Sutra is in its description, not modelled as a production event (no new class was
   added in the frozen model).
5. **No VIAF or LC record** is given for the Diamond Sutra; it carries its shelfmark and Wikidata item.
6. **RDF/XML statement order** can change between runs (the graph stays isomorphic).

## 7. Visual upgrade of the website (final, 29 October 2026)

The design language of the earlier presentation page (paper, night blue, cinnabar, gold, archival prints and torn
manuscript fragments) was applied to the eight pages. It was built and accepted in a separate draft copy, the frozen
package was backed up (`Reconnecting_Dunhuang_HP_YIN_BACKUP_before_visual_upgrade.zip`, outside this package), and the
draft was then applied. After the replacement the whole chain was run again on this package; it is byte-identical to the
accepted draft. The website is the only entry point for the presentation: there is no `presentation.html` and no
presentation PDF in the package.

### 7.1 What changed, by kind of file (backup vs final, SHA-256 of every file)

| Kind | Files | Change |
|---|---|---|
| Visual design and layout | `assets/css/site.css`, `assets/js/site.js`, 8 page templates, the 8 pages | design system; model viewer; page structure and display text |
| Images and credits | `assets/img/fragments/fragment_1–5.png` (added), `assets/img/IMAGE_CREDITS.md` | fragments of Pelliot chinois 2778 for the home page; credits rewritten from the sources (7.5) |
| Academic data, models, transformations | — | **no change**: 49 files byte-identical, among them the TEI file, Turtle and RDF/XML, `dm-ontology.ttl`, the XSLT and both Python transformations, `run_all.py`, the TEI schema, the source PDF and every model diagram (SVG and PDF) |
| Other | `README.md` (both), `QA_REPORT.md`, `MANIFEST.txt`, `site_acceptance_report.txt`, `build_site_snippets.py` (2 additions: the fragments count as use of item 4 in the credits; `make_fragments.py` listed on the Files page), `site_build/make_fragments.py` (added) | documentation and reports of this version |

Totals: 25 files changed, 6 added, 0 removed, 80 unchanged. The full list is delivered as `CHANGES_visual_upgrade.txt`.

### 7.2 Pages

| Page | Shown first | Check |
|---|---|---|
| Home | research question (cinnabar block); Stein's photograph with the fragments; 01 the problem (five narrative layers, why this topic); 02 the method (five pages); 03 results: four stages, each with its own unit, and R6 followed from the article to the Turtle file (4 code excerpts cut from the files); limitations | numbers recomputed (7.4); no text covered by a fragment at 12 widths |
| Domain | 28 standOff entity records by kind; timeline; Direct and Enriched | no ontology term on the page |
| Models | four-step path; four modelling decisions (colours as in the diagrams: ◇ red-orange, Enriched violet); three diagrams at reading size, "Explore the model" | cards aligned (head, title, text, link) at 1440 and 1100 px |
| TEI | 65 annotations → 28 records → 19 · 38 · 6 relations; file map; code with line numbers | code identical to the file |
| Transformations | pipeline; on phones: the TEI file, then two separate branches (XSLT → HTML, Python + rdflib → RDF) | branches and arrows checked at 320–430 px |
| RDF | the purchase in Turtle; the highlighted line as one triple (checked against the Turtle file when the page is built) | — |
| Files | grouped deliverables; pass/fail table and counts of the RDF report, with the 34 / 28 note; credits | 35 listed files exist with current sizes |
| Wiki View | a title band above the unchanged XSLT output (one `h1`, from the XSLT) | equals the XSLT output |

### 7.3 Model diagrams: separate acceptance

| # | Check | Result |
|---|---|---|
| 1 | Every relation drawn exists in the data: theoretical 19 relations and 16 entities (R9, R12 the only unformalised); core Graffoo 24 usage arcs = data, 30 arcs from the domain class to the range class; second Graffoo 5 class-level arcs = data, 19 example facts found in the Turtle file, 26 arcs checked for direction (build assertions) | PASS |
| 2 | Labels of the theoretical model against the TEI, web and full versions: all 19 relation names match; R1–R15 drawn as Direct (dark), R16–R19 as Enriched (violet, ★); ◇ on R9 and R12 and in the legend | PASS |
| 3 | Graffoo notation: classes as yellow boxes, datatypes as green parallelograms, existing properties as dotted arcs (property facility), `dm:` properties as solid arcs at their declared domain and range, direct subclass arrows only (unchanged since the accepted version) | PASS |
| 4 | Overlap scan of the six SVGs: 0 labels across a box edge; the remaining text-on-text cases are the two-line labels (DUNHUANG / MANUSCRIPTS, R4 / sealed_in, R13 / facilitated_transfer_of), name and class inside the Graffoo examples, and one false hit of a rotated label (`crm:P190_has_symbolic_content`), checked by eye | PASS |
| 5 | Files: the 14 SVGs are byte-identical to the frozen version; the 5 PDFs open (one page each) and render | PASS |
| 6 | Desktop: diagrams at reading size, "Explore the model" opens a full-screen viewer (zoom, Fit, 100 %, Close, SVG and PDF links); Esc and Back close it | PASS |
| 7 | Phones: whole diagram as a thumbnail; tap opens the viewer; pinch 21 % → 103 %; one-finger drag moves the image, not the page; a swipe over the thumbnail scrolls the page; Close and Back return to the same place; labels sharp at 200 % (vector) | PASS |
| 8 | Legends and captions agree with the drawn symbols (Direct solid, Enriched dashed violet, ◇, repeated boxes) | PASS |

### 7.4 Final checks (on this package, after the replacement)

| # | Check | Result |
|---|---|---|
| 1 | `run_all.py`: TEI P5 validation, RDF V1–V7, HTML QA, diagrams, pages, full-site check | PASS (7/7) |
| 2 | Turtle and RDF/XML isomorphic, 683 triples; graph unchanged from the frozen version | PASS |
| 3 | 405 local links, images and anchors, 0 broken; 19 code blocks identical to the cited lines of their files; Wiki View = XSLT output; 35 listed files with current sizes | PASS |
| 4 | Numbers on the pages recomputed from the files: 28 records (5 persons, 5 places, 5 organisations, 6 objects, 7 events), 65 annotations, 16 entities in R1–R19 (all among the 28 records), 19 · 38 · 6 relations, 38 `rdf:Statement`, 683 triples, 17 of 28 records with authority identifiers, 34 resources with a conceptual class | PASS |
| 5 | Cross-page wording: Direct / Enriched, R9 and R12 (◇), R16, R17 P46i, R18 P24, R19 P50 (custody; one case of R9) agree on Home, Domain, Models and in the TEI/RDF | PASS |
| 6 | Headings: no word split across lines and no heading wider than its box, 8 pages × 11 widths (320–1920 px, 1,661 words); no sideways page scroll from 320 to 2560 px | PASS |
| 7 | Offline with every network request blocked: 8 pages, 0 failed requests, 0 broken images, 0 page errors | PASS |
| 8 | The package zipped, unzipped in a new folder and opened from `index.html`: all pages, styles, fonts, images, diagrams and scripts load | PASS |
| 9 | Independent review of the draft by a separate agent: 13 findings, all fixed before acceptance (meaning of story layer IV, R18 value in the R6 case, composite photograph, dropped qualifications, units, Ōtani date, fragment over the credit, second `h1`, template copy, `__pycache__`) | PASS after fixes |

### 7.5 Images: source and reuse

| Image (use) | Original work | Digital copy | Reuse conditions | Credit on the site |
|---|---|---|---|---|
| Cave 16, 1907 (home cover, overlay) | photograph by Aurel Stein (1862–1943); per the article, the piles of manuscripts near the doorway were added from another negative | Commons file, source given as the Early Tibet Blog; no holding institution named | Commons: public domain in the United States (published before 1931); no source-country tag on the page | "Photograph by Aurel Stein; Wikimedia Commons, public domain (US)" |
| Pelliot chinois 2778 (five fragments) | BnF, Manuscrits, Pelliot chinois 2778, about 800–1000, unknown author (BnF catalogue record) | Commons file from the BnF; the BnF record links two Gallica scans (from the original and from microfilm) | Commons: PD-old-100, Public Domain Mark. BnF/Gallica: non-commercial reuse free with the source credit; commercial reuse under licence; French law | "Pelliot chinois 2778, Bibliothèque nationale de France. Source gallica.bnf.fr / BnF (via Wikimedia Commons), public domain" |
| Paul Pelliot in Cave 17, 1908 (home, Domain) | photograph by Charles Nouette (1869–1910) | Commons file, source Musée Guimet | Commons: PD-old-70, Public Domain Mark | "Photograph by Charles Nouette. Wikimedia Commons, public domain" |
| Wang Yuanlu, 1921 (Domain) | photograph by Aurel Stein | Commons file | Commons: PD-Art (PD-old-70), Public Domain Mark | credited on the Files page |

The use here (a non-commercial academic project) is compatible with all of these conditions, provided the credits are
kept. Details per image are in `assets/img/IMAGE_CREDITS.md`.

### 7.6 Still open, and whether it affects the submission

1. **Images, not fully verifiable from here** — which Gallica scan the Pelliot Commons file comes from (Gallica showed
   a security check that only a person can complete); the missing United States tag on three Commons pages; no
   source-country tag and no holding institution for the Cave 16 photograph. *Effect on the submission: none for a
   non-commercial academic use; recorded, not presented as confirmed.*
2. **Display text written for this version** (research question, "Why this topic", stage labels, card summaries) was
   confirmed by the author. The frozen home page's subtitle, lead sentence and "The report" heading were replaced on
   purpose. *No effect.*
3. **Unchanged from the frozen version**: the inner pages' menu has no Home or Wiki View entry (the wordmark leads home;
   the Wiki View is linked from Home, Transformations and Files); the history paragraph on Home and Domain says the
   cache "was sold from 1907 to … Ōtani Kōzui and others" (the article gives no date for Ōtani; the story layer III now
   says so); the overlay draws the original sixteen relations (R1–R16), as its caption says. *No effect on the data.*
4. **Limitations of section 6** still apply (URIs not dereferenceable; the online version not verified). *Known and
   documented.*

### 7.7 Fix after the author's test in Safari (31 October 2026)

**Found by the author** on her Mac in Safari: in the enlarged views, a trackpad pinch zoomed the whole page instead of the
figure. Two causes: (1) the four secondary figures (core classes and instance graph on Models, the purchase case on
Models, the dataset graph on RDF) still used the simple enlarge box, which has no zoom; (2) Safari on macOS sends pinches
as WebKit gesture events, which the viewer did not handle (Chromium sends ctrl + wheel, which it did handle — the tests
had used Chromium only).

**Fix, in `assets/js/site.js` only:** every zoomable figure opens the full-screen viewer (an inline SVG is shown as an
image of the same markup); while the viewer is open, gesture events and ctrl + wheel zoom the figure and never the
page; the zoom limit is relative to the fitted size (up to six times), so small figures can also be enlarged. No page,
figure file or data changed.

**Checked:** all 7 zoomable figures (3 model diagrams, 4 secondary figures) open the viewer with the figure loaded;
a simulated Safari pinch (gesture events) zooms the figure and is prevented from zooming the page; ctrl + wheel the
same; Esc closes; with the viewer closed, page gestures are untouched; phone tests (tap, pinch, drag, Close, Back)
unchanged; `run_all.py` 7/7; 405 links, 19 code blocks identical. Compared with the version of 29 October only
`site.js` changed (and the dates in the generated reports). **Safari on a real Mac: PASS — manually verified by the
project author** (pinch zoom enlarges the figure only); this is a manual check, not an automated test.

## 8. Final technical round and acceptance (31 October 2026)

Every result below comes from tests **run in this round**, on a fresh unzip of the submission ZIP unless stated;
earlier results are not carried over. Legend: **PASS** run and passed · **FAIL** run and failed · **NOT VERIFIED** could not
be run here · **NOT APPLICABLE**.

Test environment: Linux, Python 3.13, lxml 6.1.3 (libxml2 2.14.6), rdflib 7.6.0, Pillow 12.3, Playwright with
Chromium, Graphviz 2.43, xmllint (libxml2 2.9.14). Source Sans 3 is not installed system-wide (see A5).

### A. Build and reproducibility

| # | Check | Result | Evidence |
|---|---|---|---|
| A1 | `python3 final_report_files/run_all.py` on a fresh unzip, clean environment (empty HOME, PATH with only python3, dot, xmllint) | PASS | 7/7 steps PASS: TEI validation, RDF V1–V7, XSLT + HTML QA, diagrams from the RDF, theoretical model and Graffoo diagrams, pages, full-site check |
| A2 | Same, with `xmllint` removed from the PATH | PASS | 7/7; the report reads "Validator: lxml … RelaxNG (libxml2 2.14.6), same schema" |
| A3 | `xmllint` and lxml give the same verdict | PASS | TEI file: valid / valid. Unknown element, attribute not allowed on `relation`, title removed: invalid / invalid |
| A4 | Missing dependency is reported before building | PASS | `RD_CHROMIUM` set to a missing file: "Missing … RESULT: FAIL (missing dependencies; nothing was built)" |
| A5 | Rebuilt outputs equal the files in the ZIP | PASS | TEI unchanged (SHA-256 before = after). Turtle and RDF/XML: 683 = 683 triples, isomorphic with the ZIP version. The 14 diagram SVGs and all pages are byte-identical. Differences, all expected: the 5 PDFs (creation time only; text identical), RDF/XML statement order and `rdf.html` (which prints that file; identical apart from that listing), and in A2 the validator line of the TEI report |
| A6 | Diagram rendering needs no network; local Chromium can be given (`RD_CHROMIUM`) | PASS | Rendering with `RD_CHROMIUM`: PASS; web requests blocked by design; fonts embedded as data URIs |
| A7 | Diagram rendering in a sandbox that forbids local files to the browser (the independent check's environment) | NOT VERIFIED | Environment limit (`ERR_BLOCKED_BY_ADMINISTRATOR`), not a project fault; A1 shows the step in a normal environment |
| A8 | Font for Graphviz text metrics (Source Sans 3) installed on the build machine | NOT APPLICABLE | Only affects spacing in the instance and core-class diagrams if regenerated without it; the shipped SVGs were reproduced byte for byte here |

### B. Data and semantic consistency

| # | Check | Result | Evidence |
|---|---|---|---|
| B1 | TEI P5 valid (RELAX NG, `tei_all.rng` 4.12.0) | PASS | A1, A2 |
| B2 | RDF checks V1–V7 | PASS | `rdf_qa_report.txt`, 7 × PASS |
| B3 | Turtle and RDF/XML: same graph | PASS | 683 triples each, isomorphic |
| B4 | XML → HTML: Wiki View = XSLT output; TEI unchanged | PASS | site check 3; HTML QA |
| B5 | R1–R19 complete; R1–R15 Direct, R16–R19 Enriched; every conceptual relation points to its proposition with the same evidence | PASS | script on the TEI file |
| B6 | R9, R12: no holding triple (no `P50` from the corpus to the BL; the Tokyo National Museum never an object) | PASS | `P50` only for pelliot-portion → BnF, remaining-chinese-manuscripts → NLC, diamond-sutra-868 → BL |
| B7 | R17 `P46i` (E19 → E18), R18 `P24` from the existing purchase (E96 → E19), R19 `P50` (custody; `P52` unused); the Diamond Sutra has no further claims (only labels, identifiers, a note) | PASS | triples checked in the Turtle file |
| B8 | Enriched relations carry their sources (`dcterms:source`), Direct ones none | PASS | cr30, cr38, cr39, cr40 with IDP URLs; V7 |
| B9 | Domain and range of the 37 CRM-family and `dm:` relations | PASS | V2 |
| B10 | Diagrams against the data: 19 relations and 16 entities, R9 and R12 the only unformalised; 24 usage arcs = data, 30 arcs from domain to range; 5 class-level arcs, 19 example facts in the Turtle file, 26 arcs checked for direction | PASS | build assertions in A1 |
| B11 | 19 code excerpts identical to the cited lines | PASS | site check 2 |
| B12 | Numbers on the pages | PASS | 28 records, 65 annotations, 16 entities, 19 · 38 · 6 relations, 683 triples, all recomputed from the files |

### C. Website in a browser (Chromium, the shipped files, network blocked)

| # | Check | Result | Evidence |
|---|---|---|---|
| C1 | 8 pages open; 0 console errors, 0 failed requests, 0 broken images | PASS | desktop 1,440 px and phone 390 px |
| C2 | Navigation: all home links (8/8) open; "Next" chain Domain → Models → TEI → Transformations → RDF → Files | PASS | |
| C3 | In-page anchors: Domain 4/4, Models 6/6, TEI 5/5, Transformations 4/4, RDF 5/5, Files 3/3 reached | PASS | |
| C4 | Code: 19 blocks with syntax highlighting (Prism tokens) and line numbers | PASS | |
| C5 | Layout: no sideways scroll and no split word in any heading (8 pages, 320–2,560 px, 1,661 words) | PASS | |
| C6 | No text cut off inside a frame (8 pages × 9 widths) | PASS **after fix** | Found in this round: Wiki View cut off on phones and long URLs at 861–1,099 px (both present since before the visual upgrade); two card labels at 320 px. Fixed in `site.css` (CHANGELOG 3) |
| C7 | Viewer, desktop: the 7 zoomable figures open full screen; zoom buttons, ctrl + wheel and simulated Safari gesture events zoom the figure, not the page; Esc closes | PASS | |
| C8 | Viewer, phone (touch emulation): tap opens; pinch 21 % → 103 %; one-finger drag moves the image, not the page; Close and Back return to the same place | PASS | |
| C9 | Safari, real Mac, trackpad pinch in the viewer | PASS | manually verified by the project author (not automated) |
| C10 | Real iPhone / Android, Firefox | NOT VERIFIED | no such device or browser in this environment |
| C11 | Offline: the unzipped site opened from `index.html` with every network request blocked | PASS | C1 |

### D. Course guidelines (Guidelines for a LODLAM project, a.y. 2025–2026)

| Requirement | Result | Where |
|---|---|---|
| Idea from an identifiable Wikipedia page | PASS | "Dunhuang manuscripts", revision 1347007263 (Domain; TEI `sourceDesc`; PDF snapshot) |
| At least 10 entities | PASS | 16 in the theoretical model; 28 entity records in the TEI |
| Theoretical model: relations in natural language/graphic; indirect relations; authority links; subjects | PASS | theoretical model diagram (R1–R19, events and Enriched relations, identifier chips, subjects of the corpus) |
| Conceptual model reusing existing ontologies, with justification; new terms only where none fits; Graffoo diagram | PASS | Models: ontologies used, modelling decisions, three `dm:` properties with the properties considered; two Graffoo diagrams |
| TEI with the page text and at least 10 annotated entities: real-world entities, concepts, textual phenomena | PASS | 65 entity annotations; 23 concept terms; 3 quotations, 36 citation references |
| Entities described in dedicated TEI elements and reconciled to authority files | PASS | listPerson, listPlace, listOrg, listObject, listEvent, listRelation, listBibl; 45 identifiers (Wikidata, VIAF, LC, LCSH, FAST, WorldCat, BL shelfmark) |
| XML → HTML transformation (Python and/or XSLT) and the output | PASS | `tei_to_html.xsl`, `transform_tei_to_html.py`, `reconnecting_dunhuang.html`, Wiki View |
| XML/TEI → RDF transformation (Python) for the whole set of entities and relations of the ontology | PASS | `transform_tei_to_rdf.py`; V5: all 38 conceptual and 6 subject relations present. R9 and R12 are theoretical only, by design (B6) |
| Report, preferably a web page, with all files | PASS | the website; Files page lists 35 deliverables |
| Individual project | PASS | author HAOPU YIN (TEI `titleStmt`) |

### E. Status

No test failed. The items not verified are environment limits (A7, C10), not project faults.

**FINAL STATUS: READY FOR SUBMISSION — FROZEN** (31 October 2026).

