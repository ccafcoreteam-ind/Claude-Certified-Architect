#!/usr/bin/env python3
"""
ui/console/build_data.py — regenerate assets/data.js from the repo's authoritative content.

The console's content model must match the official Exam Guide. Rather than hand-maintain
it, this generator derives everything from the repo, which already matches the guide:

  * task titles      -> the verbatim official task statements (TITLES below)
  * concept/anti/right/tip -> ast-extracted from each demo's concept()/wrong()/right()/tip()
  * per-task output  -> the REAL demo stdout (ui/console/api_server.run_file), truncated
  * questions        -> the official 12 from exam/sample_questions.QUESTIONS
  * cheat facts      -> exam/cheatsheet.FACTS
  * scenarios        -> titles + corrected step task-numbers (mapped to the guide)

Run:  python3 ui/console/build_data.py     # rewrites ui/console/assets/data.js
"""
import ast
import json
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)   # api_server
sys.path.insert(0, REPO)   # exam.*

import api_server  # noqa: E402
from exam.sample_questions import QUESTIONS  # noqa: E402
from exam.practice_questions import PRACTICE  # noqa: E402
from exam.mock_bank import MOCK_BANK  # noqa: E402
from exam.cheatsheet import FACTS  # noqa: E402

TITLES = {
 "1.1":"Design and implement agentic loops for autonomous task execution",
 "1.2":"Orchestrate multi-agent systems with coordinator-subagent patterns",
 "1.3":"Configure subagent invocation, context passing, and spawning",
 "1.4":"Implement multi-step workflows with enforcement and handoff patterns",
 "1.5":"Apply Agent SDK hooks for tool call interception and data normalization",
 "1.6":"Design task decomposition strategies for complex workflows",
 "1.7":"Manage session state, resumption, and forking",
 "2.1":"Design effective tool interfaces with clear descriptions and boundaries",
 "2.2":"Implement structured error responses for MCP tools",
 "2.3":"Distribute tools appropriately across agents and configure tool choice",
 "2.4":"Integrate MCP servers into Claude Code and agent workflows",
 "2.5":"Select and apply built-in tools (Read, Write, Edit, Bash, Grep, Glob) effectively",
 "3.1":"Configure CLAUDE.md files with appropriate hierarchy, scoping, and modular organization",
 "3.2":"Create and configure custom slash commands and skills",
 "3.3":"Apply path-specific rules for conditional convention loading",
 "3.4":"Determine when to use plan mode vs direct execution",
 "3.5":"Apply iterative refinement techniques for progressive improvement",
 "3.6":"Integrate Claude Code into CI/CD pipelines",
 "4.1":"Design prompts with explicit criteria to improve precision and reduce false positives",
 "4.2":"Apply few-shot prompting to improve output consistency and quality",
 "4.3":"Enforce structured output using tool use and JSON schemas",
 "4.4":"Implement validation, retry, and feedback loops for extraction quality",
 "4.5":"Design efficient batch processing strategies",
 "4.6":"Design multi-instance and multi-pass review architectures",
 "5.1":"Manage conversation context to preserve critical information across long interactions",
 "5.2":"Design effective escalation and ambiguity resolution patterns",
 "5.3":"Implement error propagation strategies across multi-agent systems",
 "5.4":"Manage context effectively in large codebase exploration",
 "5.5":"Design human review workflows and confidence calibration",
 "5.6":"Preserve information provenance and handle uncertainty in multi-source synthesis",
}

