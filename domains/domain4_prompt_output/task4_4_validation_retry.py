"""
Domain 4 · Task 4.4 — Validation, retry, and feedback loops.

THE BIG IDEA
============
  * RETRY-WITH-ERROR-FEEDBACK: on validation failure, send a follow-up containing the
    original document + the failed extraction + the SPECIFIC validation errors. Specific
    feedback steers self-correction; blind retries don't.
  * KNOW WHEN RETRY IS FUTILE: retries fix FORMAT/STRUCTURAL errors; they can NEVER fix
    information that is simply ABSENT from the source. Recognizing futile retries is tested.
  * SELF-CORRECTING SCHEMA DESIGN: extract calculated_total alongside stated_total so
    discrepancies flag themselves; add a conflict_detected boolean for inconsistent sources.
  * FEEDBACK LOOPS: add a detected_pattern field to each finding so you can analyze, across
    many dismissals, which code constructs drive false positives.
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from ccarch import banner, concept, h1, h2, wrong, right, tip, note, kv, code, rule, pause


def validate(extraction: dict):
    """Return a list of specific, actionable validation errors."""
    errors = []
    items = extraction.get("line_items", [])
    stated = extraction.get("stated_total")
    if items and stated is not None:
        calc = round(sum(items), 2)
        if calc != stated:
            errors.append(f"line_items sum to {calc} but stated_total is {stated}")
    if extraction.get("date") and not str(extraction["date"]).count("-") == 2:
        errors.append(f"date {extraction['date']!r} is not ISO 8601 (YYYY-MM-DD)")
    return errors


def is_futile(missing_field_absent_from_source: bool) -> bool:
    # The key judgment: if the info isn't in the source, no retry can conjure it.
    return missing_field_absent_from_source


def main():
    banner("Domain 4 · Task 4.4", "Validation, retry & feedback loops")
    concept("Domain 4: Prompt Engineering & Structured Output (20%)",
            "Task 4.4 — Implement validation, retry, and feedback loops for extraction quality",
            "Retry WITH specific errors; know when retry is futile")

    h1("Retry-with-error-feedback (a real validation loop)")
    bad = {"line_items": [10.0, 20.0], "stated_total": 35.0, "date": "03/04/2025"}
    h2("Attempt 1 output")
    kv("  extraction", str(bad))
    errs = validate(bad)
    wrong("Validation failed:")
    for e in errs:
        note(f"    - {e}")
    h2("Retry message we send back")
    code("Here is the original document, your previous extraction, and these errors:\n"
         f"  - {errs[0]}\n  - {errs[1]}\n"
         "Re-extract, fixing exactly these issues.", "retry-with-feedback")
    good = {"line_items": [10.0, 20.0], "stated_total": 30.0, "date": "2025-03-04"}
    h2("Attempt 2 output")
    kv("  extraction", str(good))
    kv("  validation", "PASS" if not validate(good) else "FAIL")
    right("Specific feedback steers self-correction. A blind 'try again' would not.")

    pause("futile retries")
    rule()
    h1("Know when retry is FUTILE")
    note("A field is missing because the value lives in an EXTERNAL document you didn't provide.")
    kv("  retry will help?", "NO — the info is absent from the source")
    wrong("Retrying forever on absent information. It can never appear; you waste tokens.")
    right("Retries fix FORMAT/STRUCTURE. For ABSENT info: emit null and route to a human or "
          "fetch the missing source. Recognizing this is a tested skill.")

    pause("self-correcting schemas")
    rule()
    h1("Self-correcting schema design")
    code('{\n'
         '  "stated_total": 30.00,\n'
         '  "calculated_total": 30.00,   # extract BOTH so mismatches self-flag\n'
         '  "conflict_detected": false   # true when the source is internally inconsistent\n'
         '}', "schema that flags its own errors")
    right("Make the data reveal its own inconsistencies instead of hoping a human notices.")

    rule()
    h1("Feedback loops for review systems")
    right("Add a detected_pattern field to each finding. When developers dismiss findings, "
          "analyze WHICH code constructs drive false positives — systematically, not anecdotally.")

    tip("Retry WITH the specific errors attached. Retry fixes format/structure, never "
        "absent information. Extract calculated_total + stated_total so errors self-flag.")


if __name__ == "__main__":
    main()
