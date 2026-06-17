"""
Domain 4 · Task 4.2 — Few-shot prompting.

THE BIG IDEA
============
Include 2-4 worked examples in the prompt showing input -> correct output. This is the
most effective technique when detailed INSTRUCTIONS alone still produce inconsistent
results, because the model generalizes the DEMONSTRATED judgment to novel cases — it
doesn't just match the literal examples.

The invoice-extraction examples below teach, silently and reliably:
  * normalization (strip $ and commas, expand/standardize dates), and
  * the single most important behavior: when info is genuinely MISSING, write null —
    do NOT invent a number.

Where few-shot shines (per the guide): ambiguous-case handling, format consistency,
false-positive reduction, and hallucination reduction in extraction (including null handling).
"""

import sys, pathlib, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from ccarch import banner, concept, h1, h2, wrong, right, tip, note, kv, code, rule, pause
from ccarch import ClaudeClient, LLMResponse


FEW_SHOT = [
    ('Pd $1,200.50 to Acme Corp on 3/4/25',
     {"vendor": "Acme Corp", "amount": 1200.50, "date": "2025-03-04"}),
    ('Invoice received from Beta LLC, amount to be confirmed',
     {"vendor": "Beta LLC", "amount": None, "date": None}),
]


def build_prompt(new_input: str) -> str:
    lines = ["Extract invoice fields as JSON. Follow the examples exactly.\n"]
    for i, (inp, out) in enumerate(FEW_SHOT, 1):
        lines.append(f"Example {i}\nInput:  {inp!r}\nOutput: {json.dumps(out)}\n")
    lines.append(f"Now do this one.\nInput:  {new_input!r}\nOutput:")
    return "\n".join(lines)


def simulator(system, messages, tools) -> LLMResponse:
    """Offline: imitate a model that has LEARNED the demonstrated null-handling rule."""
    text = messages[-1]["content"]
    if "to be confirmed" in text or "TBD" in text:
        out = {"vendor": "Gamma Inc", "amount": None, "date": None}
    else:
        out = {"vendor": "Delta Co", "amount": 89.99, "date": "2025-01-15"}
    return LLMResponse(text=json.dumps(out), stop_reason="end_turn")


def main():
    banner("Domain 4 · Task 4.2", "Few-shot prompting — show, don't tell")
    concept("Domain 4: Prompt Engineering & Structured Output (20%)",
            "Task 4.2 — Few-shot prompting",
            "2-4 worked examples teach judgment that prose can't")

    h1("What few-shot actually looks like")
    for i, (inp, out) in enumerate(FEW_SHOT, 1):
        h2(f"Example {i}")
        kv("  input", inp)
        kv("  output", json.dumps(out))
    note("Example 1 silently teaches 3 normalization rules (strip $/comma, expand the "
         "date, standard format). Example 2 teaches the MOST important rule: missing info "
         "-> null, never invent.")

    pause("run it")
    rule()
    h1("Run the few-shot prompt on a new input")
    client = ClaudeClient()
    kv("client mode", client.mode)
    new_input = "Charge from Gamma Inc, total to be confirmed next week"
    resp = client.complete("You extract invoice JSON.",
                           [{"role": "user", "content": build_prompt(new_input)}],
                           simulator=simulator)
    kv("  input", new_input)
    kv("  model output", resp.text + ("  (simulated)" if resp.simulated else "  (live)"))
    right("Because Example 2 demonstrated null, the model writes amount: null instead of "
          "fabricating a number — the boundary no paragraph of prose conveys as reliably.")

    rule()
    h1("Where few-shot shines (per the exam guide)")
    note("- Ambiguous-case handling: show the REASONING for the chosen action vs the alternative.")
    note("- Format consistency: demonstrate the exact output shape.")
    note("- False-positive reduction: pair acceptable patterns WITH genuine issues to teach "
         "the boundary.")
    note("- Hallucination reduction: show extraction from varied structures (inline "
         "citations vs bibliographies, narrative vs tabular), including correct null handling.")

    tip("Reach for few-shot when DETAILED INSTRUCTIONS still give inconsistent results. "
        "2-4 examples; always include an example of the hard/edge case (the null case).")


if __name__ == "__main__":
    main()
