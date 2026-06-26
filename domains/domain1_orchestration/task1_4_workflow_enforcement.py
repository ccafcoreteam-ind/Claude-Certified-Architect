"""
Domain 1 · Task 1.4 — Multi-step workflows: enforcement and handoff patterns.

THE SINGLE MOST IMPORTANT IDEA IN THIS DOMAIN
=============================================
Prompt instructions are PROBABILISTIC; programmatic enforcement is DETERMINISTIC.

Telling Claude "always verify the customer before refunding" works MOST of the time.
"Most of the time" is a disaster for money, security, or compliance. When compliance
must be GUARANTEED, build a programmatic PREREQUISITE GATE: code that blocks
process_refund until get_customer has returned a verified customer ID.

This is the logic behind official sample question Q1 (agent skips identity check 12% of
the time). The fix is a gate, not better prompt wording.

Also here: decomposing multi-concern requests, and structured escalation handoffs.
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from ccarch import banner, concept, h1, h2, wrong, right, tip, note, kv, code, rule, pause, analogy, pitfall


class RefundGate:
    """A deterministic prerequisite gate. process_refund is impossible until identity
    is verified — regardless of what the prompt says or what the model 'decides'."""

    def __init__(self):
        self.verified_customer_id = None

    def get_customer(self, name=None, customer_id=None):
        # In reality this hits your CRM and returns a verified id.
        self.verified_customer_id = "CUST-9"
        return {"verified_customer_id": self.verified_customer_id, "name": "Dana Lee"}

    def process_refund(self, order_id, amount):
        if not self.verified_customer_id:           # <-- THE GATE
            raise PermissionError(
                "BLOCKED: process_refund requires a verified customer ID first "
                "(call get_customer)."
            )
        return {"refunded": amount, "order_id": order_id,
                "to": self.verified_customer_id}


def main():
    banner("Domain 1 · Task 1.4", "Enforcement & handoff — guarantees beat instructions")
    concept("Domain 1: Agentic Architecture & Orchestration (27%)",
            "Task 1.4 — Implement multi-step workflows with enforcement and handoff patterns",
            "Prerequisite gates (deterministic) vs prompt guidance (probabilistic)")

    h1("The distinction the exam tests more than any other")
    note("Prompt-based guidance ('you must do X first'): PROBABILISTIC — non-zero failure "
         "rate. Fine for style/soft ordering.")
    note("Programmatic enforcement (hooks, prerequisite gates): DETERMINISTIC — guaranteed. "
         "Use for identity, financial limits, compliance, security.")

    pause("the gate in action")
    rule()
    h1("Demo: a refund gate that physically cannot be skipped")
    gate = RefundGate()

    h2("Attempt 1 — agent tries to refund WITHOUT verifying identity")
    try:
        gate.process_refund(order_id="12345", amount=80.0)
    except PermissionError as e:
        wrong("Agent skipped get_customer (this happens ~12% of the time with prompt-only "
              "rules). With a gate, the call is rejected:")
        note(f"    {e}")

    h2("Attempt 2 — verify first, then refund")
    cust = gate.get_customer(name="Dana Lee")
    note(f"    get_customer -> {cust}")
    result = gate.process_refund(order_id="12345", amount=80.0)
    right(f"Refund allowed only after verification: {result}")

    rule()
    h1("Plain-language analogy & the common confusion")
    analogy("A bank teller cannot release cash until the system confirms your ID — the block lives in the software, not in the teller's good intentions. A prerequisite gate is exactly that software block.")
    pitfall("The trap is thinking a strongly-worded prompt ('ALWAYS verify first!') is enough. Prompts work most of the time; gates work every time. For money, security, and compliance, 'most of the time' is a failure.")

    tip("Sample Q1: agent skips identity check 12% of the time. Correct answer = a "
        "programmatic prerequisite gate. Distractors (stronger prompt wording, few-shot "
        "examples) are probabilistic; a routing classifier fixes availability, not ORDERING.")

    pause("multi-concern requests")
    rule()
    h1("Multi-concern requests: decompose, investigate, synthesize ONE answer")
    note('Customer: "My order is late, I was double-charged, and I want to update my email."')
    concerns = ["late delivery", "double charge", "email update"]
    for c in concerns:
        kv("  concern", f"{c}  -> investigated (in parallel, shared context)")
    right("Decompose into distinct items, investigate each, then synthesize a single "
          "unified resolution. Don't answer only the first issue and drop the rest.")

    rule()
    h1("Structured handoff summary when escalating to a human")
    summary = {
        "customer_id": "CUST-9",
        "root_cause": "Carrier lost the package; second damaged delivery",
        "refund_amount": 847.50,
        "recommended_action": "Approve full refund + expedited replacement",
    }
    code("\n".join(f"{k}: {v}" for k, v in summary.items()), "handoff packet")
    right("The human can't see the chat transcript. Compile customer ID, root cause, "
          "amount, and recommended action. NEVER hand a human a cold start.")


if __name__ == "__main__":
    main()
