"""
Domain 5 · Task 5.3 — Error propagation across multi-agent systems.

THE BIG IDEA
============
When a subagent fails (e.g., a web-search timeout), WHAT FLOWS BACK to the coordinator
determines whether intelligent recovery is possible.

  CORRECT: Structured error context — failure type, attempted query, partial results,
           alternative approaches. The coordinator can then retry-modified, try an
           alternative source, or proceed with partials and ANNOTATE the gap.

  ANTI-PATTERNS:
   - Retry internally, then return a GENERIC "search unavailable" — local retries are good,
     but the generic status hides everything the coordinator needs.
   - Return EMPTY results marked as SUCCESS — silent suppression; the report ships with
     invisible holes.
   - Propagate the exception and TERMINATE the whole workflow — one recoverable failure
     kills the entire run.

COVERAGE ANNOTATIONS: synthesis output should mark which findings are well-supported and
which topic areas have gaps due to unavailable sources. Honest uncertainty beats false
completeness. (This is official sample question Q8.)
"""

import sys, pathlib, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from ccarch import banner, concept, h1, h2, wrong, right, tip, note, kv, code, rule, pause


GOOD_PROPAGATION = {
    "status": "partial_failure",
    "failure_type": "timeout",
    "attempted_query": "AI adoption in film production 2024",
    "partial_results": ["1 source retrieved before timeout"],
    "alternatives": ["retry with narrower query", "try industry-report source"],
}


def coordinator_decide(report: dict) -> str:
    if report.get("status") == "partial_failure":
        return ("Retry with a modified query, OR proceed with partials and annotate the "
                "coverage gap — an INFORMED choice.")
    return "Proceed."


def main():
    banner("Domain 5 · Task 5.3", "Error propagation across agents")
    concept("Domain 5: Context Management & Reliability (15%)",
            "Task 5.3 — Error propagation across multi-agent systems",
            "Structured error context enables intelligent recovery")

    h1("The CORRECT approach (sample Q8): structured error context")
    code(json.dumps(GOOD_PROPAGATION, indent=2), "what flows back to the coordinator")
    right(f"Coordinator can act: {coordinator_decide(GOOD_PROPAGATION)}")

    pause("the three anti-patterns")
    rule()
    h1("The three anti-patterns")
    h2("1) Retry internally, then return generic 'search unavailable'")
    wrong("Local retries are GOOD, but the GENERIC status hides the query, partials, and "
          "alternatives the coordinator needs.")
    h2("2) Return empty results marked as success")
    wrong("Silent suppression. The final report ships with invisible holes — the worst "
          "outcome because nobody knows data is missing.")
    h2("3) Propagate the exception, terminate the whole workflow")
    wrong("One recoverable failure kills the entire research run. Massive over-reaction.")

    pause("coverage annotations")
    rule()
    h1("Coverage annotations in synthesis")
    code('{\n'
         '  "well_supported": ["AI in music", "AI in writing"],\n'
         '  "coverage_gaps": ["AI in film — source timed out, NOT researched"]\n'
         '}', "honest uncertainty")
    right("Mark which findings are well-supported and which areas have gaps from "
          "unavailable sources. Honest uncertainty beats false completeness.")

    tip("CORRECT = structured error context (type, query, partials, alternatives). "
        "Generic status hides; empty-as-success suppresses; full termination overreacts. "
        "Local retry first, propagate only the unresolved WITH context.")


if __name__ == "__main__":
    main()
