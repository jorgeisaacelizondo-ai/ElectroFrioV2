import re

with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# 1. Module HTML
tareas_html = r'''
                <!-- ======================= -->
                <!-- MÓDULO DE TAREAS        -->
                <!-- ======================= -->
                <div id="mod-tareas" class="page-content hidden">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                        <h2 style="margin:0; font-size: 24px;">Gestión de Tareas</h2>
                        <button class="role-admin-only" onclick="openModalNuevaTarea()" style="padding: 10px 15px; background-color: var(--color-blue); color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; display: flex; align-items: center; gap: 8px;">
                            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
                            Nueva Tarea
                        </button>
                    </div>
                    
                    <!-- CONTENEDOR TAREAS ADMIN -->
                    <div id="tareas-admin-container" class="role-admin-only">
                        <div class="content-card">
                            <div class="card-header">
                                <h3 class="card-title">Todas las Tareas</h3>
                            </div>
                            <div class="table-responsive">
                                <table class="custom-table" id="table-tareas-admin">
                                    <thead>
                                        <tr>
                                            <th>FECHA</th>
                                            <th>TAREA</th>
                                            <th>ASIGNADO A</th>
                                            <th>PROGRESO</th>
                                            <th>ACCIONES</th>
                                        </tr>
                                    </thead>
                                    <tbody id="tbody-tareas-admin"></tbody>
                                </table>
                            </div>
                        </div>
                    </div>

                    <!-- CONTENEDOR TAREAS COLABORADOR -->
                    <div id="tareas-collab-container" class="role-collab-only" style="display: grid; gap: 15px; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));">
                        <!-- Se llenan dinámicamente -->
                    </div>
                </div>

                <!-- Modal Nueva Tarea -->
                <div id="modalNuevaTarea" class="modal">
                    <div class="modal-content" style="max-width: 500px;">
                        <div class="modal-header">
                            <h3>Crear Nueva Tarea</h3>
                            <span class="close" onclick="document.getElementById('modalNuevaTarea').classList.remove('show')">&times;</span>
                        </div>
                        <div class="modal-body">
                            <form id="formNuevaTarea" onsubmit="saveNuevaTarea(event)">
                                <div class="form-group">
                                    <label>Título / Descripción principal de la tarea</label>
                                    <input type="text" id="tarea-title" required placeholder="Ej: Revisión de Vehículos">
                                </div>
                                <div class="form-group">
                                    <label>Fecha</label>
                                    <input type="date" id="tarea-date" required>
                                </div>
                                <div class="form-group">
                                    <label>Asignar a Colaboradores</label>
                                    <div class="checkbox-group" id="tarea-collabs-container" style="max-height: 150px; overflow-y: auto;">
                                        <!-- Se llena en openModalNuevaTarea() -->
                                    </div>
                                </div>
                                
                                <hr style="margin:20px 0; border:none; border-top: 1px solid var(--border-color);">
                                
                                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                                    <label style="margin:0; font-weight:bold;">Checklist (Ítems a cumplir)</label>
                                    <button type="button" onclick="addTareaItem()" style="padding: 5px 10px; background:var(--bg-secondary); border:1px solid var(--border-color); border-radius:4px; cursor:pointer;">+ Añadir Ítem</button>
                                </div>
                                <div id="tarea-items-container" style="display:flex; flex-direction:column; gap:8px;">
                                    <div class="tarea-item-row" style="display:flex; gap:10px; align-items:center;">
                                        <input type="text" class="tarea-item-input" required placeholder="Ej: Controlar aceite" style="flex:1;">
                                        <button type="button" onclick="this.parentElement.remove()" style="color:red; background:none; border:none; cursor:pointer; font-size:16px;">&times;</button>
                                    </div>
                                </div>

                                <div class="form-actions" style="margin-top:20px;">
                                    <button type="button" class="btn-cancel" onclick="document.getElementById('modalNuevaTarea').classList.remove('show')">Cancelar</button>
                                    <button type="submit" class="btn-save">Crear Tarea</button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>

\g<0>'''
c = re.sub(r'<!--\s*3\.\s*ÓRDENES TRABAJO\s*-->', tareas_html, c)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(c)

print("Injected HTML for Tareas!")
