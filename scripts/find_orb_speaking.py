with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = re.findall(r'setOrbSpeaking', text)
print(f'Count of setOrbSpeaking: {len(matches)}')
matches_def = re.findall(r'function setOrbSpeaking|setOrbSpeaking\s*=', text)
print(f'Definitions of setOrbSpeaking: {matches_def}')
