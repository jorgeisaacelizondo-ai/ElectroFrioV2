
import re
with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

pattern = re.compile(r'\s*;\s*// 1\. Agregar y guardar localmente al instante.*?\}\)\(\);\s*\}\);\s*\}\);\s*\}\s*', re.DOTALL)
new_c = pattern.sub('\n\n', c)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(new_c)
print('Replaced successfully:', c != new_c)

