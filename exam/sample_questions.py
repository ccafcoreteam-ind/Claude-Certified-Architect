"""
THE 12 OFFICIAL SAMPLE QUESTIONS — interactive walkthroughs
===========================================================
These are the twelve sample questions published in the official Exam Guide, with their
correct answers and the reasoning for why each distractor fails. Each question is tagged
with the scenario, the domain/task it exercises, and the demo file that shows the concept
running.

Run interactively (it prompts A/B/C/D and grades you), or set CCARCH_NONSTOP=1 to print
all questions with answers and explanations (used by run_all.py and CI).

The transferable pattern across ALL twelve:
    root cause + the SIMPLEST reliable mechanism wins.
Distractors are: (1) more prompting where ENFORCEMENT is needed, (2) more infrastructure
where prompting suffices, and (3) features that DON'T EXIST. Spot an invented flag/config
and eliminate it instantly.
"""

import sys, os, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from ccarch import banner, h1, h2, wrong, right, tip, note, kv, rule, pause
from ccarch.display import _c


QUESTIONS = [
    dict(
        n=1, scenario="Customer Support", maps="D1 T1.4 · demo: domain1/task1_4 · scenario 1",
        q="In 12% of cases the agent skips get_customer and calls lookup_order using only "
          "the customer's stated name, causing misidentified accounts and wrong refunds. "
          "What change most effectively fixes this reliability issue?",
        options={
            "A": "Add a programmatic prerequisite that blocks lookup_order and "
                 "process_refund until get_customer returns a verified customer ID.",
            "B": "Enhance the system prompt to state that verification is mandatory.",
            "C": "Add few-shot examples showing the agent always calling get_customer first.",
            "D": "Implement a routing classifier that enables a subset of tools per request.",
        },
        answer="A",
        why="A required tool SEQUENCE for critical business logic needs DETERMINISTIC "
            "enforcement — a gate. Strengthening the prompt or adding few-shot examples "
            "relies on probabilistic LLM compliance, insufficient when errors move money. "
            "A routing classifier addresses tool AVAILABILITY, not the ORDERING that is the "
            "actual problem.",
    ),
    dict(
        n=2, scenario="Customer Support", maps="D2 T2.1 · demo: domain2/task2_1 · scenario 1",
        q="The agent calls get_customer when users ask about orders. Both tools have minimal "
          "descriptions and accept similar IDs. Most effective FIRST step to improve tool "
          "selection?",
        options={
            "A": "Add 5-8 few-shot examples of correct tool selection to the system prompt.",
            "B": "Expand each tool's description: input formats, example queries, edge "
                 "cases, and boundaries (when to use it vs the similar tool).",
            "C": "Implement a routing layer that parses input and pre-selects the tool.",
            "D": "Consolidate both tools into one lookup_entity tool.",
        },
        answer="B",
        why="Descriptions are the PRIMARY tool-selection mechanism; minimal ones starve the "
            "model of context, so richer descriptions are the low-effort root-cause fix. "
            "Few-shot examples add tokens without fixing the cause; a routing layer is "
            "over-engineered; consolidating the tools is a bigger change than a 'first "
            "step' warrants.",
    ),
    dict(
        n=3, scenario="Customer Support", maps="D5 T5.2 · demo: domain5/task5_2 · scenario 1",
        q="The agent hits 55% first-contact resolution (target 80%): it escalates "
          "straightforward cases and attempts complex policy-exception ones. Best fix for "
          "escalation calibration?",
        options={
            "A": "Add explicit escalation criteria + few-shot examples to the system prompt.",
            "B": "Have the agent self-report a confidence score and route below a threshold.",
            "C": "Deploy a separate classifier trained on historical tickets.",
            "D": "Add sentiment analysis and escalate on high negative sentiment.",
        },
        answer="A",
        why="Root cause = unclear decision boundaries; explicit criteria + few-shot is the "
            "proportionate fix. Self-reported confidence is miscalibrated (overconfident on "
            "hard cases); a separate trained classifier is over-engineered; sentiment "
            "analysis solves a different problem — sentiment ≠ complexity.",
    ),
    dict(
        n=4, scenario="Code Generation", maps="D3 T3.2 · demo: domain3/task3_2 · scenario 2",
        q="You want a /review command available to every developer when they clone or pull "
          "the repo. Where do you create it?",
        options={
            "A": "In .claude/commands/ in the project repository.",
            "B": "In ~/.claude/commands/ in each developer's home directory.",
            "C": "In the CLAUDE.md file at the project root.",
            "D": "In a .claude/config.json file with a commands array.",
        },
        answer="A",
        why="Project-scoped commands in .claude/commands/ are version-controlled and reach "
            "everyone. A personal ~/.claude/ command is not shared; the root CLAUDE.md is for "
            "context, not command definitions; a .claude/config.json commands array describes "
            "a mechanism that doesn't exist.",
    ),
    dict(
        n=5, scenario="Code Generation", maps="D3 T3.4 · demo: domain3/task3_4 · scenario 2",
        q="You must restructure a monolith into microservices: changes across dozens of "
          "files, decisions about service boundaries and dependencies. Which approach?",
        options={
            "A": "Enter plan mode to explore, understand dependencies, and design first.",
            "B": "Start with direct execution; let implementation reveal boundaries.",
            "C": "Direct execution with comprehensive upfront instructions.",
            "D": "Begin direct; switch to plan mode only if complexity emerges.",
        },
        answer="A",
        why="Plan mode is built for large-scale, multi-approach, architectural work. "
            "Starting with direct execution risks costly rework; comprehensive upfront "
            "instructions assume you already know the structure; deferring to plan mode "
            "'only if complexity emerges' ignores that the complexity is ALREADY stated, "
            "not hypothetical.",
    ),
    dict(
        n=6, scenario="Code Generation", maps="D3 T3.3 · demo: domain3/task3_3 · scenario 2",
        q="Distinct areas have different conventions; test files are spread throughout next "
          "to the code they test. You want the right conventions applied AUTOMATICALLY by "
          "file path. Most maintainable approach?",
        options={
            "A": "Rule files in .claude/rules/ with YAML frontmatter glob patterns.",
            "B": "Consolidate everything in the root CLAUDE.md under headers.",
            "C": "Create skills in .claude/skills/ for each code type.",
            "D": "A separate CLAUDE.md in each subdirectory.",
        },
        answer="A",
        why="Glob-pattern rule files (e.g., **/*.test.tsx) apply by path regardless of "
            "directory — essential for scattered files. A single root CLAUDE.md relies on "
            "inference; skills need manual invocation; a per-directory CLAUDE.md can't follow "
            "files spread across many directories.",
    ),
    dict(
        n=7, scenario="Multi-Agent Research", maps="D1 T1.2 · demo: domain1/task1_2 · scenario 3",
        q="Each subagent succeeds, but reports cover only visual arts (missing music, "
          "writing, film). The coordinator's log shows it decomposed into 'digital art', "
          "'graphic design', 'photography'. Most likely root cause?",
        options={
            "A": "The synthesis agent lacks gap-identification instructions.",
            "B": "The coordinator's task decomposition is too narrow.",
            "C": "The web search agent's queries aren't comprehensive enough.",
            "D": "The document analysis agent filters out non-visual sources.",
        },
        answer="B",
        why="The logs show the coordinator only created visual-arts subtasks. Subagents "
            "executed their assignments correctly — the problem is WHAT they were assigned. "
            "The other options blame downstream agents (synthesis, web search, document "
            "analysis) that worked correctly.",
    ),
    dict(
        n=8, scenario="Multi-Agent Research", maps="D5 T5.3 · demo: domain5/task5_3 · scenario 3",
        q="The web search subagent times out. How should that failure flow back to the "
          "coordinator to enable intelligent recovery?",
        options={
            "A": "Structured error context: failure type, attempted query, partial results, "
                 "alternative approaches.",
            "B": "Retry internally with backoff; return a generic 'search unavailable'.",
            "C": "Catch the timeout and return an empty result set marked successful.",
            "D": "Propagate the exception to a top-level handler that terminates the workflow.",
        },
        answer="A",
        why="Structured error context lets the coordinator retry with modifications, try an "
            "alternative, or proceed with partial results. A generic 'search unavailable' "
            "status hides that context; marking a timeout as successful suppresses the error "
            "into silent holes; propagating an exception that terminates the workflow "
            "overreacts by killing the whole run.",
    ),
    dict(
        n=9, scenario="Multi-Agent Research", maps="D2 T2.3 · demo: domain2/task2_3 · scenario 3",
        q="The synthesis agent frequently round-trips through the coordinator to verify "
          "facts (+40% latency). 85% are simple fact-checks, 15% need deeper investigation. "
          "Most effective fix?",
        options={
            "A": "Give synthesis a scoped verify_fact tool for simple lookups; complex ones "
                 "still go through the coordinator.",
            "B": "Have synthesis batch all verifications and return them at the end.",
            "C": "Give synthesis access to all web search tools.",
            "D": "Have the web search agent pre-cache extra context around each source.",
        },
        answer="A",
        why="Least privilege: give synthesis exactly the scoped tool for the common 85% and "
            "keep the complex 15% routed through the coordinator. Batching all verifications "
            "creates blocking dependencies; giving it every web-search tool over-provisions "
            "(it starts searching instead of synthesizing); pre-caching extra context can't "
            "predict what will be needed.",
    ),
    dict(
        n=10, scenario="CI/CD", maps="D3 T3.6 · demo: domain3/task3_6 · scenario 5",
        q="Your pipeline runs `claude \"Analyze this PR\"` but the job hangs waiting for "
          "interactive input. Correct approach to run in an automated pipeline?",
        options={
            "A": 'Add the -p flag: claude -p "Analyze this PR".',
            "B": "Set CLAUDE_HEADLESS=true before running.",
            "C": "Redirect stdin from /dev/null.",
            "D": "Add the --batch flag.",
        },
        answer="A",
        why="-p / --print is the documented non-interactive mode: process, print, exit. "
            "CLAUDE_HEADLESS and --batch reference non-existent features; redirecting stdin "
            "from /dev/null is a Unix workaround that doesn't address Claude Code's command "
            "syntax.",
    ),
    dict(
        n=11, scenario="CI/CD / Cost", maps="D4 T4.5 · demo: domain4/task4_5 · scenario 5/6",
        q="Two workflows use real-time calls: (1) a BLOCKING pre-merge check, (2) an "
          "overnight technical-debt report. A manager proposes switching BOTH to the Batch "
          "API for 50% savings. How do you evaluate it?",
        options={
            "A": "Batch the overnight reports only; keep real-time for pre-merge checks.",
            "B": "Switch both to batch with status polling.",
            "C": "Keep real-time for both to avoid batch result ordering issues.",
            "D": "Switch both to batch with a timeout fallback to real-time.",
        },
        answer="A",
        why="Batch is 50% cheaper but takes up to 24h with NO latency SLA — unfit for a "
            "blocking pre-merge check, ideal for overnight jobs. Switching both to batch "
            "isn't acceptable for blocking work; keeping both real-time forgoes easy savings "
            "and misreads batch ordering (custom_id correlates results); a timeout fallback "
            "adds needless complexity.",
    ),
    dict(
        n=12, scenario="CI/CD / Review", maps="D4 T4.6 · demo: domain4/task4_6 · scenario 5",
        q="A 14-file PR reviewed in one pass gives inconsistent, contradictory results "
          "(detailed for some files, superficial for others; flags a pattern in one file, "
          "approves identical code in another). How to restructure?",
        options={
            "A": "Per-file passes for local issues + a separate cross-file integration pass.",
            "B": "Require developers to split PRs into 3-4 files before review.",
            "C": "Switch to a higher-tier model with a larger context window.",
            "D": "Run three passes; flag only issues appearing in ≥2 of 3.",
        },
        answer="A",
        why="Root cause = attention dilution. Per-file passes give consistent depth and a "
            "separate integration pass catches cross-file issues. Forcing developers to split "
            "PRs shifts the burden to them; a bigger context window misunderstands that more "
            "context ≠ better attention; keeping only issues found in ≥2 of 3 passes "
            "suppresses real, intermittently-caught bugs.",
    ),
]


