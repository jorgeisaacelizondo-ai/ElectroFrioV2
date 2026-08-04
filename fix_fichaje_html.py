
with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

target = '''                              <div class="fichaje-actions">
                                  <button id="btnFicharEntrada" class="fichaje-btn in">Fichar Entrada</button>
                                  <button id="btnFicharSalida" class="fichaje-btn out" disabled>Fichar Salida</button>
                              </div>'''

replacement = '''                              <div class="fichaje-actions">
                                  <button id="btnFicharUnico" class="fichaje-btn" disabled>Cargando...</button>
                              </div>'''

c = c.replace(target, replacement)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(c)
print('Done HTML')

