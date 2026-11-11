with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'function handleSend\b|const handleSend\b|handleSend =', text)]
for idx in matches:
    print(text[idx:idx+800])
    print('='*50)
