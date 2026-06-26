#!/usr/bin/env python3
"""
ui/console/snapshot.py — render the React Exam Prep Console into ONE offline HTML file.

It pre-runs every task demo (via the same logic api_server.py uses), inlines the CSS and
all the assets, and embeds a fetch shim so the live "Run demo" path returns the REAL
boxed output with no server running. Open the result by double-clicking it.

    python3 ui/console/snapshot.py                 # -> ui/console/console_snapshot.html
    python3 ui/console/snapshot.py /tmp/cca.html

Note: React + Babel still load from a CDN (as the bundle was authored), so the file needs
internet access the first time you open it. Everything else is self-contained.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import api_server  # noqa: E402  (reuse resolve_task / run_file / classify)


def collect_task_outputs() -> dict:
    """task id ('2.4') -> {ok, file, lines:[{type,text}]} using the real demo stdout."""
    out = {}
    files = sorted(__import__("glob").glob(
        os.path.join(api_server.REPO_ROOT, "domains", "**", "task*_*.py"), recursive=True))
    for f in files:
        m = re.search(r"task(\d+)_(\d+)_", os.path.basename(f))
        if not m:
            continue
        tid = f"{m.group(1)}.{m.group(2)}"
        rel = os.path.relpath(f, api_server.REPO_ROOT)
        lines = [{"type": "cmd", "text": f"$ python3 {rel}"}] + api_server.run_file(f)
        out[tid] = {"ok": True, "file": rel, "lines": lines}
    return out


def _safe(js_text: str) -> str:
    # never let an embedded </script> end the inline script tag
    return js_text.replace("</script", "<\\/script")


def build(out_path: str) -> str:
    runs = collect_task_outputs()
    runs_json = _safe(json.dumps(runs))

    read = lambda p: open(os.path.join(HERE, p), encoding="utf-8").read()
    css = read("assets/styles.css")
    config_js = read("assets/config.js")
    data_js = read("assets/data.js")
    app_jsx = read("assets/app.jsx")
    html = read("index.html")

    shim = (
        "<script>\n"
        "// Offline shim: serve pre-run demo output embedded in this file.\n"
        f"window.__RUNS = JSON.parse({json.dumps(runs_json)});\n"
        "const __realFetch = window.fetch ? window.fetch.bind(window) : null;\n"
        "window.fetch = async (url, opts) => {\n"
        "  try {\n"
        "    const u = String(url);\n"
        "    const m = u.match(/[?&]task=([^&]+)/);\n"
        "    if (u.indexOf('/api/run') !== -1 && m) {\n"
        "      const id = decodeURIComponent(m[1]);\n"
        "      const data = window.__RUNS[id] || { ok:false, lines:[] };\n"
        "      return { ok:true, json: async () => data };\n"
        "    }\n"
        "  } catch (e) {}\n"
        "  if (__realFetch) return __realFetch(url, opts);\n"
        "  return { ok:false, json: async () => ({}) };\n"
        "};\n"
        "</script>\n"
    )

    # inline the stylesheet
    html = html.replace('<link rel="stylesheet" href="assets/styles.css" />',
                        f"<style>\n{css}\n</style>")
    # inline config + data + app, and drop the external <script src=...> tags
    html = html.replace('<script src="assets/config.js"></script>',
                        shim + f"<script>\n{_safe(config_js)}\n</script>")
    html = html.replace('<script src="assets/data.js"></script>',
                        f"<script>\n{_safe(data_js)}\n</script>")
    html = html.replace('<script type="text/babel" src="assets/app.jsx"></script>',
                        f'<script type="text/babel">\n{_safe(app_jsx)}\n</script>')

    banner = ('<div style="background:#1c2330;color:#9aa6b4;'
              'padding:6px 16px;font:12px system-ui;border-bottom:1px solid #2a3441">'
              '📸 Offline snapshot — click <b>Run demo</b> on any task for the real output. '
              '(Needs internet once to load React/Babel from CDN.)</div>')
    html = html.replace("<body>", "<body>\n" + banner)

    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(html)
    return out_path


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "console_snapshot.html")
    build(out)
    print(f"wrote {out}  ({os.path.getsize(out)/1024:.0f} KB)")
    print(f"repo root: {api_server.REPO_ROOT}")
    print("open it directly in a browser (internet needed once for the React/Babel CDN).")


if __name__ == "__main__":
    main()
