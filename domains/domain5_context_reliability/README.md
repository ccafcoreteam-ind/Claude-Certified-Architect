# Domain 5 — Context Management & Reliability (15%)

The smallest domain by weight but woven through every scenario: keep critical facts alive
in long interactions, escalate wisely, propagate errors usefully, survive huge codebases,
calibrate human review, and preserve "who said what" through synthesis.

| Task | Demo | One-line idea |
|---|---|---|
| 5.1 Manage conversation context to preserve critical information across long interactions | `task5_1_preserve_context.py` | The "case facts" block survives summarization |
| 5.2 Design effective escalation and ambiguity resolution patterns | `task5_2_escalation.py` | Escalate by rule (explicit/policy-gap/no-progress), not vibe |
| 5.3 Implement error propagation strategies across multi-agent systems | `task5_3_error_propagation.py` | Structured error context enables recovery |
| 5.4 Manage context effectively in large codebase exploration | `task5_4_large_codebase.py` | Scratchpads, delegation, manifests, /compact |
| 5.5 Design human review workflows and confidence calibration | `task5_5_human_review.py` | Segment accuracy; calibrate; audit the fast lane |
| 5.6 Preserve information provenance and handle uncertainty in multi-source synthesis | `task5_6_provenance.py` | Claim-source mappings; conflicts vs temporal trends |

```bash
python3 run_all.py domain5
```

**Watch out for:** aggregate "97% accuracy" hiding a 60% pocket; a 2021 vs 2024 figure is a
*trend*, not a contradiction; numbers and dates are the first casualties of summarization.
