# Domain 5 — Context Management & Reliability (15%)

The smallest domain by weight but woven through every scenario: keep critical facts alive
in long interactions, escalate wisely, propagate errors usefully, survive huge codebases,
calibrate human review, and preserve "who said what" through synthesis.

| Task | Demo | One-line idea |
|---|---|---|
| 5.1 Preserve context | `task5_1_preserve_context.py` | The "case facts" block survives summarization |
| 5.2 Escalation | `task5_2_escalation.py` | Escalate by rule (explicit/policy-gap/no-progress), not vibe |
| 5.3 Error propagation | `task5_3_error_propagation.py` | Structured error context enables recovery |
| 5.4 Large codebases | `task5_4_large_codebase.py` | Scratchpads, delegation, manifests, /compact |
| 5.5 Human review | `task5_5_human_review.py` | Segment accuracy; calibrate; audit the fast lane |
| 5.6 Provenance | `task5_6_provenance.py` | Claim-source mappings; conflicts vs temporal trends |

```bash
python3 run_all.py domain5
```

**Watch out for:** aggregate "97% accuracy" hiding a 60% pocket; a 2021 vs 2024 figure is a
*trend*, not a contradiction; numbers and dates are the first casualties of summarization.
