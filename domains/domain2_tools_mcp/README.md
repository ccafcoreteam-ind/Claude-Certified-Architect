# Domain 2 — Tool Design & MCP Integration (18%)

Agents choose tools by reading their descriptions. This domain is about unambiguous
descriptions, structured errors agents can recover from, scoping tools per agent, and
configuring MCP correctly.

| Task | Demo | One-line idea |
|---|---|---|
| 2.1 Design effective tool interfaces with clear descriptions and boundaries | `task2_1_tool_interfaces.py` | Descriptions are the **primary** tool-selection mechanism |
| 2.2 Implement structured error responses for MCP tools | `task2_2_structured_errors.py` | `errorCategory` + `isRetryable`; empty ≠ failure |
| 2.3 Distribute tools appropriately across agents and configure tool choice | `task2_3_tool_distribution_choice.py` | Least privilege; `auto`/`any`/forced |
| 2.4 Integrate MCP servers into Claude Code and agent workflows | `task2_4_mcp_integration.py` | `.mcp.json` (shared) vs `~/.claude.json` (personal); resources vs tools |
| 2.5 Select and apply built-in tools (Read, Write, Edit, Bash, Grep, Glob) effectively | `task2_5_builtin_tools.py` | **Grep = contents, Glob = names** |

```bash
python3 run_all.py domain2
```

**Most-tested reflexes:** misrouting between thin tools → *expand the descriptions first*;
Grep vs Glob; `auto`/`any`/forced `tool_choice`.
