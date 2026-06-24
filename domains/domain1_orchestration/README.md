# Domain 1 — Agentic Architecture & Orchestration (27%, the biggest domain)

How a single agent runs its work loop, how a coordinator manages a team of subagents, and
how you enforce workflows that must happen in order.

| Task | Demo | One-line idea |
|---|---|---|
| 1.1 Design and implement agentic loops for autonomous task execution | `task1_1_agentic_loop.py` | Loop on `stop_reason`; append tool results to history |
| 1.2 Orchestrate multi-agent systems with coordinator-subagent patterns | `task1_2_coordinator_subagents.py` | Hub-and-spoke; the coordinator's decomposition is the risk |
| 1.3 Configure subagent invocation, context passing, and spawning | `task1_3_subagent_invocation.py` | `Task` tool, explicit context, parallel spawning, structured handoffs |
| 1.4 Implement multi-step workflows with enforcement and handoff patterns | `task1_4_workflow_enforcement.py` | Prerequisite **gates** (deterministic) beat prompt guidance |
| 1.5 Apply Agent SDK hooks for tool call interception and data normalization | `task1_5_hooks.py` | PostToolUse normalizes after; interception blocks before |
| 1.6 Design task decomposition strategies for complex workflows | `task1_6_task_decomposition.py` | Prompt chaining (known steps) vs dynamic adaptive |
| 1.7 Manage session state, resumption, and forking | `task1_7_session_state.py` | `--resume` vs `fork_session` vs fresh-start |

```bash
python3 run_all.py domain1     # run all seven, non-stop
```

**Exam priority:** Domains 1 + 2 are 45% of the exam and share one philosophy — *agents
are only as reliable as the structure around them.* Master 1.1, 1.2, and 1.4 first.
