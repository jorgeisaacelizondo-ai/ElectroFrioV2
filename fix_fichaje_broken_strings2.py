
import re
with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

c = re.sub(r'Entrada registrada a las\s*;', r'Entrada registrada a las ;', c)
c = re.sub(r'\?\s*Salida registrada hoy a las\s*', r'? Salida registrada hoy a las ', c)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(c)
print('Done string fix 2')

