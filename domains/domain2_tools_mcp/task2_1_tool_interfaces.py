"""
Domain 2 · Task 2.1 — Design effective tool interfaces.

THE BIG IDEA
============
Agents choose tools by reading their DESCRIPTIONS — nothing more. If two tools have
minimal, near-identical descriptions, the model misroutes between them, and no amount of
clever prompting fixes the root cause.

A good description includes: purpose, accepted input formats, example queries, edge cases,
and EXPLICIT BOUNDARIES ("use this for X; for Y, use tool Z instead").

This is official sample question Q2: the FIRST step for misrouting between two
thinly-described tools is to EXPAND the descriptions — not few-shot, not a router.
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from ccarch import banner, concept, h1, h2, wrong, right, tip, note, kv, code, rule, pause


def score_description(desc: str) -> dict:
    """A toy 'router readiness' score: does the text contain the signals a model needs?"""
    checks = {
        "states purpose": any(w in desc.lower() for w in ["look", "retriev", "return", "extract"]),
        "input format": any(w in desc for w in ["format", "CUST-", "email", "ID", "#"]),
        "example query": "example" in desc.lower() or "e.g." in desc.lower() or "'" in desc,
        "edge cases": any(w in desc.lower() for w in ["if", "when", "no ", "missing"]),
        "boundary to sibling": "instead" in desc.lower() or "use " in desc.lower(),
    }
    return checks


def show(name, desc):
    h2(name)
    code(desc, "description")
    checks = score_description(desc)
    passed = sum(checks.values())
    for k, v in checks.items():
        kv(f"  {'✓' if v else '✗'} {k}", "present" if v else "MISSING")
    kv("  router-readiness", f"{passed}/5")
    return passed


def main():
    banner("Domain 2 · Task 2.1", "Tool interfaces — descriptions drive selection")
    concept("Domain 2: Tool Design & MCP Integration (18%)",
            "Task 2.1 — Design effective tool interfaces",
            "Descriptions are the PRIMARY tool-selection mechanism")

    h1("Weak descriptions cause misrouting (sample Q2)")
    weak = score_description and show(
        "get_customer (weak)", "Retrieves customer information.")
    show("lookup_order (weak)", "Retrieves order details.")
    wrong("Two near-identical one-liners. Both accept similar IDs. The model literally "
          "cannot tell them apart and routes order questions to get_customer.")

    pause("the strong version")
    rule()
    h1("Strong description: purpose + inputs + example + boundary")
    strong = (
        "Looks up a customer profile by email address or customer ID (format: CUST-12345). "
        "Returns name, account status, loyalty tier, and contact details. "
        "Example query: 'find the account for jane@example.com'. "
        "If the question is about a specific purchase or delivery, use lookup_order "
        "instead — this tool has no order data."
    )
    n = show("get_customer (strong)", strong)
    right(f"Purpose, input formats, a worked example, and — critically — an explicit "
          f"boundary pointing to the neighbor. Router-readiness {n}/5.")

    rule()
    h1("Remedies the exam tests (in order of preference)")
    note("1. EXPAND descriptions first — low-effort, high-leverage, the correct 'first step'.")
    note("2. RENAME to kill overlap — analyze_content -> extract_web_results.")
    note("3. SPLIT a generic tool into purpose-specific ones — analyze_document -> "
         "extract_data_points / summarize_content / verify_claim_against_source.")
    note("4. AUDIT the system prompt for keyword traps — 'always analyze documents "
         "thoroughly' can bias the model toward any tool with 'document' in its name.")

    tip("When misrouting appears with MINIMAL descriptions, the answer is 'improve the "
        "descriptions'. Distractors: few-shot (token overhead, doesn't fix the cause), a "
        "keyword routing layer (over-engineered), or merging tools (bigger than a 'first step').")


if __name__ == "__main__":
    main()
