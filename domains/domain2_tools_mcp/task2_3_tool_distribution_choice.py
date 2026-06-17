"""
Domain 2 · Task 2.3 — Distribute tools across agents and configure tool_choice.

THE BIG IDEA
============
FEWER TOOLS = BETTER DECISIONS. Giving an agent 18 tools instead of 4-5 measurably
degrades selection reliability — every extra tool adds decision complexity. Agents with
tools outside their specialty tend to MISUSE them (a synthesis agent with web search starts
searching instead of synthesizing).

SCOPED ACCESS: each subagent gets only its role's tools, plus narrowly scoped cross-role
tools for high-frequency needs. Flagship example (sample Q9): the synthesis agent needs
constant small fact-checks (85% simple, 15% deep). Right answer: a scoped `verify_fact`
tool for the simple 85%, and keep routing the complex 15% through the coordinator.

tool_choice settings (Claude API):
  "auto"                       -> may call a tool OR just reply with text
  "any"                        -> MUST call some tool (its choice which)
  {"type":"tool","name":"..."} -> MUST call THAT specific tool
"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from ccarch import banner, concept, h1, h2, wrong, right, tip, note, kv, code, rule, pause


def main():
    banner("Domain 2 · Task 2.3", "Tool distribution & tool_choice")
    concept("Domain 2: Tool Design & MCP Integration (18%)",
            "Task 2.3 — Distribute tools & configure tool_choice",
            "Least privilege for tools + the tool_choice modes")

    h1("Fewer tools = better decisions")
    wrong("Handing one agent all 18 tools 'just in case'. Selection reliability drops; "
          "the agent burns turns deciding and picks wrong more often.")
    right("~4-5 well-described, role-relevant tools per agent. Scope to the role.")

    pause("the flagship example")
    rule()
    h1("Flagship example (sample Q9): synthesis agent needs frequent fact checks")
    note("Profile: 85% are simple fact-checks (dates, names, stats); 15% need deep research.")
    h2("Right answer")
    right("Give the synthesis agent a SCOPED verify_fact tool for the simple 85%; keep "
          "routing the complex 15% through the coordinator to the web-search agent.")
    h2("Why the distractors fail")
    wrong("Give it ALL search tools -> over-provisioning; it starts doing research, not synthesis.")
    wrong("Batch the verifications -> creates blocking dependencies; synthesis stalls.")
    wrong("Speculatively cache 'what it might need' -> you can't predict needs.")

    rule()
    h1("Constrain rather than trust")
    right("Replace a generic fetch_url with a load_document tool that VALIDATES document "
          "URLs — the tool itself enforces the boundary, so the agent can't wander off.")

    pause("tool_choice")
    rule()
    h1("tool_choice — three modes")
    modes = [
        ('"auto"', "Model may call a tool OR reply with text",
         "Normal conversation; tool use is optional"),
        ('"any"', "Model MUST call SOME tool (its choice which)",
         "You need structured output but the right schema depends on input (unknown doc type)"),
        ('{"type":"tool","name":"extract_metadata"}', "Model MUST call THAT specific tool",
         "A specific step must run first; handle later steps in follow-up turns"),
    ]
    for setting, behavior, use in modes:
        h2(setting)
        kv("  behavior", behavior)
        kv("  use when", use)

    code('# Force extract_metadata to run before any enrichment step\n'
         'tool_choice = {"type": "tool", "name": "extract_metadata"}', "forced first step")

    tip("'auto' = optional, 'any' = must call something, forced = must call that one. "
        "Pair with Task 4.3: 'any' guarantees structured output when the document type "
        "(hence the right schema) is unknown.")


if __name__ == "__main__":
    main()
