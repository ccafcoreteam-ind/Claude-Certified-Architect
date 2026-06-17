"""
PREPARATION EXERCISES — the 3 official hands-on exercises, mapped to this codebase
==================================================================================
The Exam Guide ends with three build-it-yourself exercises. This module restates each and
points to the files in THIS codebase that already implement a worked version, so learners
can read the reference, then rebuild from scratch.
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from ccarch import banner, h1, h2, kv, note, rule, tip


EXERCISES = [
    dict(
        title="Exercise 1 — Build a Multi-Tool Agent with Escalation Logic",
        domains="D1, D2, D5",
        steps=[
            "Define 3-4 MCP tools with detailed, differentiated descriptions (include two "
            "similar tools that need careful descriptions to avoid confusion).",
            "Implement an agentic loop that checks stop_reason ('tool_use' vs 'end_turn').",
            "Add structured error responses (errorCategory, isRetryable, human message); "
            "handle each type appropriately.",
            "Add a hook that intercepts tool calls to enforce a business rule (block over a "
            "threshold), redirecting to escalation.",
            "Test multi-concern messages: decompose, handle each, synthesize one response.",
        ],
        reference=["scenarios/scenario1_customer_support/support_agent.py",
                   "domains/domain1_orchestration/task1_1_agentic_loop.py",
                   "domains/domain2_tools_mcp/task2_2_structured_errors.py",
                   "domains/domain1_orchestration/task1_5_hooks.py"],
    ),
    dict(
        title="Exercise 2 — Configure Claude Code for a Team Development Workflow",
        domains="D3, D2",
        steps=[
            "Create a project-level CLAUDE.md with universal standards; verify it applies "
            "to all team members.",
            "Create .claude/rules/ files with YAML glob frontmatter (api, testing); verify "
            "they load only on matching files.",
            "Create a project skill with context: fork and allowed-tools; verify isolation.",
            "Configure an MCP server in .mcp.json with ${ENV_VAR}; add a personal one in "
            "~/.claude.json; verify both are available.",
            "Compare plan mode vs direct execution across a 1-file fix, a 45-file migration, "
            "and a multi-approach feature.",
        ],
        reference=["domains/domain3_claude_code/examples/  (CLAUDE.md, .claude/, .mcp.json)",
                   "domains/domain3_claude_code/task3_1_claudemd_hierarchy.py",
                   "domains/domain3_claude_code/task3_3_path_rules.py",
                   "domains/domain3_claude_code/task3_4_plan_mode.py",
                   "scenarios/scenario2_code_generation/code_generation_workflow.py"],
    ),
    dict(
        title="Exercise 3 — Build a Structured Data Extraction Pipeline",
        domains="D4, D5",
        steps=[
            "Define an extraction tool whose JSON schema has required + optional fields, an "
            "enum with 'other'+detail, and nullable fields; verify null (not fabrication) "
            "when data is absent.",
            "Implement a validation-retry loop: on failure, resend document + failed "
            "extraction + specific errors. Track resolvable (format) vs futile (absent info).",
            "Add self-correcting fields (stated_total vs calculated_total).",
            "Design batch vs synchronous routing; use custom_id for correlation + partial "
            "resubmission.",
            "Add field-level confidence + route low-confidence to humans; audit high-conf "
            "samples (stratified).",
        ],
        reference=["scenarios/scenario6_structured_extraction/extraction_pipeline.py",
                   "domains/domain4_prompt_output/task4_3_structured_output_schema.py",
                   "domains/domain4_prompt_output/task4_4_validation_retry.py",
                   "domains/domain4_prompt_output/task4_5_batch_processing.py",
                   "domains/domain5_context_reliability/task5_5_human_review.py"],
    ),
]


def main():
    banner("Preparation Exercises", "The 3 official hands-on builds, with references")
    for ex in EXERCISES:
        h1(ex["title"])
        kv("  domains reinforced", ex["domains"])
        h2("Steps")
        for i, s in enumerate(ex["steps"], 1):
            note(f"  {i}. {s}")
        h2("Worked reference in THIS codebase")
        for r in ex["reference"]:
            kv("  →", r)
        rule()
    tip("Read the reference implementation, then rebuild the exercise from a blank file. "
        "The exam rewards judgment you can only get from hands-on practice.")


if __name__ == "__main__":
    main()
