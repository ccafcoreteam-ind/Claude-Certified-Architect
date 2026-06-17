---
name: analyze-codebase
description: Map an unfamiliar module's structure and dependencies, returning a summary
context: fork
allowed-tools: [Read, Grep, Glob]
argument-hint: <module-path>
---
# analyze-codebase — example SKILL (Domain 3, Task 3.2)
#
# Frontmatter demonstrates all three tested options:
#   context: fork    -> runs in an ISOLATED sub-agent context so the (verbose) findings
#                       do NOT pollute the main conversation. Only a summary returns.
#   allowed-tools    -> read-only (Read/Grep/Glob). The skill physically cannot Write,
#                       Edit, or run Bash — a deterministic guardrail against side effects.
#   argument-hint    -> if invoked as bare /analyze-codebase, Claude prompts for <module-path>.
#
# Skills are ON-DEMAND, task-specific workflows. Always-on universal standards belong in
# CLAUDE.md instead. Want a personal variant? Put it in ~/.claude/skills/ under a
# DIFFERENT name so teammates are unaffected.

# Playbook
1. Glob the module path to list files (by NAME) — do not read everything.
2. Grep for entry points: exported names, route registrations, `main`/`handler`.
3. Read only the entry-point files; follow imports outward (incremental exploration).
4. For wrapper modules: list all exported names first, then Grep each across the repo.
5. Return a concise summary: purpose, key files, external dependencies, risk areas.
