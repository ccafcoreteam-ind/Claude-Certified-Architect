"""
Domain 5 · Task 5.4 — Context management in large codebase exploration.

THE BIG IDEA
============
  * RECOGNIZE CONTEXT DEGRADATION: in long sessions the model starts answering from
    "typical patterns" instead of the specific classes it actually discovered earlier — a
    sign its working memory has been squeezed.
  * SCRATCHPAD FILES: have the agent write key findings to a file and consult it later —
    external memory that survives context pressure.
  * DELEGATE the verbose work: spawn subagents for noisy investigations ("find all test
    files", "trace refund-flow deps") so only SUMMARIES return to the main agent.
  * PHASE SUMMARIES: summarize each exploration phase before spawning the next phase's
    subagents, injecting the summary into their initial context.
  * CRASH RECOVERY via MANIFESTS: each agent exports structured state to a known location;
    on resume, the coordinator loads the manifest and injects it — no restart from zero.
  * /compact condenses the conversation when verbose discovery fills the context.
"""

import sys, pathlib, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from ccarch import banner, concept, h1, h2, wrong, right, tip, note, kv, code, rule, pause


def main():
    banner("Domain 5 · Task 5.4", "Large codebase exploration")
    concept("Domain 5: Context Management & Reliability (15%)",
            "Task 5.4 — Manage context effectively in large codebase exploration",
            "External memory + delegation keep the main context clean")

    h1("Recognize context degradation")
    wrong("After a long session, the agent describes 'a typical repository pattern' instead "
          "of the SPECIFIC classes it found earlier. Its working memory got squeezed.")
    right("Treat that as a signal to externalize memory and/or /compact — don't trust "
          "answers drawn from 'typical patterns'.")

    pause("the toolkit")
    rule()
    h1("The toolkit for surviving huge codebases")
    h2("Scratchpad files (external memory)")
    code('write_file("findings.md", "RefundService lives in services/refund.py; "\n'
         '                          "calls billing.charge() and ledger.append()")',
         "persist findings, consult later")

    h2("Delegate verbose investigations to subagents")
    note("Spawn a subagent for 'find all test files' or 'trace refund-flow dependencies'. "
         "Only its SUMMARY returns to the main agent, preserving clean coordination.")

    h2("Phase summaries")
    note("Summarize phase 1 (structure mapping) BEFORE spawning phase 2 subagents; inject "
         "that summary into their initial context.")

    h2("Crash recovery via manifests")
    code(json.dumps({"agent": "dep-tracer", "completed": ["payments", "billing"],
                     "next": "ledger", "findings_file": "findings.md"}, indent=2),
         "manifest written to a known location")
    right("On resume, the coordinator loads the manifest and injects it — no restart from zero.")

    h2("/compact")
    note("Condenses the conversation when extended exploration fills context with verbose "
         "discovery output.")

    tip("Symptoms of degradation = answers from 'typical patterns'. Cures: scratchpad "
        "files, delegate verbose work (summaries only), phase summaries, manifests, /compact.")


if __name__ == "__main__":
    main()
