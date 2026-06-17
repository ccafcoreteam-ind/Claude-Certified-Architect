# Exam practice

| File | What it does |
|---|---|
| `sample_questions.py` | The **12 official sample questions**, interactive and self-grading. Each is tagged with its scenario, domain/task, and the demo that shows the concept running. |
| `cheatsheet.py` | The high-yield **facts to memorize**, grouped by topic, each pointing to its demo. |
| `prep_exercises.py` | The **3 official hands-on exercises**, mapped to worked references in this repo. |

```bash
# Interactive self-grading quiz (votes A/B/C/D, then reveals the answer + why)
python3 exam/sample_questions.py

# Print everything non-stop (answers shown)
python3 run_all.py exam
```

## The pattern behind every question

> **root cause + the simplest reliable mechanism wins.**

The three distractor families:
1. **More prompting where enforcement is needed** (prompt wording / few-shot / confidence
   thresholds for a rule that must hold 100% of the time).
2. **More infrastructure where prompting suffices** (a classifier / routing layer when
   better descriptions or explicit criteria would fix it).
3. **Features that don't exist** (`CLAUDE_HEADLESS`, `--batch`, a `.claude/config.json`
   commands array). Spot the invented flag and eliminate it instantly.
