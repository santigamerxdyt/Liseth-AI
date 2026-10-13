"""
Synchronizes root jarvis.html with app/static (index.html, style.css, app.js).
Creates a standalone, self-contained monolithic file so that opening jarvis.html
directly in any browser retains 100% of the futuristic features and dynamic window.
"""
from pathlib import Path
import re

BASE_DIR = Path(__file__).resolve().parent.parent
INDEX_HTML = BASE_DIR / "app" / "static" / "index.html"
STYLE_CSS = BASE_DIR / "app" / "static" / "css" / "style.css"
APP_JS = BASE_DIR / "app" / "static" / "js" / "app.js"
JARVIS_HTML = BASE_DIR / "jarvis.html"

index_content = INDEX_HTML.read_text(encoding="utf-8")
style_content = STYLE_CSS.read_text(encoding="utf-8")
js_content = APP_JS.read_text(encoding="utf-8")

# Inlining CSS
css_inlined = re.sub(
    r'<link rel="stylesheet" href="/static/css/style\.css[^"]*">',
    lambda _: f"<style>\n{style_content}\n</style>",
    index_content
)

# Inlining JS
monolithic = re.sub(
    r'<script src="/static/js/app\.js[^"]*"></script>',
    lambda _: f"<script>\n{js_content}\n</script>",
    css_inlined
)

JARVIS_HTML.write_text(monolithic, encoding="utf-8")
print(f"[OK] jarvis.html synchronized! Total size: {len(monolithic)} bytes.")
