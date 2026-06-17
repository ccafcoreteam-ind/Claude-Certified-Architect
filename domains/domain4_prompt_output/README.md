# Domain 4 — Prompt Engineering & Structured Output (20%)

Precise, consistent, machine-readable output: explicit criteria, worked examples,
schema-enforced structure, validation loops, batch economics, and review architectures.

| Task | Demo | One-line idea |
|---|---|---|
| 4.1 Explicit criteria | `task4_1_explicit_criteria.py` | Specific categories > vague "be conservative" |
| 4.2 Few-shot | `task4_2_few_shot.py` | 2–4 examples teach judgment prose can't (run live!) |
| 4.3 Structured output | `task4_3_structured_output_schema.py` | Tool-use schema; nullable prevents fabrication |
| 4.4 Validation & retry | `task4_4_validation_retry.py` | Retry WITH errors; futile when info is absent |
| 4.5 Batch processing | `task4_5_batch_processing.py` | 50% cheaper, ≤24h, NO latency SLA |
| 4.6 Multi-pass review | `task4_6_multi_pass_review.py` | Fresh eyes + per-file passes |

```bash
python3 run_all.py domain4
```

**The single most important schema fact:** required fields cause fabrication — make
uncertain fields **nullable** so the model can honestly emit `null`.
