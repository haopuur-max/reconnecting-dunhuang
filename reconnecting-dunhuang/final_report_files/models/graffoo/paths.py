"""Locations used by the model-diagram scripts, relative to this folder (final_report_files/models/graffoo)."""
from pathlib import Path

HERE = Path(__file__).resolve().parent
FRF = HERE.parents[1]                                   # final_report_files
SITE = FRF.parent                                       # website root
TTL = FRF / "xml_to_rdf" / "reconnecting_dunhuang.ttl"
TEI = FRF / "tei_xml" / "reconnecting_dunhuang.xml"
OUT = FRF / "models"                                    # published diagrams
WOFF2 = SITE / "assets" / "fonts"                       # fonts embedded in the SVGs
TTF = HERE / "fonts"                                    # the same fonts as TTF, for measuring text

# published file names: (web SVG, full SVG, PDF made from the full SVG)
NAMES = {
    "theoretical": "Reconnecting_Dunhuang_Theoretical_Model_FINAL",
    "core": "conceptual_model_core_graffoo",
    "doc": "conceptual_model_subjects_identifiers_evidence_graffoo",
}


def out(kind, mode):
    return OUT / (NAMES[kind] + ("" if mode == "web" else "_full") + ".svg")
