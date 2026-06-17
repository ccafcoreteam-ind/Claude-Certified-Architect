#!/usr/bin/env python3
"""
ui/server.py — a zero-dependency web UI for the teaching codebase.

Uses only the Python standard library (http.server), so it runs anywhere Python 3 does —
no pip install, consistent with the rest of this repo. It:

  * lists every runnable demo (domains, scenarios, exam) in a sidebar,
  * runs a demo on demand and streams its captured output to the browser,
  * renders the ✗/✓/★ teaching blocks as styled cards,
  * serves the 12 sample questions as an interactive, self-grading quiz.

Run:
    python3 ui/server.py            # then open http://127.0.0.1:8000
    python3 ui/server.py --port 9000
    python3 run_all.py ui           # convenience wrapper (also opens nothing, prints URL)

Live model mode: if ANTHROPIC_API_KEY is set in the server's environment, the
model-calling demos hit the real Claude API; otherwise they run simulated. Either way the
teaching content is identical.
"""

from __future__ import annotations

import ast
import contextlib
import glob
import io
import json
import os
import runpy
import sys
import threading
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UI_DIR = os.path.join(ROOT, "ui")
sys.path.insert(0, ROOT)

# Serialize demo runs: they capture stdout process-wide, so one at a time.
_RUN_LOCK = threading.Lock()


