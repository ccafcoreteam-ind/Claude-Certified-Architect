"""
Domain 4 · Task 4.6 — Multi-instance and multi-pass review architectures.

THE BIG IDEA
============
  * SELF-REVIEW IS STRUCTURALLY WEAK: a model reviewing code in the SAME session that
    generated it carries its own reasoning and won't question its decisions. A FRESH,
    independent instance catches subtler issues than self-review instructions or extended
    thinking ever will.
  * MULTI-PASS BEATS SINGLE-PASS for large reviews: per-file passes for local issues + a
    separate cross-file integration pass — avoids attention dilution and contradictory
    findings (the 14-file PR, sample Q12). Bigger context windows do NOT fix attention
    quality, and 2-of-3 consensus voting SUPPRESSES real intermittent catches.
  * CONFIDENCE-ANNOTATED passes: have the model self-report a confidence score per finding
    to route human attention.

Analogy: authors don't copy-edit their own manuscripts — they read what they MEANT to
write. Publishers hire fresh eyes. Same model, different session, no shared reasoning =
fresh eyes.
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from ccarch import banner, concept, h1, h2, wrong, right, tip, note, kv, code, rule, pause


def review_plan(num_files: int):
    passes = [f"Pass {i+1}: file {i+1} — local issues only" for i in range(num_files)]
    passes.append(f"Pass {num_files+1}: cross-file integration (data flow across all files)")
    return passes


def main():
    banner("Domain 4 · Task 4.6", "Multi-instance & multi-pass review")
    concept("Domain 4: Prompt Engineering & Structured Output (20%)",
            "Task 4.6 — Design multi-instance and multi-pass review architectures",
            "Fresh eyes beat self-review; split passes beat one big pass")

    h1("Self-review is structurally weak")
    wrong("Asking the SAME session that wrote the code to review it. It re-reads what it "
          "MEANT to write and rubber-stamps its own decisions.")
    right("Use a FRESH, independent instance with no generation context. It catches subtler "
          "issues than 'review your own work carefully' or extended thinking ever will.")
    note("Analogy: authors don't copy-edit themselves; publishers hire fresh eyes.")

    pause("multi-pass")
    rule()
    h1("Multi-pass beats single-pass for large reviews (sample Q12)")
    note("A 14-file PR reviewed in ONE pass gives uneven depth, missed bugs, and "
         "contradictory findings (flag a pattern in one file, approve it in another).")
    for step in review_plan(3):   # show the shape with 3 files
        kv("  ", step)
    right("Per-file passes for consistent local depth + ONE integration pass for cross-file "
          "data flow.")

    h2("Why the distractors fail")
    wrong("Bigger context window / higher-tier model — context size does NOT fix ATTENTION "
          "quality.")
    wrong("Force developers to split PRs into 3-4 files — shifts the burden, doesn't fix "
          "the system.")
    wrong("Run 3 passes, keep only issues found in >=2 — consensus voting SUPPRESSES real "
          "bugs that are only caught intermittently.")

    pause("confidence routing")
    rule()
    h1("Confidence-annotated verification passes")
    code('{"file": "orders.py", "line": 88, "issue": "unchecked index",\n'
         ' "severity": "high", "confidence": 0.6}   # route the 0.6 to a human',
         "self-reported confidence per finding")
    right("Confidence scores enable CALIBRATED routing of scarce human review attention "
          "(more in Task 5.5).")

    tip("Independent fresh instance > self-review. Large PR -> per-file passes + integration "
        "pass. Bigger context != better attention. Consensus voting hides intermittent bugs.")


if __name__ == "__main__":
    main()
