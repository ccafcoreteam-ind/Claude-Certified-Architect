"""
SCENARIO 4 — Developer Productivity with Claude  (Agent SDK)
============================================================
An assistant that helps engineers explore unfamiliar codebases and legacy systems using
the built-in tools (Read, Write, Bash, Grep, Glob) plus MCP servers. Demonstrates the
concepts the exam attaches to this scenario: D2 Tools/MCP, D3 Claude Code Config, D1
Orchestration.

This demo runs a REAL incremental exploration over a tiny sample codebase it creates in a
temp dir — so you can watch Grep-find-entry-point → Read-follow-imports in action, the
right way (incremental) vs the wrong way (bulk read).

In ONE program:
  * Grep = CONTENTS vs Glob = NAMES (D2 T2.5)
  * incremental exploration beats bulk reading (D2 T2.5)
  * delegate verbose investigation to a subagent; only a summary returns (D5 T5.4 / D1)
  * scratchpad file as external memory (D5 T5.4)
"""

import sys, pathlib, tempfile, os, re
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from ccarch import banner, concept, h1, h2, wrong, right, tip, note, kv, code, rule, pause, analogy, pitfall


SAMPLE = {
    "app/main.py": "from app.refund import process_refund\n\ndef handler(req):\n    return process_refund(req['order'], req['amount'])\n",
    "app/refund.py": "from app.ledger import append\n\ndef process_refund(order, amount):\n    append(order, -amount)\n    return {'ok': True}\n",
    "app/ledger.py": "def append(order, delta):\n    pass  # writes to the ledger\n",
    "app/utils.py": "def unrelated_helper():\n    return 42\n",
    "tests/test_refund.py": "def test_refund():\n    assert True\n",
}


def build_sample(root):
    for rel, content in SAMPLE.items():
        p = pathlib.Path(root) / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)


def glob_names(root, pattern):
    return [str(p.relative_to(root)) for p in pathlib.Path(root).rglob(pattern)]


def grep_contents(root, term):
    hits = []
    for p in pathlib.Path(root).rglob("*.py"):
        for i, line in enumerate(p.read_text().splitlines(), 1):
            if term in line:
                hits.append((str(p.relative_to(root)), i, line.strip()))
    return hits


def read_imports(root, relpath):
    text = (pathlib.Path(root) / relpath).read_text()
    return re.findall(r"from ([\w.]+) import (\w+)", text)


def main():
    banner("Scenario 4", "Developer Productivity — D2 · D3 · D1")
    concept("Scenario 4: Developer Productivity with Claude",
            "Built-in tools (Read/Write/Bash/Grep/Glob) + MCP, on a real sample repo",
            "Incremental exploration, not bulk reading")

    with tempfile.TemporaryDirectory() as root:
        build_sample(root)
        kv("sample repo", root)

        h1("Glob = file NAMES (which files exist)")
        kv("  Glob('**/*.py')", glob_names(root, "*.py"))
        kv("  Glob('**/test_*.py')", glob_names(root, "test_*.py"))

        pause("Grep")
        h1("Grep = file CONTENTS (find the entry point)")
        for f, ln, txt in grep_contents(root, "process_refund"):
            kv(f"  {f}:{ln}", txt)
        right("Grep located every reference to process_refund — that's CONTENT search, the "
              "thing Glob cannot do.")

        pause("incremental exploration")
        h1("Incremental exploration: Read to follow the imports")
        chain, current = ["app/main.py"], "app/main.py"
        for _ in range(3):
            imports = read_imports(root, current)
            if not imports:
                break
            module, name = imports[0]
            nxt = module.replace(".", "/") + ".py"
            kv(f"  {current}", f"imports {name} from {nxt}")
            chain.append(nxt)
            current = nxt
        kv("  dependency chain", " → ".join(chain))
        wrong("Reading ALL files upfront (including utils.py, tests) wastes context.")
        right("Grep for the entry point, then Read to follow only the relevant thread "
              "(main → refund → ledger). utils.py never needed loading.")

        pause("delegate + scratchpad")
        h1("Delegate verbose work to a subagent; persist a scratchpad (D5 T5.4)")
        summary = "refund flow: app/main.handler → app/refund.process_refund → app/ledger.append"
        scratch = pathlib.Path(root) / "findings.md"
        scratch.write_text(summary + "\n")
        kv("  subagent returns (summary only)", summary)
        kv("  findings.md (external memory)", scratch.read_text().strip())
        right("A subagent does the noisy tracing; only the SUMMARY returns to the main "
              "agent, and the scratchpad survives context pressure.")

    rule()
    h1("Plain-language analogy & the common confusion")
    analogy('Dropped into a 10-year-old codebase with no map, you do not read every file — you find the front door (Grep for an entry point) and follow the hallways (Read the imports), taking notes as you go.')
    pitfall("The wasteful instinct is to bulk-read everything 'to understand it' — that blows the context budget. Search for entry points first, then follow only the threads that matter, and let subagents do the noisy digging.")

    tip("Grep=CONTENTS, Glob=NAMES. Explore incrementally (Grep→Read), never bulk-read. "
        "Delegate verbose investigations so only summaries return. That's D2 + D3 + D1.")


if __name__ == "__main__":
    main()
