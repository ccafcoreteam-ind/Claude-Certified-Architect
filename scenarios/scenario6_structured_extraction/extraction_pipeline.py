"""
SCENARIO 6 — Structured Data Extraction  (Claude API)
=====================================================
A runnable extraction pipeline that reads unstructured "documents" and emits clean,
schema-validated data. Demonstrates the concepts the exam attaches to this scenario:
D4 Prompt Engineering & Structured Output, D5 Context & Reliability.

In ONE program:
  * STRUCTURED OUTPUT via a tool whose input_schema IS the output contract (D4 T4.3)
  * NULLABLE fields so the model emits null instead of fabricating (D4 T4.3)
  * an EXTENSIBLE enum ("other" + detail) (D4 T4.3)
  * VALIDATION + retry-with-error-feedback; and recognizing a FUTILE retry (D4 T4.4)
  * SELF-CORRECTING schema: stated_total vs calculated_total (D4 T4.4)
  * BATCH vs synchronous routing + custom_id (D4 T4.5)
  * CONFIDENCE-ANNOTATED routing to human review (D5 T5.5)
"""

import sys, pathlib, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from ccarch import banner, concept, h1, h2, wrong, right, tip, note, kv, code, rule, pause

# The extraction tool's input_schema = the output contract (D4 T4.3)
SCHEMA = {
    "type": "object",
    "properties": {
        "vendor": {"type": "string"},
        "amount": {"type": ["number", "null"]},          # nullable -> no fabrication
        "currency": {"type": ["string", "null"]},
        "date": {"type": ["string", "null"]},             # ISO 8601
        "category": {"type": "string", "enum": ["goods", "services", "unclear", "other"]},
        "category_detail": {"type": ["string", "null"]},
        "line_items": {"type": "array", "items": {"type": "number"}},
        "stated_total": {"type": ["number", "null"]},
        "calculated_total": {"type": ["number", "null"]},  # self-correcting (D4 T4.4)
    },
    "required": ["vendor", "category"],
}


def validate(rec: dict):
    errs = []
    if rec.get("stated_total") is not None and rec.get("line_items"):
        calc = round(sum(rec["line_items"]), 2)
        if rec.get("calculated_total") != calc:
            errs.append(f"calculated_total should be {calc}")
        if calc != rec["stated_total"]:
            errs.append(f"line_items sum {calc} != stated_total {rec['stated_total']}")
    if rec.get("date") and str(rec["date"]).count("-") != 2:
        errs.append(f"date {rec['date']!r} not ISO 8601 (YYYY-MM-DD)")
    if rec.get("category") == "other" and not rec.get("category_detail"):
        errs.append("category 'other' requires category_detail")
    return errs


def confidence_route(field_conf: dict, threshold=0.80):
    return {f: ("HUMAN" if c < threshold else "auto") for f, c in field_conf.items()}


def main():
    banner("Scenario 6", "Structured Data Extraction — D4 · D5")
    concept("Scenario 6: Structured Data Extraction",
            "Unstructured documents → schema-validated JSON → downstream systems",
            "Tool-use schema + nullable + validation/retry + confidence routing")

    h1("The extraction tool's input_schema IS the output contract")
    code(json.dumps(SCHEMA, indent=2), "extraction schema")

    # 1) nullable prevents fabrication
    pause("nullable fields prevent fabrication")
    h1("1) A document genuinely missing the amount")
    doc = "Invoice from Beta LLC, amount to be confirmed next week."
    rec = {"vendor": "Beta LLC", "amount": None, "currency": None, "date": None,
           "category": "services", "line_items": [], "stated_total": None,
           "calculated_total": None}
    kv("  document", doc)
    kv("  extraction", json.dumps({k: rec[k] for k in ("vendor", "amount", "date")}))
    right("amount=null instead of a fabricated number. Required fields would have FORCED a "
          "made-up value — the #1 schema-design fact.")

    # 2) validation + retry with feedback
    pause("validation + retry-with-feedback")
    h1("2) Validation catches a SEMANTIC error a schema can't")
    bad = {"vendor": "Acme", "category": "goods", "line_items": [10.0, 20.0],
           "stated_total": 35.0, "calculated_total": 30.0, "date": "03/04/2025"}
    errs = validate(bad)
    kv("  extraction", json.dumps({k: bad[k] for k in ("line_items", "stated_total",
                                                       "calculated_total", "date")}))
    wrong("Schema-valid but WRONG: " + "; ".join(errs))
    h2("Retry message (document + failed extraction + SPECIFIC errors)")
    code("\n".join(f"- {e}" for e in errs), "feedback that steers self-correction")
    fixed = {**bad, "stated_total": 30.0, "calculated_total": 30.0, "date": "2025-03-04"}
    kv("  retry result valid?", "yes" if not validate(fixed) else "no")
    right("Specific feedback fixes format/structure errors. Blind retries would not.")

    # 3) futile retry
    pause("recognizing a futile retry")
    h1("3) When retry is FUTILE")
    note("The PO number lives in a separate document you didn't provide.")
    wrong("Retrying forever — the info is ABSENT from the source; it can never appear.")
    right("Emit null and route to a human / fetch the missing source. Retry can't conjure "
          "absent data (D4 T4.4).")

    # 4) batch routing
    pause("batch vs synchronous")
    h1("4) Batch vs synchronous routing (D4 T4.5)")
    kv("  100k overnight invoices", "BATCH (50% cheaper, <=24h, nobody waiting)")
    kv("  one invoice a user is waiting on", "SYNCHRONOUS (no batch latency SLA)")
    code('requests=[{"custom_id":"inv-001",...}, ...]  '
         '# correlate + resubmit only failures', "custom_id")

    # 5) confidence routing
    pause("confidence-annotated human review")
    h1("5) Confidence-annotated routing to humans (D5 T5.5)")
    field_conf = {"vendor": 0.98, "amount": 0.55, "date": 0.91}
    routing = confidence_route(field_conf)
    for f, decision in routing.items():
        kv(f"  {f} (conf={field_conf[f]})", decision)
    right("Route low-confidence FIELDS to humans; auto-accept the rest. Calibrate the "
          "threshold on a labeled set; also audit high-confidence samples (stratified).")

    rule()
    tip("Tool-use schema kills SYNTAX errors; nullable kills fabrication; validation+retry "
        "handles SEMANTICS (but not absent info); batch for non-blocking; confidence routing "
        "for human review. That's D4 + D5.")


if __name__ == "__main__":
    main()
