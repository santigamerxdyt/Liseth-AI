with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'function speakText\b', text)]
for idx in matches:
    print(text[idx:idx+1200])
    print('='*50)
