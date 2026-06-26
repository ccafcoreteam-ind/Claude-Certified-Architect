"""
SCENARIO 3 — Multi-Agent Research System  (Agent SDK)
=====================================================
A runnable coordinator + specialist subagents (web search, document analysis, synthesis,
report). Demonstrates the concepts the exam attaches to this scenario: D1 Orchestration,
D2 Tools/MCP, D5 Context & Reliability.

In ONE program:
  * HUB-AND-SPOKE: all communication flows through the coordinator (D1 T1.2)
  * the NARROW-DECOMPOSITION failure and its fix (D1 T1.2 / sample Q7)
  * PARALLEL spawning of subagents (D1 T1.3)
  * STRUCTURED handoffs that preserve claim→source attribution (D1 T1.3 / D5 T5.6)
  * STRUCTURED error propagation on a subagent timeout (D5 T5.3 / sample Q8)
  * COVERAGE annotations + conflict/temporal handling in the report (D5 T5.3, T5.6)
"""

import sys, pathlib, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from ccarch import banner, concept, h1, h2, wrong, right, tip, note, kv, code, rule, pause, analogy, pitfall

ALL_SECTORS = ["digital art", "graphic design", "photography", "music", "writing", "film"]


# ----------------------------------------------------------------- subagents
def web_search_subagent(subtopic, fail=False):
    """Returns structured findings, or a STRUCTURED error on timeout (D5 T5.3)."""
    if fail:
        return {"status": "partial_failure", "failure_type": "timeout",
                "attempted_query": subtopic, "partial_results": [],
                "alternatives": ["retry narrower", "try industry-report source"]}
    return {"status": "ok", "subtopic": subtopic,
            "claims": [{"claim": f"Key trend in {subtopic}",
                        "source_url": f"https://example.org/{subtopic.replace(' ', '-')}",
                        "source_name": f"{subtopic.title()} Report",
                        "year": 2024}]}


def synthesis_subagent(all_findings):
    """Merges claims; PRESERVES attribution; annotates coverage gaps (D5 T5.6)."""
    well_supported, gaps, claims = [], [], []
    for f in all_findings:
        if f.get("status") == "ok":
            well_supported.append(f["subtopic"])
            claims.extend(f["claims"])
        else:
            gaps.append(f"{f['attempted_query']} (source {f['failure_type']})")
    return {"well_supported": well_supported, "coverage_gaps": gaps, "claims": claims}


# ----------------------------------------------------------------- coordinator
def coordinator(topic, decomposition, inject_timeout_on=None):
    h2("Coordinator decomposes the topic")
    for st in decomposition:
        kv("  subtask", st)
    note("(Subagents have ISOLATED context — the coordinator passes each its assignment "
         "explicitly, and they never talk to each other.)")

    h2("Coordinator spawns web-search subagents IN PARALLEL (multiple Task calls, one turn)")
    findings = []
    for st in decomposition:
        fail = (st == inject_timeout_on)
        result = web_search_subagent(st, fail=fail)
        mark = "TIMEOUT→structured error" if fail else "ok"
        kv(f"  subagent[{st}]", mark)
        findings.append(result)

    h2("Coordinator aggregates → synthesis subagent")
    report = synthesis_subagent(findings)
    return report


def main():
    banner("Scenario 3", "Multi-Agent Research System — D1 · D2 · D5")
    concept("Scenario 3: Multi-Agent Research System",
            "Coordinator → web-search / doc-analysis / synthesis / report subagents",
            "Hub-and-spoke; decomposition is the risk; preserve provenance")

    topic = "impact of AI on creative industries"
    kv("research topic", topic)

    # PART 1 — the narrow-decomposition failure (sample Q7)
    pause("Part 1: the narrow-decomposition failure")
    h1("Part 1 — NARROW decomposition (every subagent succeeds, report is incomplete)")
    narrow = ["AI in digital art", "AI in graphic design", "AI in photography"]
    report = coordinator(topic, narrow)
    covered = set(report["well_supported"])
    missing = [s for s in ALL_SECTORS if not any(s in c for c in covered)]
    kv("  report covers", report["well_supported"])
    wrong(f"Report MISSES {missing}. Every subagent 'completed successfully' — but the "
          "coordinator's decomposition never assigned music, writing, or film.")
    right("Root cause is UPSTREAM: the coordinator's task decomposition (sample Q7).")

    # PART 2 — broad, partitioned decomposition
    pause("Part 2: broad, partitioned decomposition")
    h1("Part 2 — BROAD decomposition spanning the whole topic")
    broad = [f"AI in {s}" for s in ALL_SECTORS]
    report = coordinator(topic, broad)
    kv("  report covers", report["well_supported"])
    right("Distinct subtopics partition the scope (no duplication) and cover the full topic.")

    # PART 3 — a subagent timeout + structured error propagation
    pause("Part 3: a subagent times out — structured error propagation")
    h1("Part 3 — web-search subagent for 'AI in film' TIMES OUT")
    report = coordinator(topic, broad, inject_timeout_on="AI in film")
    kv("  well_supported", report["well_supported"])
    kv("  coverage_gaps", report["coverage_gaps"])
    right("The failure flows back as STRUCTURED context, so the coordinator could retry or "
          "proceed-with-partials. The report ANNOTATES the gap instead of shipping a silent "
          "hole (sample Q8).")

    # PART 4 — provenance preserved through synthesis
    pause("Part 4: provenance preserved")
    h1("Part 4 — claim→source attribution survives synthesis")
    code(json.dumps(report["claims"][0], indent=2), "a merged claim with its source")
    right("Subagents returned claim-source mappings (claim + URL + name + year); synthesis "
          "PRESERVED them, so the final report can be cited (D5 T5.6).")

    rule()
    h1("Plain-language analogy & the common confusion")
    analogy('A research director assigns analysts, routes notes between them (they never talk directly), and checks the final draft for gaps before publishing — that central desk is the coordinator.')
    pitfall("When the report misses whole areas, do not blame the analysts — they covered what they were assigned. The real failure is the coordinator's decomposition being too narrow. Read the assignment list first.")

    tip("One system shows: hub-and-spoke, the decomposition failure + fix, parallel "
        "spawning, structured error propagation with coverage annotations, and provenance "
        "preservation. That's D1 + D2 + D5.")


if __name__ == "__main__":
    main()
