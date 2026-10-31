#!/usr/bin/env python3
"""
Reconnecting Dunhuang - rebuild and check everything with one command.

    python3 final_report_files/run_all.py          (from the website root, or from anywhere)

Steps, in order (the run stops at the first step that fails):
  0. dependency check: every tool a step needs is looked up first; a missing one stops the run with the command to install it
  1. TEI validation against TEI P5 (RELAX NG schema tei_all.rng, with xmllint; if xmllint is not installed, with
     lxml, which runs the same libxml2 RELAX NG validator on the same schema) -> validation/tei_validation_report.txt
  2. TEI -> RDF (Turtle + RDF/XML) with checks V1-V7     -> xml_to_rdf/rdf_qa_report.txt
  3. TEI -> HTML with the XSLT stylesheet and HTML QA     -> xml_to_html/html_qa_report.txt
  4. model diagrams from the RDF dataset (instance graph, core classes, case diagrams)
  5. theoretical model and the two Graffoo diagrams, with their checks against the data
  6. website pages
  7. full-site check (links, code excerpts, Wiki View, files, QA reports) -> validation/site_acceptance_report.txt

Optional: --skip-diagrams leaves steps 4-5 out (they need Graphviz, Pillow and Playwright with Chromium); the summary then
marks them NOT RUN and the result is not a full PASS.
Chromium: Playwright's own browser (`python3 -m playwright install chromium`), or an installed Chromium/Chrome given in
the environment variable RD_CHROMIUM (path to the executable).
"""

import importlib.util
import os
import shutil
import subprocess
import sys
import time
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]          # the website root (reconnecting-dunhuang/)
F = "final_report_files"
TEI = f"{F}/tei_xml/reconnecting_dunhuang.xml"
RNG = f"{F}/schemas/tei_all.rng"

STEPS = [
    ("TEI validation (TEI P5, RELAX NG)", None),
    ("TEI -> RDF, checks V1-V7", [sys.executable, f"{F}/xml_to_rdf/transform_tei_to_rdf.py"]),
    ("TEI -> HTML (XSLT), HTML QA", [sys.executable, f"{F}/xml_to_html/transform_tei_to_html.py"]),
    ("Model diagrams from the RDF", [sys.executable, f"{F}/models/generate_model_diagrams.py"]),
    ("Theoretical model and Graffoo diagrams", [sys.executable, f"{F}/models/graffoo/build_model_diagrams.py"]),
    ("Website pages", [sys.executable, f"{F}/site_build/build_site_snippets.py"]),
    ("Full-site check", [sys.executable, f"{F}/site_build/check_site.py"]),
]
DIAGRAM_STEPS = {"Model diagrams from the RDF", "Theoretical model and Graffoo diagrams"}


def validate_with_lxml(rng, tei):
    """The same RELAX NG validation as xmllint, through lxml (both use libxml2's validator)."""
    from lxml import etree
    schema = etree.RelaxNG(etree.parse(str(rng)))
    ok = schema.validate(etree.parse(str(tei)))
    name = os.path.relpath(tei, ROOT)
    errors = [f"{name}:{e.line}: {e.message}" for e in schema.error_log]
    return ok, "\n".join(errors) if errors else f"{name} validates"


def validate_tei(tei=TEI):
    if shutil.which("xmllint"):
        cmd = ["xmllint", "--noout", "--relaxng", RNG, tei]
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        out = (r.stdout + r.stderr).strip()
        ok = r.returncode == 0
        engine = f"Command: {' '.join(cmd)}"
    else:
        from lxml import etree
        ok, out = validate_with_lxml(ROOT / RNG, ROOT / tei)
        engine = (f"Validator: lxml {etree.__version__} RelaxNG (libxml2 {'.'.join(map(str, etree.LIBXML_VERSION))}), "
                  f"same schema; xmllint is not installed")
    report = "\n".join([
        f"Validation file: {tei}",
        f"Schema: {RNG} (TEI P5 Version 4.12.0)",
        f"Date: {date.today().isoformat()}",
        engine,
        out,
        f"TEI P5 Relax NG validation: {'PASS' if ok else 'FAIL'}",
    ]) + "\n"
    (ROOT / F / "validation" / "tei_validation_report.txt").write_text(report, encoding="utf-8")
    return ok, out


def chromium_ok():
    """Playwright can start Chromium: RD_CHROMIUM, or Playwright's own browser."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return False, "the Python package playwright is not installed (pip install playwright)"
    exe = os.environ.get("RD_CHROMIUM")
    if exe and not Path(exe).is_file():
        return False, f"RD_CHROMIUM points to {exe}, which does not exist"
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(executable_path=exe) if exe else p.chromium.launch()
            b.close()
        return True, ""
    except Exception as e:  # noqa: BLE001
        first = str(e).strip().splitlines()[0] if str(e).strip() else type(e).__name__
        return False, (f"Playwright cannot start Chromium ({first}). Install it with `python3 -m playwright install "
                       f"chromium`, or set RD_CHROMIUM to an installed Chromium/Chrome")


def check_dependencies(skip_diagrams):
    """Find every missing tool before anything is built, so the run never stops half-way for a missing program."""
    missing = []
    for mod, pip in (("lxml", "lxml"), ("rdflib", "rdflib")):
        if importlib.util.find_spec(mod) is None:
            missing.append(f"Python package {mod} (pip install {pip})")
    if not skip_diagrams:
        if shutil.which("dot") is None:
            missing.append("Graphviz `dot` (e.g. apt install graphviz / brew install graphviz)")
        if importlib.util.find_spec("PIL") is None:
            missing.append("Python package Pillow (pip install pillow)")
        ok, why = chromium_ok()
        if not ok:
            missing.append(why)
    return missing


def main():
    skip_diagrams = "--skip-diagrams" in sys.argv
    print("=== Dependencies ===")
    print("  xmllint:", shutil.which("xmllint") or "not installed - TEI validation will use lxml with the same RELAX NG schema")
    missing = check_dependencies(skip_diagrams)
    if missing:
        print("Missing, install before running (or use --skip-diagrams for steps 4-5 only):")
        for m in missing:
            print("  -", m)
        print("\nRESULT: FAIL (missing dependencies; nothing was built)")
        return 2
    print("  all required tools found")
    results = []
    for name, cmd in STEPS:
        if skip_diagrams and name in DIAGRAM_STEPS:
            results.append((name, "NOT RUN", 0.0))
            continue
        print(f"\n=== {name} ===", flush=True)
        t0 = time.time()
        if cmd is None:
            ok, out = validate_tei()
            print(out)
        else:
            r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
            ok = r.returncode == 0
            tail = (r.stdout + r.stderr).strip().splitlines()
            print("\n".join(tail[-12:]))
        results.append((name, "PASS" if ok else "FAIL", time.time() - t0))
        if not ok:
            break
    print("\n=== Summary ===")
    for name, status, secs in results:
        print(f"  {status:<8} {name}  ({secs:.0f} s)")
    failed = any(s == "FAIL" for _, s, _ in results)
    partial = any(s == "NOT RUN" for _, s, _ in results)
    print("\nRESULT:", "FAIL" if failed else ("PASS for the steps run (diagram steps NOT RUN)" if partial else "PASS"))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
