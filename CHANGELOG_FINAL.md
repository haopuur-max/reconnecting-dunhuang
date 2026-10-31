# CHANGELOG — final technical round (31 October 2026)

Scope: technical fixes found in the final independent checks. **No change to the TEI file, the RDF (Turtle and
RDF/XML), the ontology, the XSLT, the Python transformations, the model diagrams (SVG, PDF) or the research content.**
Those files are byte-identical to the version of 31 October (morning); the RDF graph has 683 triples, isomorphic.

## 1. `reconnecting-dunhuang/final_report_files/run_all.py`

- **Problem.** In a fresh environment without `xmllint`, the one-command build stopped at the first step with
  `FileNotFoundError: 'xmllint'` (found by the independent check). A missing Graphviz, Pillow or Chromium would also only
  show up half-way through the build.
- **Change.**
  - Every tool is checked before anything is built. A missing one stops the run with the command to install it, and
    nothing is built ("RESULT: FAIL (missing dependencies)").
  - The TEI is validated with `xmllint` if it is installed. Otherwise lxml (`lxml.etree.RelaxNG`) is used, which runs
    the same libxml2 RELAX NG validator on the **same schema** `schemas/tei_all.rng`. Nothing is skipped and the
    standard is not lowered. The report states which validator was used, and file names in it are relative.
  - With `--skip-diagrams`, the two diagram steps are reported as **NOT RUN** (before: "skipped"), and the result reads
    "PASS for the steps run".
- **Checked.**
  - `xmllint` and lxml gave the same verdict on four files: the TEI file (valid with both), a copy with an unknown
    element (`personName`), a copy with an attribute not allowed on `relation`, and a copy with the title removed
    (invalid with both).
  - Full build from a fresh unzip, once with `xmllint` and once with `xmllint` removed from the PATH: 7/7 PASS both
    times.
  - The dependency check was shown to stop the run when Chromium is unavailable.
- **Academic data or model semantics changed:** no.

## 2. `reconnecting-dunhuang/final_report_files/models/graffoo/render.py`

- **Problem.** The script started Playwright's Chromium with no way to use an installed browser, and gave no clear
  message when Chromium was missing. In the independent check, the Playwright download failed, and a system Chromium was
  refused by that environment's policy (`ERR_BLOCKED_BY_ADMINISTRATOR`, a sandbox restriction on local files).
- **Change.**
  - An installed Chromium/Chrome can be given in the environment variable `RD_CHROMIUM`.
  - A clear error message with the install command (`python3 -m playwright install chromium`) is shown when Chromium is
    missing.
  - Any request that is not a local file is blocked and reported as an error. Rendering needs no network: the page is a
    local file and the fonts are embedded in the SVGs as data URIs.
  - The temporary HTML file is always removed.
- **Checked.**
  - A test SVG rendered with `RD_CHROMIUM` set to an installed Chromium.
  - A wrong `RD_CHROMIUM` path gives the clear message.
  - The full build regenerates the three diagrams with all their checks against the data. The regenerated SVGs are
    byte-identical; the PDFs differ only in their creation time (`pdftotext` output identical).
- **Not fixable in the project:** a sandbox that forbids a browser to open local files (as in the independent check)
  cannot run step 4b. This is recorded as an environment limit, not as a pass.
- **Academic data or model semantics changed:** no.

## 3. `reconnecting-dunhuang/assets/css/site.css`

- **Problem 1, Wiki View (present since before the visual upgrade).** Below 860 px, the XSLT output's own layout
  switches to one column defined as `1fr`. That column could not shrink below its longest line, so the article was 784
  px wide inside a 358 px frame and its text was cut off on phones. Between 861 and 1,099 px, two long web-archive URLs
  in the references ran out of the frame.
- **Problem 2, Models.** On a 320 px screen, two labels of the "Four modelling decisions" cards were cut short with "…".
- **Change.**
  - Three CSS rules in the site's stylesheet: the Wiki View column may shrink to the screen (`minmax(0, 1fr)`), and long
    unbroken strings wrap.
  - The card labels wrap below 420 px.
  - The XSLT and its HTML output are not changed: the site check still finds the Wiki View equal to the XSLT output.
- **Checked.** The new check "text cut off by a clipping container" (8 pages × 9 widths, 320–1,920 px) finds 0 cases.
  The Wiki View was checked at 17 widths (320–2,560 px) with 0 elements outside its frame. The decision cards keep their
  alignment on desktop.
- **Academic data or model semantics changed:** no.

## 4. `reconnecting-dunhuang/assets/js/site.js` (earlier the same day, 31 October)

- **Problem.** In Safari on macOS, a trackpad pinch in an enlarged figure zoomed the whole page. The four secondary
  figures had no zoom at all.
- **Change.**
  - All 7 zoomable figures open the full-screen viewer.
  - WebKit gesture events and ctrl + wheel zoom the figure, not the page.
  - The zoom limit is relative to the fitted size.
- **Checked.**
  - Automated: simulated gesture events and ctrl + wheel on all 7 figures; phone touch tests.
  - Manual, by the project author: pinch zoom on her Mac in Safari.
- **Academic data or model semantics changed:** no.

## 5. Documentation and reports

- `README.md` and `reconnecting-dunhuang/README.md`: how to install each dependency, the lxml route, `RD_CHROMIUM`,
  `--skip-diagrams`.
- `QA_REPORT.md`: section 7.7 (Safari) and section 8 (this round, with PASS / FAIL / NOT VERIFIED / NOT APPLICABLE).
- `CHANGELOG_FINAL.md`: this file.
- `MANIFEST.txt`: regenerated.
- `files.html`: the size shown for `run_all.py` (4 KB → 7 KB), regenerated by the build.

## 6. Online publication (31 October 2026)

- **What happened.** The package was pushed to `haopuur-max/reconnecting-dunhuang`, replacing the September version (which
  stays in the git history). The GitHub Pages workflow now publishes the `reconnecting-dunhuang/` folder instead of the
  old `output/` folder, so the site's address matches the project namespace.
- **Text corrected.** The statements "not yet published / online not verified" became false and were updated: both
  READMEs, QA_REPORT section 6, the URIs paragraph on the RDF page (template `rdf.html`), and limitation 3 on the home
  page (`index.html` and its reference copy). The URIs are still not dereferenceable, and the text says so.
- **Checked.** QA_REPORT section 8.F.
- **Academic data or model semantics changed:** no.

