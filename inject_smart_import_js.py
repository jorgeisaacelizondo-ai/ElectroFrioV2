import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Smart Importer & Excel Export JavaScript logic
import_export_js = """
        // ==========================================
        // IMPORTADOR INTELIGENTE (ANTI-DUPLICADOS) & EXPORTADOR EXCEL
        // ==========================================
        window.mdoParsedItems = [];

        // Abrir Modal
        document.getElementById('btnMdoOpenImportModal')?.addEventListener('click', () => {
            const modal = document.getElementById('modalMdoImport');
            if (modal) modal.style.display = 'flex';
        });

        // Cerrar Modal
        document.getElementById('btnMdoCloseModal')?.addEventListener('click', () => {
            const modal = document.getElementById('modalMdoImport');
            if (modal) modal.style.display = 'none';
        });

        // Limpiar Input del Modal
        document.getElementById('btnMdoLimpiarImport')?.addEventListener('click', () => {
            const txt = document.getElementById('mdoImportTextarea');
            const res = document.getElementById('mdoAnalysisResults');
            if (txt) txt.value = '';
            if (res) res.style.display = 'none';
            window.mdoParsedItems = [];
        });

        // Exportar a Excel
        document.getElementById('btnMdoExportExcel')?.addEventListener('click', () => {
            if (!window.mdoData || window.mdoData.length === 0) {
                alert('No hay tareas disponibles para exportar.');
                return;
            }

            try {
                if (typeof XLSX === 'undefined') {
                    alert('Librería XLSX no disponible para exportar.');
                    return;
                }

                // Preparar datos ordenados para la planilla Excel
                const excelRows = window.mdoData.map((d, index) => ({
                    'N°': index + 1,
                    'Rubro': d.rubro || 'Refrigeración',
                    'Categoría (Equipo)': d.equipo || '',
                    'Subcategoría (Sistema)': d.sistema || '',
                    'Descripción de la Tarea': d.tarea || '',
                    'Precio Sugerido ($)': d.precio_sugerido || 0,
                    'Estado': d.activo !== false ? 'Activo' : 'Inactivo'
                }));

                const worksheet = XLSX.utils.json_to_sheet(excelRows);
                const workbook = XLSX.utils.book_new();
                XLSX.utils.book_append_sheet(workbook, worksheet, 'Mano de Obra');
                
                // Generar y descargar archivo
                const fecha = new Date().toISOString().split('T')[0];
                XLSX.writeFile(workbook, `ElectroFrio_Mano_De_Obra_${fecha}.xlsx`);
            } catch(err) {
                console.error("Error al exportar Excel:", err);
                alert("Error al generar archivo Excel: " + err.message);
            }
        });

        // Analizar Texto y Detectar Duplicados
        document.getElementById('btnMdoAnalizarTexto')?.addEventListener('click', () => {
            const rawText = document.getElementById('mdoImportTextarea')?.value || '';
            const rubroDefault = (document.getElementById('mdoImportRubro')?.value || 'Refrigeración').trim();
            const equipoDefault = (document.getElementById('mdoImportEquipo')?.value || 'General').trim();
            const sistemaDefault = (document.getElementById('mdoImportSistema')?.value || 'General').trim();
            const resultsPanel = document.getElementById('mdoAnalysisResults');
            const previewList = document.getElementById('mdoPreviewList');
            const statNuevas = document.getElementById('mdoStatNuevas');
            const statDuplicadas = document.getElementById('mdoStatDuplicadas');

            if (!rawText.trim()) {
                alert('Por favor, pega una lista de tareas en el cuadro de texto.');
                return;
            }

            const lines = rawText.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
            if (lines.length === 0) {
                alert('No se encontraron líneas válidas para analizar.');
                return;
            }

            // Normalizador para comparar strings sin acentos, espacios extras ni mayúsculas
            const normalize = (str) => (str || '').toLowerCase().normalize("NFD").replace(/[\\u0300-\\u036f]/g, "").replace(/[^a-z0-9]/g, "");

            // Crear mapa de tareas existentes en la base de datos
            const existingMap = new Set();
            (window.mdoData || []).forEach(d => {
                const key = normalize(`${d.rubro}_${d.equipo}_${d.sistema}_${d.tarea}`);
                existingMap.add(key);
                // También llave simplificada (equipo + tarea)
                existingMap.add(normalize(`${d.equipo}_${d.tarea}`));
            });

            let currentEquipo = equipoDefault;
            let currentSistema = sistemaDefault;
            let currentRubro = rubroDefault;

            let nuevas = [];
            let duplicadas = [];

            lines.forEach(line => {
                // Detectar si la línea es un encabezado de Equipo/Categoría
                if (/^[0-9]+\\.\\s+[A-Z\\s/]+$/.test(line) || (line.toUpperCase() === line && !line.startsWith('•') && !line.startsWith('*') && line.length > 3)) {
                    currentEquipo = line.replace(/^[0-9]+\\.\\s+/, '').trim();
                    currentSistema = "General";
                    return;
                }
                // Detectar si la línea es una Subcategoría (A. Nombre)
                else if (/^[A-Z]\\.\\s+/.test(line)) {
                    currentSistema = line.replace(/^[A-Z]\\.\\s+/, '').trim();
                    return;
                }

                // Es una tarea
                const cleanTarea = line.replace(/^[•*\\-\\d.]+\\s*/, '').trim();
                if (cleanTarea.length < 2) return;

                const itemObj = {
                    rubro: currentRubro || 'Refrigeración',
                    equipo: currentEquipo || 'General',
                    sistema: currentSistema || 'General',
                    tarea: cleanTarea,
                    precio_sugerido: 0,
                    activo: true
                };

                const itemKey = normalize(`${itemObj.rubro}_${itemObj.equipo}_${itemObj.sistema}_${itemObj.tarea}`);
                const simpleKey = normalize(`${itemObj.equipo}_${itemObj.tarea}`);

                if (existingMap.has(itemKey) || existingMap.has(simpleKey)) {
                    duplicadas.push(itemObj);
                } else {
                    nuevas.push(itemObj);
                    existingMap.add(itemKey); // Evitar duplicados dentro del mismo lote
                }
            });

            window.mdoParsedItems = nuevas;

            // Renderizar vista previa del análisis
            if (resultsPanel) resultsPanel.style.display = 'block';
            if (statNuevas) statNuevas.innerHTML = `🟢 <b>${nuevas.length}</b> Nuevas para importar`;
            if (statDuplicadas) statDuplicadas.innerHTML = `🟡 <b>${duplicadas.length}</b> Duplicadas (Se omitirán)`;

            if (previewList) {
                previewList.innerHTML = '';
                
                if (nuevas.length === 0 && duplicadas.length === 0) {
                    previewList.innerHTML = '<div style="padding: 10px; color: var(--text-muted);">No se detectaron tareas válidas.</div>';
                    return;
                }

                if (nuevas.length === 0) {
                    previewList.innerHTML = '<div style="padding: 15px; color: var(--color-yellow); background: rgba(245, 158, 11, 0.1); border-radius: 8px;">Todas las tareas analizadas ya existen en la base de datos. No hay nada nuevo que importar.</div>';
                    return;
                }

                // Mostrar lista de las nuevas que se van a importar
                nuevas.forEach((item, i) => {
                    const row = document.createElement('div');
                    row.style.cssText = 'display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; border-bottom: 1px solid rgba(255,255,255,0.05); gap: 10px;';
                    row.innerHTML = `
                        <div style="flex: 1;">
                            <span style="display: inline-block; font-size: 11px; background: rgba(16, 185, 129, 0.15); color: #10b981; padding: 2px 6px; border-radius: 4px; font-weight: 600; margin-right: 6px;">NUEVA</span>
                            <b>${item.equipo}</b> &bull; <span style="color: var(--text-secondary);">${item.sistema}</span> &bull; <span>${item.tarea}</span>
                        </div>
                        <div style="display: flex; align-items: center; gap: 4px;">
                            <span style="font-size: 12px; color: var(--text-muted);">$</span>
                            <input type="number" value="${item.precio_sugerido}" onchange="window.mdoParsedItems[${i}].precio_sugerido = parseFloat(this.value) || 0" style="width: 75px; padding: 4px 6px; border: 1px solid var(--border-color); background: var(--bg-card); color: var(--text-primary); border-radius: 4px; font-size: 12px;">
                        </div>
                    `;
                    previewList.appendChild(row);
                });
            }
        });

        // Confirmar y Subir Tareas Nuevas a Firebase
        document.getElementById('btnMdoConfirmarImportacion')?.addEventListener('click', async () => {
            if (!window.mdoParsedItems || window.mdoParsedItems.length === 0) {
                alert('No hay tareas nuevas para importar.');
                return;
            }

            const role = localStorage.getItem('electrofrio_role');
            if (role !== 'Administrador') {
                alert('Solo los administradores pueden importar nuevas tareas a la base de datos.');
                return;
            }

            const password = prompt(`Se importarán ${window.mdoParsedItems.length} tareas nuevas.\\n\\nPor favor ingresa la clave de administrador para confirmar:`);
            if (password !== '123') {
                if (password !== null) alert('Contraseña incorrecta. No se realizó la importación.');
                return;
            }

            const btnConfirmar = document.getElementById('btnMdoConfirmarImportacion');
            if (btnConfirmar) {
                btnConfirmar.disabled = true;
                btnConfirmar.innerHTML = '⏳ Subiendo a Firebase...';
            }

            try {
                const firestoreDb = (typeof db !== 'undefined' && db) ? db : firebase.firestore();
                let subidas = 0;

                for (let i = 0; i < window.mdoParsedItems.length; i++) {
                    const item = window.mdoParsedItems[i];
                    const docRef = await firestoreDb.collection('mano_de_obra').add(item);
                    item.id = docRef.id;
                    window.mdoData.push(item);
                    subidas++;
                }

                // Guardar en caché local
                try {
                    localStorage.setItem('electrofrio_mdo_cache', JSON.stringify(window.mdoData));
                } catch(e) {}

                alert(`¡Éxito! Se importaron ${subidas} tareas nuevas a la base de datos de Firebase.`);
                
                // Cerrar modal y refrescar vista
                const modal = document.getElementById('modalMdoImport');
                if (modal) modal.style.display = 'none';
                
                renderizarTodoMDO();

            } catch (err) {
                console.error("Error al importar:", err);
                alert("Ocurrió un error durante la importación: " + err.message);
            } finally {
                if (btnConfirmar) {
                    btnConfirmar.disabled = false;
                    btnConfirmar.innerHTML = '🚀 Subir Tareas Nuevas a Firebase';
                }
            }
        });
        // ==========================================
"""

# Insert right after the MDO module JS block
if 'IMPORTADOR INTELIGENTE (ANTI-DUPLICADOS)' not in content:
    content = content.replace('// ==========================================\n\n    </script>', import_export_js + '\n\n    </script>', 1)
    print("JS de Importador y Exportador inyectado con éxito")
else:
    print("El JS ya estaba presente")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Inyección finalizada")