DOMAINS = [
  {"id":"d1","n":1,"title":"Agentic Architecture & Orchestration","short":"Orchestration",
   "weight":27,"folder":"domain1_orchestration/",
   "blurb":"How agents loop on stop_reason, when a coordinator delegates to subagents, and how must-follow rules are enforced in code."},
  {"id":"d2","n":2,"title":"Tool Design & MCP Integration","short":"Tools & MCP",
   "weight":18,"folder":"domain2_tools_mcp/",
   "blurb":"Tool descriptions the model can pick correctly, structured errors it can recover from, scoped tool sets, and MCP servers."},
  {"id":"d3","n":3,"title":"Claude Code Configuration & Workflows","short":"Claude Code",
   "weight":20,"folder":"domain3_claude_code/",
   "blurb":"CLAUDE.md scope, slash commands & skills, path-specific rules, plan vs direct execution, refinement, and CI/CD."},
  {"id":"d4","n":4,"title":"Prompt Engineering & Structured Output","short":"Prompting",
   "weight":20,"folder":"domain4_prompt_output/",
   "blurb":"Explicit criteria, few-shot, JSON-schema tool use, validation/retry loops, batch economics, and review architectures."},
  {"id":"d5","n":5,"title":"Context Management & Reliability","short":"Context",
   "weight":15,"folder":"domain5_context_reliability/",
   "blurb":"Preserve key facts across long interactions, escalate by rule, propagate errors usefully, and keep provenance."},
]

THEMES = [
  {"id":"t1","title":"Guarantees beat instructions",
   "body":"Must-follow rules — verify identity before a refund — belong in code: hooks, gates, schemas. Prompts are probabilistic; code is deterministic."},
  {"id":"t2","title":"Fix the root cause, proportionately",
   "body":"A vague tool description calls for a better description — not a routing classifier. The exam loves over-engineered distractors."},
  {"id":"t3","title":"Context is a scarce, leaky resource",
   "body":"Extract the key facts, trim the noise, and pass information explicitly between agents. Never assume the next step can see everything."},
]

