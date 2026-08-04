with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace(
    "if (role === 'Colaborador' && activeModule === 'dashboard') {",
    "if (role === 'Colaborador' && (activeModule === 'dashboard' || activeModule === 'fichajes')) {"
)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(c)
print('Replaced!')
