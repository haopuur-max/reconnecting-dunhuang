#!/usr/bin/env python3
"""Draw the three published model diagrams and their PDFs.

    Theoretical model                                  Reconnecting_Dunhuang_Theoretical_Model_FINAL(.svg | _full.svg | .pdf)
    Conceptual model, core (Graffoo)                   conceptual_model_core_graffoo(...)
    Conceptual model, subjects, identifiers, evidence  conceptual_model_subjects_identifiers_evidence_graffoo(...)

Each diagram has a web version (.svg, shown on the Models page) and a full version (_full.svg, rendered to the .pdf) with
the complete notes, legend, prefixes and tables. Both are drawn by the same script from the TEI file and the Turtle file;
every script stops if what it draws differs from the data (arcs, directions, example facts, counts).

Run after transform_tei_to_rdf.py:   python3 final_report_files/models/graffoo/build_model_diagrams.py
Requires: rdflib, lxml, Pillow (text metrics) and Playwright with Chromium (PDF).
"""
import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from paths import NAMES, OUT, out  # noqa: E402
from render import render  # noqa: E402

for script in ("theoretical.py", "core_graffoo.py", "doc_graffoo.py"):
    runpy.run_path(str(HERE / script), run_name="__main__")
for kind, stem in NAMES.items():
    render(out(kind, "full"), pdf=OUT / f"{stem}.pdf")
    print(f"  {stem}: web SVG, full SVG, PDF")