# Scenario step task-numbers re-pointed to the guide's correct task ids.
SCENARIOS = [
  {"id":"s1","n":1,"title":"Customer Support Resolution Agent","domains":["d1","d2","d5"],
   "summary":"A real support agent: an agentic loop guarded by a prerequisite gate and an interception hook, returning structured errors, carrying a case-facts block, and escalating cleanly.",
   "steps":[
     {"t":"Agentic loop","d":"Gather → act → verify on stop_reason until resolved.","task":"1.1"},
     {"t":"Prerequisite gate","d":"No refund until get_customer verifies identity — in code.","task":"1.4"},
     {"t":"Interception hook","d":"Block refunds over $500; redirect to escalation.","task":"1.5"},
     {"t":"Structured errors","d":"Tools return errorCategory + isRetryable so the agent recovers.","task":"2.2"},
     {"t":"Case-facts block","d":"Persistent transactional facts survive summarization.","task":"5.1"},
     {"t":"Escalation","d":"Hand to a human with a structured handoff packet.","task":"5.2"}]},
  {"id":"s2","n":2,"title":"Code Generation with Claude Code","domains":["d3","d5"],
   "summary":"Team enablement: configuration scope, custom commands & skills, path rules, plan-vs-direct execution, and iterative refinement on a real change.",
   "steps":[
     {"t":"Config scope","d":"Shared project CLAUDE.md vs personal ~/.claude.","task":"3.1"},
     {"t":"Commands & skills","d":"Team /review lives in .claude/commands.","task":"3.2"},
     {"t":"Path rules","d":"Glob-scoped conventions for scattered files.","task":"3.3"},
     {"t":"Plan vs direct","d":"Plan mode for the multi-file change.","task":"3.4"},
     {"t":"Iterative refinement","d":"Show examples; use test failures as feedback.","task":"3.5"}]},
  {"id":"s3","n":3,"title":"Multi-Agent Research System","domains":["d1","d2","d5"],
   "summary":"A coordinator with specialist subagents. Shows the narrow-decomposition failure and its fix, structured error propagation, and end-to-end provenance.",
   "steps":[
     {"t":"Coordinator + subagents","d":"Hub-and-spoke delegation.","task":"1.2"},
     {"t":"Invocation & context","d":"Task tool, explicit context, parallel spawning.","task":"1.3"},
     {"t":"Decomposition","d":"Avoid the narrow-decomposition failure.","task":"1.6"},
     {"t":"Tool distribution","d":"Scoped verify_fact for the synthesis agent.","task":"2.3"},
     {"t":"Error propagation","d":"Structured error context; annotate coverage gaps.","task":"5.3"},
     {"t":"Provenance","d":"Claim-source mappings survive synthesis.","task":"5.6"}]},
  {"id":"s4","n":4,"title":"Developer Productivity","domains":["d2","d3","d1"],
   "summary":"An assistant exploring an unfamiliar codebase with the built-in tools and MCP — incremental Grep→Read, delegation, and external memory.",
   "steps":[
     {"t":"Built-in tools","d":"Grep = contents, Glob = names; incremental exploration.","task":"2.5"},
     {"t":"MCP integration","d":"Project vs personal servers; resources vs tools.","task":"2.4"},
     {"t":"Large-codebase context","d":"Scratchpads + delegation keep context clean.","task":"5.4"},
     {"t":"Task decomposition","d":"Adaptive plan for legacy exploration.","task":"1.6"}]},
  {"id":"s5","n":5,"title":"Claude Code for CI/CD","domains":["d3","d4"],
   "summary":"Claude Code in the pipeline: non-interactive runs, structured findings, low false positives, and multi-pass review.",
   "steps":[
     {"t":"Non-interactive CI","d":"claude -p; --output-format json for PR comments.","task":"3.6"},
     {"t":"Structured output","d":"Schema via tool use so a bot can post findings.","task":"4.3"},
     {"t":"Explicit criteria","d":"Cut false positives with specific categories.","task":"4.1"},
     {"t":"Multi-pass review","d":"Per-file + integration passes; fresh instance.","task":"4.6"}]},
  {"id":"s6","n":6,"title":"Structured Data Extraction","domains":["d4","d5"],
   "summary":"Unstructured documents → schema-validated JSON: tool-use schema, nullable fields, validation/retry, batch routing, and confidence-based human review.",
   "steps":[
     {"t":"Schema via tool use","d":"input_schema = output contract; nullable prevents fabrication.","task":"4.3"},
     {"t":"Validation & retry","d":"Retry with specific errors; futile when info is absent.","task":"4.4"},
     {"t":"Batch processing","d":"Batch the non-blocking; sync what a human waits on.","task":"4.5"},
     {"t":"Human review","d":"Confidence routing + stratified audit.","task":"5.5"},
     {"t":"Preserve context","d":"Case-facts block resists summarization.","task":"5.1"}]},
]


# --- ast helpers: pull concept summary + first wrong/right + tip from a demo ---
def _const_str(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        l, r = _const_str(node.left), _const_str(node.right)
        if l is not None and r is not None:
            return l + r
    return None


# Curated text for the few demos whose first wrong()/right() is an f-string (which the
# constant-only extractor skips). Sourced from the same demo's teaching content.
OVERRIDES = {
  ("1.2", "antipattern"): "Blaming the subagents when the report is incomplete — every subagent 'completed successfully', but the coordinator carved the topic too narrowly.",
  ("1.5", "antipattern"): "Relying on a prompt ('always normalize the dates', 'never refund over $500') for a guarantee — prompts are probabilistic and fail a fraction of the time.",
  ("2.1", "right"): "Expand the description first: purpose, input formats, a worked example, and an explicit boundary pointing to the neighbouring tool. The low-effort, root-cause fix.",
  ("4.2", "antipattern"): "Adding more prose to force consistency when detailed instructions already fail — prose can't convey the boundary case (e.g. when to emit null) as reliably as a worked example.",
}


def extract_demo_strings(path):
    tree = ast.parse(open(path, encoding="utf-8").read())
    concept_summary = ""
    first = {"wrong": None, "right": None, "tip": None, "analogy": None, "pitfall": None}
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)]
    calls.sort(key=lambda n: getattr(n, "lineno", 0))
    for n in calls:
        name = n.func.id
        if name == "concept" and len(n.args) >= 3 and not concept_summary:
            s = _const_str(n.args[2])
            if s:
                concept_summary = s
        elif name in first and first[name] is None and n.args:
            s = _const_str(n.args[0])
            if s:
                first[name] = s
    return concept_summary, first


