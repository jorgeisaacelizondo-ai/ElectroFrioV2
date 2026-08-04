
import re
with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

pattern = re.compile(r'if\s*\(shiftStatusVal && shiftSubtext\)\s*\{\s*if\s*\(latestFichajeToday && latestFichajeToday\.type === \'Entrada\'\).*?if\s*\(btnFicharSalida\)\s*btnFicharSalida\.style\.display = \'none\';\s*\}\s*\}', re.DOTALL)

replacement = '''if (shiftStatusVal && shiftSubtext) {
                      const btnUnico = document.getElementById('btnFicharUnico');
                      if (latestFichajeToday && latestFichajeToday.type === 'Entrada') {
                          shiftStatusVal.textContent = 'En Servicio';
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

new_c = pattern.sub(replacement, c)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(new_c)
print('Replaced successfully:', c != new_c)

