
with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

target_vars = '''          // Fichaje Simulator
          const btnFicharEntrada = document.getElementById('btnFicharEntrada');
          const btnFicharSalida = document.getElementById('btnFicharSalida');'''
c = c.replace(target_vars, '''          // Fichaje Simulator
          const btnFicharUnico = document.getElementById('btnFicharUnico');''')

target_logic = '''                  const shiftStatusVal = document.getElementById('shiftStatusVal');
                  const shiftSubtext = document.getElementById('shiftSubtext');
                  
                  if (shiftStatusVal && shiftSubtext) {
                      if (latestFichajeToday && latestFichajeToday.type === 'Entrada') {
                          shiftStatusVal.textContent = 'En Turno';
                          shiftStatusVal.style.color = 'var(--color-green)';
                          shiftSubtext.textContent = Entrada registrada a las ;
  
                          if (btnFicharEntrada) btnFicharEntrada.style.display = 'none';
                          if (btnFicharSalida) {
                              btnFicharSalida.style.display = 'block';
                              btnFicharSalida.disabled = false;
                          }
                      } else {
                          shiftStatusVal.textContent = 'Fuera de Turno';
                          shiftStatusVal.style.color = 'var(--color-red)';
                          shiftSubtext.textContent = latestFichajeToday
                              ? Salida registrada hoy a las 
                              : 'No has iniciado jornada hoy';
  
                          if (btnFicharEntrada) {
                              btnFicharEntrada.style.display = 'block';
                              btnFicharEntrada.disabled = false;
                          }
                          if (btnFicharSalida) btnFicharSalida.style.display = 'none';
                      }
                  }'''

replacement_logic = '''                  const shiftStatusVal = document.getElementById('shiftStatusVal');
                  const shiftSubtext = document.getElementById('shiftSubtext');
                  
                  if (shiftStatusVal && shiftSubtext) {
                      const btnUnico = document.getElementById('btnFicharUnico');
                      if (latestFichajeToday && latestFichajeToday.type === 'Entrada') {
                          shiftStatusVal.textContent = 'En Turno';
                          shiftStatusVal.style.color = 'var(--color-green)';
                          shiftSubtext.textContent = Entrada registrada a las ;
  
                          if (btnUnico) {
                              btnUnico.textContent = 'Marcar Salida';
                              btnUnico.className = 'fichaje-btn out';
                              btnUnico.disabled = false;
                          }
                      } else {
                          shiftStatusVal.textContent = 'Fuera de Turno';
                          shiftStatusVal.style.color = 'var(--color-red)';
                          shiftSubtext.textContent = latestFichajeToday
                              ? Salida registrada hoy a las 
                              : 'No has iniciado jornada hoy';
  
                          if (btnUnico) {
                              btnUnico.textContent = 'Marcar Entrada';
                              btnUnico.className = 'fichaje-btn in';
                              btnUnico.disabled = false;
                          }
                      }
                  }'''

c = c.replace(target_logic, replacement_logic)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(c)
print('Done JS Logic')