def demo_output(rel, limit=18):
    full = api_server.run_file(os.path.join(REPO, rel))
    lines = [{"type": "cmd", "text": f"$ python3 {rel}"}]
    lines.extend(full[:limit])
    # If a code() box lives past the preview window, append the FIRST one so the
    # "see it as code" snippet still shows in the static console preview. code()
    # boxes are indented "  ┌─" (banners/concept boxes start at column 0).
    is_code_top = lambda ln: ln.get("text", "").startswith("  ┌")
    is_code_end = lambda ln: ln.get("text", "").startswith("  └")
    head_has_code = any(is_code_top(ln) for ln in full[:limit])
    if not head_has_code:
        start = next((i for i in range(limit, len(full)) if is_code_top(full[i])), None)
        if start is not None:
            end = next((j for j in range(start, len(full)) if is_code_end(full[j])), start)
            lines.append({"type": "dim", "text": "   … (skipping ahead to the code) …"})
            lines.extend(full[start:end + 1])
    return lines


# --- questions + cheat from the exam modules ---
def _shuffle_options(options, answer_idx, seed):
    """Deterministically reorder the 4 options so the correct answer isn't always A.
    Seeded by the question id, so the order is stable across regenerations (no churn).
    The explanations are letter-free, so reordering never invalidates them."""
    order = list(range(len(options)))
    random.Random(seed).shuffle(order)
    return [options[i] for i in order], order.index(answer_idx)


def build_questions():
    out = []
    for q in QUESTIONS:
        maps = q["maps"]
        task = re.search(r"T(\d\.\d)", maps).group(1)
        dom = "d" + re.search(r"D(\d)", maps).group(1)
        qid = f"q{q['n']}"
        opts, ans = _shuffle_options(
            [q["options"][k] for k in ("A", "B", "C", "D")], "ABCD".index(q["answer"]), qid)
        out.append({
            "id": qid, "task": task, "domain": dom, "prompt": q["q"],
            "options": opts, "answer": ans, "why": q["why"],
        })
    for i, q in enumerate(PRACTICE, 1):   # authored practice questions (P1..P18)
        pid = f"p{i}"
        opts, ans = _shuffle_options(
            [q["options"][k] for k in ("A", "B", "C", "D")], "ABCD".index(q["answer"]), pid)
        out.append({
            "id": pid, "task": q["task"], "domain": q["domain"], "prompt": q["q"],
            "options": opts, "answer": ans, "why": q["why"],
        })
    return out


def build_mock():
    """The verified 60-question (+3 supplementary) blueprint-aligned mock-exam bank.
    Options are shuffled (source answers are B/A/C only, never D); explanations are
    letter-free, and each item keeps its official Domain/Task reference line."""
    out = []
    for i, q in enumerate(MOCK_BANK, 1):
        mid = f"m{i}"
        opts, ans = _shuffle_options(
            [q["options"][k] for k in ("A", "B", "C", "D")], "ABCD".index(q["answer"]), mid)
        out.append({
            "id": mid, "task": q["task"], "domain": q["domain"], "prompt": q["q"],
            "options": opts, "answer": ans, "why": q["why"], "ref": q["ref"],
        })
    return out


def build_cheat():
    out = []
    for topic, fact, demo in FACTS:
        m = re.match(r"domain(\d)/task(\d)_(\d)", demo)
        if not m:
            continue
        out.append({"d": f"d{m.group(1)}", "fact": fact,
                    "task": f"{m.group(2)}.{m.group(3)}"})
    return out


