"""
SCENARIO 6 app — Structured Data Extraction (FUNCTIONAL)
========================================================
A real, basic extractor: it parses unstructured invoice-like text into a schema-validated
record, emitting null (never a fabricated value) for genuinely-absent fields, validating
totals, attaching per-field confidence, and routing low-confidence fields to a human —
Domain 4.3/4.4 + Domain 5.5 in action.

Run:
  python3 scenarios/scenario6_structured_extraction/app.py            # scripted demo
  python3 scenarios/scenario6_structured_extraction/app.py -i         # paste your own text
  python3 scenarios/scenario6_structured_extraction/app.py "Pd $20 to Acme on 3/4/25"
"""
import sys, re, json, pathlib
from datetime import datetime

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from ccarch import banner, h1, h2, kv, note, rule, wrong, right, tip, code

MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}


def _norm_date(text):
    # m/d/yy or m/d/yyyy
    m = re.search(r"\b(\d{1,2})/(\d{1,2})/(\d{2,4})\b", text)
    if m:
        mo, da, yr = (int(x) for x in m.groups())
        yr += 2000 if yr < 100 else 0
        try:
            return datetime(yr, mo, da).date().isoformat(), 0.9
        except ValueError:
            return None, 0.0
    # "March 4, 2025" / "Mar 4 2025"
    m = re.search(r"\b([A-Za-z]{3,9})\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})\b", text)
    if m and m.group(1)[:3].lower() in MONTHS:
        mo = MONTHS[m.group(1)[:3].lower()]
        try:
            return datetime(int(m.group(3)), mo, int(m.group(2))).date().isoformat(), 0.85
        except ValueError:
            return None, 0.0
    return None, 0.0


def extract(text):
    """Return (record, confidence) — null for absent fields, never fabricated."""
    conf = {}
    # vendor: after 'to'/'from'/'vendor:' up to punctuation
    vm = re.search(r"\b(?:to|from|vendor:?)\s+([A-Z][\w&.\- ]+?)(?:\s+(?:on|for|amount|\$)|[,.\n]|$)",
                   text, re.I)
    vendor = vm.group(1).strip() if vm else None
    conf["vendor"] = 0.9 if vendor else 0.0

    # amount: $1,200.50 or 'amount 20'
    am = re.search(r"\$\s?([\d,]+(?:\.\d{1,2})?)", text) or \
        re.search(r"\bamount\s+(?:of\s+)?([\d,]+(?:\.\d{1,2})?)", text, re.I)
    amount = float(am.group(1).replace(",", "")) if am else None
    # explicit "to be confirmed / TBD / unknown" => stay null, do NOT invent
    if amount is None and re.search(r"to be confirmed|TBD|unknown|N/?A", text, re.I):
        conf["amount"] = 0.0
    else:
        conf["amount"] = 0.9 if amount is not None else 0.0

    currency = "USD" if "$" in text else (
        "EUR" if "€" in text else (re.search(r"\b(USD|EUR|GBP)\b", text).group(1)
                                    if re.search(r"\b(USD|EUR|GBP)\b", text) else None))
    conf["currency"] = 0.8 if currency else 0.0

    date, dconf = _norm_date(text)
    conf["date"] = dconf

    # line items: numbers in a "items: a, b, c" clause
    items = []
    im = re.search(r"items?:?\s*([\d.,\s]+)", text, re.I)
    if im:
        items = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", im.group(1))]
    stated_total = amount
    calculated_total = round(sum(items), 2) if items else None

    rec = {"vendor": vendor, "amount": amount, "currency": currency, "date": date,
           "line_items": items, "stated_total": stated_total,
           "calculated_total": calculated_total}
    return rec, conf


def validate(rec):
    errs = []
    if rec["line_items"] and rec["stated_total"] is not None:
        if rec["calculated_total"] != rec["stated_total"]:
            errs.append(f"line_items sum {rec['calculated_total']} != stated_total {rec['stated_total']}")
    if rec["vendor"] is None:
        errs.append("required field 'vendor' is missing")
    return errs


def route(conf, threshold=0.7):
    return {f: ("HUMAN" if c < threshold else "auto") for f, c in conf.items()}


def process(text, as_json=False):
    rec, conf = extract(text)
    errs = validate(rec)
    routing = route(conf)
    if as_json:
        print(json.dumps({"record": rec, "confidence": conf, "validation_errors": errs,
                          "routing": routing}, indent=2))
        return rec, errs
    kv("input", text.strip())
    code(json.dumps(rec, indent=2), "extracted record")
    nulls = [k for k, v in rec.items() if v is None]
    if nulls:
        right(f"emitted null (not fabricated) for: {', '.join(nulls)}")
    if errs:
        wrong("validation: " + "; ".join(errs))
    else:
        right("validation passed")
    low = [f for f, d in routing.items() if d == "HUMAN" and conf[f] > 0]
    flagged_absent = [f for f, c in conf.items() if c == 0.0]
    kv("route to human (low confidence)", ", ".join(low) or "none")
    kv("absent → null", ", ".join(flagged_absent) or "none")
    return rec, errs


SAMPLES = [
    "Pd $1,200.50 to Acme Corp on 3/4/25",
    "Invoice from Beta LLC, amount to be confirmed next week",
    "Charge to Gamma Inc on March 4, 2025, items: 10, 20, amount $35",  # sum mismatch
]


def interactive():
    banner("Scenario 6 — Structured Extraction", "paste a line of invoice text; 'quit' to exit")
    while True:
        try:
            line = input("\ndoc> ").strip()
        except (EOFError, KeyboardInterrupt):
            print(); break
        if line.lower() in ("quit", "exit", "q"):
            break
        if line:
            process(line)


def main():
    args = sys.argv[1:]
    as_json = "--json" in args
    free = [a for a in args if not a.startswith("-")]
    if any(a in ("-i", "--interactive") for a in args) and sys.stdin.isatty():
        interactive(); return
    if free:
        process(" ".join(free), as_json=as_json); return
    banner("Scenario 6 — Structured Extraction (demo)", "real parsing of 3 sample documents")
    for i, s in enumerate(SAMPLES, 1):
        h2(f"document {i}")
        process(s)
    rule()
    tip("Absent info → null (never fabricated); a schema can't catch semantic errors so we "
        "validate totals; low-confidence fields route to a human. Run -i to paste your own.")


if __name__ == "__main__":
    main()
