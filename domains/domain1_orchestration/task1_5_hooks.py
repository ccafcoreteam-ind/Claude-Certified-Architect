"""
Domain 1 · Task 1.5 — Agent SDK hooks: interception and normalization.

THE BIG IDEA
============
Hooks are checkpoints around tool calls. Two patterns matter:

  * PostToolUse (AFTER a tool returns): transform/normalize results before Claude sees
    them. E.g., three backends return dates as Unix timestamps, ISO 8601 strings, and
    numeric status codes — a PostToolUse hook normalizes them to ONE format so the agent
    never juggles inconsistencies.

  * Tool-call interception (BEFORE a tool runs): inspect outgoing calls and BLOCK policy
    violations. E.g., any process_refund above $500 is blocked and redirected to human
    escalation — guaranteed, every time, regardless of the prompt.

Same dichotomy as Task 1.4: "guaranteed compliance required" -> hook (deterministic).
The distractors offer prompt wording / few-shot / confidence thresholds instead.
"""

import sys, pathlib
from datetime import datetime, timezone
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from ccarch import banner, concept, h1, h2, wrong, right, tip, note, kv, code, rule, pause, analogy, pitfall


# --- PostToolUse: normalize heterogeneous date formats to one ISO 8601 string -
def normalize_dates(tool_name, raw_result: dict) -> dict:
    out = dict(raw_result)
    val = out.get("date")
    if isinstance(val, (int, float)):                      # Unix timestamp
        out["date"] = datetime.fromtimestamp(val, tz=timezone.utc).date().isoformat()
    elif isinstance(val, str) and val.isdigit():           # numeric status code as string
        out["date"] = datetime.fromtimestamp(int(val), tz=timezone.utc).date().isoformat()
    # already-ISO strings pass through unchanged
    out["_normalized_by"] = "PostToolUse hook"
    return out


# --- Interception: block refunds over the policy threshold --------------------
REFUND_LIMIT = 500.0

def refund_interceptor(tool_name, tool_input: dict):
    """Return (allowed, redirected_action)."""
    if tool_name == "process_refund" and tool_input.get("amount", 0) > REFUND_LIMIT:
        return False, {
            "action": "escalate_to_human",
            "reason": f"Refund ${tool_input['amount']:.2f} exceeds ${REFUND_LIMIT:.0f} limit",
        }
    return True, None


def main():
    banner("Domain 1 · Task 1.5", "Hooks — normalize after, intercept before")
    concept("Domain 1: Agentic Architecture & Orchestration (27%)",
            "Task 1.5 — Apply Agent SDK hooks for tool call interception and data normalization",
            "PostToolUse normalization + interception gating")

    h1("PostToolUse hook: normalize heterogeneous tool outputs")
    note("Three backends return the same 'date' field three different ways. The hook makes "
         "them uniform BEFORE the agent reasons over them.")
    samples = [
        ("billing_system", {"date": 1717200000}),            # Unix timestamp
        ("orders_system", {"date": "2024-06-01"}),           # already ISO
        ("legacy_system", {"date": "1717200000"}),           # numeric string
    ]
    for name, raw in samples:
        fixed = normalize_dates(name, raw)
        kv(f"  {name}", f"{raw}  ->  {fixed['date']}")
    right("One PostToolUse hook = the agent never has to know three date formats exist.")

    pause("interception")
    rule()
    h1("Interception hook: block policy violations BEFORE they run")
    for amount in (80.0, 620.0):
        allowed, redirect = refund_interceptor("process_refund", {"amount": amount})
        if allowed:
            right(f"process_refund(${amount:.2f}) -> allowed (under ${REFUND_LIMIT:.0f}).")
        else:
            wrong(f"process_refund(${amount:.2f}) -> BLOCKED.")
            note(f"    redirected: {redirect}")

    rule()
    h1("Hooks vs prompts — the same dichotomy as Task 1.4")
    note("Analogy: a mailroom that opens every package and standardizes the paperwork "
         "(PostToolUse), plus a finance gate that physically cannot release payments above "
         "a threshold without a manager's signature (interception).")

    rule()
    h1("A common confusion to clear up")
    pitfall('Learners mix up the two hook directions. PostToolUse runs AFTER a tool to clean up its RESULT; interception runs BEFORE a tool to allow or block the CALL. After = tidy the data; before = guard the action.')

    tip("'Guaranteed compliance required' -> hook. Distractors will offer prompt wording, "
        "few-shot examples, or confidence thresholds — all probabilistic, all wrong when "
        "the rule must hold 100% of the time.")


if __name__ == "__main__":
    main()
