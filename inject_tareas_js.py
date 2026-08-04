import re

with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# 2. JS Logic
js_logic = r'''
        // --- LOGICA DE TAREAS ---
        window.openModalNuevaTarea = function() {
            const container = document.getElementById('tarea-collabs-container');
            container.innerHTML = '';
            
            // Llenar colaboradores activos
            const activeCollabs = colaboradores.filter(c => c.estado !== 'Inactivo');
            activeCollabs.forEach(c => {
                const div = document.createElement('div');
                div.innerHTML = `<label style="display:flex; align-items:center; gap:8px; font-weight:normal; margin-bottom:5px;"><input type="checkbox" class="tarea-collab-cb" value="${c.name}"> ${c.name}</label>`;
                container.appendChild(div);
            });

            document.getElementById('tarea-date').value = getLocalISODate(getSyncedDate());
            document.getElementById('formNuevaTarea').reset();
            
            // Restaurar 1 item vacío por defecto
            document.getElementById('tarea-items-container').innerHTML = `
                <div class="tarea-item-row" style="display:flex; gap:10px; align-items:center;">
                    <input type="text" class="tarea-item-input" required placeholder="Ej: Controlar aceite" style="flex:1;">
                    <button type="button" onclick="this.parentElement.remove()" style="color:red; background:none; border:none; cursor:pointer; font-size:16px;">&times;</button>
                </div>
            `;
            
            document.getElementById('modalNuevaTarea').classList.add('show');
        }

        window.addTareaItem = function() {
            const row = document.createElement('div');
            row.className = 'tarea-item-row';
            row.style.cssText = 'display:flex; gap:10px; align-items:center;';
            row.innerHTML = `<input type="text" class="tarea-item-input" required placeholder="Nuevo ítem..." style="flex:1;"><button type="button" onclick="this.parentElement.remove()" style="color:red; background:none; border:none; cursor:pointer; font-size:16px;">&times;</button>`;
            document.getElementById('tarea-items-container').appendChild(row);
        }

        window.saveNuevaTarea = async function(e) {
            e.preventDefault();
            const title = document.getElementById('tarea-title').value;
            const date = document.getElementById('tarea-date').value;
            
            const collabsChecks = document.querySelectorAll('.tarea-collab-cb:checked');
            const assignees = Array.from(collabsChecks).map(cb => cb.value);
            
            if (assignees.length === 0) {
                alert("Debes asignar la tarea a al menos un colaborador.");
                return;
            }

            const itemInputs = document.querySelectorAll('.tarea-item-input');
            const items = Array.from(itemInputs).map(inp => ({ text: inp.value, checked: false }));

            if (items.length === 0) {
                alert("Debes añadir al menos un ítem al checklist.");
                return;
            }

            const tareaObj = {
                id: `tarea-${Date.now()}`,
                title,
                date,
                assignees,
                items,
                status: 'Pendiente',
                timestamp: getSyncedDate().toISOString(),
                createdBy: localStorage.getItem('electrofrio_name') || 'Admin'
            };

            try {
                const btn = e.target.querySelector('.btn-save');
                btn.innerHTML = 'Guardando...';
                btn.disabled = true;
                
                if (typeof db !== 'undefined') {
                    await db.collection('tareas').doc(tareaObj.id).set(tareaObj);
                } else {
                    tareas.push(tareaObj);
                    localStorage.setItem('electrofrio_tareas', JSON.stringify(tareas));
                    updateTablesAndViews();
                }
                document.getElementById('modalNuevaTarea').classList.remove('show');
            } catch (err) {
                console.error("Error al guardar tarea", err);
                alert("Error al guardar la tarea");
            } finally {
                const btn = e.target.querySelector('.btn-save');
                if(btn) { btn.innerHTML = 'Crear Tarea'; btn.disabled = false; }
            }
        }

        window.deleteTarea = async function(id) {
            if(!confirm("¿Estás seguro de eliminar esta tarea?")) return;
            try {
                if (typeof db !== 'undefined') {
                    await db.collection('tareas').doc(id).delete();
                } else {
                    tareas = tareas.filter(t => t.id !== id);
                    localStorage.setItem('electrofrio_tareas', JSON.stringify(tareas));
                    updateTablesAndViews();
                }
            } catch (e) {
                console.error(e);
                alert("Error al eliminar");
            }
        }

        window.toggleTareaItemCollab = function(tareaId, itemIndex, isChecked) {
            // Actualizar local
            const t = tareas.find(x => x.id === tareaId);
            if(t && t.items[itemIndex]) {
                t.items[itemIndex].checked = isChecked;
            }
        }

        window.saveTareaProgress = async function(tareaId) {
            const btn = document.getElementById('btn-save-tarea-' + tareaId);
            if(btn) { btn.innerHTML = '⏳'; btn.disabled = true; }
            const t = tareas.find(x => x.id === tareaId);
            if(!t) return;
            
            try {
                if(typeof db !== 'undefined') {
                    await db.collection('tareas').doc(tareaId).update({
                        items: t.items
                    });
                }
                if(btn) { 
                    btn.innerHTML = '✅ Guardado'; 
                    setTimeout(() => { if(btn){ btn.innerHTML = '💾 Guardar Cambios'; btn.disabled = false; } }, 2000); 
                }
            } catch (e) {
                console.error(e);
                alert("Error al guardar progreso");
                if(btn) { btn.innerHTML = 'Guardar Cambios'; btn.disabled = false; }
            }
        }

        function renderTareas() {
            const role = localStorage.getItem('electrofrio_role');
            const userName = localStorage.getItem('electrofrio_name');
            
            if (role === 'Administrador') {
                const tbody = document.getElementById('tbody-tareas-admin');
                if(!tbody) return;
                
                // Ordenar por fecha y timestamp invertido
                const sorted = [...tareas].sort((a,b) => b.timestamp.localeCompare(a.timestamp));
                
                let html = '';
                sorted.forEach(t => {
                    const total = t.items.length;
                    const done = t.items.filter(x => x.checked).length;
                    const pct = Math.round((done/total)*100);
                    
                    const fParts = t.date.split('-');
                    const dateAr = fParts.length===3 ? `${fParts[2]}/${fParts[1]}/${fParts[0]}` : t.date;
                    
                    const pColor = pct === 100 ? '#4caf50' : (pct > 0 ? '#ffb300' : 'var(--text-secondary)');
                    
                    let checklistPreview = `<div style="text-align:left; font-size:11px; margin-top:5px; color:var(--text-secondary);">`;
                    t.items.forEach(i => {
                        checklistPreview += `<div>${i.checked ? '✅' : '❌'} ${i.text}</div>`;
                    });
                    checklistPreview += `</div>`;

                    html += `<tr>
                        <td data-label="FECHA">${dateAr}</td>
                        <td data-label="TAREA"><strong>${t.title}</strong>${checklistPreview}</td>
                        <td data-label="ASIGNADO A">${t.assignees.join(', ')}</td>
                        <td data-label="PROGRESO"><span style="color:${pColor}; font-weight:bold;">${done}/${total} (${pct}%)</span></td>
                        <td data-label="ACCIONES">
                            <button class="action-icon-btn" onclick="deleteTarea('${t.id}')" title="Eliminar Tarea" style="background-color: #7a1a1a; border: 1px solid #992020; border-radius: 6px; width: 32px; height: 32px; display: inline-flex; align-items: center; justify-content: center; font-size: 15px; cursor: pointer; transition: all 0.2s ease;">🗑️</button>
                        </td>
                    </tr>`;
                });
                if(sorted.length === 0) {
                    html = `<tr><td colspan="5" style="text-align:center;">No hay tareas activas</td></tr>`;
                }
                tbody.innerHTML = html;
            } else {
                const container = document.getElementById('tareas-collab-container');
                if(!container) return;
                
                const myTareas = tareas.filter(t => t.assignees.includes(userName) || t.assignees.includes(localStorage.getItem('electrofrio_user')));
                // Ordenar mostrando las pendientes primero o por fecha
                const sorted = [...myTareas].sort((a,b) => b.timestamp.localeCompare(a.timestamp));
                
                let html = '';
                sorted.forEach(t => {
                    const fParts = t.date.split('-');
                    const dateAr = fParts.length===3 ? `${fParts[2]}/${fParts[1]}/${fParts[0]}` : t.date;
                    const total = t.items.length;
                    const done = t.items.filter(x => x.checked).length;
                    
                    let itemsHtml = '';
                    t.items.forEach((item, idx) => {
                        itemsHtml += `<label style="display:flex; align-items:flex-start; gap:10px; margin-bottom:8px; padding:8px; background:var(--bg-primary); border-radius:6px; cursor:pointer;">
                            <input type="checkbox" style="width:20px; height:20px; flex-shrink:0;" ${item.checked ? 'checked' : ''} onchange="toggleTareaItemCollab('${t.id}', ${idx}, this.checked)">
                            <span style="${item.checked ? 'text-decoration:line-through; color:var(--text-secondary);' : 'color:var(--text-primary);'}">${item.text}</span>
                        </label>`;
                    });

                    html += `<div class="content-card" style="display:flex; flex-direction:column;">
                        <div class="card-header" style="flex-direction:column; align-items:flex-start; gap:5px;">
                            <h3 class="card-title">${t.title}</h3>
                            <span style="font-size:12px; color:var(--text-secondary);">📅 ${dateAr} • Progreso: ${done}/${total}</span>
                        </div>
                        <div style="padding:15px; flex:1;">
                            ${itemsHtml}
                        </div>
                        <div style="padding:15px; border-top:1px solid var(--border-color); text-align:right;">
                            <button id="btn-save-tarea-${t.id}" onclick="saveTareaProgress('${t.id}')" style="padding: 10px 15px; background-color: #2e7d32; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; width:100%;">
                                💾 Guardar Cambios
                            </button>
                        </div>
                    </div>`;
                });
                
                if(sorted.length === 0) {
                    html = `<div class="content-card"><div style="padding:20px; text-align:center;">No tienes tareas asignadas.</div></div>`;
                }
                container.innerHTML = html;
            }
        }
\g<0>'''
c = re.sub(r'//\s*---\s*FUNCIONES DEL MÓDULO DE CLIENTES\s*---', js_logic, c, flags=re.IGNORECASE)
if "LOGICA DE TAREAS" not in c:
    # try with different encoding/matching
    c = re.sub(r'//\s*---\s*FUNCIONES DEL M.DULO DE CLIENTES\s*---', js_logic, c, flags=re.IGNORECASE)

# 3. Add to updateTablesAndViews
c = re.sub(r'(renderPresupuestoTable\(\);)', r'\1 renderTareas();', c)

# 4. Add to Firebase Listeners
snapshot_logic = r'''\g<0>
                if (typeof db !== 'undefined') {
                    // Sincronizar Tareas
                    db.collection('tareas').onSnapshot((querySnapshot) => {
                        let updatedTareas = [];
                        querySnapshot.forEach((doc) => {
                            updatedTareas.push(doc.data());
                        });
                        tareas = updatedTareas;
                        window.tareas = tareas;
                        localStorage.setItem('electrofrio_tareas', JSON.stringify(tareas));
                        renderTareas();
                    }, (error) => {
                        console.error("Error al sincronizar tareas:", error);
                    });
                }
'''
c = re.sub(r'function initializeFirebaseListeners\(\) \{', snapshot_logic, c)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(c)

print("Injected JS logic for Tareas!")
