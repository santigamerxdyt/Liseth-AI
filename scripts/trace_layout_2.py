with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(8230, 8600):
    line = lines[i]
    if any(tag in line for tag in ['<div class="', '<main', '</main', '<section', '</section', '<footer', '</header', 'chat-container', 'input-container', 'holographic-main-stage']):
        print(f'{i+1}: {line.strip()[:100]}')
