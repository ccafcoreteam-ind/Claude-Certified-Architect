"""
SCENARIO 1 — Customer Support Resolution Agent  (Agent SDK)
===========================================================
A runnable, end-to-end support agent that ties together the concepts the exam attaches to
this scenario: D1 Orchestration, D2 Tools/MCP, D5 Context & Reliability.

It exposes four MCP-style tools — get_customer, lookup_order, process_refund,
escalate_to_human — and demonstrates, in ONE program:

  * the agentic loop driven by stop_reason                 (D1 T1.1)
  * a PREREQUISITE GATE: process_refund is impossible until get_customer verifies identity
    (D1 T1.4 / sample Q1)
  * an INTERCEPTION HOOK: refunds over $500 are blocked and redirected to escalation
    (D1 T1.5)
  * STRUCTURED tool errors with errorCategory + isRetryable (D2 T2.2)
  * a persistent CASE-FACTS block that survives summarization (D5 T5.1)
  * rule-based ESCALATION (explicit request / policy gap / no progress) (D5 T5.2)
  * a STRUCTURED HANDOFF packet for the human (D1 T1.4)

Target (per the scenario): 80%+ first-contact resolution while knowing when to escalate.

Run it offline (deterministic simulator) or live (ANTHROPIC_API_KEY). Use --demo to run a
scripted walkthrough, or run with no args for the same.
"""

import sys, pathlib, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from ccarch import ClaudeClient, LLMResponse, ToolCall
from ccarch import banner, concept, h1, h2, wrong, right, tip, note, kv, code, rule, pause

REFUND_LIMIT = 500.0

# ---------------------------------------------------------------- backend data
CUSTOMERS = {
    "dana@example.com": {"customer_id": "CUST-9", "name": "Dana Lee", "tier": "gold"},
}
ORDERS = {
    "88231": {"customer_id": "CUST-9", "status": "delivered_damaged", "total": 84.75},
    "90011": {"customer_id": "CUST-9", "status": "shipped", "total": 620.00},
}


# ------------------------------------------------------- structured error helper
def tool_error(category, retryable, message):
    return {"isError": True, "errorCategory": category, "isRetryable": retryable,
            "message": message}


# ------------------------------------------------------------------- the agent
class SupportAgent:
    def __init__(self, client: ClaudeClient):
        self.client = client
        self.verified_customer_id = None          # the gate's state (D1 T1.4)
        self.case_facts = {}                      # persistent facts block (D5 T5.1)
        self.transcript = []

    # ---- tools (your code owns these; Claude only REQUESTS them) ----
    def get_customer(self, email=None):
        cust = CUSTOMERS.get(email)
        if not cust:
            return tool_error("validation", False, f"No customer for {email!r}; ask for a "
                              "valid email or customer ID.")
        self.verified_customer_id = cust["customer_id"]      # <-- unlocks the gate
        self.case_facts["customer_id"] = cust["customer_id"]
        self.case_facts["name"] = cust["name"]
        return {"verified_customer_id": cust["customer_id"], "name": cust["name"],
                "tier": cust["tier"]}

    def lookup_order(self, order_id=None):
        # PREREQUISITE GATE: cannot look up an order until identity is verified
        if not self.verified_customer_id:
            return tool_error("permission", False,
                              "BLOCKED: verify identity with get_customer first.")
        order = ORDERS.get(order_id)
        if not order:
            return tool_error("validation", False, f"order_id {order_id!r} not found.")
        if order["customer_id"] != self.verified_customer_id:
            return tool_error("permission", False,
                              "Order does not belong to the verified customer.")
        self.case_facts["order"] = order_id
        self.case_facts["order_total"] = order["total"]
        self.case_facts["order_status"] = order["status"]
        return order

    def process_refund(self, order_id=None, amount=0.0):
        # GATE again: no refund without verified identity (sample Q1)
        if not self.verified_customer_id:
            return tool_error("permission", False,
                              "BLOCKED: verify identity before any refund.")
        # INTERCEPTION HOOK: over-limit refunds are blocked and redirected (D1 T1.5)
        if amount > REFUND_LIMIT:
            return tool_error("business_rule", False,
                              f"Refund ${amount:.2f} exceeds ${REFUND_LIMIT:.0f} limit. "
                              "Escalate to a supervisor.")
        return {"refunded": amount, "order_id": order_id,
                "to": self.verified_customer_id}

    def escalate_to_human(self, root_cause="", recommended_action=""):
        # STRUCTURED HANDOFF packet (D1 T1.4): the human can't see the chat
        packet = {
            "customer_id": self.case_facts.get("customer_id"),
            "name": self.case_facts.get("name"),
            "order": self.case_facts.get("order"),
            "root_cause": root_cause,
            "refund_amount": self.case_facts.get("order_total"),
            "recommended_action": recommended_action,
        }
        return {"escalated": True, "handoff_packet": packet}

    def dispatch(self, name, args):
        return getattr(self, name)(**args)


