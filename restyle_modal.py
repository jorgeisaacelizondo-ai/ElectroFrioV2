import re

with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Define the new styled HTML for modalNuevaTarea
new_modal_html = r'''                <!-- Modal Nueva Tarea -->
                <div id="modalNuevaTarea" class="modal-overlay">
                    <div class="modal-content" style="max-width: 500px;">
                        <div class="modal-header">
                            <h3 class="modal-title">
                                <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 6px;">
                                    <path d="M9 11l3 3L22 4"></path>
                                    <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>
                                </svg>
                                Crear Nueva Tarea
                            </h3>
                            <button type="button" class="modal-close" onclick="document.getElementById('modalNuevaTarea').classList.remove('show')">&times;</button>
                        </div>
                        <div class="modal-body" style="padding: 20px;">
                            <form id="formNuevaTarea" onsubmit="saveNuevaTarea(event)">
                                <div class="input-group">
                                    <label>Título / Descripción principal de la tarea</label>
                                    <input type="text" id="tarea-title" required placeholder="Ej: Revisión de Vehículos" style="width: 100%; padding: 10px; background: var(--bg-input); border: 1px solid var(--border-color); color: var(--text-primary); border-radius: 6px;">
                                </div>
                                <div class="input-group">
                                    <label>Fecha</label>
                                    <input type="date" id="tarea-date" required style="width: 100%; padding: 10px; background: var(--bg-input); border: 1px solid var(--border-color); color: var(--text-primary); border-radius: 6px;">
                                </div>
                                <div class="input-group">
                                    <label>Asignar a Colaboradores</label>
                                    <div class="collab-checkbox-list" id="tarea-collabs-container" style="max-height: 120px; overflow-y: auto; padding: 6px; border: 1px solid var(--border-color); border-radius: 8px; background-color: var(--bg-input); display: flex; flex-direction: column; gap: 4px;">
                                        <!-- Se llena en openModalNuevaTarea() -->
                                    </div>
                                </div>
                                
                                <hr style="margin:20px 0; border:none; border-top: 1px solid var(--border-color);">
                                
                                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                                    <label style="margin:0; font-weight:bold; font-size: 14px; color: var(--text-primary);">Checklist (Ítems a cumplir)</label>
                                    <button type="button" onclick="addTareaItem()" style="padding: 6px 12px; background:var(--bg-secondary); border:1px solid var(--border-color); border-radius:6px; cursor:pointer; color: var(--text-primary); font-size: 13px;">+ Añadir Ítem</button>
                                </div>
                                <div id="tarea-items-container" style="display:flex; flex-direction:column; gap:8px;">
                                    <div class="tarea-item-row" style="display:flex; gap:10px; align-items:center;">
                                        <input type="text" class="tarea-item-input" required placeholder="Ej: Controlar aceite" style="flex:1; padding: 10px; background: var(--bg-input); border: 1px solid var(--border-color); color: var(--text-primary); border-radius: 6px;">
                                        <button type="button" onclick="this.parentElement.remove()" style="color:var(--color-red); background:none; border:none; cursor:pointer; font-size:20px; display:flex; align-items:center; justify-content:center; width:30px; height:30px;">&times;</button>
                                    </div>
                                </div>

                                <button type="submit" class="login-btn btn-save" style="background-color: var(--color-blue); color: #000; font-weight: 700; margin-top: 20px; width: 100%;">
                                    Crear Tarea
                                </button>
                            </form>
                        </div>
                    </div>
                </div>'''

# We want to replace the whole block starting with `<!-- Modal Nueva Tarea -->` up to its closing `</div>`
pattern = r'<!-- Modal Nueva Tarea -->\s*<div id="modalNuevaTarea" class="modal-overlay">.*?</div>\s*</div>\s*</div>'

c = re.sub(pattern, new_modal_html, c, flags=re.DOTALL)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(c)

print("Modal styling updated!")
