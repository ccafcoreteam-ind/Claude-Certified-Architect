"""
Domain 1 · Task 1.2 — Orchestrate multi-agent systems (coordinator + subagents).

THE BIG IDEA
============
For big tasks, one COORDINATOR delegates to specialist SUBAGENTS. The standard shape is
HUB-AND-SPOKE: every message flows through the coordinator; subagents NEVER talk to each
other directly. That central routing buys you observability, consistent error handling,
and controlled information flow.

The coordinator has four jobs:
  1. DECOMPOSE the task into subtasks
  2. DELEGATE to the right subagents (dynamically — not always the full pipeline)
  3. AGGREGATE results
  4. EVALUATE for gaps and re-delegate (iterative refinement)

THE #1 TESTED FAILURE: narrow decomposition. Every subagent can succeed perfectly while
the REPORT is incomplete — because the coordinator carved the topic too thin. This demo
reproduces the official sample question (Q7): researching "impact of AI on creative
industries" but only covering visual arts.
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from ccarch import banner, concept, h1, h2, wrong, right, tip, note, kv, code, rule, pause, analogy, pitfall


def research(subtopics):
    """Each 'subagent' succeeds at its assigned slice. Success != coverage."""
    findings = {}
    for st in subtopics:
        findings[st] = f"[3 sources found and summarized for '{st}']  ✓ subagent OK"
    return findings


ALL_SECTORS = {"digital art", "graphic design", "photography",
               "music", "writing", "film production"}


def main():
    banner("Domain 1 · Task 1.2", "Coordinator + Subagents — hub-and-spoke")
    concept("Domain 1: Agentic Architecture & Orchestration (27%)",
            "Task 1.2 — Orchestrate multi-agent systems with coordinator-subagent patterns",
            "Hub-and-spoke; the coordinator's decomposition is the risk")

    h1("Hub-and-spoke architecture")
    code(
        "            ┌───────────────┐\n"
        "   web ───► │               │ ◄─── docs\n"
        "            │  COORDINATOR  │\n"
        "  synth ──► │   (the hub)   │ ◄─── report\n"
        "            └───────────────┘\n"
        "   web  ✗──────────────────✗  synth   <-- this direct link must NOT exist",
        "topology")
    note("Analogy: a general contractor. The plumber and electrician don't coordinate "
         "with each other — the contractor sequences work, routes info, handles problems.")

    rule()
    h1("Reproducing the classic failure (sample Q7)")
    h2("Topic: 'impact of AI on creative industries'")

    narrow = ["AI in digital art creation", "AI in graphic design", "AI in photography"]
    note("Coordinator decomposed into 3 narrow subtasks:")
    for s in narrow:
        kv("  subtask", s)
    findings = research(narrow)
    for st, f in findings.items():
        note(f"    {st}: {f}")

    covered = {"digital art", "graphic design", "photography"}
    missing = ALL_SECTORS - covered
    print()
    wrong(f"Every subagent reported success, yet the report MISSES: {sorted(missing)}. "
          f"Blaming the subagents is the trap — the logs show the decomposition was narrow.")
    right("Root cause = the coordinator's task decomposition. Fix it upstream.")

    pause("the fix")
    rule()
    h1("The fix: broad, partitioned decomposition")
    broad = [f"AI in {s}" for s in sorted(ALL_SECTORS)]
    note("Coordinator now assigns DISTINCT subtopics spanning the whole topic:")
    for s in broad:
        kv("  subtask", s)
    note("Plus an EVALUATE step: after synthesis, check coverage vs. the topic's known "
         "sectors and re-delegate to fill any gap (iterative refinement loop).")

    rule()
    h1("Critical facts to remember")
    note("- Subagents have ISOLATED context — they do not inherit the coordinator's history. "
         "Anything they need must be written into their prompt (see Task 1.3).")
    note("- DYNAMIC delegation: pick which subagents to run based on the query; don't always "
         "run the full pipeline.")
    note("- PARTITION scope so two subagents don't research the same thing.")

    rule()
    h1("Plain-language analogy & the common confusion")
    analogy('A general contractor and trade crews: the plumber and electrician never coordinate directly — the contractor sequences the work, passes information between them, and inspects the result. That central desk is the coordinator.')
    pitfall("Learners blame the subagent when a report comes back thin. But each subagent only did the slice it was handed — the gap was created upstream when the coordinator carved the topic. Always read the coordinator's decomposition first.")

    tip("When a multi-agent system produces an incomplete report but every subagent "
        "'completed successfully', look UPSTREAM: the root cause is the coordinator's "
        "decomposition, not the subagents.")


if __name__ == "__main__":
    main()
