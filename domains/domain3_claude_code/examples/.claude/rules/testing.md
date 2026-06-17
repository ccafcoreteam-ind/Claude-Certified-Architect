---
paths: ["**/*.test.tsx", "**/*.test.ts"]
---
# Testing conventions — example PATH-SCOPED rule (Domain 3, Task 3.3; sample Q6)
#
# The YAML frontmatter `paths` globs make this rule load ONLY when Claude edits a test
# file — no matter where it lives in the tree (Button.test.tsx sits next to Button.tsx,
# scattered everywhere). A directory-bound CLAUDE.md cannot follow scattered files;
# a single glob rule applies the conventions to ALL of them, automatically.

When writing or editing tests:
- Every test name describes the behavior being verified (not "test1").
- Mock external services; never call real APIs in tests.
- Cover the empty-input and error cases FIRST, then the happy path.
- One behavior per test; avoid asserting unrelated things together.
