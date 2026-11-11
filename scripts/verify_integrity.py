import sys

with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

checks = [
    'hud-sidebar-nav',
    'ai-core-orb-canvas',
    'hud-top-bar',
    'hud-context-inspector',
    'agent-hub-modal',
    'initAICoreOrbEngine',
    'window.setOrbState',
    'window.activateAgentPersona'
]

for c in checks:
    if c not in text:
        print(f'FAIL: {c} not found in index.html')
        sys.exit(1)
    print(f'PASS: {c} found')

print('All 8 core components successfully verified!')
