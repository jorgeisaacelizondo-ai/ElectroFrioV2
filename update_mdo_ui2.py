import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. HTML Replacement
new_html = """
                <div id="mod-manodeobra" class="page-content hidden">
                    <div class="content-card">
                        <div class="card-header" style="display: flex; flex-direction: column; gap: 15px;">
                            <h3 class="card-title">Base de Datos de Mano de Obra</h3>
                            <div style="display: flex; gap: 10px; flex-wrap: wrap; align-items: center; width: 100%;">
                                <input type="text" id="mdoSearchText" class="form-input" placeholder="Buscador general (ej. filtro, caño, gas...)" style="flex: 1; min-width: 250px;">
                                <select id="mdoFilterEquipo" class="form-input" style="width: auto; min-width: 180px;">
                                    <option value="">Categoría (Todas)</option>
                                </select>
                                <select id="mdoFilterSistema" class="form-input" style="width: auto; min-width: 180px;" disabled>
                                    <option value="">Subcategoría (Todas)</option>
                                </select>
                                <button id="btnBuscarMDO" class="btn btn-primary" style="padding: 8px 16px;">Filtrar</button>
                            </div>
                        </div>
                        <div class="table-responsive" style="max-height: 65vh; overflow-y: auto;">
                            <table class="data-table" id="tablaMDO">
                                <thead>
                                    <tr>
                                        <th>Rubro</th>
                                        <th>Categoría</th>
                                        <th>Subcategoría</th>
                                        <th>Tarea</th>
                                        <th style="width: 150px;">Precio Sugerido ($)</th>
                                        <th style="width: 120px;">Acción</th>
                                    </tr>
                                </thead>
                                <tbody id="tbodyMDO">
                                    <tr><td colspan="6" style="text-align:center; padding: 30px; color: var(--text-muted);">Cargando base de datos...</td></tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
"""

pattern_html = re.compile(r'<div id="mod-manodeobra" class="page-content hidden">.*?</div>\s*</div>\s*</div>', re.DOTALL)
content = pattern_html.sub(new_html.strip(), content, count=1)

