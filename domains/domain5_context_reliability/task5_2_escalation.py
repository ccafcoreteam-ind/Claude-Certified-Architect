"""
Domain 5 · Task 5.2 — Escalation and ambiguity resolution.

LEGITIMATE ESCALATION TRIGGERS
==============================
  1. The customer EXPLICITLY asks for a human (honor immediately — don't "investigate first").
  2. Policy is AMBIGUOUS or SILENT on the request (e.g., competitor price-matching when
     policy only covers own-site adjustments).
  3. The agent CANNOT make meaningful progress.

NOT reliable triggers:
  * Customer frustrated but issue is simple   -> resolve it; escalate only if they reiterate.
  * Negative SENTIMENT score                  -> sentiment does NOT correlate with complexity.
  * Model SELF-REPORTED confidence            -> poorly calibrated; the agent is MOST
                                                 overconfident on the hard cases.

THE CALIBRATION FIX (sample Q3): when an agent escalates easy cases while fumbling hard
ones (55% vs an 80% target), add EXPLICIT escalation criteria WITH FEW-SHOT EXAMPLES to
the system prompt — not confidence thresholds, not a classifier, not sentiment analysis.

Multiple customer matches: ASK for additional identifiers. Never pick "most likely" by
heuristic — that's how wrong-account refunds happen.
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from ccarch import banner, concept, h1, h2, wrong, right, tip, note, kv, code, rule, pause


def should_escalate(explicit_human=False, policy_gap=False, no_progress=False,
                    frustrated=False, neg_sentiment=False, low_self_confidence=False):
    if explicit_human:
        return True, "Customer explicitly asked for a human — honor immediately."
    if policy_gap:
        return True, "Policy is ambiguous/silent — the agent must not invent policy."
    if no_progress:
        return True, "Agent cannot make meaningful progress."
    if frustrated:
        return False, "Frustration alone isn't a trigger — acknowledge and resolve."
    if neg_sentiment:
        return False, "Sentiment does not correlate with case complexity."
    if low_self_confidence:
        return False, "LLM self-confidence is poorly calibrated; not a reliable trigger."
    return False, "Resolve autonomously."


def main():
    banner("Domain 5 · Task 5.2", "Escalation & ambiguity resolution")
    concept("Domain 5: Context Management & Reliability (15%)",
            "Task 5.2 — Escalation and ambiguity resolution",
            "Escalate by RULE, not by vibe")

    h1("Reliable vs unreliable escalation signals")
    cases = [
        ("Customer demands a human", dict(explicit_human=True)),
        ("Policy silent on competitor price-match", dict(policy_gap=True)),
        ("Agent stuck, no progress", dict(no_progress=True)),
        ("Customer frustrated, issue is simple", dict(frustrated=True)),
        ("Negative sentiment score", dict(neg_sentiment=True)),
        ("Model self-reports low confidence", dict(low_self_confidence=True)),
    ]
    for desc, kw in cases:
        esc, why = should_escalate(**kw)
        h2(desc)
        (right if esc else wrong)(f"{'ESCALATE' if esc else 'do NOT escalate'} — {why}")

    pause("the calibration fix")
    rule()
    h1("The calibration fix (sample Q3): 55% vs 80% target")
    note("Agent escalates straightforward cases (standard damage replacements w/ photos) "
         "while attempting complex policy-exception cases itself.")
    right("Add EXPLICIT escalation criteria + FEW-SHOT examples to the system prompt "
          "(showing when to escalate vs resolve).")
    wrong("Self-reported confidence threshold — already miscalibrated on hard cases.")
    wrong("A separate classifier model — over-engineered before prompt optimization is tried.")
    wrong("Sentiment analysis — solves a different problem; sentiment != complexity.")

    rule()
    h1("Multiple customer matches")
    wrong("Picking 'the most likely' account by heuristic — that's how wrong-account "
          "refunds happen.")
    right("ASK for additional identifiers (email, order #, last 4 of card).")

    tip("Reliable triggers: explicit human request (honor NOW), policy gap, no progress. "
        "NOT sentiment, NOT self-confidence, NOT frustration alone. Calibration fix = "
        "explicit criteria + few-shot.")


if __name__ == "__main__":
    main()
