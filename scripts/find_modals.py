import re

with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

modals = re.findall(r'id=["\']([a-zA-Z0-9\-_]*modal[a-zA-Z0-9\-_]*)["\']', text, re.I)
print(sorted(list(set(modals))))