# 2. JS Replacement
new_js = """
        // ==========================================
        // MÓDULO MANO DE OBRA (MDO)
        // ==========================================
        window.mdoData = [];
        let mdoEquiposLoaded = false;
        
        // Listener para cuando se abre la pestaña
        document.querySelectorAll('.nav-item[data-module]').forEach(item => {
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
            const tbody = document.getElementById('tbodyMDO');
            
            try {
                tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;">Descargando base de datos completa...</td></tr>';
                const snapshot = await firebase.firestore().collection('mano_de_obra').get();
                window.mdoData = [];
                const equipos = new Set();
                const sistemasPorEquipo = {};
                
                snapshot.forEach(doc => {
                    const data = doc.data();
                    data.id = doc.id;
                    window.mdoData.push(data);
                    
                    if(data.equipo) equipos.add(data.equipo);
                    if(data.equipo && data.sistema) {
                        if(!sistemasPorEquipo[data.equipo]) sistemasPorEquipo[data.equipo] = new Set();
                        sistemasPorEquipo[data.equipo].add(data.sistema);
                    }
                });
                
                // Llenar select de Equipo (Categoría)
                selectEquipo.innerHTML = '<option value="">Categoría (Todas)</option>';
                Array.from(equipos).sort().forEach(eq => {
                    selectEquipo.innerHTML += `<option value="${eq}">${eq}</option>`;
                });
                
                // Cuando cambia el equipo, llenar sistemas (Subcategorías)
                selectEquipo.addEventListener('change', (e) => {
                    const equipoSelec = e.target.value;
                    if(!equipoSelec) {
                        selectSistema.innerHTML = '<option value="">Subcategoría (Todas)</option>';
                        selectSistema.disabled = true;
                        // Trigger search automatically when filter cleared
                        ejecutarBusquedaMDO();
                        return;
                    }
                    
                    selectSistema.disabled = false;
                    selectSistema.innerHTML = '<option value="">Subcategoría (Todas)</option>';
                    const sistemas = sistemasPorEquipo[equipoSelec] || new Set();
                    Array.from(sistemas).sort().forEach(sis => {
                        selectSistema.innerHTML += `<option value="${sis}">${sis}</option>`;
                    });
                    
                    ejecutarBusquedaMDO();
                });
                
                selectSistema.addEventListener('change', ejecutarBusquedaMDO);
                document.getElementById('mdoSearchText').addEventListener('keyup', ejecutarBusquedaMDO);
                
                // Renderizar los primeros 50 por defecto
                ejecutarBusquedaMDO();
                
            } catch (error) {
                console.error("Error cargando MDO:", error);
                tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; color:red;">Error al cargar la base de datos.</td></tr>';
            }
        }
        
        function ejecutarBusquedaMDO() {
            const search = (document.getElementById('mdoSearchText').value || '').toLowerCase().trim();
            const equipo = document.getElementById('mdoFilterEquipo').value;
            const sistema = document.getElementById('mdoFilterSistema').value;
            const tbody = document.getElementById('tbodyMDO');
            
            let resultados = window.mdoData;
            
            if (equipo) {
                resultados = resultados.filter(d => d.equipo === equipo);
            }
            if (sistema) {
                resultados = resultados.filter(d => d.sistema === sistema);
            }
            if (search) {
                resultados = resultados.filter(d => {
                    const texto = `${d.tarea} ${d.equipo} ${d.sistema} ${d.rubro}`.toLowerCase();
                    return texto.includes(search);
                });
            }
            
            // Limit to 50 if no search text to keep DOM fast
            const mostrandoTodos = resultados.length;
            if (!search && !equipo && !sistema) {
                resultados = resultados.slice(0, 50);
            } else if (resultados.length > 200) {
                resultados = resultados.slice(0, 200);
            }
            
            if (resultados.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;">No se encontraron resultados.</td></tr>';
                return;
            }
            
            tbody.innerHTML = '';
            resultados.forEach(d => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${d.rubro || '-'}</td>
                    <td>${d.equipo || '-'}</td>
                    <td>${d.sistema || '-'}</td>
                    <td style="font-weight: 500;">${d.tarea || '-'}</td>
                    <td>
                        <input type="number" id="precio-${d.id}" class="form-input" value="${d.precio_sugerido || 0}" style="width: 100px; padding: 4px 8px;">
                    </td>
                    <td>
                        <button class="btn btn-primary" onclick="guardarPrecioMDO('${d.id}')" style="padding: 4px 10px; font-size: 12px;">Guardar</button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
            
            if ((!search && !equipo && !sistema && mostrandoTodos > 50) || mostrandoTodos > 200) {
                tbody.innerHTML += `<tr><td colspan="6" style="text-align:center; color: var(--color-yellow);">Mostrando ${resultados.length} de ${mostrandoTodos} resultados. Usa el buscador para afinar.</td></tr>`;
            }
        }
        
        document.getElementById('btnBuscarMDO')?.addEventListener('click', ejecutarBusquedaMDO);
        
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
                await firebase.firestore().collection('mano_de_obra').doc(docId).update({
                    precio_sugerido: nuevoPrecio
                });
                // Actualizar el array local
                const index = window.mdoData.findIndex(d => d.id === docId);
                if(index !== -1) window.mdoData[index].precio_sugerido = nuevoPrecio;
                
                alert('¡Precio actualizado correctamente!');
            } catch(e) {
                console.error(e);
                alert('Error al guardar el precio: ' + e.message);
            }
        };
        // ==========================================
"""

pattern_js = re.compile(r'// ==========================================\s*// MÓDULO MANO DE OBRA \(MDO\)\s*// ==========================================.*?// ==========================================', re.DOTALL)
content = pattern_js.sub(new_js.strip(), content, count=1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Actualización de buscador general completada")
