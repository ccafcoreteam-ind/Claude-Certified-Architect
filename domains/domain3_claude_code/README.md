# Domain 3 — Claude Code Configuration & Workflows (20%)

The most directly practical domain: where instructions live and who they apply to,
reusable commands and skills, plan mode vs direct execution, refinement, and CI/CD.

| Task | Demo | One-line idea |
|---|---|---|
| 3.1 CLAUDE.md hierarchy | `task3_1_claudemd_hierarchy.py` | Level decides WHO the instructions reach |
| 3.2 Commands & skills | `task3_2_commands_skills.py` | Project (shared) vs personal; skill frontmatter |
| 3.3 Path-specific rules | `task3_3_path_rules.py` | Glob-scoped rules follow scattered files |
| 3.4 Plan mode vs direct | `task3_4_plan_mode.py` | Architectural/multi-file → plan; small fix → direct |
| 3.5 Iterative refinement | `task3_5_iterative_refinement.py` | Show don't tell; tests-as-feedback; interview |
| 3.6 CI/CD | `task3_6_cicd.py` | `-p` for non-interactive; structured output |

```bash
python3 run_all.py domain3
```

## Real config artifacts — `examples/`

Open these alongside the demos; they are working examples of the things the exam asks about:

```
examples/
├── CLAUDE.md                      # project-level standing instructions (+ @import)
├── .mcp.json                      # shared MCP servers with ${ENV_VAR} secrets
├── standards/                     # files pulled in via @import
└── .claude/
    ├── commands/review.md         # team /review command (sample Q4)
    ├── rules/testing.md           # path-scoped: paths: ["**/*.test.tsx"]  (sample Q6)
    ├── rules/api-conventions.md   # path-scoped: paths: ["src/api/**/*"]
    └── skills/analyze-codebase/SKILL.md   # context: fork, allowed-tools, argument-hint
```
