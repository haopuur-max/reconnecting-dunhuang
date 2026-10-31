#!/usr/bin/env python3
"""
Full-site acceptance check for the Reconnecting Dunhuang Web Report.
Run after the whole chain (see README). Writes final_report_files/validation/site_acceptance_report.txt
and exits with an error if any check fails.

Checks
  1. every local link, image and #anchor on the eight pages resolves
  2. every code block on the pages is identical to the lines of the file it cites
  3. the Wiki View is the XSLT output (re-runs the stylesheet and compares)
  4. every file listed on the Files page exists and its displayed size is current
  5. the QA reports all pass (TEI validation, RDF V1-V7, HTML QA)
  6. Turtle and RDF/XML are isomorphic
  7. the Domain page contains no ontology class or property names
"""

import html
import os
import re
import sys
import urllib.parse
from datetime import date
from pathlib import Path

from lxml import etree
from lxml import html as LH
from rdflib import Graph, compare

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_site_snippets as build  # noqa: E402

PAGES = [p[0] for p in build.PAGES]
CODE_SOURCES = [
    "final_report_files/tei_xml/reconnecting_dunhuang.xml",
    "final_report_files/xml_to_rdf/reconnecting_dunhuang.ttl",
    "final_report_files/xml_to_rdf/reconnecting_dunhuang.rdf",
    "final_report_files/xml_to_html/tei_to_html.xsl",
    "final_report_files/xml_to_html/transform_tei_to_html.py",
    "final_report_files/xml_to_rdf/transform_tei_to_rdf.py",
    "README.md",
]


def main():
    lines, failures = [], []
    texts = {p: (ROOT / p).read_text(encoding="utf-8") for p in PAGES}
    ids = {p: set(re.findall(r'\bid="([^"]+)"', t)) for p, t in texts.items()}

    # 1 links and anchors
    n_links, bad = 0, []
    for p in PAGES:
        for el in LH.parse(str(ROOT / p)).getroot().xpath("//*[@href or @src]"):
            u = el.get("href") or el.get("src")
            if u.startswith(("http", "mailto", "data:")):
                continue
            n_links += 1
            path, _, frag = u.partition("#")
            target = urllib.parse.unquote(path) or p
            if not (ROOT / target).exists():
                bad.append(f"{p}: {u}")
            elif frag and target in ids and frag not in ids[target]:
                bad.append(f"{p}: {u}")
    failures += bad
    lines.append(f"1 Local links, images and anchors: {n_links} checked, {len(bad)} broken")

    # 2 code blocks identical to their files
    sources = [(ROOT / s).read_text(encoding="utf-8").split("\n") for s in CODE_SOURCES]
    n_blocks, diff = 0, []
    for p, t in texts.items():
        for m in re.finditer(r'<pre class="([^"]*)" data-start="(\d+)"[^>]*><code[^>]*>(.*?)</code></pre>', t, flags=re.S):
            n_blocks += 1
            start = int(m.group(2))
            code = html.unescape(m.group(3)).split("\n")
            if not any(code == s[start - 1:start - 1 + len(code)] for s in sources):
                diff.append(f"{p}: block at line {start}")
    failures += diff
    lines.append(f"2 Code blocks identical to the cited files: {n_blocks} checked, {len(diff)} different")

    # 3 Wiki View is the XSLT output
    try:
        view = build.wiki_view()
        same = view in texts["wiki-view.html"]
    except SystemExit as e:
        same = False
        failures.append(str(e))
    if not same:
        failures.append("wiki-view.html does not contain the current XSLT output")
    lines.append(f"3 Wiki View equals the XSLT output (stylesheet re-run with base=''): {'PASS' if same else 'FAIL'}")

    # 4 Files page listing
    listed, stale = 0, []
    for group, items in build.FILE_GROUPS:
        for path, desc in items:
            listed += 1
            if not (ROOT / path).exists():
                stale.append(f"missing: {path}")
                continue
            size = build.human_size((ROOT / path).stat().st_size)
            if f'href="{path}"' not in texts["files.html"] or size not in texts["files.html"]:
                stale.append(f"not current on the page: {path}")
    failures += stale
    lines.append(f"4 Files page: {listed} listed deliverables exist and are shown with current sizes; {len(stale)} problems")

    # 5 QA reports
    fr = ROOT / "final_report_files"
    tei_ok = "Relax NG validation: PASS" in (fr / "validation/tei_validation_report.txt").read_text(encoding="utf-8")
    rdf_txt = (fr / "xml_to_rdf/rdf_qa_report.txt").read_text(encoding="utf-8")
    rdf_ok = rdf_txt.rstrip().endswith("RESULT: PASS") and len(re.findall(r"^  V\d .*: PASS$", rdf_txt, flags=re.M)) == 7
    html_ok = (fr / "xml_to_html/html_qa_report.txt").read_text(encoding="utf-8").strip().endswith("HTML QA PASS")
    for name, ok in (("TEI validation", tei_ok), ("RDF V1-V7", rdf_ok), ("HTML QA", html_ok)):
        if not ok:
            failures.append(f"{name} does not pass")
    lines.append(f"5 QA reports: TEI validation {'PASS' if tei_ok else 'FAIL'}, RDF V1-V7 {'PASS' if rdf_ok else 'FAIL'}, HTML QA {'PASS' if html_ok else 'FAIL'}")

    # 6 isomorphism
    g1 = Graph().parse(fr / "xml_to_rdf/reconnecting_dunhuang.ttl", format="turtle")
    g2 = Graph().parse(fr / "xml_to_rdf/reconnecting_dunhuang.rdf", format="xml")
    iso = compare.isomorphic(g1, g2)
    if not iso:
        failures.append("Turtle and RDF/XML are not isomorphic")
    lines.append(f"6 Turtle ({len(g1)} triples) and RDF/XML ({len(g2)} triples) isomorphic: {'PASS' if iso else 'FAIL'}")

    # 7 Domain page wording
    leak = re.findall(r"\b(?:crm|crmsci|crmdig):\w+|\b[EDS]\d{1,3}_[A-Z]\w*", texts["domain.html"])
    if leak:
        failures.append(f"Domain page contains ontology terms: {sorted(set(leak))}")
    lines.append(f"7 Domain page free of ontology class and property names: {'PASS' if not leak else 'FAIL'}")

    report = [f"=== Reconnecting Dunhuang - site acceptance report ===", f"Generated: {date.today().isoformat()}",
              f"Pages: {', '.join(PAGES)}", "", *lines, ""]
    report += (["RESULT: FAIL", *[f"  - {f}" for f in failures]] if failures else ["RESULT: PASS"])
    out = "\n".join(report) + "\n"
    (fr / "validation/site_acceptance_report.txt").write_text(out, encoding="utf-8")
    print(out)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
