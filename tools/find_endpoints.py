import re
from pathlib import Path

app_js = Path("app/static/js/app.js").read_text(encoding="utf-8")
matches = re.findall(r'fetch\([\'"`](/api/[^\'"`?]+)', app_js)
unique_endpoints = sorted(set(matches))
print(f"Total API endpoints called in app.js: {len(unique_endpoints)}")
for ep in unique_endpoints:
    print(" -", ep)
