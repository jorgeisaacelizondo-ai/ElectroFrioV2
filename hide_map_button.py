
import re
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# find the block and remove it
pattern = r'<button class="nav-item role-admin-only" data-module="mapa"[^>]*>.*?<\/button>'
content = re.sub(pattern, '<!-- MAPA DESHABILITADO -->', content, flags=re.DOTALL)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Button removed')

