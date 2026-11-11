import re

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

print(f"Total size of index.html: {len(html)} characters, {html.count(chr(10))} lines")

# 1. Extract all onclick handlers
onclick_matches = re.findall(r'onclick=["\']([^"\']+)["\']', html)
print(f"Total onclick handlers found: {len(onclick_matches)}")

# Extract unique function calls from onclick
called_funcs = set()
for h in onclick_matches:
    # simple extraction of func name before (
    m = re.match(r'([a-zA-Z0-9_$]+)\s*\(', h.strip())
    if m:
        called_funcs.add(m.group(1))

print(f"Unique functions invoked via onclick: {len(called_funcs)}")

# Check which ones are defined
missing_funcs = []
for fn in sorted(list(called_funcs)):
    # check if defined as function fn, var fn =, window.fn =, fn =
    pattern = rf'(?:function\s+{re.escape(fn)}\b|window\.{re.escape(fn)}\s*=|const\s+{re.escape(fn)}\s*=|let\s+{re.escape(fn)}\s*=|var\s+{re.escape(fn)}\s*=|{re.escape(fn)}\s*=\s*function)'
    if not re.search(pattern, html):
        missing_funcs.append(fn)

print("\n--- AUDIT 1: Missing onclick functions ---")
if missing_funcs:
    for mf in missing_funcs:
        print(f"  [MISSING/UNDEFINED ONCLICK]: {mf}")
else:
    print("  [PASS] All onclick functions are defined!")

# 2. Extract all document.getElementById calls
get_id_matches = re.findall(r'document\.getElementById\(["\']([^"\']+)["\']\)', html)
print(f"\nTotal document.getElementById calls: {len(get_id_matches)}")
unique_ids = set(get_id_matches)

missing_ids = []
for dom_id in sorted(list(unique_ids)):
    # Check if id="..." exists in html
    id_pattern = rf'id=["\']{re.escape(dom_id)}["\']'
    if not re.search(id_pattern, html):
        missing_ids.append(dom_id)

print("\n--- AUDIT 2: document.getElementById targeting missing DOM elements ---")
if missing_ids:
    for mid in missing_ids:
        print(f"  [MISSING DOM ID]: {mid}")
else:
    print("  [PASS] All referenced DOM IDs exist in HTML!")

# 3. Check for syntax error indicators in script
script_blocks = re.findall(r'<script(?:\s+[^>]*)?>([\s\S]*?)</script>', html)
print(f"\nTotal script blocks: {len(script_blocks)}")

# 4. Check for duplicate IDs in DOM
from collections import Counter
all_dom_ids = re.findall(r'id=["\']([^"\']+)["\']', html)
id_counts = Counter(all_dom_ids)
dups = {k: v for k, v in id_counts.items() if v > 1}
print(f"\n--- AUDIT 3: Duplicate IDs in HTML ---")
if dups:
    for k, v in dups.items():
        print(f"  [DUPLICATE ID ({v}x)]: {k}")
else:
    print("  [PASS] Zero duplicate IDs in HTML!")

