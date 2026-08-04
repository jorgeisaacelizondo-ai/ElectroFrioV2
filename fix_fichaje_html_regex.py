
import re
with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

c = re.sub(r'<button id="btnFicharEntrada".*?<\/button>\s*<button id="btnFicharSalida".*?<\/button>', r'<button id="btnFicharUnico" class="fichaje-btn in">Cargando...</button>', c, flags=re.DOTALL)

c = re.sub(r'const btnFicharEntrada = document\.getElementById\(\'btnFicharEntrada\'\);\s*const btnFicharSalida = document\.getElementById\(\'btnFicharSalida\'\);', r'', c)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(c)
print('Done HTML replace')

