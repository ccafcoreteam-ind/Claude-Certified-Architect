---
description: Run the team's standard code-review checklist on the current diff
argument-hint: "[optional: path or PR number]"
---
# /review  — example PROJECT-scoped slash command (Domain 3, Task 3.2; sample Q4)
#
# Because this file lives in .claude/commands/ INSIDE the repo, it is version-controlled
# and every developer gets /review automatically when they clone or pull. That is the
# correct answer to "the whole team should get /review."
#   - ~/.claude/commands/  would be PERSONAL (only you).
#   - CLAUDE.md is for context/standards, NOT command definitions.
#   - A ".claude/config.json commands array" does NOT exist.

Review the current diff against our checklist and report findings as a list of
{file, line, severity, issue, suggested_fix}:

1. Correctness: logic bugs, off-by-one, null/undefined handling, error paths.
2. Security: injection, secret leakage, missing authz checks.
3. Tests: is new behavior covered? Are edge/error cases tested first?
4. Conventions: currency in cents, British English in UI text, no edits under /legacy.

Only flag genuine issues. Skip pure style nits — high false-positive rates make the
team ignore the reviewer (Domain 4, Task 4.1).
