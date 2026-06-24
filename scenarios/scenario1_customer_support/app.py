"""
SCENARIO 1 app — Customer Support Resolution Agent (FUNCTIONAL)
==============================================================
A working agent you can actually talk to. It parses a free-text customer message, then runs
a real loop over four tools with a PREREQUISITE GATE (no refund before identity is
verified), an INTERCEPTION HOOK ($500 cap → escalation), STRUCTURED errors, a persistent
CASE-FACTS block, and rule-based escalation — Domains 1, 2, 5 in action.

Run:
  python3 scenarios/scenario1_customer_support/app.py            # scripted demo (3 messages)
  python3 scenarios/scenario1_customer_support/app.py -i         # chat with the agent
  python3 scenarios/scenario1_customer_support/app.py "I'm dana@example.com, refund order 88231"

Try (interactive): give an email + order, ask for a refund; or ask for a refund first
(blocked); or ask to cancel order 90011 ($620) (escalates).
"""
import sys, re, json, pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from ccarch import banner, h1, h2, kv, note, rule, wrong, right, tip

REFUND_LIMIT = 500.0
CUSTOMERS = {"dana@example.com": {"id": "CUST-9", "name": "Dana Lee"},
             "sam@example.com": {"id": "CUST-4", "name": "Sam Ortiz"}}
ORDERS = {"88231": {"customer": "CUST-9", "status": "delivered_damaged", "total": 84.75},
          "90011": {"customer": "CUST-9", "status": "shipped", "total": 620.00},
          "55012": {"customer": "CUST-4", "status": "shipped", "total": 45.00}}


def err(cat, retryable, msg):
    return {"error": True, "errorCategory": cat, "isRetryable": retryable, "message": msg}


class Agent:
    def __init__(self):
        self.verified = None          # the gate's state
        self.facts = {}               # persistent case-facts block

    # --- tools (real logic) ---
    def get_customer(self, email):
        c = CUSTOMERS.get(email)
        if not c:
            return err("validation", False, f"no customer for {email}")
        self.verified = c["id"]
        self.facts.update(customer_id=c["id"], name=c["name"])
        return {"verified_customer_id": c["id"], "name": c["name"]}

    def lookup_order(self, oid):
        if not self.verified:
            return err("permission", False, "verify identity first (prerequisite gate)")
        o = ORDERS.get(oid)
        if not o:
            return err("validation", False, f"order {oid} not found")
        if o["customer"] != self.verified:
            return err("permission", False, "order belongs to a different customer")
        self.facts.update(order=oid, order_total=o["total"], order_status=o["status"])
        return o

    def process_refund(self, oid, amount):
        if not self.verified:                                   # gate
            return err("permission", False, "verify identity before any refund")
        if amount > REFUND_LIMIT:                               # interception hook
            return err("business_rule", False,
                       f"refund ${amount:.2f} exceeds ${REFUND_LIMIT:.0f} limit; escalate")
        return {"refunded": amount, "order": oid, "to": self.verified}

    def escalate(self, reason):
        return {"escalated": True, "handoff": {**self.facts, "reason": reason}}


def parse(msg):
    return {
        "email": (re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", msg) or [None])[0]
                 if re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", msg) else None,
        "order": (re.search(r"\b(\d{5})\b", msg).group(1) if re.search(r"\b(\d{5})\b", msg) else None),
        "amount": (float(re.search(r"\$\s?([\d,]+(?:\.\d+)?)", msg).group(1).replace(",", ""))
                   if re.search(r"\$\s?([\d,]+(?:\.\d+)?)", msg) else None),
        "wants_refund": bool(re.search(r"refund|return|money back|damaged|cancel", msg, re.I)),
        "wants_human": bool(re.search(r"\b(human|person|agent|supervisor|manager)\b", msg, re.I)),
    }


def handle(agent, msg, trace):
    """One real agent turn: plan tool calls from the message + current state."""
    p = parse(msg)
    log = trace.append

    if p["wants_human"]:
        r = agent.escalate("customer explicitly requested a human")
        log(("escalate_to_human", {}, r))
        return "I'm connecting you with a human now — I've passed along your details."

    if p["email"] and not agent.verified:
        r = agent.get_customer(p["email"])
        log(("get_customer", {"email": p["email"]}, r))

    if p["order"]:
        r = agent.lookup_order(p["order"])
        log(("lookup_order", {"order_id": p["order"]}, r))
        if isinstance(r, dict) and r.get("error") and r["errorCategory"] == "permission":
            return "Before I can look up that order, I need to verify your identity — what's the email on the account?"

    if p["wants_refund"]:
        if not agent.verified:
            return "Happy to help with a refund — first, what's the email on your account so I can verify you?"
        oid = p["order"] or agent.facts.get("order")
        if not oid:
            return "Which order number should I refund?"
        amount = p["amount"] or agent.facts.get("order_total")
        r = agent.process_refund(oid, amount)
        log(("process_refund", {"order_id": oid, "amount": amount}, r))
        if isinstance(r, dict) and r.get("error"):
            esc = agent.escalate(r["message"])
            log(("escalate_to_human", {}, esc))
            return (f"That refund (${amount:.2f}) is above what I can approve, so I've "
                    f"escalated to a supervisor with all your details.")
        return f"Done — I've refunded ${amount:.2f} for order #{oid}. Anything else?"

    if agent.verified:
        return f"Thanks, {agent.facts.get('name','')} — you're verified. How can I help?"
    return "Hi! Tell me your order number and the email on your account and I'll help."


def run_turn(agent, msg, show=True):
    trace = []
    reply = handle(agent, msg, trace)
    if show:
        kv("customer", msg)
        for name, args, result in trace:
            mark = "ERR" if isinstance(result, dict) and result.get("error") else "ok"
            note(f"    → {name}({args}) [{mark}] {result}")
        right(f"agent: {reply}")
        if agent.facts:
            kv("    case-facts", json.dumps(agent.facts))
    return reply


def interactive():
    banner("Scenario 1 — Support Agent", "chat with the agent; 'quit' to exit, 'reset' for a new case")
    agent = Agent()
    while True:
        try:
            msg = input("\nyou> ").strip()
        except (EOFError, KeyboardInterrupt):
            print(); break
        if msg.lower() in ("quit", "exit", "q"):
            break
        if msg.lower() == "reset":
            agent = Agent(); note("  (new case)"); continue
        if msg:
            run_turn(agent, msg)


def demo():
    banner("Scenario 1 — Support Agent (demo)", "three real messages through the live logic")
    h1("Case A — verify + small refund (resolved)")
    a = Agent()
    run_turn(a, "Hi, I'm dana@example.com and order 88231 arrived damaged — I'd like a refund.")

    h1("Case B — refund requested before identity is known (gate asks to verify)")
    b = Agent()
    run_turn(b, "Just refund order 88231 to me please.")
    run_turn(b, "sure, it's dana@example.com")

    h1("Case C — over-limit refund (interception hook → escalation)")
    c = Agent()
    run_turn(c, "I'm dana@example.com, please cancel order 90011 and refund the $620.")
    rule()
    tip("The gate makes 'verify before refund' deterministic; the hook stops >$500 refunds; "
        "case-facts persist across turns. Run with -i to talk to it yourself.")


def main():
    args = sys.argv[1:]
    if any(a in ("-i", "--interactive") for a in args) and sys.stdin.isatty():
        interactive(); return
    free = [a for a in args if not a.startswith("-")]
    if free:
        run_turn(Agent(), " ".join(free)); return
    demo()


if __name__ == "__main__":
    main()
