"""
Domain 1 · Task 1.1 — Design and implement agentic loops for autonomous task execution.

THE BIG IDEA
============
An "agent" is not one API call. It is a LOOP between your code and Claude:

    your code sends a request
      -> Claude replies with a `stop_reason`
         -> if stop_reason == "tool_use":  run the tool, append the result, loop again
         -> if stop_reason == "end_turn":  Claude is finished, exit and show the answer

Claude DECIDES which tool to call; YOUR CODE executes it. Claude never touches your
systems directly. Tool results MUST be appended to the conversation history or Claude
literally never learns what happened (it has no memory outside the conversation).

This file runs a complete loop for: "Where is my order #12345?"
Run it live (with ANTHROPIC_API_KEY) or offline (a deterministic simulator stands in
for the model so the control-flow is identical).
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from ccarch import ClaudeClient, LLMResponse, ToolCall
from ccarch import banner, concept, h1, h2, wrong, right, tip, note, kv, code, rule, pause, analogy, pitfall


# --- The tools the agent can call (your code owns these) ----------------------
ORDERS = {"12345": {"status": "shipped", "eta": "June 15", "customer_id": "CUST-9"}}


def lookup_order(order_id: str) -> dict:
    """Your code actually hits the backend here."""
    return ORDERS.get(order_id, {"error": "not_found"})


TOOLS = [
    {
        "name": "lookup_order",
        "description": "Look up the status and ETA of an order by its order_id.",
        "input_schema": {
            "type": "object",
            "properties": {"order_id": {"type": "string"}},
            "required": ["order_id"],
        },
    }
]


# --- Offline simulator: mimics how Claude would drive THIS conversation -------
def simulator(system, messages, tools) -> LLMResponse:
    """Turn 1: ask for the tool. Turn 2 (after a tool result is present): answer."""
    has_tool_result = any(
        isinstance(m.get("content"), list)
        and any(b.get("type") == "tool_result" for b in m["content"])
        for m in messages
    )
    if not has_tool_result:
        return LLMResponse(
            text="I'll look that up.",
            stop_reason="tool_use",
            tool_calls=[ToolCall(name="lookup_order", input={"order_id": "12345"})],
        )
    return LLMResponse(
        text="Good news — your order #12345 shipped and arrives June 15.",
        stop_reason="end_turn",
    )


def run_agent(client: ClaudeClient, user_message: str, max_safety_iterations: int = 10):
    system = (
        "You are a support agent. Use tools to find facts before answering. "
        "Never invent order status."
    )
    messages = [{"role": "user", "content": user_message}]

    for i in range(max_safety_iterations):  # safety net ONLY, not the real stop signal
        resp = client.complete(system, messages, tools=TOOLS, simulator=simulator)
        tag = "  (simulated)" if resp.simulated else "  (live)"
        h2(f"Iteration {i + 1}{tag} — stop_reason = {resp.stop_reason!r}")

        # >>> The decision that the whole exam hinges on <<<
        if resp.stop_reason == "end_turn":
            note(f"Claude is done. Final answer: {resp.text}")
            return resp.text

        if resp.stop_reason == "tool_use":
            # 1. record what Claude asked for
            messages.append(
                {"role": "assistant", "content": [
                    {"type": "tool_use", "id": tc.id, "name": tc.name, "input": tc.input}
                    for tc in resp.tool_calls
                ]}
            )
            # 2. YOUR CODE executes each tool and appends the result
            results = []
            for tc in resp.tool_calls:
                out = lookup_order(**tc.input)
                note(f"    your code ran {tc.name}({tc.input}) -> {out}")
                results.append({"type": "tool_result", "tool_use_id": tc.id,
                                "content": str(out)})
            messages.append({"role": "user", "content": results})
            # 3. loop continues so Claude can reason over the new facts

    return "[safety cap hit — investigate, this should rarely happen]"


def main():
    banner("Domain 1 · Task 1.1", "The Agentic Loop — stop_reason drives everything")
    concept("Domain 1: Agentic Architecture & Orchestration (27%)",
            "Task 1.1 — Design and implement agentic loops for autonomous task execution",
            "Loop on stop_reason; append tool results to history")

    h1("Watch one complete loop: 'Where is my order #12345?'")
    client = ClaudeClient()
    kv("client mode", client.mode)
    pause("the loop")
    run_agent(client, "Where is my order #12345?")

    rule()
    h1("Why tool results MUST go back into the conversation")
    note("Claude has no memory outside the messages list. If you execute lookup_order "
         "but forget to append the result, the next turn Claude is blind to it and will "
         "either re-call the tool forever or hallucinate an answer.")

    rule()
    h1("Anti-patterns the exam will tempt you with")
    wrong("Parsing Claude's natural-language text for 'I'm done' to decide when to stop. "
          "Fragile — Claude can add commentary next to a tool call.")
    wrong("Using an iteration cap ('stop after 10') as the PRIMARY stop mechanism. "
          "A cap is a safety net only; normal termination must be stop_reason == 'end_turn'.")
    wrong("Treating 'response contains text' as a completion signal. A turn can contain "
          "BOTH text and a tool_use block.")
    right("Inspect stop_reason. 'tool_use' -> run tool, append result, continue. "
          "'end_turn' -> exit and present the answer.")

    rule()
    h1("Plain-language analogy & the common confusion")
    analogy("Think of a chef (Claude) and a kitchen runner (your code). The chef calls out 'dice an onion' — a tool_use — but cannot reach the pantry; the runner fetches, dices, and hands the bowl back. The chef looks, calls the next step, and only when they say 'plate it, done' (end_turn) does the runner stop. The chef is the brain; the runner is the hands.")
    pitfall("The number-one beginner confusion: 'Claude runs the tool.' It does not. Claude only REQUESTS a tool; your code executes it and appends the result. Miss that and the whole loop stops making sense.")

    tip("If an answer option decides loop termination by anything other than stop_reason, "
        "it is almost certainly a distractor.")

    note("\nAlso know: model-driven > pre-scripted. The agent's value is that Claude picks "
         "the next tool from what it has learned — not a fixed flowchart your team hard-coded. "
         "Decision trees are brittle; model-driven loops adapt.")


if __name__ == "__main__":
    main()
