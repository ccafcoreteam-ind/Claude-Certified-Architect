# Project Conventions (example PROJECT-level CLAUDE.md)
#
# WHY THIS FILE EXISTS (Domain 3, Task 3.1):
# This lives in the repo, so it is shared with every teammate via version control.
# Contrast with ~/.claude/CLAUDE.md, which stays on one machine and never travels.
# If a new teammate clones the repo and Claude "ignores the team's conventions,"
# the conventions were almost certainly put in a USER-level file instead of here.

## Coding standards
- All currency amounts are stored in **cents**, never dollars (integer math only).
- Every new function needs a matching test in the same package.
- Use British English in customer-facing text.
- Never modify files in `/legacy` without asking first.

## Architecture context
- Backend talks to Claude via the Agent SDK; tool execution happens in `services/agent/`.
- MCP tools are defined in `mcp/` and shared through `.mcp.json`.

## Modular organization
# Keep this file small. Pull in topic-specific standards with @import, and put
# path-scoped conventions in .claude/rules/ (see Task 3.3).
@import ./standards/testing.md
@import ./standards/api-conventions.md

## Debugging tip for learners
# Run `/memory` in Claude Code to see exactly which memory files are currently loaded.
# That is the first move when behavior is inconsistent across sessions.
