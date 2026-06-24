"""
Domain 2 · Task 2.2 — Structured error responses for MCP tools.

THE BIG IDEA
============
When a tool fails, HOW it reports failure determines whether the agent can recover. MCP
has an `isError` flag, but a bare "Operation failed" is useless — the agent can't tell
whether to retry, fix the input, apologize, or escalate.

Four error categories you MUST distinguish:
  transient  (timeout / service down)        -> retryable: YES  -> retry (locally first)
  validation (bad/missing input)             -> retryable: NO   -> fix input, try again
  business   (refund exceeds policy)         -> retryable: NO   -> explain politely / escalate
  permission (agent lacks access)            -> retryable: NO   -> escalate / authorized path

Return: errorCategory + isRetryable + a human-readable message.
Crucial: "the search FAILED" (access failure) != "the search SUCCEEDED and found nothing"
(a valid empty result). Conflating them wastes retries or hides data gaps.
"""

import sys, pathlib, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from ccarch import banner, concept, h1, h2, wrong, right, tip, note, kv, code, rule, pause


def err(category, retryable, message):
    return {"isError": True, "errorCategory": category,
            "isRetryable": retryable, "message": message}


def agent_decide(error: dict) -> str:
    """How a well-built agent reacts to each category."""
    cat = error["errorCategory"]
    return {
        "transient": "Retry (subagent attempts local recovery before bothering coordinator).",
        "validation": "Fix the malformed input, then retry once corrected.",
        "business_rule": "Explain the policy to the customer; offer alternatives or escalate.",
        "permission": "Escalate or route to an authorized path. Do not retry.",
    }[cat]


def main():
    banner("Domain 2 · Task 2.2", "Structured errors — so the agent can recover")
    concept("Domain 2: Tool Design & MCP Integration (18%)",
            "Task 2.2 — Implement structured error responses for MCP tools",
            "errorCategory + isRetryable + human-readable message")

    h1("A bare error teaches the agent nothing")
    wrong('{"isError": true, "message": "Operation failed"}  '
          '-- retry? rephrase? apologize? escalate? The agent is blind.')

    pause("the four categories")
    rule()
    h1("The four categories and the right agent behavior")
    cases = [
        err("transient", True, "Upstream service timed out."),
        err("validation", False, "order_id 'ABC' is malformed; expected #NNNNN."),
        err("business_rule", False,
            "Refund of $620.00 exceeds the $500 automatic limit. Offer escalation to a supervisor."),
        err("permission", False, "Agent lacks access to the billing system."),
    ]
    for e in cases:
        h2(f"{e['errorCategory']}  (isRetryable={e['isRetryable']})")
        note(f"    message: {e['message']}")
        right(f"agent: {agent_decide(e)}")

    rule()
    h1("Well-structured business-rule error (the model can act on every field)")
    code(json.dumps(cases[2], indent=2), "MCP error")
    note("Reading this, the agent knows: don't retry (fails forever), it's policy not a "
         "glitch, and here's the friendly path forward to offer.")

    pause("the subtle distinction")
    rule()
    h1("Failure vs. valid-empty — the subtle, tested distinction")
    wrong('Returning the SAME shape for "the search failed" and "the search found nothing". '
          'The agent either wastes retries on an empty result, or treats a real failure as '
          '"no data" and ships a report with silent holes.')
    code('# access failure (needs a retry decision)\n'
         '{"isError": true, "errorCategory": "transient", "isRetryable": true}\n\n'
         '# valid empty result (success!)\n'
         '{"isError": false, "results": [], "message": "0 matches"}', "two different things")

    rule()
    h1("Local recovery first")
    right("Subagents handle transient failures THEMSELVES and propagate upward only what "
          "they cannot resolve — together with partial results and a record of what was "
          "attempted. (Ties to Task 5.3 error propagation.)")

    tip("Memorize the categories: transient / validation / business / permission. Return "
        "errorCategory + isRetryable. Empty result != failure.")


if __name__ == "__main__":
    main()