def build_tasks(questions):
    q_by_task = {}
    for q in questions:
        q_by_task.setdefault(q["task"], []).append(q["id"])
    tasks = []
    for tid, title in TITLES.items():
        d = "d" + tid.split(".")[0]
        folder = next(x["folder"] for x in DOMAINS if x["id"] == d)
        # locate the demo file
        import glob
        hits = glob.glob(os.path.join(REPO, "domains", "*", f"task{tid.replace('.', '_')}_*.py"))
        rel = os.path.relpath(hits[0], REPO)
        concept, first = extract_demo_strings(hits[0])
        fields = {"concept": concept, "antipattern": first["wrong"] or "",
                  "right": first["right"] or "", "tip": first["tip"] or "",
                  "analogy": first["analogy"] or "", "pitfall": first["pitfall"] or ""}
        for key in fields:
            if (tid, key) in OVERRIDES:
                fields[key] = OVERRIDES[(tid, key)]
            if not fields[key] and key != "analogy":   # analogy is optional per demo
                print(f"  WARNING: task {tid} has empty {key}")
        tasks.append({
            "id": tid, "d": d, "title": title, **fields,
            "output": demo_output(rel), "q": q_by_task.get(tid, []), "links": [],
        })
    return tasks


def js(obj):
    return json.dumps(obj, ensure_ascii=False)


def emit_output(lines):
    return "[" + ", ".join(f'L({js(l["type"])}, {js(l["text"])})' for l in lines) + "]"


def render(domains, themes, tasks, scenarios, questions, cheat, mock):
    P = []
    P.append("/* CCA Exam Prep Console — content model.")
    P.append("   AUTO-GENERATED by ui/console/build_data.py from the repo's demos + exam")
    P.append("   modules + the official task statements. Do not edit by hand; regenerate. */")
    P.append("(function () {")
    P.append("  const L = (type, text) => ({ type, text });")
    P.append("")
    P.append("  const domains = " + js(domains) + ";")
    P.append("  const themes = " + js(themes) + ";")
    P.append("")
    P.append("  const tasks = [")
    for t in tasks:
        head = {k: t[k] for k in ("id", "d", "title", "concept", "antipattern", "right",
                                  "tip", "analogy", "pitfall")}
        body = js(head)[:-1]  # drop closing brace to append output/q/links
        P.append("    " + body + ", " +
                 f'"output": {emit_output(t["output"])}, ' +
                 f'"q": {js(t["q"])}, "links": {js(t["links"])}' + "},")
    P.append("  ];")
    P.append("")
    P.append("  const scenarios = " + js(scenarios) + ";")
    P.append("  const questions = " + js(questions) + ";")
    P.append("  const cheat = " + js(cheat) + ";")
    P.append("  const mock = " + js(mock) + ";")
    P.append("")
    P.append("  window.CCA = { domains, themes, tasks, scenarios, questions, cheat, mock,")
    P.append("    taskById: Object.fromEntries(tasks.map((t) => [t.id, t])),")
    P.append("    questionById: Object.fromEntries(questions.map((q) => [q.id, q])),")
    P.append("    domainById: Object.fromEntries(domains.map((d) => [d.id, d])),")
    P.append("  };")
    P.append("})();")
    return "\n".join(P) + "\n"


def main():
    questions = build_questions()
    cheat = build_cheat()
    tasks = build_tasks(questions)
    mock = build_mock()
    out = render(DOMAINS, THEMES, tasks, SCENARIOS, questions, cheat, mock)
    dest = os.path.join(HERE, "assets", "data.js")
    open(dest, "w", encoding="utf-8").write(out)
    print(f"wrote {os.path.relpath(dest, REPO)}  ({len(out)//1024} KB)")
    print(f"tasks: {len(tasks)} · questions: {len(questions)} · mock: {len(mock)} · "
          f"cheat: {len(cheat)} · scenarios: {len(SCENARIOS)}")


if __name__ == "__main__":
    main()