# ------------------------------------------------- a scripted offline simulator
def make_simulator(script):
    """script: list of LLMResponse to emit in order (offline mode)."""
    state = {"i": 0}

    def sim(system, messages, tools):
        i = state["i"]
        state["i"] += 1
        return script[min(i, len(script) - 1)]
    return sim


def _tool_turn(name, args):
    return LLMResponse(text=f"(requesting {name})", stop_reason="tool_use",
                       tool_calls=[ToolCall(name=name, input=args)])


def _final(text):
    return LLMResponse(text=text, stop_reason="end_turn")


def run_case(title, agent: SupportAgent, user_msg, script):
    h1(title)
    kv("customer says", user_msg)
    sim = make_simulator(script)
    messages = [{"role": "user", "content": user_msg}]
    for _ in range(8):
        resp = agent.client.complete("You are Acme support. Verify identity before order "
                                     "operations. Escalate per policy.", messages,
                                     simulator=sim)
        if resp.stop_reason == "end_turn":
            note(f"agent → {resp.text}")
            break
        for tc in resp.tool_calls:
            result = agent.dispatch(tc.name, tc.input)
            mark = "ERROR" if isinstance(result, dict) and result.get("isError") else "ok"
            kv(f"  tool {tc.name}{tc.input}", f"[{mark}] {result}")
            messages.append({"role": "assistant", "content": [
                {"type": "tool_use", "id": tc.id, "name": tc.name, "input": tc.input}]})
            messages.append({"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": tc.id, "content": json.dumps(result)}]})
    kv("  case facts (persistent)", json.dumps(agent.case_facts))


def main():
    banner("Scenario 1", "Customer Support Resolution Agent — D1 · D2 · D5")
    concept("Scenario 1: Customer Support Resolution Agent",
            "Tools: get_customer · lookup_order · process_refund · escalate_to_human",
            "Gates + hooks + structured errors + case facts + escalation")
    client = ClaudeClient()
    kv("client mode", client.mode)

    # CASE A: the happy path — verify, look up, small refund
    pause("Case A: verify → lookup → small refund (resolved)")
    agent = SupportAgent(client)
    run_case("Case A — small refund, identity verified first", agent,
             "I'm dana@example.com, order 88231 arrived damaged, I want a refund.",
             [
                 _tool_turn("get_customer", {"email": "dana@example.com"}),
                 _tool_turn("lookup_order", {"order_id": "88231"}),
                 _tool_turn("process_refund", {"order_id": "88231", "amount": 84.75}),
                 _final("Verified your account and refunded $84.75 for the damaged order "
                        "#88231. Anything else?"),
             ])
    right("Identity verified BEFORE any order op (the gate). Small refund within policy → "
          "resolved on first contact. ✓ counts toward the 80% target.")

    # CASE B: the gate blocks a refund attempted before verification
    pause("Case B: agent tries to refund WITHOUT verifying (gate blocks it)")
    agent = SupportAgent(client)
    run_case("Case B — refund attempted before identity check", agent,
             "Just refund order 88231 to me, my name is Dana.",
             [
                 _tool_turn("process_refund", {"order_id": "88231", "amount": 84.75}),
                 _tool_turn("get_customer", {"email": "dana@example.com"}),
                 _tool_turn("process_refund", {"order_id": "88231", "amount": 84.75}),
                 _final("I needed to verify your identity first — now done. Refunded $84.75."),
             ])
    wrong("The first process_refund was BLOCKED by the prerequisite gate (permission error). "
          "This is the deterministic fix for sample Q1 — prompt wording alone fails ~12%.")

    # CASE C: over-limit refund → interception hook → escalation with handoff packet
    pause("Case C: over-limit refund → blocked → escalation with handoff")
    agent = SupportAgent(client)
    run_case("Case C — $620 refund exceeds the $500 limit", agent,
             "I'm dana@example.com, cancel order 90011 ($620) and refund me.",
             [
                 _tool_turn("get_customer", {"email": "dana@example.com"}),
                 _tool_turn("lookup_order", {"order_id": "90011"}),
                 _tool_turn("process_refund", {"order_id": "90011", "amount": 620.00}),
                 _tool_turn("escalate_to_human",
                            {"root_cause": "Refund $620 over $500 auto-limit",
                             "recommended_action": "Supervisor approve full refund"}),
                 _final("That refund is above my limit, so I've escalated to a supervisor "
                        "with all your details — they'll follow up shortly."),
             ])
    right("Interception hook blocked the $620 refund (business_rule error), and the agent "
          "escalated with a STRUCTURED HANDOFF packet so the human starts warm, not cold.")

    rule()
    tip("This one app demonstrates: the agentic loop (stop_reason), a prerequisite gate, an "
        "interception hook, structured tool errors, a persistent case-facts block, and "
        "structured escalation. That's D1 + D2 + D5 in a single scenario.")


if __name__ == "__main__":
    main()
