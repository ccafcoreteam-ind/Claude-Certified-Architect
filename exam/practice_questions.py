"""
exam/practice_questions.py — authored, exam-style PRACTICE questions
====================================================================
ORIGINAL practice questions written in the style and difficulty of the Foundations exam,
one for each task statement the 12 official sample questions (exam/sample_questions.py) do
NOT already cover. These are study aids, NOT official exam items.

Each is scenario-framed with one root-cause answer and three plausible distractors that
mirror the exam's recurring traps: more prompting where ENFORCEMENT is needed, more
infrastructure where prompting suffices, or a feature that does not exist / solves the
wrong problem.

The console (ui/console) links each question to its task via build_data.py, so every task
now shows at least one question. They are tagged P1..P18 (vs the official Q1..Q12).
"""
import sys
import os
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from ccarch import banner, h1, kv, note, right, tip, rule

# Each: task, domain, q (prompt), options A-D, answer letter, why.
PRACTICE = [
    dict(task="1.1", domain="d1",
         q="Your agent loop ends each turn by scanning Claude's text for the phrase "
           "'task complete' to decide whether to stop. It sometimes stops early (Claude "
           "mentions the phrase mid-reasoning) and sometimes loops forever. What is the "
           "correct fix?",
         options={
             "A": "Inspect stop_reason: keep looping while it is 'tool_use' and exit when "
                  "it is 'end_turn'.",
             "B": "Add a stricter regex and a longer list of completion phrases to detect "
                  "the end of the task.",
             "C": "Cap the loop at 10 iterations and return whatever the last turn produced.",
             "D": "Ask Claude to always end its final message with a unique sentinel token "
                  "you can match on.",
         },
         answer="A",
         why="Termination must be driven by stop_reason, the structured signal the API "
             "returns. Parsing natural-language text is probabilistic and brittle; "
             "an iteration cap is only a safety net, not the normal stop condition."),

    dict(task="1.3", domain="d1",
         q="A coordinator delegates to a synthesis subagent, but the subagent keeps "
           "producing summaries that ignore the web-search findings the coordinator already "
           "gathered. The coordinator's allowedTools already includes 'Task'. What is the "
           "most likely cause?",
         options={
             "A": "The web-search findings were never written into the synthesis subagent's "
                  "prompt — subagents do not inherit the coordinator's conversation.",
             "B": "The coordinator is missing 'Task' in allowedTools, so the subagent never "
                  "really ran.",
             "C": "The synthesis subagent needs its own web-search tool so it can re-gather "
                  "the findings.",
             "D": "The subagents must be spawned in parallel in one response for context to "
                  "transfer between them.",
         },
         answer="A",
         why="Subagents have isolated context; anything they need must be explicitly placed "
             "in their prompt. The missing-'Task'-tool explanation is contradicted by the "
             "stem; giving synthesis its own web-search tool over-provisions and duplicates "
             "work; parallel spawning affects latency, not whether context transfers."),

    dict(task="1.5", domain="d1",
         q="Three backend tools return timestamps in three formats (Unix epoch, ISO 8601, "
           "and a numeric status code), and the agent frequently misreads dates. You want a "
           "guaranteed, one-place fix the model never has to think about. What do you build?",
         options={
             "A": "A PostToolUse hook that normalizes every tool's date field to one format "
                  "before the model sees it.",
             "B": "A system-prompt instruction telling Claude to carefully convert each "
                  "format whenever it reads one.",
             "C": "Few-shot examples showing the three formats and their conversions.",
             "D": "A separate date-parsing tool the agent calls after every lookup.",
         },
         answer="A",
         why="PostToolUse hooks transform results deterministically before the model "
             "processes them. Prompt instructions and few-shot are probabilistic; "
             "an extra tool the agent must remember to call reintroduces the failure."),

    dict(task="1.6", domain="d1",
         q="You must add comprehensive tests to a large legacy codebase whose structure and "
           "dependencies you do not yet know. Which decomposition strategy fits?",
         options={
             "A": "Dynamic, adaptive decomposition: map the structure, find high-impact "
                  "areas, and generate the next subtasks from what each step discovers.",
             "B": "A fixed prompt-chaining pipeline with the full list of files to test "
                  "defined up front.",
             "C": "One large prompt asking the model to test the entire codebase at once.",
             "D": "Parallel subagents, one per directory, each writing tests independently "
                  "with no shared plan.",
         },
         answer="A",
         why="Open-ended, discovery-driven work needs adaptive decomposition; you cannot "
             "know the steps up front, which rules out a fixed pipeline. One mega-prompt "
             "(C) dilutes attention; uncoordinated parallel agents duplicate and miss "
             "cross-cutting areas."),

    dict(task="1.7", domain="d1",
         q="You resume a 3-day-old investigation session, but several of the files it "
           "analyzed have since been heavily refactored. What is the most reliable approach?",
         options={
             "A": "Start a fresh session seeded with a structured summary of the still-valid "
                  "findings, rather than resuming a session full of stale tool results.",
             "B": "Resume the session as-is; the model will notice the files changed.",
             "C": "Resume with a larger context window so both the old and new state fit.",
             "D": "Fork the session so you can compare the old and new code side by side.",
         },
         answer="A",
         why="When prior tool results are largely stale, a fresh session with an injected "
             "summary beats reasoning over outdated facts. The model will not auto-detect "
             "changed files; context size does not fix staleness; forking is for "
             "exploring divergent approaches from a still-valid baseline."),

    dict(task="2.2", domain="d2",
         q="An MCP refund tool returns a generic 'Operation failed' message for every "
           "failure — bad input, policy limits, and timeouts alike — all with isError set. "
           "The agent retries everything and apologizes generically. Which change most "
           "improves recovery?",
         options={
             "A": "Return structured error metadata: an errorCategory "
                  "(transient/validation/business/permission), an isRetryable boolean, and a "
                  "human-readable message.",
             "B": "Increase the retry count and add exponential backoff for all failures.",
             "C": "Add a system-prompt rule telling the agent which errors to retry.",
             "D": "Have the tool raise the underlying exception so the agent sees the full "
                  "stack trace.",
         },
         answer="A",
         why="The agent cannot choose the right recovery without categorized, structured "
             "errors. Blanket retries waste calls on non-retryable failures; a prompt "
             "rule is probabilistic and blind to the tool's internal cause; a raw stack "
             "trace is noise the agent can't reliably act on."),

    dict(task="2.4", domain="d2",
         q="Your team needs everyone to share a Jira MCP server, authenticated with a token "
           "that must not be committed to the repo. Where and how do you configure it?",
         options={
             "A": "In the project's .mcp.json, with the token referenced as ${JIRA_TOKEN} "
                  "via environment-variable expansion.",
             "B": "In each developer's ~/.claude.json, with the real token pasted in.",
             "C": "In the project's .mcp.json with the real token, then add .mcp.json to "
                  ".gitignore.",
             "D": "As a built-in tool, since Jira is a standard integration.",
         },
         answer="A",
         why="Project-scoped .mcp.json shares the server with the team via version control, "
             "and ${ENV_VAR} expansion keeps the secret out of the committed file. Personal "
             "config isn't shared and hardcodes the secret; gitignoring the config "
             "means teammates don't get the server; Jira is not a built-in tool."),

    dict(task="2.5", domain="d2",
         q="You need to find every file whose name ends in .test.tsx, then within one of "
           "them change a single import line that appears exactly once. Which tools fit, in "
           "order?",
         options={
             "A": "Glob for the file names, then Edit for the unique import line.",
             "B": "Grep for the file names, then Write to rewrite the whole file.",
             "C": "Glob to search the file contents, then Bash sed to change the line.",
             "D": "Read every file to find the matches, then Edit the import.",
         },
         answer="A",
         why="Glob matches file NAMES/paths; Edit makes a targeted change anchored on unique "
             "text. Grep searches CONTENTS, not names; Glob does not search contents "
             "(C); reading every file upfront is wasteful."),

    dict(task="3.1", domain="d3",
         q="A new teammate clones the repo, but Claude ignores the team's coding conventions "
           "for them — even though it follows them for you. Where were the conventions most "
           "likely defined, and what is the fix?",
         options={
             "A": "In your user-level ~/.claude/CLAUDE.md (which never travels via git); move "
                  "them to the project-level CLAUDE.md in the repo.",
             "B": "In the project CLAUDE.md; tell the teammate to run /memory to load it.",
             "C": "In a directory-level CLAUDE.md; move it into your ~/.claude/ so it always "
                  "applies.",
             "D": "Nowhere — Claude just needs a few sessions to learn the conventions.",
         },
         answer="A",
         why="User-level config is personal and not shared through version control, so a "
             "teammate never receives it; the project CLAUDE.md is. Telling them to run "
             "/memory misdiagnoses it (project-level would already reach them); moving it "
             "into ~/.claude/ goes the wrong direction; 'wait a few sessions' is not how "
             "CLAUDE.md works."),

    dict(task="3.5", domain="d3",
         q="Claude's data-transformation output is inconsistent run-to-run despite a "
           "detailed paragraph of instructions. What is the most effective next step?",
         options={
             "A": "Replace the prose with 2-3 concrete input-to-output examples showing the "
                  "exact transformation.",
             "B": "Make the instruction paragraph longer and more emphatic.",
             "C": "Tell Claude to lower its temperature and be more deterministic.",
             "D": "Add a rule telling Claude to double-check its work before responding.",
         },
         answer="A",
         why="Concrete input-to-output examples communicate a transformation far more "
             "reliably than prose, which is interpreted inconsistently. More/longer prose "
             "(B) and exhortations don't pin the behavior down; temperature isn't a "
             "prompt instruction and doesn't fix ambiguous intent."),

    dict(task="4.1", domain="d4",
         q="Your automated comment-accuracy reviewer produces too many false positives, so "
           "developers ignore it. It currently is told to 'only report high-confidence "
           "issues.' What most improves precision?",
         options={
             "A": "Replace the vague modifier with specific, testable criteria — e.g., flag "
                  "a comment only when the claimed behavior contradicts the actual code.",
             "B": "Add 'be conservative and avoid false positives' to the instructions.",
             "C": "Have the model output a confidence score and drop anything below 0.9.",
             "D": "Switch to a larger model so its judgment is more accurate.",
         },
         answer="A",
         why="Specific categorical criteria give a decidable boundary; vague modifiers like "
             "'high-confidence' / 'be conservative' do not move precision. Self-reported "
             "confidence is poorly calibrated; a bigger model doesn't fix an "
             "underspecified task."),

    dict(task="4.2", domain="d4",
         q="An extraction prompt with detailed instructions still sometimes invents a value "
           "when a field is missing from the document. What is the most effective fix?",
         options={
             "A": "Add 2-3 few-shot examples, including one where a missing field is "
                  "correctly extracted as null.",
             "B": "Add a stern instruction: never make up values, use null if missing.",
             "C": "Make the field required in the schema so the model always fills it.",
             "D": "Lower the temperature so the model is less creative.",
         },
         answer="A",
         why="A demonstrated example of the null/edge case teaches the boundary more "
             "reliably than any prose rule. Making the field required actively forces "
             "fabrication; temperature doesn't address missing-data behavior."),

    dict(task="4.3", domain="d4",
         q="You must extract data from documents of an unknown type and need guaranteed "
           "schema-compliant JSON with no syntax errors. Which setup is correct?",
         options={
             "A": "Define a tool whose input_schema is your output schema, set tool_choice "
                  "to 'any', and make fields nullable where a document may lack them.",
             "B": "Ask for JSON in the prompt and parse the text, retrying on syntax errors.",
             "C": "Use a tool with all fields required and tool_choice 'auto'.",
             "D": "Force one specific extraction tool with a fixed tool_choice regardless of "
                  "document type.",
         },
         answer="A",
         why="Tool-use with a JSON schema eliminates syntax errors; 'any' guarantees a tool "
             "is called when the right schema depends on the unknown input; nullable fields "
             "prevent fabrication. Free-text JSON reintroduces syntax errors; required "
             "fields force made-up values; forcing one tool fails when the type "
             "varies."),

    dict(task="4.4", domain="d4",
         q="Your validator fails because a required PO number is missing — and that PO "
           "number is not in the source document at all (it lives in a separate system). "
           "What should the pipeline do?",
         options={
             "A": "Recognize the retry is futile, emit null for the field, and route the "
                  "document to a human / fetch the external source.",
             "B": "Retry with the validation error appended; the model will find the PO "
                  "number.",
             "C": "Retry up to 5 times with backoff before giving up.",
             "D": "Lower the schema's requirements so the field is no longer validated.",
         },
         answer="A",
         why="Retries fix format/structure errors but can never conjure information absent "
             "from the source, so retrying is futile. Silently dropping the validation "
             "(D) hides a real data gap."),

    dict(task="5.1", domain="d5",
         q="In a long support conversation the agent loses track of the exact refund amount "
           "and deadline it promised earlier, and repeated summaries keep getting vaguer. "
           "What is the most reliable fix?",
         options={
             "A": "Maintain a persistent 'case facts' block (amount, dates, order ID, status) "
                  "included in every prompt, outside the summarized history.",
             "B": "Summarize the conversation more often so it stays short.",
             "C": "Increase the model's context window so nothing is dropped.",
             "D": "Ask the model to remember the important details carefully.",
         },
         answer="A",
         why="Numbers and dates are the first casualties of progressive summarization; a "
             "structured facts block kept outside the summary preserves them. More "
             "summarization worsens it; a bigger window doesn't stop "
             "lost-in-the-middle/erosion; 'remember carefully' is no guarantee."),

    dict(task="5.4", domain="d5",
         q="Deep into a long codebase-exploration session, the agent starts answering with "
           "'a typical implementation would...' instead of the specific classes it found "
           "earlier. What does this indicate, and what is the right response?",
         options={
             "A": "Context degradation — externalize findings to a scratchpad file (and/or "
                  "/compact) and delegate verbose investigations to subagents that return "
                  "summaries.",
             "B": "The model has finished exploring and is now generalizing correctly.",
             "C": "The model needs the entire codebase pasted into one prompt.",
             "D": "Restart from scratch and re-read every file in a new session.",
         },
         answer="A",
         why="Answering from 'typical patterns' instead of discovered specifics signals "
             "working-memory pressure; the fix is external memory + delegation/compaction. "
             "It is not correct generalization; pasting everything worsens the "
             "pressure; a full restart wastes the progress a summary could preserve."),

    dict(task="5.5", domain="d5",
         q="An extraction system reports 97% overall accuracy, so a manager wants to fully "
           "automate it. What is the responsible next step before automating?",
         options={
             "A": "Validate accuracy by document type AND by field (a high average can hide "
                  "a 60% pocket), and keep auditing high-confidence outputs via stratified "
                  "sampling.",
             "B": "Automate everything; 97% is well above any reasonable bar.",
             "C": "Route only the lowest-confidence 3% to humans and automate the rest.",
             "D": "Raise the confidence threshold until overall accuracy reads 99%.",
         },
         answer="A",
         why="Aggregate metrics hide segment-level failure; validate per type/field and keep "
             "auditing the trusted lane. Blanket automation ships the hidden pockets; "
             "routing by a global percentage ignores per-segment risk; tuning the "
             "threshold to inflate the headline number games the metric."),

    dict(task="5.6", domain="d5",
         q="A multi-source research report cites a 2021 figure of $136B and a 2024 figure of "
           "$184B for the same market and labels them 'a contradiction in the sources.' What "
           "went wrong, and what is the fix?",
         options={
             "A": "These are different-year data points — a trend, not a contradiction; "
                  "require publication/collection dates in the structured outputs so time "
                  "differences are not misread.",
             "B": "The synthesis agent should pick the more recent value and drop the other.",
             "C": "One source is wrong; flag the report for manual correction.",
             "D": "Average the two figures to resolve the discrepancy.",
         },
         answer="A",
         why="Figures from different years represent change over time, not disagreement; "
             "attaching dates prevents the misreading. Dropping or averaging destroys "
             "real information; assuming an error misdiagnoses a temporal trend."),
]


def main():
    banner("Practice Questions", "Authored, exam-style — one per task the official 12 don't cover")
    note("These are ORIGINAL study questions in the exam's style (P1..P18), not official "
         "items. Each targets a task statement with no official sample question.")
    for i, q in enumerate(PRACTICE, 1):
        h1(f"P{i} — Task {q['task']} ({q['domain'].upper()})")
        note(q["q"])
        print()
        for k in ("A", "B", "C", "D"):
            kv(f"  {k}", q["options"][k])
        right(f"Answer: {q['answer']}")
        note("Why: " + q["why"])
    rule()
    tip("Practice questions follow the same logic as the real exam: the answer is the "
        "simplest mechanism that fixes the actual root cause; distractors over-prompt where "
        "enforcement is needed, over-build where prompting suffices, or invent a feature.")


if __name__ == "__main__":
    main()
