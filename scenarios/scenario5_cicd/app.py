"""
SCENARIO 5 app — CI/CD automated review (FUNCTIONAL)
====================================================
A real, basic static reviewer: it reads actual Python file(s), applies EXPLICIT criteria
(Domain 4.1), emits STRUCTURED findings (Domain 4.3), runs PER-FILE + a cross-file
INTEGRATION pass (Domain 4.6), and prints machine-readable JSON like a `-p` CI run would.

Run:
  python3 scenarios/scenario5_cicd/app.py                      # scripted demo (sample code)
  python3 scenarios/scenario5_cicd/app.py path/to/file.py      # review a real file
  python3 scenarios/scenario5_cicd/app.py a.py b.py --json     # JSON only (CI mode)
  python3 scenarios/scenario5_cicd/app.py --all path/to/file   # include style findings
"""
import sys, os, re, json, tempfile, pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from ccarch import banner, h1, h2, kv, note, rule, wrong, right, tip, code

# Explicit criteria: (regex, category, severity, message). bug/security reported by
# default; style only with --all (false-positive control).
RULES = [
    (r"\beval\s*\(", "security", "critical", "eval() on dynamic input enables code execution"),
    (r"\bexec\s*\(", "security", "critical", "exec() executes arbitrary code"),
    (r"except\s*:", "bug", "high", "bare 'except:' swallows every error, incl. KeyboardInterrupt"),
    (r"==\s*None\b", "bug", "low", "use 'is None', not '== None'"),
    (r"!=\s*None\b", "bug", "low", "use 'is not None', not '!= None'"),
    (r"\b(password|secret|api_key|token)\s*=\s*[\"'][^\"']+[\"']", "security", "high",
     "hard-coded credential — use an environment variable"),
    (r"#\s*(TODO|FIXME)", "style", "low", "unresolved TODO/FIXME"),
    (r"\bprint\s*\(", "style", "low", "stray print() — use logging in library code"),
]
DEFAULT_CATS = {"bug", "security"}


def review_file(path, include_style=False):
    findings = []
    try:
        lines = pathlib.Path(path).read_text(errors="ignore").splitlines()
    except Exception as e:
        return [{"file": path, "line": 0, "severity": "high", "category": "bug",
                 "issue": f"could not read file: {e}", "confidence": 1.0}]
    for i, line in enumerate(lines, 1):
        if line.lstrip().startswith("#") and "TODO" not in line and "FIXME" not in line:
            continue  # skip comment lines except TODO/FIXME
        for rx, cat, sev, msg in RULES:
            if cat not in DEFAULT_CATS and not include_style:
                continue
            if re.search(rx, line):
                findings.append({"file": os.path.basename(path), "line": i, "severity": sev,
                                 "category": cat, "issue": msg, "confidence": 0.9})
    return findings


def integration_pass(paths):
    """Cross-file check: a function name defined in more than one file (possible dup)."""
    seen, dupes = {}, []
    for p in paths:
        try:
            for i, line in enumerate(pathlib.Path(p).read_text(errors="ignore").splitlines(), 1):
                m = re.match(r"\s*def\s+(\w+)", line)
                if m:
                    seen.setdefault(m.group(1), []).append((os.path.basename(p), i))
        except Exception:
            pass
    for name, locs in seen.items():
        files = {f for f, _ in locs}
        if len(files) > 1 and not name.startswith("_") and name not in ("main",):
            dupes.append({"category": "integration", "severity": "low",
                          "issue": f"function '{name}' defined in {len(files)} files",
                          "locations": locs, "confidence": 0.6})
    return dupes


SAMPLE = '''\
import os
password = "hunter2"          # planted: hard-coded secret

def parse(data):
    try:
        return eval(data)      # planted: eval on input
    except:                    # planted: bare except
        print("bad")           # planted: stray print

def is_ready(x):
    return x == None           # planted: == None
# TODO: handle empty input     # planted: TODO
'''


def render(per_file, integration, as_json):
    if as_json:
        print(json.dumps({"findings": [f for fs in per_file.values() for f in fs],
                          "integration": integration}, indent=2))
        return
    total = 0
    for path, findings in per_file.items():
        h2(f"{os.path.basename(path)} — {len(findings)} finding(s)")
        for f in sorted(findings, key=lambda x: x["line"]):
            total += 1
            label = right if f["severity"] == "low" else wrong
            label(f"L{f['line']} [{f['severity']}/{f['category']}] {f['issue']}")
    if integration:
        h2("cross-file integration pass")
        for f in integration:
            note(f"  [{f['severity']}/integration] {f['issue']}  @ {f['locations']}")
    kv("\ntotal findings", str(total + len(integration)))


def main():
    args = sys.argv[1:]
    as_json = "--json" in args
    include_style = "--all" in args
    paths = [a for a in args if not a.startswith("-")]

    if not paths:
        # scripted demo on a planted sample file
        tmp = pathlib.Path(tempfile.mkdtemp()) / "payments.py"
        tmp.write_text(SAMPLE)
        paths = [str(tmp)]
        if not as_json:
            banner("Scenario 5 — CI/CD Review (demo)", "reviewing a planted sample file")
            h1("The file under review")
            code(SAMPLE.rstrip(), "payments.py")
            h1("Findings (explicit criteria; bug/security by default)")
    elif not as_json:
        banner("Scenario 5 — CI/CD Review", f"reviewing {len(paths)} file(s)")

    per_file = {p: review_file(p, include_style) for p in paths}
    integration = integration_pass(paths) if len(paths) > 1 else []
    render(per_file, integration, as_json)

    if not as_json:
        rule()
        tip("Explicit criteria + severities keep false positives low; bug/security report "
            "by default, style only with --all. Per-file + integration passes avoid "
            "attention dilution. Add --json for the machine-parseable CI output (claude -p).")


if __name__ == "__main__":
    main()
