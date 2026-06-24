"""
Domain 5 · Task 5.6 — Information provenance and uncertainty in multi-source synthesis.

THE BIG IDEA
============
  * ATTRIBUTION DIES IN SUMMARIZATION unless you force structure: subagents must output
    CLAIM-SOURCE MAPPINGS (claim + source URL/doc name + relevant excerpt) that downstream
    agents are REQUIRED to preserve and merge.
  * CONFLICTING STATISTICS from credible sources: annotate the conflict with BOTH values
    and their sources — never arbitrarily pick one. Let the coordinator decide reconciliation.
  * TEMPORAL TRAPS: a 2021 figure and a 2024 figure are NOT a "contradiction" — they're a
    trend. Require publication/collection DATES in structured outputs.
  * REPORT STRUCTURE: explicitly separate well-established findings from contested ones,
    preserving each source's characterization and methodology.
  * RENDER CONTENT NATIVELY: financial data as tables, news as prose, technical findings as
    structured lists — don't flatten everything into one uniform format.
"""

import sys, pathlib, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from ccarch import banner, concept, h1, h2, wrong, right, tip, note, kv, code, rule, pause


CLAIM_MAP = {
    "claim": "Global AI market size",
    "values": [
        {"value": "$184B", "source": "Report A", "url": "https://a.example/2024", "year": 2024},
        {"value": "$136B", "source": "Report B", "url": "https://b.example/2021", "year": 2021},
    ],
}


def classify_conflict(values):
    years = {v["year"] for v in values}
    if len(years) > 1:
        return "TREND (different years) — not a contradiction; report as a time series."
    return "CONFLICT (same period) — annotate both values + sources; coordinator reconciles."


def main():
    banner("Domain 5 · Task 5.6", "Provenance & uncertainty in synthesis")
    concept("Domain 5: Context Management & Reliability (15%)",
            "Task 5.6 — Preserve information provenance and handle uncertainty in multi-source synthesis",
            "Force claim-source mappings; conflicts & temporal traps")

    h1("Attribution dies in summarization unless you force structure")
    wrong("Letting subagents return prose. By the time synthesis summarizes it, the source "
          "URLs and page numbers are gone — citations can't be reconstructed.")
    code('{"claim": "...", "source_url": "...", "source_name": "...", "excerpt": "..."}',
         "required claim-source mapping")
    right("Subagents MUST output claim-source mappings that downstream agents PRESERVE and "
          "merge — non-negotiable for cited reports.")

    pause("conflicts vs trends")
    rule()
    h1("Conflicting statistics — annotate, don't pick")
    code(json.dumps(CLAIM_MAP, indent=2), "two values from credible sources")
    verdict = classify_conflict(CLAIM_MAP["values"])
    right(f"Classification: {verdict}")
    wrong("Arbitrarily picking $184B and dropping the other. You've hidden a real "
          "disagreement (or a trend).")

    rule()
    h1("Temporal traps")
    note("A 2021 figure and a 2024 figure differ because TIME PASSED, not because the "
         "sources disagree.")
    right("Require publication/collection DATES in structured outputs so a trend isn't "
          "misread as a contradiction.")

    pause("report structure")
    rule()
    h1("Report structure & native rendering")
    right("Separate WELL-ESTABLISHED findings from CONTESTED ones; preserve each source's "
          "characterization and methodology.")
    right("Render natively: financial data as TABLES, news as PROSE, technical findings as "
          "LISTS. Don't flatten everything into one uniform format.")

    tip("Force claim-source mappings end to end. Annotate conflicts with BOTH sources. "
        "Include dates so different-year figures read as a trend, not a contradiction.")


if __name__ == "__main__":
    main()