def ask(qd) -> bool:
    h1(f"Q{qd['n']} — Scenario: {qd['scenario']}")
    note(f"[{qd['maps']}]")
    note(qd["q"])
    print()
    for k in ("A", "B", "C", "D"):
        kv(f"  {k}", qd["options"][k])
    interactive = sys.stdin.isatty() and not os.environ.get("CCARCH_NONSTOP")
    chosen = None
    if interactive:
        try:
            chosen = input(_c("    Your answer (A/B/C/D): ", "dim")).strip().upper()
        except (EOFError, KeyboardInterrupt):
            print()
    correct = qd["answer"]
    if chosen in ("A", "B", "C", "D"):
        if chosen == correct:
            right(f"Correct — {correct}.")
        else:
            wrong(f"You chose {chosen}. Correct answer: {correct}.")
    else:
        right(f"Correct answer: {correct}.")
    note("Why: " + qd["why"])
    return chosen == correct if chosen else None


def main():
    banner("Exam Practice", "The 12 official sample questions, with reasoning")
    note("Pattern to internalize: root cause + simplest reliable mechanism wins. "
         "Distractors = more-prompting-where-enforcement-is-needed, "
         "more-infrastructure-where-prompting-suffices, or invented features.")
    score, answered = 0, 0
    for qd in QUESTIONS:
        pause(f"Q{qd['n']}")
        result = ask(qd)
        if result is not None:
            answered += 1
            score += 1 if result else 0
    rule()
    if answered:
        h1(f"Score: {score}/{answered}")
        note("Exam passing score is 720/1000. Re-study any domain where you missed a "
             "question — each maps to a demo file above.")
    else:
        tip("All 12 follow the same logic. Run interactively (without CCARCH_NONSTOP) to "
            "grade yourself.")


if __name__ == "__main__":
    main()
