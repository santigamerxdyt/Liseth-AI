"""
Frontend extractor for JARVIS / Liseth
Decouples monolithic jarvis.html into app/static/index.html, style.css, and app.js.
Preserves 100% of HTML structure, CSS rules, animations, and JS logic.
"""
import os
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
JARVIS_HTML = BASE_DIR / "jarvis.html"
STATIC_DIR = BASE_DIR / "app" / "static"
CSS_DIR = STATIC_DIR / "css"
JS_DIR = STATIC_DIR / "js"

CSS_DIR.mkdir(parents=True, exist_ok=True)
JS_DIR.mkdir(parents=True, exist_ok=True)

with open(JARVIS_HTML, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Locate boundaries
style_start = None
style_end = None
script_start = None
script_end = None

for idx, line in enumerate(lines):
    if "<style>" in line and style_start is None:
        style_start = idx
    elif "</style>" in line and style_end is None:
        style_end = idx
    elif "<script>" in line and script_start is None:
        script_start = idx
    elif "</script>" in line and script_end is None:
        script_end = idx

print(f"Style bounds: {style_start} to {style_end}")
print(f"Script bounds: {script_start} to {script_end}")

# Extract CSS
css_content = "".join(lines[style_start + 1:style_end])
with open(CSS_DIR / "style.css", "w", encoding="utf-8") as f:
    f.write(css_content)

# Extract JS
js_content = "".join(lines[script_start + 1:script_end])
with open(JS_DIR / "app.js", "w", encoding="utf-8") as f:
    f.write(js_content)

# Extract HTML
head_part = "".join(lines[0:style_start])
body_part = "".join(lines[style_end + 1:script_start])

index_html = (
    head_part
    + '  <link rel="stylesheet" href="/static/css/style.css">\n'
    + '  <link rel="manifest" href="/static/manifest.json">\n'
    + '  <meta name="theme-color" content="#04070d">\n'
    + body_part
    + '  <script src="/static/js/app.js"></script>\n'
    + '</body>\n'
    + '</html>\n'
)

with open(STATIC_DIR / "index.html", "w", encoding="utf-8") as f:
    f.write(index_html)

# Copy favicon
ico_source = BASE_DIR / "liseth.ico"
if ico_source.exists():
    shutil.copy(ico_source, STATIC_DIR / "liseth.ico")

print("Frontend successfully extracted into app/static/!")
