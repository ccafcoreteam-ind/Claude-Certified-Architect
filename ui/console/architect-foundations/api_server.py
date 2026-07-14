#!/usr/bin/env python3
"""
CCA Exam Prep Console — local API + static server (zero dependencies).

Serves the console UI *and* runs your repo's real demo files when a "Run"
button is clicked, returning their actual stdout as JSON. This makes the
console show the full output (boxed sections, code examples, the real
titles) instead of the simulated summaries.

HOW IT WORKS
  GET /api/run?task=2.4      -> globs domains/**/task2_4_*.py, runs it with
                                CCARCH_NONSTOP=1 (same as run_all.py),
                                strips ANSI, classifies lines, returns JSON.
  GET /api/run?scenario=1    -> runs scenarios/**/scenario1_*.py
  GET /api/manifest          -> lists the task ids it can find in your repo
  everything else            -> static files from this folder (index.html, assets/)

SETUP
  1. Copy index.html, the assets/ folder, and this file into your
     Claude-Certified-Architect checkout (repo root, or inside ui/).
  2. Run it:
         python3 api_server.py                 # http://127.0.0.1:8000
         python3 api_server.py --port 9000 --host 0.0.0.0
  3. Open the printed URL. Click Run on any task -> real demo output.

It auto-detects the repo root by walking up to the folder that contains
`domains/`. To run the live (API-calling) demos, export ANTHROPIC_API_KEY
before launching; it is inherited by the demo subprocess.
"""
import argparse, glob, json, os, re, subprocess, sys, urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ANSI = re.compile(r"\x1b\[[0-9;]*m")
HERE = os.path.dirname(os.path.abspath(__file__))


def find_repo_root(start):
    d = start
    for _ in range(8):
        if os.path.isdir(os.path.join(d, "domains")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    return start


REPO_ROOT = find_repo_root(HERE)


def classify(s):
    """Map a raw output line to the console's line types."""
    if any(c in s for c in ("✗", "✕", "❌")):
        return {"type": "bad", "text": s}
    if any(c in s for c in ("✓", "✔", "✅")):
        return {"type": "good", "text": s}
    if any(c in s for c in ("★", "☆", "⭐")):
        return {"type": "tip", "text": s}
    st = s.lstrip()
    if st.startswith("$ ") or st.startswith("python3 "):
        return {"type": "cmd", "text": s}
    if st.startswith("#") or st.startswith("//"):
        return {"type": "dim", "text": s}
    return {"type": "info", "text": s}


def resolve_task(task):
    maj, _, minr = task.partition(".")
    pat = "task{}_{}_*.py".format(maj, minr)
    hits = sorted(glob.glob(os.path.join(REPO_ROOT, "domains", "**", pat), recursive=True))
    return hits[0] if hits else None


def resolve_scenario(num):
    for pat in ("scenario{}_*.py".format(num), "scenario_{}_*.py".format(num), "*scenario*{}*.py".format(num)):
        hits = sorted(glob.glob(os.path.join(REPO_ROOT, "scenarios", "**", pat), recursive=True))
        if hits:
            return hits[0]
    return None


def run_file(path):
    env = dict(os.environ)
    env["CCARCH_NONSTOP"] = "1"
    env["PYTHONUNBUFFERED"] = "1"
    try:
        p = subprocess.run([sys.executable, path], cwd=REPO_ROOT, env=env,
                           capture_output=True, text=True, timeout=60)
        out = (p.stdout or "") + (p.stderr or "")
    except subprocess.TimeoutExpired:
        out = "✗ demo timed out after 60s"
    except Exception as e:  # noqa
        out = "✗ failed to run: {}".format(e)
    out = ANSI.sub("", out)
    lines = [classify(l) for l in out.split("\n")]
    while lines and not lines[-1]["text"].strip():
        lines.pop()
    return lines


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="application/json"):
        b = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(u.query)
        if u.path == "/api/run":
            task = (q.get("task") or [None])[0]
            scen = (q.get("scenario") or [None])[0]
            path = resolve_task(task) if task else (resolve_scenario(scen) if scen else None)
            if not path:
                return self._send(404, json.dumps({"ok": False, "error": "demo not found", "lines": []}))
            rel = os.path.relpath(path, REPO_ROOT)
            lines = [{"type": "cmd", "text": "$ python3 {}".format(rel)}] + run_file(path)
            return self._send(200, json.dumps({"ok": True, "file": rel, "lines": lines}))
        if u.path == "/api/manifest":
            files = sorted(glob.glob(os.path.join(REPO_ROOT, "domains", "**", "task*_*.py"), recursive=True))
            ids = []
            for f in files:
                m = re.search(r"task(\d+)_(\d+)_", os.path.basename(f))
                if m:
                    ids.append("{}.{}".format(m.group(1), m.group(2)))
            return self._send(200, json.dumps({"ok": True, "repoRoot": REPO_ROOT, "tasks": ids}))
        return self.serve_static(u.path)

    def serve_static(self, path):
        if path in ("/", ""):
            path = "/index.html"
        path = urllib.parse.unquote(path)
        full = os.path.normpath(os.path.join(HERE, path.lstrip("/")))
        if not full.startswith(HERE) or not os.path.isfile(full):
            return self._send(404, "Not found", "text/plain")
        ext = os.path.splitext(full)[1].lower()
        ctype = {".html": "text/html", ".js": "text/javascript", ".jsx": "text/babel",
                 ".css": "text/css", ".json": "application/json", ".svg": "image/svg+xml",
                 ".png": "image/png", ".ico": "image/x-icon"}.get(ext, "application/octet-stream")
        with open(full, "rb") as fh:
            self._send(200, fh.read(), ctype)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8000)
    a = ap.parse_args()
    print("CCA console  ->  http://{}:{}".format(a.host, a.port))
    print("repo root    ->  {}".format(REPO_ROOT))
    if not os.path.isdir(os.path.join(REPO_ROOT, "domains")):
        print("WARNING: domains/ not found next to or above this file.")
        print("         Put api_server.py inside your repo so Run can find the demos.")
    ThreadingHTTPServer((a.host, a.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
