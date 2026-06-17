# Teaching Guide — running this codebase in a session

This codebase is built to be **taught from a terminal**. Each demo is a sequence of slides
that print to the screen with `[press ENTER]` pauses, so you can talk between steps and
control the pace.

## Before the session

- Projector-friendly output: the demos auto-detect a terminal and use colour. To force
  plain text (some projectors mangle colour), run with `NO_COLOR=1`.
- Decide live vs simulated. Simulated needs nothing. For live model calls,
  `pip install -r requirements.txt` and `export ANTHROPIC_API_KEY=...` first.
- Sanity check everything in one shot: `python3 run_all.py --check` (should print `ALL PASS`).

## How to drive a demo live

Run a single file directly so the pauses are active:

```bash
python3 domains/domain1_orchestration/task1_1_agentic_loop.py
```

Each file follows the same rhythm:
1. **Banner + Concept** — which domain/task and the one-line idea.
2. **Demonstration** — the concept actually running (a loop, a gate, a schema, a router…).
3. **✗ Anti-patterns** — the exact shapes the exam uses as distractors.
4. **✓ Root-cause fix** and a **★ Exam tip**.

## A suggested 5-session course (maps to the study guide's 2-week plan)

### Session 1 — Foundations & the mindset (30–40 min)
- Open with `python3 exam/cheatsheet.py` → "Exam at a glance" + the three themes.
- Teach the central distinction with `domains/domain1_orchestration/task1_4_workflow_enforcement.py`
  (guarantees beat instructions). This single idea unlocks ~a third of the exam.

### Session 2 — Domain 1 + 2 (the 45%) (60 min)
- `domain1` group: loop → coordinator/subagents → invocation → enforcement → hooks →
  decomposition → sessions. Spend longest on 1.1, 1.2, 1.4.
- `domain2` group: tool descriptions (2.1), structured errors (2.2), tool_choice (2.3),
  MCP scoping (2.4), Grep-vs-Glob (2.5).
- Close by running **Scenario 1** (`scenarios/scenario1_customer_support/support_agent.py`)
  and **Scenario 3** (`.../research_system.py`) — they tie D1+D2 together.

### Session 3 — Domain 3, hands-on (45 min)
- Walk the real artifacts in `domains/domain3_claude_code/examples/` (CLAUDE.md, the
  `.claude/` tree, `.mcp.json`). Open the files alongside the demos.
- Run 3.1 (hierarchy), 3.3 (path rules), 3.4 (plan mode), 3.6 (CI/CD).
- Run **Scenario 2** and **Scenario 4** (Scenario 4 does real Grep→Read exploration).

### Session 4 — Domain 4 + 5 (60 min)
- `domain4`: explicit criteria (4.1), few-shot (4.2 — run live if you have a key), schemas
  (4.3), validation/retry (4.4), batch (4.5), multi-pass review (4.6).
- `domain5`: case-facts (5.1), escalation (5.2), error propagation (5.3), large codebases
  (5.4), human review (5.5), provenance (5.6).
- Run **Scenario 5** and **Scenario 6**.

### Session 5 — Exam logic & practice (45 min)
- Run `python3 exam/sample_questions.py` **interactively** — let the room vote A/B/C/D
  before revealing each answer, then discuss *why each distractor fails*.
- Hand out `exam/prep_exercises.py` as homework; the worked references are in the repo.

## Facilitation tips

- For every question, ask the room to name the **root cause** before picking an option.
- Train the reflex: an **invented flag or config file** (`CLAUDE_HEADLESS`, `--batch`,
  `.claude/config.json commands array`) is always a distractor — eliminate on sight.
- When two options both "sound reasonable", the right one is usually the **simpler,
  more deterministic** mechanism that fixes the actual cause.
