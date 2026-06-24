"""
SCENARIO 3 app — Multi-Agent Research System (FUNCTIONAL)
========================================================
A working coordinator: give it a topic and it decomposes into subtopics, runs (simulated)
web-search subagents in parallel, propagates a structured error if one "times out", and
synthesizes a cited report with coverage gaps — Domains 1, 2, 5 in action.

Run:
  python3 scenarios/scenario3_multi_agent_research/app.py                 # scripted demo
  python3 scenarios/scenario3_multi_agent_research/app.py -i              # your own topic
  python3 scenarios/scenario3_multi_agent_research/app.py "impact of AI on healthcare"
  python3 scenarios/scenario3_multi_agent_research/app.py "..." --fail 2  # time out subagent 2
"""
import sys, re, pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from ccarch import banner, h1, h2, kv, note, rule, wrong, right, tip, code

# A tiny "domain knowledge" table the coordinator uses to broaden known topics so the
# decomposition isn't too narrow (the classic failure mode).
SECTORS = {
    "creative": ["digital art", "graphic design", "photography", "music", "writing", "film"],
    "healthcare": ["diagnostics", "drug discovery", "clinical workflow", "patient triage", "medical imaging"],
    "education": ["tutoring", "grading", "curriculum design", "accessibility"],
    "finance": ["fraud detection", "risk modeling", "trading", "customer service"],
}


def decompose(topic):
    t = topic.lower()
    for key, sectors in SECTORS.items():
        if key in t or (key == "creative" and "creative" in t):
            return [f"{topic.split(' on ')[-1] if ' on ' in topic else topic}: {s}" for s in sectors]
    # generic broad facets when the topic isn't in the table
    return [f"{topic}: {facet}" for facet in
            ["overview & definitions", "key players & tools", "recent developments",
             "challenges & risks", "outlook"]]


def web_search_subagent(subtopic, fail=False):
    if fail:
        return {"status": "timeout", "subtopic": subtopic,
                "attempted_query": subtopic, "partial": [],
                "alternatives": ["retry with a narrower query", "try an alternative source"]}
    slug = re.sub(r"[^a-z0-9]+", "-", subtopic.lower()).strip("-")
    return {"status": "ok", "subtopic": subtopic, "claims": [{
        "claim": f"Notable trend in {subtopic}",
        "source_url": f"https://example.org/{slug}",
        "source_name": f"{subtopic.title()} — survey",
        "year": 2024}]}


def synthesize(findings):
    report = {"sections": [], "citations": [], "coverage_gaps": []}
    for f in findings:
        if f["status"] == "ok":
            c = f["claims"][0]
            report["sections"].append({"subtopic": f["subtopic"], "finding": c["claim"]})
            report["citations"].append(f"{c['source_name']} ({c['year']}) — {c['source_url']}")
        else:
            report["coverage_gaps"].append(f"{f['subtopic']} (source {f['status']})")
    return report


def run(topic, fail_idx=None, show=True):
    subtopics = decompose(topic)
    if show:
        h2("coordinator decomposed the topic")
        for s in subtopics:
            kv("  subtask", s)
        h2(f"spawning {len(subtopics)} web-search subagents (parallel)")
    findings = []
    for i, st in enumerate(subtopics, 1):
        f = web_search_subagent(st, fail=(fail_idx == i))
        findings.append(f)
        if show:
            note(f"    subagent {i}: {st} → {f['status']}")
    report = synthesize(findings)
    if show:
        h2("synthesized report")
        for sec in report["sections"]:
            right(f"{sec['subtopic']}: {sec['finding']}")
        if report["coverage_gaps"]:
            wrong("coverage gaps (subagent failures, honestly annotated): " +
                  "; ".join(report["coverage_gaps"]))
        h2("citations")
        for c in report["citations"]:
            note("  - " + c)
    return report


def interactive():
    banner("Scenario 3 — Research System", "type a topic; 'quit' to exit")
    while True:
        try:
            topic = input("\ntopic> ").strip()
        except (EOFError, KeyboardInterrupt):
            print(); break
        if topic.lower() in ("quit", "exit", "q"):
            break
        if topic:
            run(topic)


def main():
    args = sys.argv[1:]
    fail_idx = None
    if "--fail" in args:
        i = args.index("--fail")
        try:
            fail_idx = int(args[i + 1]); del args[i:i + 2]
        except (IndexError, ValueError):
            del args[i:i + 1]
    if any(a in ("-i", "--interactive") for a in args) and sys.stdin.isatty():
        interactive(); return
    free = [a for a in args if not a.startswith("-")]
    if free:
        banner("Scenario 3 — Research System", " ".join(free))
        run(" ".join(free), fail_idx=fail_idx); return
    banner("Scenario 3 — Research System (demo)", "topic: impact of AI on creative industries")
    h1("Broad decomposition, with subagent 6 timing out to show error propagation")
    run("impact of AI on creative industries", fail_idx=6)
    rule()
    tip("The coordinator broadens a known topic so decomposition isn't too narrow; a failed "
        "subagent returns STRUCTURED error context and the report ANNOTATES the gap instead "
        "of hiding it. Run -i for your own topic.")


if __name__ == "__main__":
    main()
