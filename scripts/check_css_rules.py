with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

keywords = ['header-top', 'sphere-workspace', 'console-workspace', 'holographic-main-stage']
for kw in keywords:
    pos = 0
    print(f'=== KEYWORD: {kw} ===')
    count = 0
    while True:
        pos = text.find(kw, pos)
        if pos == -1 or count >= 3:
            break
        print(text[max(0, pos-40):min(len(text), pos+100)])
        print('---')
        pos += len(kw)
        count += 1
