"""
ONE-PAGE CHEAT SHEET — facts to memorize
=========================================
Prints the exam's high-yield facts, grouped by topic, each tagged with the demo that
shows it running. This mirrors Chapter 12 of the study guide.
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from ccarch import banner, h1, kv, note, rule, tip


FACTS = [
    ("stop_reason", "'tool_use' = run tool & continue; 'end_turn' = done. Never parse text "
     "or rely on iteration caps to terminate.", "domain1/task1_1"),
    ("Subagent memory", "Isolated — pass context explicitly in the prompt; coordinator needs "
     "'Task' in allowedTools.", "domain1/task1_3"),
    ("Parallel subagents", "Multiple Task calls in ONE coordinator response.", "domain1/task1_3"),
    ("Enforcement", "Guaranteed rules → hooks/gates (deterministic); preferences → prompts "
     "(probabilistic).", "domain1/task1_4"),
    ("Hooks", "PostToolUse = normalize results after; interception = block policy violations "
     "before (refunds > $500).", "domain1/task1_5"),
    ("Decomposition", "Known steps → prompt chaining; unknown/open-ended → dynamic adaptive.",
     "domain1/task1_6"),
    ("Sessions", "--resume = continue named thread; fork_session = branches from one baseline; "
     "stale results → fresh start + summary.", "domain1/task1_7"),
    ("Tool selection", "Driven by DESCRIPTIONS; ~4-5 well-described beat 18; first fix = "
     "better descriptions.", "domain2/task2_1"),
    ("Errors", "Categories transient/validation/business/permission; return errorCategory + "
     "isRetryable; empty result ≠ failure.", "domain2/task2_2"),
    ("tool_choice", '"auto" = optional; "any" = must call some tool; '
     '{"type":"tool","name":…} = must call that tool.', "domain2/task2_3"),
    ("MCP scoping", ".mcp.json = project/shared; ~/.claude.json = personal; secrets via "
     "${ENV_VAR}; resources = catalogs, tools = actions.", "domain2/task2_4"),
    ("Built-ins", "Grep = file CONTENTS; Glob = file NAMES; Edit needs a unique anchor "
     "(fallback Read + Write).", "domain2/task2_5"),
    ("CLAUDE.md levels", "User (~/.claude, personal) · Project (repo, shared) · Directory "
     "(scoped); @import for modularity; /memory to debug.", "domain3/task3_1"),
    ("Commands & skills", ".claude/commands/ = shared; ~/.claude/commands/ = personal; skill "
     "frontmatter: context: fork, allowed-tools, argument-hint.", "domain3/task3_2"),
    ("Path rules", ".claude/rules/ + YAML paths: ['glob'] → loads only when editing matching "
     "files.", "domain3/task3_3"),
    ("Plan mode", "Architectural / multi-file / multiple approaches → plan; single "
     "well-scoped fix → direct.", "domain3/task3_4"),
    ("CI/CD", "-p / --print = non-interactive; --output-format json + --json-schema = "
     "structured CI output. (CLAUDE_HEADLESS / --batch don't exist.)", "domain3/task3_6"),
    ("Schemas", "Tool use kills JSON SYNTAX errors, NOT semantic; nullable fields prevent "
     "fabrication; enums need 'unclear'/'other'+detail.", "domain4/task4_3"),
    ("Retry", "Works for format/structure errors; FUTILE when info is absent from the "
     "source.", "domain4/task4_4"),
    ("Batches API", "50% cheaper, ≤24h window, NO latency SLA, no multi-turn tool calling; "
     "custom_id correlates & enables partial resubmission.", "domain4/task4_5"),
    ("Review", "Independent fresh instance > self-review; large PRs → per-file passes + "
     "integration pass.", "domain4/task4_6"),
    ("Context", "'Case facts' block survives summarization; lost-in-the-middle → summary "
     "first + section headers; trim tool outputs early.", "domain5/task5_1"),
    ("Escalation", "Triggers: explicit human request (honor now), policy gap, no progress. "
     "NOT sentiment, NOT self-confidence.", "domain5/task5_2"),
    ("Provenance", "Preserve claim-source mappings through synthesis; annotate conflicts "
     "with both sources; include dates to avoid temporal 'contradictions'.", "domain5/task5_6"),
]

WEIGHTS = [
    ("Domain 1 — Agentic Architecture & Orchestration", "27%"),
    ("Domain 2 — Tool Design & MCP Integration", "18%"),
    ("Domain 3 — Claude Code Configuration & Workflows", "20%"),
    ("Domain 4 — Prompt Engineering & Structured Output", "20%"),
    ("Domain 5 — Context Management & Reliability", "15%"),
]


def main():
    banner("Cheat Sheet", "High-yield facts · each tagged with its demo")
    h1("Exam at a glance")
    kv("  Format", "Multiple choice, 1 correct + 3 distractors; no penalty for guessing")
    kv("  Scenarios", "4 of 6 published scenarios, drawn at random")
    kv("  Score", "Scaled 100-1000; passing = 720; Pass/Fail")
    kv("  Candidate", "Solution architect, ~6+ months hands-on with Claude")

    h1("Domain weights (study Domains 1 + 2 first — 45% together)")
    for name, w in WEIGHTS:
        kv(f"  {w}", name)

    h1("Facts to memorize")
    for topic, fact, demo in FACTS:
        kv(f"  {topic}", fact)
        note(f"      ↳ run: domains/{demo}.py")
    rule()

    h1("The three recurring themes")
    note("1. GUARANTEES BEAT INSTRUCTIONS — must-follow rules → code (hooks/gates), not prompts.")
    note("2. FIX THE ROOT CAUSE, PROPORTIONATELY — vague tool descriptions → better "
         "descriptions, not a classifier. The exam loves over-engineered distractors.")
    note("3. CONTEXT IS A SCARCE, LEAKY RESOURCE — extract key facts, trim noise, pass "
         "information explicitly between agents.")

    tip("The exam's underlying question is always: what is the SIMPLEST mechanism that "
        "RELIABLY fixes the actual ROOT CAUSE?")


if __name__ == "__main__":
    main()
