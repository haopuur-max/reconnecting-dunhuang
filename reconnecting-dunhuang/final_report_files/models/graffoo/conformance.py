"""Shared text for the core Graffoo diagram (SVG) and its HTML companion: the declared signature of every reused
property and the inheritance that makes each use valid, and the E96 note."""
ROWS = [
    ("crm:P4_has_time-span", "E2 → E52", "E96, E9, E7, S19", ["E96 ⊑ E8 ⊑ E7;  E9 ⊑ E7;  E7 ⊑ E5 ⊑ E4 ⊑ E2", "S19 ⊑ S27 ⊑ I1 ⊑ E7"]),
    ("crm:P7_took_place_at", "E4 → E53", "E7 → E53", ["E7 ⊑ E5 ⊑ E4"]),
    ("crm:P12_occurred_in_the_presence_of", "E5 → E77", "E7 → E18", ["E7 ⊑ E5;  E18 ⊑ E72 ⊑ E70 ⊑ E77"]),
    ("crm:P14_carried_out_by", "E7 → E39", "S19 → E21, D2 → E74", ["S19 ⊑ S27 ⊑ I1 ⊑ E7;  D2 ⊑ D11 ⊑ D7 ⊑ E11 ⊑ E7", "E21 ⊑ E39;  E74 ⊑ E39"]),
    ("crm:P15_was_influenced_by", "E7 → E1", "E9 → E21", ["E9 ⊑ E7;  E21 ⊑ … ⊑ E1"]),
    ("crm:P22_transferred_title_to", "E8 → E39", "E96 → E21", ["E96 ⊑ E8;  E21 ⊑ E39"]),
    ("crm:P23_transferred_title_from", "E8 → E39", "E96 → E21", ["E96 ⊑ E8;  E21 ⊑ E39"]),
    ("crm:P24_transferred_title_of", "E8 → E18", "E96 → E19", ["E96 ⊑ E8;  E19 ⊑ E18"]),
    ("crm:P25_moved", "E9 → E19", "E9 → E19", ["direct"]),
    ("crm:P26_moved_to", "E9 → E53", "E9 → E53", ["direct"]),
    ("crm:P46i_forms_part_of", "E18 → E18", "E19 → E18", ["E19 ⊑ E18"]),
    ("crm:P50_has_current_keeper", "E18 → E39", "E19 → E74", ["E19 ⊑ E18;  E74 ⊑ E39"]),
    ("crm:P89_falls_within", "E53 → E53", "E53 → E53", ["direct"]),
    ("crm:P3_has_note", "E1 → E62", "E19 → xsd:string", ["E19 ⊑ … ⊑ E1; E62 String as literal"]),
    ("crm:P82a / P82b", "E52 → E61", "E52 → xsd:dateTime", ["direct; E61 Time Primitive as literal"]),
    ("crmsci:O19_encountered_object", "S19 → E18", "S19 → E18", ["direct"]),
    ("crmdig:L1_digitized", "D2 → E18", "D2 → E18", ["direct"]),
    ("crmdig:L11_had_output", "D7 → D1", "D2 → D1", ["D2 ⊑ D11 ⊑ D7"]),
    ("dcterms:publisher", "none", "D1 → E74", ["no domain or range (range includes Agent)"]),
]

E96_LINES = ["A sale is not a link between", "two people: crm:E96_Purchase", "is an event that holds the",
         "seller (P23), the buyer (P22),", "the part of the corpus sold", "(P24) and, where the source", "gives it, the date (P4).",
         "It formalises R6–R8."]
