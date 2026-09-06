#!/usr/bin/env python3
"""Transform the final Reconnecting Dunhuang TEI file to HTML and QA the result."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
from typing import Iterable

from lxml import etree, html


TEI_NS = {"tei": "http://www.tei-c.org/ns/1.0"}
SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_TEI = SCRIPT_DIR.parent / "tei_xml" / "reconnecting_dunhuang.xml"
DEFAULT_XSL = SCRIPT_DIR / "tei_to_html.xsl"
DEFAULT_HTML = SCRIPT_DIR / "reconnecting_dunhuang.html"
DEFAULT_QA_REPORT = SCRIPT_DIR / "html_qa_report.txt"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_tei(path: Path) -> etree._ElementTree:
    parser = etree.XMLParser(remove_blank_text=False, resolve_entities=False)
    return etree.parse(str(path), parser)


def transform(tei_path: Path, xsl_path: Path, html_path: Path) -> None:
    tei_doc = parse_tei(tei_path)
    xsl_doc = etree.parse(str(xsl_path))
    result = etree.XSLT(xsl_doc)(tei_doc)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_bytes(etree.tostring(result, method="html", encoding="UTF-8", pretty_print=True))


def norm_ref(value: str | None) -> str:
    return (value or "").lstrip("#")


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def ids(elements: Iterable[etree._Element]) -> set[str]:
    return {element.get("{http://www.w3.org/XML/1998/namespace}id") for element in elements}


def text_content(element: etree._Element) -> str:
    return " ".join("".join(element.itertext()).split())


def display_path(path: Path) -> str:
    resolved = path.resolve()
    package_root = SCRIPT_DIR.parents[2]
    try:
        return str(resolved.relative_to(package_root))
    except ValueError:
        return str(path)


def tei_relation_signature(relation: etree._Element) -> tuple[str, str, str, str, str, str, str]:
    relation_id = relation.get("{http://www.w3.org/XML/1998/namespace}id") or ""
    return (
        relation_id,
        relation.get("active") or "",
        relation.get("passive") or "",
        relation.get("mutual") or "",
        relation.get("name") or "",
        relation.get("corresp") or "",
        relation.get("ana") or "",
    )


def qa_html(tei_path: Path, html_path: Path) -> tuple[bool, str]:
    failures: list[str] = []
    tei_doc = parse_tei(tei_path)
    html_doc = html.parse(str(html_path))
    root = html_doc.getroot()

    body_section_ids = ["lead", "history", "studies", "languages-scripts", "buddhist-texts", "other-textual-genres"]
    back_section_ids = ["see-also", "references", "cited-works", "further-reading", "external-links"]

    tei_standoff_nodes = (
        tei_doc.xpath("//tei:standOff/tei:listPerson/tei:person", namespaces=TEI_NS)
        + tei_doc.xpath("//tei:standOff/tei:listPlace/tei:place", namespaces=TEI_NS)
        + tei_doc.xpath("//tei:standOff/tei:listOrg/tei:org", namespaces=TEI_NS)
        + tei_doc.xpath("//tei:standOff/tei:list[@xml:id='aggregate-holdings']/tei:item", namespaces=TEI_NS)
        + tei_doc.xpath("//tei:standOff/tei:list[@xml:id='digital-objects']/tei:item", namespaces=TEI_NS)
        + tei_doc.xpath("//tei:standOff/tei:list[@xml:id='time-spans']/tei:item", namespaces=TEI_NS)
        + tei_doc.xpath("//tei:standOff/tei:listEvent/tei:event", namespaces=TEI_NS)
    )
    standoff_ids = ids(tei_standoff_nodes)

    all_html_ids = {element.get("id") for element in root.xpath("//*[@id]")}
    entity_cards = root.xpath("//article[contains(concat(' ', normalize-space(@class), ' '), ' entity-card ')]")
    entity_card_te_ids = {card.get("data-tei-id") for card in entity_cards}
    entity_card_ids = {card.get("id") for card in entity_cards}

    canonical_xml = tei_doc.xpath("//tei:standOff/tei:listRelation[@type='canonical']/tei:relation", namespaces=TEI_NS)
    conceptual_xml = tei_doc.xpath("//tei:standOff/tei:listRelation[@type='conceptual']/tei:relation", namespaces=TEI_NS)
    canonical_html = root.xpath("//tr[contains(concat(' ', normalize-space(@class), ' '), ' canonical-relation ')]")
    conceptual_html = root.xpath("//tr[contains(concat(' ', normalize-space(@class), ' '), ' conceptual-relation ')]")

    require(html_path.exists(), "HTML output file was not created", failures)
    require(len(root.xpath("//h1")) == 1, "HTML must contain exactly one H1", failures)
    require(all(root.xpath(f"//*[@id='{section_id}']") for section_id in body_section_ids), "Not all body sections rendered", failures)
    require(all(root.xpath(f"//*[@id='{section_id}']") for section_id in back_section_ids), "Not all back sections rendered", failures)
    require(not root.xpath("//section[@id='lead']/h2"), "Lead must not have an invented H2 heading", failures)
    require(len(root.xpath("//main//section/h2")) == 10, "Expected 10 source section H2 headings", failures)
    require(len(root.xpath("//figure/figcaption")) == 8, "Expected 8 figure captions", failures)
    require(root.xpath("//section[@id='other-textual-genres']//li[contains(normalize-space(.), 'Non-Buddhist religious texts')]/ul/li"), "Nested Non-Buddhist list was not preserved", failures)
    require(not root.xpath("//p//blockquote"), "blockquote must not be nested inside p", failures)
    require(len(root.xpath("//blockquote[contains(@class, 'tei-cit')]")) == 2, "Expected 2 rendered cited passages", failures)
    require(len(root.xpath("//span[contains(@class, 'tei-quote')]")) >= 3, "TEI quote elements were not rendered as span.tei-quote", failures)
    require(not root.xpath("//q"), "HTML q elements must not be used", failures)
    require(root.xpath("//span[contains(@class, 'tei-attribution') and contains(., 'Arthur Waley')]"), "Waley attribution span is missing", failures)
    require(not root.xpath("//cite[contains(., 'Arthur Waley')]"), "Waley attribution must not use HTML cite", failures)
    require(root.xpath("//section[@id='references']/ol[contains(@class, 'references')]"), "References must render as ol.references", failures)
    require(len(root.xpath("//section[@id='references']/ol[contains(@class, 'references')]/li[starts-with(@id, 'bibl-')]")) == 34, "Expected 34 numbered reference li elements", failures)
    require(all(root.xpath(f"//li[@id='bibl-{number}']") for number in range(1, 35)), "Reference IDs bibl-1 through bibl-34 are incomplete", failures)
    citation_hrefs = [anchor.get("href") for anchor in root.xpath("//a[contains(concat(' ', normalize-space(@class), ' '), ' citation ')]")]
    require(all(href and href.startswith("#bibl-") for href in citation_hrefs), "Internal citations must link to bibl IDs", failures)
    require(all(norm_ref(href) in all_html_ids for href in citation_hrefs), "At least one internal citation link does not resolve", failures)
    require(not root.xpath("//a[contains(concat(' ', normalize-space(@class), ' '), ' citation ') and @data-target]"), "Citation links must not add data-target", failures)
    require(not root.xpath("//time[@data-when]"), "Dates must not add data-when when datetime exists", failures)
    require(len(root.xpath("//time[@datetime]")) >= 3, "Expected rendered datetime attributes for TEI dates", failures)
    require(root.xpath("//a[starts-with(@href, 'http') and @target='_blank' and contains(@rel, 'noopener') and contains(@rel, 'noreferrer')]"), "External links must use target blank and noopener noreferrer", failures)
    require(root.xpath("//section[@id='tei-semantic-layer']"), "TEI Semantic Layer section is missing", failures)
    require(set(entity_card_te_ids) == standoff_ids, "Entity register does not exactly match expected standOff records", failures)
    require(all((f"entity-{tei_id}" in entity_card_ids) for tei_id in standoff_ids), "Entity card IDs do not match standOff xml:id values", failures)
    inline_entity_links = root.xpath("//main//a[contains(concat(' ', normalize-space(@class), ' '), ' tei-entity ')]")
    require(all((link.get("href") or "").startswith("#entity-") for link in inline_entity_links), "Inline entity links must point to entity cards", failures)
    require(all(norm_ref(link.get("href")) in all_html_ids for link in inline_entity_links), "At least one inline entity link does not resolve", failures)
    require(root.xpath("//span[contains(concat(' ', normalize-space(@class), ' '), ' tei-concept ') and @data-ana]"), "Concept annotations must remain traceable with data-ana", failures)
    require(len(root.xpath("//article[@data-entity-kind='event']")) == 7, "All 7 event nodes must appear in the semantic layer", failures)
    require(len(canonical_html) == 16, "Canonical relation display count must be 16", failures)
    require(len(conceptual_html) == 30, "Conceptual relation display count must be 30", failures)
    require(root.xpath("//tr[@data-relation-id='r16']//span[contains(@class, 'evidence-enriched') and normalize-space(.)='Enriched']"), "R16 must visibly show Enriched evidence", failures)
    require(root.xpath("//tr[@data-relation-id='cr2' and @data-mutual='true']/td[2]//a[@href='#entity-mogao-caves']"), "R2 source display must be Mogao Caves", failures)
    require(root.xpath("//tr[@data-relation-id='cr2' and @data-mutual='true']/td[4]//a[@href='#entity-dunhuang']"), "R2 target display must be Dunhuang", failures)
    require(root.xpath("//tr[@data-relation-id='cr2' and @data-mutual='true']//span[contains(@class, 'property-semantics') and contains(., 'symmetric') and contains(., '@mutual')]"), "R2 property semantics note must explain symmetric @mutual encoding", failures)
    require(not root.xpath("//tr[@data-relation-id='cr2']/td[2][normalize-space(.)='mutual']"), "R2 must not display mutual as a pseudo-source node", failures)
    require(root.xpath("//tr[@data-relation-id='cr29']//a[@href='#entity-digital-surrogate']") and root.xpath("//tr[@data-relation-id='cr30']//a[@href='#entity-digital-surrogate']"), "R15/R16 conceptual display must resolve to the same Digital Surrogate", failures)
    require(set(row.get("data-relation-id") for row in canonical_html) == ids(canonical_xml), "Displayed canonical relation IDs diverge from TEI", failures)
    require(set(row.get("data-relation-id") for row in conceptual_html) == ids(conceptual_xml), "Displayed conceptual relation IDs diverge from TEI", failures)
    require(len(root.xpath("//section[@id='references']//cite[contains(@class, 'tei-title')]")) >= 1, "Bibliography work titles may use cite.tei-title and none were found", failures)
    require(not root.xpath("//*[@data-target]"), "No redundant data-target attributes should appear", failures)
    require(not root.xpath("//*[@data-when]"), "No redundant data-when attributes should appear", failures)

    reference_count = len(root.xpath("//section[@id='references']/ol[contains(@class, 'references')]/li[starts-with(@id, 'bibl-')]"))
    event_node_count = len(root.xpath("//article[@data-entity-kind='event']"))

    report_lines = [
        f"HTML QA file: {display_path(html_path)}",
        f"Source TEI file: {display_path(tei_path)}",
        "Source sections: body=6/6, back=5/5",
        "Source structure: paragraphs rendered; nested Non-Buddhist list preserved; figure captions=8/8",
        f"References: numbered bibliography entries={reference_count}/34; internal citation links={len(citation_hrefs)}; all checked for resolution",
        "Quotation rendering: cit -> blockquote.tei-cit; quote -> span.tei-quote; HTML q unused; Waley attribution -> span.tei-attribution",
        f"Inline annotation links: {len(inline_entity_links)} entity anchors checked for #entity-* resolution; concepts use data-ana",
        f"Semantic layer: entity cards={len(entity_cards)}/{len(standoff_ids)} from standOff; event nodes={event_node_count}/7",
        f"Relation layer: canonical={len(canonical_html)}/16; conceptual={len(conceptual_html)}/30; R16 Enriched visible; R2 source/target display and symmetric @mutual note checked; R15/R16 Digital Surrogate target checked",
        "Semantic data provenance: entity card IDs and displayed relation IDs exactly match TEI standOff records; no extra semantic records detected",
        "HTML semantics: no cite used for Waley attribution; bibliography title cite elements allowed; no redundant data-target/data-when attributes",
        "No RDF export was attempted.",
    ]

    if failures:
        report_lines.append("")
        report_lines.append("HTML QA FAIL")
        report_lines.extend(f"- {failure}" for failure in failures)
        return False, "\n".join(report_lines) + "\n"

    report_lines.append("")
    report_lines.append("HTML QA PASS")
    return True, "\n".join(report_lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tei", default=DEFAULT_TEI, type=Path)
    parser.add_argument("--xsl", default=DEFAULT_XSL, type=Path)
    parser.add_argument("--html", default=DEFAULT_HTML, type=Path)
    parser.add_argument("--qa-report", default=DEFAULT_QA_REPORT, type=Path)
    args = parser.parse_args()

    before_hash = sha256(args.tei)
    transform(args.tei, args.xsl, args.html)
    after_hash = sha256(args.tei)

    passed, qa_report = qa_html(args.tei, args.html)
    immutability_lines = [
        "XML immutability check:",
        f"- Before SHA-256: {before_hash}",
        f"- After SHA-256:  {after_hash}",
        f"- Result: {'PASS' if before_hash == after_hash else 'FAIL'}",
        "",
    ]
    args.qa_report.parent.mkdir(parents=True, exist_ok=True)
    args.qa_report.write_text("\n".join(immutability_lines) + qa_report, encoding="utf-8")

    print(f"Generated HTML: {args.html}")
    print(f"Generated QA report: {args.qa_report}")
    print(f"XML SHA-256 before: {before_hash}")
    print(f"XML SHA-256 after:  {after_hash}")
    print("XML immutability: " + ("PASS" if before_hash == after_hash else "FAIL"))
    print("HTML QA: " + ("PASS" if passed else "FAIL"))

    return 0 if passed and before_hash == after_hash else 1


if __name__ == "__main__":
    raise SystemExit(main())
