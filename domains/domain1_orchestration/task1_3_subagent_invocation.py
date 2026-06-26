"""
Domain 1 · Task 1.3 — Configure subagent invocation, context passing, and spawning.

THE BIG IDEA
============
The MECHANICS of launching subagents in the Claude Agent SDK:

  * The `Task` tool spawns subagents. The coordinator's `allowedTools` MUST include
    "Task" or it physically cannot delegate (classic exam gotcha).
  * Subagents have NO shared memory. Context must be PASTED INTO their prompt.
  * `AgentDefinition` = a subagent's job description (purpose, system prompt, tool limits).
  * PARALLEL spawning = emit MULTIPLE Task calls in ONE response (not one per turn).
  * STRUCTURED handoffs separate content from metadata so citations survive.
  * Prompts should state GOALS + quality criteria, not rigid step-by-step scripts.
  * `fork_session` branches from a shared baseline to explore divergent approaches.
"""

import sys, pathlib, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from ccarch import banner, concept, h1, h2, wrong, right, tip, note, kv, code, rule, pause, analogy, pitfall


def main():
    banner("Domain 1 · Task 1.3", "Subagent invocation, context passing, spawning")
    concept("Domain 1: Agentic Architecture & Orchestration (27%)",
            "Task 1.3 — Configure subagent invocation, context passing, and spawning",
            "Task tool + explicit context + parallel spawning")

    h1("1) The coordinator needs 'Task' in allowedTools")
    code('coordinator = AgentDefinition(\n'
         '    description="Research coordinator",\n'
         '    allowedTools=["Task"],   # <-- without this it CANNOT spawn subagents\n'
         ')', "agent sdk")
    wrong("Forgetting 'Task' in allowedTools, then debugging why delegation 'silently' "
          "does nothing.")

    rule()
    h1("2) Subagents have isolated context — pass it EXPLICITLY")
    note("The synthesis subagent cannot see what the web-search subagent found unless the "
         "coordinator pastes those findings into the synthesis prompt.")
    handoff = {
        "claim": "Global AI market reached $184B in 2024",
        "source_url": "https://example.org/ai-report-2024",
        "source_name": "AI Industry Report 2024",
        "page": 12,
        "relevance": 0.92,
    }
    code(json.dumps(handoff, indent=2), "structured handoff (content + metadata)")
    right("Pass findings as STRUCTURED data separating content from metadata (URL, doc "
          "name, page). Citations and attribution survive the journey between agents.")
    wrong("Handing the next agent a blob of prose. The source URLs and page numbers blur "
          "out and citations die in summarization.")

    pause("parallel spawning")
    rule()
    h1("3) Parallel spawning = multiple Task calls in ONE response")
    code("# SLOW: one Task per turn (serial)\n"
         "turn 1 -> Task(web_search)\n"
         "turn 2 -> Task(doc_analysis)\n\n"
         "# FAST: multiple Task calls emitted together (parallel)\n"
         "turn 1 -> [ Task(web_search), Task(doc_analysis) ]", "latency")
    note("Emitting them together lets the runtime run the subagents simultaneously, "
         "cutting wall-clock latency.")

    rule()
    h1("4) Goals over procedures")
    wrong('Coordinator prompt: "Step 1: search Google. Step 2: open the first 3 links. '
          'Step 3: ..." — rigid scripts stop subagents from adapting.')
    right('Coordinator prompt: "Find peer-reviewed sources covering ALL major creative '
          'sectors; flag any sector you could not cover." — goals + quality criteria.')

    rule()
    h1("5) fork_session — branch from a shared baseline")
    note("fork_session creates independent branches from one analysis baseline — e.g., "
         "explore two refactoring strategies from the same codebase understanding WITHOUT "
         "redoing the analysis. (More in Task 1.7.)")

    rule()
    h1("Plain-language analogy & the common confusion")
    analogy("A coordinator briefing analysts who work in separate rooms with the doors shut. Nothing on the coordinator's whiteboard is visible to them — whatever they need (prior findings, source URLs) must be photocopied into the briefing packet.")
    pitfall("Beginners assume subagents can 'see' the parent conversation. They cannot — context is isolated. If you do not paste it into the subagent's prompt, it simply does not exist for that agent.")

    tip("Gotchas bundled here: 'Task' must be in allowedTools; subagents inherit NOTHING; "
        "parallelism = multiple Task calls in a single response; structured handoffs "
        "preserve citations.")


if __name__ == "__main__":
    main()
