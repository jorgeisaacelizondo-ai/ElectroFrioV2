import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Reemplazar la sección HTML
html_to_insert = """
                <div id="mod-manodeobra" class="page-content hidden">
                    <div class="content-card">
                        <div class="card-header" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px;">
                            <h3 class="card-title">Base de Datos de Mano de Obra</h3>
                            <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                                <select id="mdoFilterEquipo" class="form-input" style="width: auto; min-width: 200px;">
                                    <option value="">Cargando equipos...</option>
                                </select>
                                <select id="mdoFilterSistema" class="form-input" style="width: auto; min-width: 200px;" disabled>
                                    <option value="">Seleccione un Equipo primero</option>
                                </select>
                                <button id="btnBuscarMDO" class="btn btn-primary" style="padding: 8px 16px;">Buscar</button>
                            </div>
                        </div>
                        <div class="table-responsive" style="max-height: 65vh; overflow-y: auto;">
                            <table class="data-table" id="tablaMDO">
                                <thead>
                                    <tr>
                                        <th>Rubro</th>
                                        <th>Equipo</th>
                                        <th>Sistema</th>
                                        <th>Tarea</th>
                                        <th style="width: 150px;">Precio Sugerido ($)</th>
                                        <th style="width: 120px;">Acción</th>
                                    </tr>
                                </thead>
                                <tbody id="tbodyMDO">
                                    <tr><td colspan="6" style="text-align:center; padding: 30px; color: var(--text-muted);">Seleccione el Equipo y Sistema en los filtros de arriba y presione Buscar.</td></tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
"""

# Find where <!-- MANO DE OBRA --> starts and replace the whole div
pattern_html = re.compile(r'<div id="mod-manodeobra" class="page-content hidden">.*?</div>\s*</div>\s*</div>', re.DOTALL)
if '<div id="mod-manodeobra"' in content:
    content = pattern_html.sub(html_to_insert.strip(), content, count=1)
else:
    print("No se encontró mod-manodeobra")

# 2. Inyectar la lógica JS
js_logic = """
        // ==========================================
        // MÓDULO MANO DE OBRA (MDO)
        // ==========================================
        let mdoEquiposLoaded = false;
        
        // Listener para cuando se abre la pestaña
        navItems.forEach(item => {
            item.addEventListener('click', () => {
                if(item.getAttribute('data-module') === 'manodeobra' && !mdoEquiposLoaded) {
                    cargarFiltrosMDO();
                    mdoEquiposLoaded = true;
                }
            });
        });

        async function cargarFiltrosMDO() {
            const selectEquipo = document.getElementById('mdoFilterEquipo');
            const selectSistema = document.getElementById('mdoFilterSistema');
            
            try {
                // To get distinct equipos, we can query a few or fetch all and extract unique.
                // Since there are 800 items, reading all once is fine for an admin panel.
                const snapshot = await db.collection('mano_de_obra').get();
                const equipos = new Set();
                const sistemasPorEquipo = {};
                
                snapshot.forEach(doc => {
                    const data = doc.data();
                    if(data.equipo) equipos.add(data.equipo);
                    if(data.equipo && data.sistema) {
                        if(!sistemasPorEquipo[data.equipo]) sistemasPorEquipo[data.equipo] = new Set();
                        sistemasPorEquipo[data.equipo].add(data.sistema);
                    }
                });
                
                // Llenar select de Equipo
                selectEquipo.innerHTML = '<option value="">Todos los Equipos</option>';
                Array.from(equipos).sort().forEach(eq => {
                    selectEquipo.innerHTML += `<option value="${eq}">${eq}</option>`;
                });
                
                // Cuando cambia el equipo, llenar sistemas
                selectEquipo.addEventListener('change', (e) => {
                    const equipoSelec = e.target.value;
                    if(!equipoSelec) {
                        selectSistema.innerHTML = '<option value="">Seleccione un Equipo primero</option>';
                        selectSistema.disabled = true;
                        return;
                    }
                    
                    selectSistema.disabled = false;
                    selectSistema.innerHTML = '<option value="">Todos los Sistemas</option>';
                    const sistemas = sistemasPorEquipo[equipoSelec] || new Set();
                    Array.from(sistemas).sort().forEach(sis => {
                        selectSistema.innerHTML += `<option value="${sis}">${sis}</option>`;
                    });
                });
                
            } catch (error) {
                console.error("Error cargando filtros MDO:", error);
                selectEquipo.innerHTML = '<option value="">Error al cargar</option>';
            }
        }
        
        document.getElementById('btnBuscarMDO')?.addEventListener('click', async () => {
            const equipo = document.getElementById('mdoFilterEquipo').value;
            const sistema = document.getElementById('mdoFilterSistema').value;
            const tbody = document.getElementById('tbodyMDO');
            
            tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;">Buscando...</td></tr>';
            
            try {
                let query = db.collection('mano_de_obra');
                if(equipo) query = query.where('equipo', '==', equipo);
                if(sistema) query = query.where('sistema', '==', sistema);
                
                // Limit to 100 if no filters to prevent hanging
                if(!equipo && !sistema) query = query.limit(50);
                
                const snapshot = await query.get();
                if(snapshot.empty) {
                    tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;">No se encontraron tareas con estos filtros.</td></tr>';
                    return;
                }
                
                tbody.innerHTML = '';
                snapshot.forEach(doc => {
                    const d = doc.data();
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td>${d.rubro || '-'}</td>
                        <td>${d.equipo || '-'}</td>
                        <td>${d.sistema || '-'}</td>
                        <td>${d.tarea || '-'}</td>
                        <td>
                            <input type="number" id="precio-${doc.id}" class="form-input" value="${d.precio_sugerido || 0}" style="width: 100px; padding: 4px 8px;">
                        </td>
                        <td>
                            <button class="btn btn-primary" onclick="guardarPrecioMDO('${doc.id}')" style="padding: 4px 10px; font-size: 12px;">Guardar</button>
                        </td>
                    `;
                    tbody.appendChild(tr);
                });
                
                if(!equipo && !sistema) {
                    tbody.innerHTML += '<tr><td colspan="6" style="text-align:center; color: var(--color-yellow);">Mostrando solo los primeros 50 resultados. Usa los filtros para ver tareas específicas.</td></tr>';
                }
                
            } catch (e) {
                console.error(e);
                tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; color:red;">Error en la búsqueda.</td></tr>';
            }
        });
        
        window.guardarPrecioMDO = async function(docId) {
            const role = localStorage.getItem('electrofrio_role');
            if (role !== 'Administrador') {
                alert('Solo los administradores pueden modificar precios.');
                return;
            }
            
            const password = prompt('Por seguridad, ingresa la contraseña de confirmación para cambiar el precio:');
            if (password !== '123') {
                alert('Contraseña incorrecta. No se guardaron los cambios.');
                return;
            }
            
            const nuevoPrecio = parseFloat(document.getElementById(`precio-${docId}`).value) || 0;
            
            try {
                await db.collection('mano_de_obra').doc(docId).update({
                    precio_sugerido: nuevoPrecio
                });
                alert('¡Precio actualizado correctamente!');
            } catch(e) {
                console.error(e);
                alert('Error al guardar el precio: ' + e.message);
            }
        };
        // ==========================================
"""

# Insert JS right before the main script tag ends. Looking for `    </script>\n</body>` or similar.
# In index.html, line 12409 is `    </script>`. Let's just find the last `</script>` that precedes `</body>` or `</html>`.

parts = content.rsplit('</script>', 1)
if len(parts) == 2:
    content = parts[0] + js_logic + '\n</script>' + parts[1]

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Inyección completada")