# --------------------------------------------------------------------------- #
# Catalog: discover every runnable file and describe it (without executing it).
# --------------------------------------------------------------------------- #
def _docstring_summary(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as fh:
            tree = ast.parse(fh.read())
        doc = ast.get_docstring(tree) or ""
    except Exception:
        return ""
    for line in doc.splitlines():
        s = line.strip()
        if s and not set(s) <= set("=-"):
            return s
    return ""


def _title_from_filename(path: str) -> str:
    base = os.path.splitext(os.path.basename(path))[0]
    parts = base.split("_")
    # task1_4_workflow_enforcement -> "Task 1.4 — Workflow Enforcement"
    if parts and parts[0].startswith("task") and len(parts) >= 2:
        num = parts[0][4:]
        sub = parts[1]
        words = " ".join(w.capitalize() for w in parts[2:])
        return f"Task {num}.{sub} — {words}"
    return base.replace("_", " ").title()


def build_catalog() -> dict:
    groups = []

    domain_labels = {
        "domain1": "Domain 1 · Agentic Architecture & Orchestration (27%)",
        "domain2": "Domain 2 · Tool Design & MCP Integration (18%)",
        "domain3": "Domain 3 · Claude Code Configuration & Workflows (20%)",
        "domain4": "Domain 4 · Prompt Engineering & Structured Output (20%)",
        "domain5": "Domain 5 · Context Management & Reliability (15%)",
    }
    for d in sorted(glob.glob(os.path.join(ROOT, "domains", "domain*"))):
        key = os.path.basename(d).split("_")[0]
        items = []
        for f in sorted(glob.glob(os.path.join(d, "task*.py"))):
            rel = os.path.relpath(f, ROOT)
            items.append({"path": rel, "title": _title_from_filename(f),
                          "summary": _docstring_summary(f)})
        groups.append({"id": key, "kind": "domain",
                       "label": domain_labels.get(key, key), "items": items})

    scenario_titles = {
        "scenario1": "Scenario 1 · Customer Support Resolution Agent",
        "scenario2": "Scenario 2 · Code Generation with Claude Code",
        "scenario3": "Scenario 3 · Multi-Agent Research System",
        "scenario4": "Scenario 4 · Developer Productivity",
        "scenario5": "Scenario 5 · Claude Code for CI/CD",
        "scenario6": "Scenario 6 · Structured Data Extraction",
    }
    scen_items = []
    for d in sorted(glob.glob(os.path.join(ROOT, "scenarios", "scenario*"))):
        key = os.path.basename(d).split("_")[0]
        for f in sorted(glob.glob(os.path.join(d, "*.py"))):
            rel = os.path.relpath(f, ROOT)
            scen_items.append({"path": rel, "title": scenario_titles.get(key, key),
                               "summary": _docstring_summary(f)})
    groups.append({"id": "scenarios", "kind": "scenario",
                   "label": "The 6 Exam Scenarios", "items": scen_items})

    exam_items = []
    for name, title in [("cheatsheet.py", "Cheat Sheet — facts to memorize"),
                        ("prep_exercises.py", "The 3 Prep Exercises"),
                        ("sample_questions.py", "12 Sample Questions (printed)")]:
        f = os.path.join(ROOT, "exam", name)
        if os.path.exists(f):
            exam_items.append({"path": os.path.relpath(f, ROOT), "title": title,
                               "summary": _docstring_summary(f)})
    groups.append({"id": "exam", "kind": "exam", "label": "Exam Practice",
                   "items": exam_items})

    # whitelist of runnable paths
    allowed = {it["path"] for g in groups for it in g["items"]}
    return {"groups": groups, "allowed": sorted(allowed)}


CATALOG = build_catalog()
ALLOWED_PATHS = set(CATALOG["allowed"])


# --------------------------------------------------------------------------- #
# Run a demo and capture its stdout.
# --------------------------------------------------------------------------- #
def run_demo(rel_path: str) -> dict:
    if rel_path not in ALLOWED_PATHS:
        return {"ok": False, "output": f"Refused: {rel_path!r} is not in the catalog."}
    abspath = os.path.join(ROOT, rel_path)
    buf = io.StringIO()
    old_argv = sys.argv
    old_env = os.environ.get("CCARCH_NONSTOP"), os.environ.get("NO_COLOR")
    with _RUN_LOCK:
        os.environ["CCARCH_NONSTOP"] = "1"   # never block on pause()
        os.environ["NO_COLOR"] = "1"         # plain text; the browser adds styling
        sys.argv = [abspath]
        try:
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                runpy.run_path(abspath, run_name="__main__")
            ok = True
        except Exception as exc:  # noqa: BLE001
            buf.write(f"\n[demo raised: {type(exc).__name__}: {exc}]")
            ok = False
        finally:
            sys.argv = old_argv
            for k, v in zip(("CCARCH_NONSTOP", "NO_COLOR"), old_env):
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v
    return {"ok": ok, "output": buf.getvalue()}


def quiz_data() -> list:
    """Pull the structured questions from exam/sample_questions.py without running main()."""
    mod_path = os.path.join(ROOT, "exam", "sample_questions.py")
    ns: dict = {}
    with open(mod_path, "r", encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    # find the QUESTIONS assignment and eval just that literal-ish structure safely
    for node in tree.body:
        if isinstance(node, ast.Assign):
            targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
            if "QUESTIONS" in targets:
                # QUESTIONS is built from dict()/list/str literals -> safe to compile+exec
                code = compile(ast.Module(body=[node], type_ignores=[]),
                               mod_path, "exec")
                exec(code, ns)  # noqa: S102 - trusted local source file
                return ns.get("QUESTIONS", [])
    return []


QUIZ = quiz_data()
CLIENT_MODE = "live" if os.environ.get("ANTHROPIC_API_KEY") else "simulated"


# --------------------------------------------------------------------------- #
# HTTP handler
# --------------------------------------------------------------------------- #
class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        if isinstance(body, (dict, list)):
            body = json.dumps(body)
        data = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _serve_file(self, path, ctype):
        try:
            with open(path, "rb") as fh:
                self._send(200, fh.read(), ctype)
        except FileNotFoundError:
            self._send(404, "not found", "text/plain")

    def do_GET(self):  # noqa: N802
        route = urlparse(self.path).path
        if route in ("/", "/index.html"):
            return self._serve_file(os.path.join(UI_DIR, "templates", "index.html"),
                                    "text/html; charset=utf-8")
        if route == "/static/style.css":
            return self._serve_file(os.path.join(UI_DIR, "static", "style.css"),
                                    "text/css")
        if route == "/static/app.js":
            return self._serve_file(os.path.join(UI_DIR, "static", "app.js"),
                                    "application/javascript")
        if route == "/api/catalog":
            return self._send(200, {"groups": CATALOG["groups"], "mode": CLIENT_MODE})
        if route == "/api/quiz":
            return self._send(200, QUIZ)
        return self._send(404, {"error": "not found"})

    def do_POST(self):  # noqa: N802
        route = urlparse(self.path).path
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw or b"{}")
        except json.JSONDecodeError:
            return self._send(400, {"error": "bad json"})
        if route == "/api/run":
            return self._send(200, run_demo(payload.get("module", "")))
        return self._send(404, {"error": "not found"})

    def log_message(self, *args):  # quiet the default console spam
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--host", default="127.0.0.1")
    args = ap.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    url = f"http://{args.host}:{args.port}"
    print("=" * 70)
    print("  Claude Certified Architect — teaching UI")
    print(f"  Open:  {url}")
    print(f"  Mode:  {CLIENT_MODE}  (set ANTHROPIC_API_KEY for live model calls)")
    print(f"  Demos: {len(ALLOWED_PATHS)} runnable · Quiz: {len(QUIZ)} questions")
    print("  Ctrl+C to stop.")
    print("=" * 70)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped.")


if __name__ == "__main__":
    main()
