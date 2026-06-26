"""
Domain 5 · Task 5.1 — Preserve critical information across long interactions.

THREE FAILURE PHYSICS YOU MUST INTERNALIZE
==========================================
  1. PROGRESSIVE SUMMARIZATION erodes precision. Each round strips detail; numbers,
     percentages, dates, and customer-stated expectations are the FIRST casualties.
  2. LOST IN THE MIDDLE. Models reliably process the BEGINNING and END of long inputs but
     may skip the middle. Mitigation: key-findings summary at the TOP + explicit section
     headers.
  3. TOOL-OUTPUT BLOAT. A lookup returns 40+ fields when 5 matter; times dozens of calls,
     context drowns. Trim tool outputs to relevant fields before they accumulate.

THE SIGNATURE PATTERN — the "case facts" block: extract transactional facts (amounts,
dates, order numbers, statuses) into a PERSISTENT structured block included in EVERY
prompt, OUTSIDE the summarized history. Summaries blur; the facts block cannot.

Also: the API is STATELESS — you must pass the complete conversation history each request.
"""

import sys, pathlib, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from ccarch import banner, concept, h1, h2, wrong, right, tip, note, kv, code, rule, pause, analogy, pitfall


CASE_FACTS = {
    "customer": "Dana Lee",
    "order": "#88231",
    "refund_amount": 847.50,
    "deadline": "March 3",
    "reason": "second damaged delivery",
}


def main():
    banner("Domain 5 · Task 5.1", "Preserve critical info across long interactions")
    concept("Domain 5: Context Management & Reliability (15%)",
            "Task 5.1 — Manage conversation context to preserve critical information across long interactions",
            "The 'case facts' block survives summarization")

    h1("1) Watch progressive summarization destroy the facts")
    original = ("Customer Dana Lee (order #88231) was promised a $847.50 refund by March 3 "
                "after a second damaged delivery.")
    s1 = "Dana Lee was promised a refund for delivery issues."
    s2 = "A customer had delivery problems; a refund was discussed."
    kv("  original", original)
    kv("  summary 1", s1)
    kv("  summary 2", s2)
    wrong("Two rounds in, EVERY actionable fact — name, order #, amount, deadline — is gone, "
          "yet each summary looked reasonable. Numbers/dates die first.")

    pause("lost in the middle")
    rule()
    h1("2) Lost in the middle")
    note("Models reliably read the BEGINNING and END of a long input; the middle gets skipped.")
    right("Put a KEY-FINDINGS summary at the TOP and organize details under explicit SECTION "
          "HEADERS so nothing critical hides in the middle.")

    rule()
    h1("3) Tool-output bloat")
    fat = {f"field_{i}": i for i in range(40)}
    fat.update({"status": "shipped", "eta": "June 15"})
    lean = {"status": fat["status"], "eta": fat["eta"]}
    kv("  raw tool output", f"{len(fat)} fields")
    kv("  trimmed to relevant", f"{lean}")
    right("Trim tool outputs to the 5 fields that matter BEFORE they accumulate across "
          "dozens of calls.")

    pause("the case facts block")
    rule()
    h1("THE signature pattern: the 'case facts' block")
    code(json.dumps(CASE_FACTS, indent=2), "persistent facts (included in EVERY prompt)")
    right("Keep transactional facts in a structured block OUTSIDE the summarized history. "
          "Summaries can blur; the facts block cannot.")

    rule()
    h1("Also: the API is stateless")
    note("Each request must carry the COMPLETE conversation history to maintain coherence. "
         "There is no server-side memory between calls.")
    note("For multi-agent handoffs: require subagents to return structured data WITH metadata "
         "(dates, source locations); under tight budgets, return key facts + citations + "
         "relevance scores instead of verbose prose.")

    rule()
    h1("Plain-language analogy & the common confusion")
    analogy('Summarizing a case file over and over is like photocopying a photocopy — each pass is fuzzier, and the fine print (amounts, dates, deadlines) vanishes first. Keep the key numbers on a separate index card that never gets re-copied.')
    pitfall("Each individual summary looks reasonable, so the loss is invisible until the actionable facts are already gone. Protect numbers, dates, and order IDs in a persistent 'case facts' block outside the summarized history.")

    tip("Numbers/dates die first in summaries. Defend them with a persistent case-facts "
        "block. Summary-at-top + section-headers beats lost-in-the-middle. Trim tool output early.")


if __name__ == "__main__":
    main()
