"""
Domain 5 · Task 5.5 — Human review workflows and confidence calibration.

THE BIG IDEA
============
  * AGGREGATE METRICS HIDE POCKETS OF FAILURE: "97% overall accuracy" can mask 60% on one
    document type or field. Validate accuracy BY DOCUMENT TYPE AND FIELD SEGMENT before
    automating anything.
  * STRATIFIED RANDOM SAMPLING: keep auditing samples from HIGH-confidence extractions too
    — it measures the true error rate where you've stopped looking and catches novel error
    patterns early.
  * CALIBRATED CONFIDENCE ROUTING: have the model output FIELD-LEVEL confidence scores,
    CALIBRATE thresholds against a labeled validation set, then route low-confidence or
    ambiguous/contradictory-source extractions to humans.

Analogy: airport security — most travelers take standard screening (high-confidence), a
calibrated system selects some for extra checks (low-confidence routing), and RANDOM audits
of the fast lane (stratified sampling) verify the system itself still works.
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from ccarch import banner, concept, h1, h2, wrong, right, tip, note, kv, code, rule, pause, analogy, pitfall


def route(field_confidence: float, threshold: float, contradictory: bool):
    if contradictory:
        return "HUMAN (contradictory sources)"
    return "HUMAN (low confidence)" if field_confidence < threshold else "AUTO-ACCEPT"


def main():
    banner("Domain 5 · Task 5.5", "Human review & confidence calibration")
    concept("Domain 5: Context Management & Reliability (15%)",
            "Task 5.5 — Design human review workflows and confidence calibration",
            "Validate by segment; route by calibrated confidence; audit the fast lane")

    h1("Aggregate metrics hide pockets of failure")
    wrong('Trusting "97% overall accuracy" and automating everything.')
    note("Hidden inside that 97%:")
    kv("  invoices", "99%")
    kv("  handwritten receipts", "60%   <-- the pocket the average hides")
    right("Validate accuracy BY document type AND BY field before automating.")

    pause("confidence routing")
    rule()
    h1("Calibrated confidence routing")
    threshold = 0.80
    samples = [
        ("vendor", 0.97, False),
        ("amount", 0.55, False),
        ("date", 0.91, False),
        ("total", 0.88, True),    # sources disagree
    ]
    note(f"Threshold (calibrated against a labeled validation set): {threshold}")
    for field, conf, contra in samples:
        kv(f"  {field} (conf={conf}, contradictory={contra})", route(conf, threshold, contra))
    right("Route low-confidence OR ambiguous/contradictory extractions to humans — spend "
          "scarce reviewer capacity where it matters most.")

    pause("stratified sampling")
    rule()
    h1("Stratified random sampling — audit the fast lane")
    wrong("Only reviewing the LOW-confidence pile. You go blind to errors hiding in the "
          "'trusted' high-confidence lane.")
    right("Keep auditing random samples of HIGH-confidence extractions too. It measures the "
          "true error rate where you stopped looking and catches NEW error patterns early.")

    note("\nAnalogy: airport security — standard screening (high-conf), selective extra "
         "checks (low-conf routing), random audits of the fast lane (stratified sampling).")

    rule()
    h1("A common confusion to clear up")
    pitfall("A headline '97% accurate' feels safe to automate, but that average can hide a 60% pocket on one document type. Validate accuracy by type AND by field before trusting it — and keep auditing the high-confidence lane too.")

    tip("Aggregate accuracy lies — segment by type & field. Calibrate thresholds on labeled "
        "data. Route low-conf/contradictory to humans. Audit the high-conf lane to stay honest.")


if __name__ == "__main__":
    main()
