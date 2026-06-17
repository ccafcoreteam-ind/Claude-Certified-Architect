#!/usr/bin/env python3
"""
ui/snapshot.py — render the whole UI into ONE self-contained, offline HTML file.

It pre-runs every demo, embeds the catalog/quiz/outputs as data, inlines the CSS and the
exact same app.js (via a tiny fetch shim that serves the embedded data), and writes a
single file you can open in any browser with no server running.

    python3 ui/snapshot.py                 # -> ui/snapshot.html
    python3 ui/snapshot.py /tmp/ccarch.html
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from ui import server  # noqa: E402  (reuse catalog/run/quiz logic)


def build(out_path: str) -> str:
    catalog = {"groups": server.CATALOG["groups"], "mode": server.CLIENT_MODE}
    quiz = server.QUIZ
    runs = {}
    for path in sorted(server.ALLOWED_PATHS):
        runs[path] = server.run_demo(path)

    data = {"catalog": catalog, "quiz": quiz, "runs": runs}
    data_json = json.dumps(data).replace("<", "\\u003c")  # keep </script> from breaking HTML

    css = open(os.path.join(HERE, "static", "style.css"), encoding="utf-8").read()
    app_js = open(os.path.join(HERE, "static", "app.js"), encoding="utf-8").read()
    html = open(os.path.join(HERE, "templates", "index.html"), encoding="utf-8").read()

    # offline fetch shim: serve the embedded data instead of hitting the server
    shim = (
        "const __DATA = JSON.parse(document.getElementById('snapshot-data').textContent);\n"
        "const __realFetch = window.fetch ? window.fetch.bind(window) : null;\n"
        "window.fetch = async (url, opts) => {\n"
        "  if (url === '/api/catalog') return { json: async () => __DATA.catalog };\n"
        "  if (url === '/api/quiz') return { json: async () => __DATA.quiz };\n"
        "  if (url === '/api/run') {\n"
        "    const b = JSON.parse((opts && opts.body) || '{}');\n"
        "    return { json: async () => (__DATA.runs[b.module] || {ok:false, output:'(no snapshot for this item)'}) };\n"
        "  }\n"
        "  return __realFetch ? __realFetch(url, opts) : { json: async () => ({}) };\n"
        "};\n"
    )

    # swap external assets for inlined ones
    html = html.replace('<link rel="stylesheet" href="/static/style.css" />',
                        f"<style>\n{css}\n</style>")
    banner = ('<div style="background:#1c2330;color:#8b97a6;border-bottom:1px solid #2a3441;'
              'padding:6px 20px;font:12px sans-serif">📸 Offline snapshot — every demo is '
              'pre-run and embedded; the quiz is fully interactive. Run the live server '
              '(<code>python3 run_all.py ui</code>) for live API mode.</div>')
    html = html.replace("<body>", "<body>\n" + banner)
    html = html.replace(
        '<script src="/static/app.js"></script>',
        f'<script type="application/json" id="snapshot-data">{data_json}</script>\n'
        f"<script>\n{shim}\n{app_js}\n</script>",
    )

    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(html)
    return out_path


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "snapshot.html")
    build(out)
    size = os.path.getsize(out)
    print(f"wrote {out}  ({size/1024:.0f} KB)")
    print(f"demos embedded: {len(server.ALLOWED_PATHS)} · quiz questions: {len(server.QUIZ)}")
    print("open it directly in a browser — no server needed.")


if __name__ == "__main__":
    main()
