"""
SCENARIO 4 app — Developer Productivity codebase explorer (FUNCTIONAL)
=====================================================================
A genuinely working tool: it performs REAL Glob / Grep / Read / trace operations over a
target directory (defaults to this repo) — the built-in-tools workflow from Domain 2.5 in
action, not a scripted print.

Run:
  python3 scenarios/scenario4_developer_productivity/app.py            # scripted demo
  python3 scenarios/scenario4_developer_productivity/app.py -i         # interactive shell
  python3 scenarios/scenario4_developer_productivity/app.py -i /path/to/repo

Interactive commands:
  glob <pattern>     list files by NAME      e.g. glob **/*.py
  grep <pattern>     search file CONTENTS    e.g. grep def main
  read <relpath>     show a file's head + its exported names
  trace <symbol>     find where a symbol is defined, then who imports it
  help | quit
"""
import sys, os, re, pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from ccarch import banner, h1, h2, kv, note, rule, right, tip

SKIP = {".git", "__pycache__", "node_modules", ".venv"}


def _walk(root):
    for p in pathlib.Path(root).rglob("*"):
        if p.is_file() and not any(s in p.parts for s in SKIP):
            yield p


def do_glob(root, pattern):
    pattern = pattern or "**/*"
    hits = [str(p.relative_to(root)) for p in pathlib.Path(root).rglob(pattern)
            if p.is_file() and not any(s in p.parts for s in SKIP)]
    return sorted(hits)


def do_grep(root, pattern, max_hits=40):
    rx = re.compile(pattern)
    out = []
    for p in _walk(root):
        if p.suffix not in (".py", ".js", ".jsx", ".md", ".json", ".css", ".txt"):
            continue
        try:
            for i, line in enumerate(p.read_text(errors="ignore").splitlines(), 1):
                if rx.search(line):
                    out.append((str(p.relative_to(root)), i, line.strip()))
                    if len(out) >= max_hits:
                        return out
        except Exception:
            pass
    return out


def exported_names(text):
    names = re.findall(r"^(?:def|class)\s+(\w+)", text, re.M)
    names += re.findall(r"^(\w+)\s*=", text, re.M)
    return sorted(set(names))


def do_read(root, relpath, head=18):
    f = pathlib.Path(root) / relpath
    if not f.is_file():
        return None
    text = f.read_text(errors="ignore")
    return text.splitlines()[:head], exported_names(text)


def do_trace(root, symbol):
    """Incremental exploration: find the definition, then who references it."""
    defs = do_grep(root, rf"^(?:def|class)\s+{re.escape(symbol)}\b")
    refs = [h for h in do_grep(root, rf"\b{re.escape(symbol)}\b") if "def " not in h[2] and "class " not in h[2]]
    return defs, refs[:12]


# --------------------------------------------------------------------------- #
def interactive(root):
    banner("Scenario 4 — Codebase Explorer", f"target: {root}")
    note("Commands: glob <pat> · grep <pat> · read <relpath> · trace <symbol> · help · quit")
    while True:
        try:
            line = input("\nexplore> ").strip()
        except (EOFError, KeyboardInterrupt):
            print(); break
        if not line:
            continue
        cmd, _, arg = line.partition(" ")
        cmd = cmd.lower()
        if cmd in ("quit", "exit", "q"):
            break
        elif cmd == "help":
            note("glob <pattern> | grep <pattern> | read <relpath> | trace <symbol> | quit")
        elif cmd == "glob":
            hits = do_glob(root, arg.strip())
            kv("matched files", str(len(hits)))
            for h in hits[:40]:
                note("  " + h)
        elif cmd == "grep":
            hits = do_grep(root, arg.strip())
            kv("matches", str(len(hits)))
            for f, ln, txt in hits:
                note(f"  {f}:{ln}: {txt}")
        elif cmd == "read":
            res = do_read(root, arg.strip())
            if not res:
                note("  no such file"); continue
            headlines, names = res
            for l in headlines:
                note("  " + l)
            kv("exported names", ", ".join(names) or "(none)")
        elif cmd == "trace":
            defs, refs = do_trace(root, arg.strip())
            h2("definition(s)")
            for f, ln, txt in defs:
                right(f"{f}:{ln}: {txt}")
            h2(f"references ({len(refs)})")
            for f, ln, txt in refs:
                note(f"  {f}:{ln}: {txt}")
        else:
            note("  unknown command — type 'help'")


def demo(root):
    banner("Scenario 4 — Codebase Explorer (demo)", f"real Glob/Grep/Read over {root}")
    h1("Glob = file NAMES")
    py = do_glob(root, "**/*.py")
    kv("  **/*.py", f"{len(py)} files; first: {py[0] if py else '—'}")

    h1("Grep = file CONTENTS")
    hits = do_grep(root, r"def main\(")
    kv("  'def main('", f"{len(hits)} matches")
    for f, ln, txt in hits[:5]:
        note(f"    {f}:{ln}: {txt}")

    h1("Incremental exploration: trace a symbol")
    defs, refs = do_trace(root, "ClaudeClient")
    for f, ln, txt in defs[:1]:
        right(f"defined at {f}:{ln}")
    kv("  references found", str(len(refs)))
    for f, ln, txt in refs[:4]:
        note(f"    {f}:{ln}")

    rule()
    tip("Glob = names, Grep = contents. Find the entry point with Grep, then Read to follow "
        "the thread — never bulk-read. Run with -i to explore interactively.")


def main():
    args = [a for a in sys.argv[1:]]
    interactive_mode = any(a in ("-i", "--interactive") for a in args)
    paths = [a for a in args if not a.startswith("-")]
    root = os.path.abspath(paths[0]) if paths else str(pathlib.Path(__file__).resolve().parents[2])
    if interactive_mode and sys.stdin.isatty():
        interactive(root)
    else:
        demo(root)


if __name__ == "__main__":
    main()
