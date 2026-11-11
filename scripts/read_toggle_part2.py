with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(15815, 15855):
    if i < len(lines):
        print(f'{i+1}: {lines[i]}', end='')
