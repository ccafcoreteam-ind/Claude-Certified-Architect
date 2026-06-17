# The Six Exam Scenarios — runnable end-to-end systems

Every exam question lives inside one of six production scenarios; you see 4 of the 6 on
your exam. Each folder here is a **runnable** system that ties together the domains that
scenario tests.

| # | Scenario | Primary domains | Run |
|---|---|---|---|
| 1 | Customer Support Resolution Agent | D1 · D2 · D5 | `python3 scenarios/scenario1_customer_support/support_agent.py` |
| 2 | Code Generation with Claude Code | D3 · D5 | `python3 scenarios/scenario2_code_generation/code_generation_workflow.py` |
| 3 | Multi-Agent Research System | D1 · D2 · D5 | `python3 scenarios/scenario3_multi_agent_research/research_system.py` |
| 4 | Developer Productivity | D2 · D3 · D1 | `python3 scenarios/scenario4_developer_productivity/codebase_explorer.py` |
| 5 | Claude Code for CI/CD | D3 · D4 | `python3 scenarios/scenario5_cicd/ci_review_pipeline.py` |
| 6 | Structured Data Extraction | D4 · D5 | `python3 scenarios/scenario6_structured_extraction/extraction_pipeline.py` |

```bash
python3 run_all.py scenarios     # run all six, non-stop
```

## What each one demonstrates

- **Scenario 1** — a real agent loop with a **prerequisite gate** (no refund before
  identity), an **interception hook** ($500 cap → escalation), **structured tool errors**,
  a persistent **case-facts** block, and a **structured handoff** to a human. Shows three
  cases: happy path, gate-blocks-early-refund, and over-limit → escalation.
- **Scenario 2** — the team-enablement judgment calls: what's shared vs personal, the
  "new teammate doesn't get conventions" diagnostic, path rules, and plan-vs-direct.
- **Scenario 3** — a coordinator + subagents that reproduces the **narrow-decomposition
  failure** (and its fix), **parallel spawning**, **structured error propagation** on a
  timeout, **coverage annotations**, and **provenance** preservation.
- **Scenario 4** — *actually* explores a tiny sample repo it creates: Glob (names) vs Grep
  (contents), then **incremental** Grep→Read following imports, plus delegation + scratchpad.
- **Scenario 5** — non-interactive `-p`, structured JSON findings, **false-positive
  control**, **independent** review instance, and **multi-pass** review of a large PR.
- **Scenario 6** — tool-use **schema**, **nullable** fields, **validation + retry** (and
  recognizing a futile retry), self-correcting totals, **batch vs sync** routing, and
  **confidence routing** to human review.
