with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 7840 <= i <= 8300:
        if any(tag in line for tag in ['<div class="hud-', '<header', '<div class="header', '<div class="holographic', 'ai-core-orb', '<main', '<div class="chat-', 'executive-ticker', 'sphere-workspace', 'stark-hud-wing']):
            print(f'{i+1}: {line.strip()[:100]}')
