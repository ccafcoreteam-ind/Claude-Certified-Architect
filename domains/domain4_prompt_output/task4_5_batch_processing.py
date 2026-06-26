"""
Domain 4 · Task 4.5 — Batch processing strategies.

THE BIG IDEA
============
The Message Batches API in one line: 50% CHEAPER, results within UP TO 24 HOURS, NO
guaranteed latency SLA, and no multi-turn tool calling within a request.

  Pre-merge code check (developers WAITING)  -> SYNCHRONOUS. Blocking; "usually fast" isn't
                                                good enough when there's no SLA.
  Overnight technical-debt report            -> BATCH. Latency-tolerant; pocket the 50%.
  Weekly compliance audit / nightly tests    -> BATCH. Nobody's waiting.

  custom_id correlates each request with its response — and lets you resubmit ONLY the
  failed documents (e.g., chunking oversized ones) instead of rerunning the whole batch.
  (This kills the "batch ordering" misconception in sample Q11.)

  SLA MATH: with a 24h batch window, guaranteeing a 30h turnaround means submitting every
  ~4-6h (the guide's example: 4-hour submission windows guarantee a 30-hour SLA).

  REFINE BEFORE YOU SCALE: tune the prompt on a small sample before running 100,000 docs.
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from ccarch import banner, concept, h1, h2, wrong, right, tip, note, kv, code, rule, pause, analogy, pitfall


def choose_api(blocking: bool, someone_waiting: bool):
    if blocking or someone_waiting:
        return "SYNCHRONOUS (real-time)", "A human is blocked; no latency SLA is unacceptable."
    return "BATCH", "Latency-tolerant; take the 50% cost savings."


WORKLOADS = [
    ("Pre-merge code check (devs waiting to merge)", True, True),
    ("Overnight technical-debt report", False, False),
    ("Weekly compliance audit", False, False),
    ("Nightly test generation", False, False),
]


def main():
    banner("Domain 4 · Task 4.5", "Batch processing strategies")
    concept("Domain 4: Prompt Engineering & Structured Output (20%)",
            "Task 4.5 — Design efficient batch processing strategies",
            "Batch = 50% cheaper, <=24h, NO latency SLA")

    h1("Match each workload to the right API (sample Q11)")
    for name, blocking, waiting in WORKLOADS:
        api, why = choose_api(blocking, waiting)
        h2(name)
        right(f"{api} — {why}")
    wrong("Switching the BLOCKING pre-merge check to batch 'because it's usually fast'. "
          "There is NO latency SLA; developers could wait hours.")

    pause("custom_id")
    rule()
    h1("custom_id: correlation + partial resubmission")
    code('requests = [\n'
         '  {"custom_id": "doc-001", ...},\n'
         '  {"custom_id": "doc-002", ...},\n'
         ']\n'
         '# results come back possibly out of order; match them by custom_id\n'
         '# resubmit ONLY the failures (e.g., chunk doc-417 that was too large)',
         "custom_id")
    right("'Batch result ORDERING' is a misconception — custom_id correlates each request "
          "with its response, so out-of-order results are a non-issue.")

    pause("SLA math")
    rule()
    h1("SLA math")
    note("Batch window is UP TO 24h. To guarantee a 30h end-to-end SLA, you need slack for "
         "a worst-case 24h run.")
    kv("  submit every", "~4-6 hours")
    kv("  guaranteed turnaround", "~30 hours (24h window + submission cadence)")
    code("submit_interval = target_sla - max_batch_window\n"
         "30h - 24h = 6h of slack  ->  submit at least every ~4-6h", "the arithmetic")

    rule()
    h1("Refine before you scale")
    right("Tune the prompt on a SMALL sample first. First-pass success across 100,000 docs "
          "is far cheaper than iterative resubmission.")

    rule()
    h1("Plain-language analogy & the common confusion")
    analogy('Batch is overnight shipping at half price; synchronous is the same-hour courier. Use overnight for the report nobody reads till morning; use the courier for the package someone is standing at the door waiting for.')
    pitfall("The tempting mistake: batch the blocking pre-merge check 'because it is usually fast.' Batch has NO latency guarantee (up to 24h) — 'usually fast' is unacceptable when a developer is blocked on the result.")

    tip("Batch: 50% cheaper, <=24h, NO latency SLA, no multi-turn tool calling. Blocking "
        "work stays synchronous. custom_id solves correlation AND partial resubmission.")


if __name__ == "__main__":
    main()
