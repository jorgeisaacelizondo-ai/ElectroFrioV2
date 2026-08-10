import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add manodeobra trigger in switchTab
switch_tab_trigger = """
            if (moduleName === 'manodeobra') {
                setTimeout(() => {
                    if (typeof cargarFiltrosMDO === 'function') {
                        cargarFiltrosMDO();
                    }
                }, 50);
            }
"""

if "if (moduleName === 'manodeobra')" not in content:
    content = content.replace("if (moduleName === 'calendario') {", switch_tab_trigger + "\n            if (moduleName === 'calendario') {", 1)
    print("switchTab actualizado con trigger de manodeobra")

# 2. Update the MDO JavaScript logic to be bulletproof
updated_js = """
        // ==========================================
        // MÓDULO MANO DE OBRA (MDO) - VERSIÓN MEJORADA
        // ==========================================
        window.mdoData = [];
        window.mdoLimit = 30;
        let mdoEquiposLoaded = false;
        let mdoIsLoading = false;
        
        // Listener para cuando se abre la pestaña
        document.querySelectorAll('.nav-item[data-module]').forEach(item => {
            item.addEventListener('click', () => {
                if(item.getAttribute('data-module') === 'manodeobra') {
                    cargarFiltrosMDO();
                }
            });
        });

        async function cargarFiltrosMDO() {
            if (mdoEquiposLoaded && window.mdoData && window.mdoData.length > 0) {
                // Ya están cargados, solo re-ejecutar búsqueda
                ejecutarBusquedaMDO();
                return;
            }
            if (mdoIsLoading) return;
            mdoIsLoading = true;

            const selectEquipo = document.getElementById('mdoFilterEquipo');
            const selectSistema = document.getElementById('mdoFilterSistema');
            const tbody = document.getElementById('tbodyMDO');
            const loadingBanner = document.getElementById('mdoLoadingBanner');
            const loadingTitle = document.getElementById('mdoLoadingTitle');
            const loadingSub = document.getElementById('mdoLoadingSub');
            const loadingBadge = document.getElementById('mdoLoadingBadge');
            const spinner = document.getElementById('mdoSpinner');
            
            try {
                if (loadingBanner) {
                    loadingBanner.style.display = 'flex';
                    loadingTitle.innerHTML = '⏳ Descargando base de datos de Mano de Obra...';
                    loadingSub.innerHTML = 'Sincronizando el catálogo completo desde Firebase. Esto puede tardar unos momentos...';
                    loadingBadge.innerHTML = 'Descargando...';
                    loadingBadge.style.color = 'var(--color-blue, #0076e5)';
                }

                if (tbody) {
                    tbody.innerHTML = `
                        <tr>
                            <td colspan="6" style="text-align: center; padding: 50px 20px;">
                                <div style="font-size: 32px; margin-bottom: 12px; animation: mdoRotate 1s linear infinite; display: inline-block;">⚙️</div>
                                <div style="font-size: 16px; font-weight: 600; color: var(--text-primary);">Conectando con el servidor...</div>
                                <div style="font-size: 13px; color: var(--text-secondary); margin-top: 5px;">Descargando tareas y configurando filtros rápidos.</div>
                            </td>
                        </tr>
                    `;
                }

                const firestoreDb = (typeof db !== 'undefined' && db) ? db : firebase.firestore();
                console.log("Cargando mano_de_obra de Firestore...");
                const snapshot = await firestoreDb.collection('mano_de_obra').get();
                console.log("Mano de obra descargada. Cantidad:", snapshot.size);

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

                mdoEquiposLoaded = true;

                // Actualizar banner a éxito
                if (loadingBanner) {
                    loadingTitle.innerHTML = '✅ Base de datos sincronizada con éxito';
                    loadingSub.innerHTML = `Se cargaron <b>${window.mdoData.length}</b> tareas y servicios listos para consultar y presupuestar.`;
                    loadingBadge.innerHTML = `${window.mdoData.length} Tareas Activas`;
                    loadingBadge.style.color = '#10b981';
                    loadingBadge.style.background = 'rgba(16, 185, 129, 0.15)';
                    loadingBadge.style.borderColor = 'rgba(16, 185, 129, 0.3)';
                    if (spinner) spinner.style.display = 'none';
                    
                    setTimeout(() => {
                        if (loadingBanner) {
                            loadingBanner.style.opacity = '0.85';
                            loadingBanner.style.padding = '12px 20px';
                        }
                    }, 4000);
                }

                // Llenar select de Categoría (Equipo)
                if (selectEquipo) {
                    selectEquipo.innerHTML = '<option value="">Todas las Categorías</option>';
                    Array.from(equipos).sort().forEach(eq => {
                        selectEquipo.innerHTML += `<option value="${eq}">${eq}</option>`;
                    });
                    
                    // Remover listeners viejos clonando
                    const newSelectEquipo = selectEquipo.cloneNode(true);
                    selectEquipo.parentNode.replaceChild(newSelectEquipo, selectEquipo);
                    
                    newSelectEquipo.addEventListener('change', (e) => {
                        const equipoSelec = e.target.value;
                        window.mdoLimit = 30;
                        const currentSelectSistema = document.getElementById('mdoFilterSistema');
                        
                        if(!equipoSelec) {
                            if (currentSelectSistema) {
                                currentSelectSistema.innerHTML = '<option value="">Seleccione una Categoría primero</option>';
                                currentSelectSistema.disabled = true;
                            }
                        } else {
                            if (currentSelectSistema) {
                                currentSelectSistema.disabled = false;
                                currentSelectSistema.innerHTML = '<option value="">Todas las Subcategorías</option>';
                                const sistemas = sistemasPorEquipo[equipoSelec] || new Set();
                                Array.from(sistemas).sort().forEach(sis => {
                                    currentSelectSistema.innerHTML += `<option value="${sis}">${sis}</option>`;
                                });
                            }
                        }
                        ejecutarBusquedaMDO();
                    });
                }
                
                // Evento cambio de Subcategoría
                const currentSelectSistema = document.getElementById('mdoFilterSistema');
                if (currentSelectSistema) {
                    const newSelectSistema = currentSelectSistema.cloneNode(true);
                    currentSelectSistema.parentNode.replaceChild(newSelectSistema, currentSelectSistema);
                    newSelectSistema.addEventListener('change', () => {
                        window.mdoLimit = 30;
                        ejecutarBusquedaMDO();
                    });
                }

                // Evento texto de búsqueda
                const searchInput = document.getElementById('mdoSearchText');
                const clearSearchBtn = document.getElementById('btnMdoClearSearch');
                
                if (searchInput) {
                    searchInput.oninput = () => {
                        if (clearSearchBtn) {
                            clearSearchBtn.style.display = searchInput.value ? 'block' : 'none';
                        }
                        window.mdoLimit = 30;
                        ejecutarBusquedaMDO();
                    };
                }

                if (clearSearchBtn) {
                    clearSearchBtn.onclick = () => {
                        if (searchInput) {
                            searchInput.value = '';
                            searchInput.focus();
                        }
                        clearSearchBtn.style.display = 'none';
                        window.mdoLimit = 30;
                        ejecutarBusquedaMDO();
                    };
                }

                // Botón Limpiar Filtros
                const btnLimpiar = document.getElementById('btnMdoLimpiarFiltros');
                if (btnLimpiar) {
                    btnLimpiar.onclick = () => {
                        const sInp = document.getElementById('mdoSearchText');
                        const sEq = document.getElementById('mdoFilterEquipo');
                        const sSis = document.getElementById('mdoFilterSistema');
                        const cBtn = document.getElementById('btnMdoClearSearch');
                        if (sInp) sInp.value = '';
                        if (cBtn) cBtn.style.display = 'none';
                        if (sEq) sEq.value = '';
                        if (sSis) {
                            sSis.innerHTML = '<option value="">Seleccione una Categoría primero</option>';
                            sSis.disabled = true;
                        }
                        window.mdoLimit = 30;
                        ejecutarBusquedaMDO();
                    };
                }

                // Botón Mostrar Más
                const btnMas = document.getElementById('btnMdoMostrarMas');
                if (btnMas) {
                    btnMas.onclick = () => {
                        window.mdoLimit += 30;
                        ejecutarBusquedaMDO(false);
                    };
                }

                // Botón Mostrar Todas
                const btnTodo = document.getElementById('btnMdoMostrarTodo');
                if (btnTodo) {
                    btnTodo.onclick = () => {
                        window.mdoLimit = 9999;
                        ejecutarBusquedaMDO(false);
                    };
                }
                
                // Renderizado inicial
                ejecutarBusquedaMDO();
                
            } catch (error) {
                console.error("Error cargando MDO:", error);
                if (loadingBanner) {
                    loadingTitle.innerHTML = '❌ Error al conectar con Firebase';
                    loadingSub.innerHTML = 'No se pudo cargar la base de datos: ' + error.message;
                    loadingBadge.innerHTML = 'Error';
                    loadingBadge.style.color = '#ef4444';
                }
                if (tbody) {
                    tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; padding: 40px; color: #ef4444;">Error al cargar datos desde Firebase: ' + error.message + '</td></tr>';
                }
            } finally {
                mdoIsLoading = false;
            }
        }
        
        function ejecutarBusquedaMDO(scrollToTop = true) {
            const search = (document.getElementById('mdoSearchText')?.value || '').toLowerCase().trim();
            const equipo = document.getElementById('mdoFilterEquipo')?.value || '';
            const sistema = document.getElementById('mdoFilterSistema')?.value || '';
            const tbody = document.getElementById('tbodyMDO');
            const totalCounter = document.getElementById('mdoTotalCounter');
            const showingText = document.getElementById('mdoShowingText');
            const btnMostrarMas = document.getElementById('btnMdoMostrarMas');
            const btnMostrarTodo = document.getElementById('btnMdoMostrarTodo');
            
            if (!tbody) return;

            let filtrados = window.mdoData || [];
            
            if (equipo) {
                filtrados = filtrados.filter(d => d.equipo === equipo);
            }
            if (sistema) {
                filtrados = filtrados.filter(d => d.sistema === sistema);
            }
            if (search) {
                // Búsqueda inteligente por múltiples términos
                const terms = search.split(/\s+/).filter(t => t.length > 0);
                filtrados = filtrados.filter(d => {
                    const fullText = `${d.tarea} ${d.equipo} ${d.sistema} ${d.rubro}`.toLowerCase();
                    return terms.every(term => fullText.includes(term));
                });
            }
            
            const totalEncontrados = filtrados.length;
            
            if (totalCounter) {
                totalCounter.innerHTML = `<b>${totalEncontrados}</b> tareas encontradas`;
            }

            if (totalEncontrados === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="6" style="text-align:center; padding: 40px 20px; color: var(--text-muted);">
                            <div style="font-size: 26px; margin-bottom: 8px;">🔍</div>
                            <div style="font-size: 15px; font-weight: 500; color: var(--text-primary);">No se encontraron tareas coincidentes</div>
                            <div style="font-size: 13px; margin-top: 4px;">Prueba ajustando los términos de búsqueda o limpiando los filtros.</div>
                        </td>
                    </tr>
                `;
                if (showingText) showingText.innerHTML = 'Mostrando 0 de 0 tareas';
                if (btnMostrarMas) btnMostrarMas.style.display = 'none';
                if (btnMostrarTodo) btnMostrarTodo.style.display = 'none';
                return;
            }

            // Aplicar paginación / límite
            const resultadosVisibles = filtrados.slice(0, window.mdoLimit);
            
            tbody.innerHTML = '';
            resultadosVisibles.forEach(d => {
                const tr = document.createElement('tr');
                tr.className = 'mdo-row';
                tr.style.borderBottom = '1px solid var(--border-color, rgba(255,255,255,0.05))';
                tr.style.transition = 'background-color 0.15s ease';

                const precioFormateado = d.precio_sugerido || 0;
                
                tr.innerHTML = `
                    <td style="padding: 12px 18px; vertical-align: middle;">
                        <span style="display: inline-block; background: rgba(0, 118, 229, 0.1); color: var(--color-blue, #0076e5); font-size: 11px; font-weight: 600; padding: 3px 8px; border-radius: 6px; border: 1px solid rgba(0, 118, 229, 0.2);">
                            ${d.rubro || 'Refrigeración'}
                        </span>
                    </td>
                    <td style="padding: 12px 18px; vertical-align: middle; font-weight: 500; font-size: 13px; color: var(--text-primary);">
                        ${d.equipo || '-'}
                    </td>
                    <td style="padding: 12px 18px; vertical-align: middle;">
                        <span style="font-size: 12px; color: var(--text-secondary); background: var(--bg-hover, rgba(255,255,255,0.04)); padding: 2px 8px; border-radius: 4px;">
                            ${d.sistema || 'General'}
                        </span>
                    </td>
                    <td style="padding: 12px 18px; vertical-align: middle; font-size: 14px; font-weight: 500; color: var(--text-primary); line-height: 1.4;">
                        ${d.tarea || '-'}
                    </td>
                    <td style="padding: 12px 18px; vertical-align: middle; text-align: right;">
                        <div style="display: inline-flex; align-items: center; background: var(--bg-main, #14171f); border: 1px solid var(--border-color); border-radius: 8px; padding: 2px 8px;">
                            <span style="color: var(--text-muted); font-size: 13px; font-weight: 600; margin-right: 4px;">$</span>
                            <input type="number" id="precio-${d.id}" class="mdo-price-input" value="${precioFormateado}" style="width: 90px; padding: 6px 0; border: none; background: transparent; color: var(--text-primary); font-size: 14px; font-weight: 600; text-align: right; outline: none;">
                        </div>
                    </td>
                    <td style="padding: 12px 18px; vertical-align: middle; text-align: center;">
                        <button id="btn-save-${d.id}" class="btn btn-primary" onclick="guardarPrecioMDO('${d.id}')" style="padding: 6px 12px; font-size: 12px; font-weight: 600; border-radius: 6px; display: inline-flex; align-items: center; gap: 4px;" title="Guardar nuevo precio">
                            <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg>
                            Guardar
                        </button>
                    </td>
                `;
                tbody.appendChild(tr);
            });

            // Actualizar controles de paginación
            if (showingText) {
                showingText.innerHTML = `Mostrando <b>${resultadosVisibles.length}</b> de <b>${totalEncontrados}</b> tareas`;
            }

            if (btnMostrarMas) {
                if (resultadosVisibles.length < totalEncontrados) {
                    btnMostrarMas.style.display = 'inline-flex';
                    const restantes = totalEncontrados - resultadosVisibles.length;
                    const proxPaso = Math.min(30, restantes);
                    btnMostrarMas.innerHTML = `
                        <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg>
                        Mostrar más (+${proxPaso})
                    `;
                } else {
                    btnMostrarMas.style.display = 'none';
                }
            }

            if (btnMostrarTodo) {
                if (resultadosVisibles.length < totalEncontrados) {
                    btnMostrarTodo.style.display = 'inline-block';
                    btnMostrarTodo.innerHTML = `Mostrar todas (${totalEncontrados})`;
                } else {
                    btnMostrarTodo.style.display = 'none';
                }
            }
        }
        
        window.guardarPrecioMDO = async function(docId) {
            const role = localStorage.getItem('electrofrio_role');
            if (role !== 'Administrador') {
                alert('Acceso denegado: Solo los administradores pueden modificar los precios del catálogo.');
                return;
            }
            
            const password = prompt('Por seguridad, ingresa la clave de confirmación para actualizar este precio:');
            if (password !== '123') {
                if (password !== null) alert('Contraseña incorrecta. No se guardaron los cambios.');
                return;
            }
            
            const inputEl = document.getElementById(`precio-${docId}`);
            const btnEl = document.getElementById(`btn-save-${docId}`);
            const nuevoPrecio = parseFloat(inputEl?.value) || 0;
            
            const originalBtnHtml = btnEl ? btnEl.innerHTML : 'Guardar';
            if (btnEl) {
                btnEl.disabled = true;
                btnEl.innerHTML = '⏳...';
            }
            
            try {
                const firestoreDb = (typeof db !== 'undefined' && db) ? db : firebase.firestore();
                await firestoreDb.collection('mano_de_obra').doc(docId).update({
                    precio_sugerido: nuevoPrecio
                });
                
                // Actualizar array en memoria
                const itemIndex = window.mdoData.findIndex(d => d.id === docId);
                if(itemIndex !== -1) {
                    window.mdoData[itemIndex].precio_sugerido = nuevoPrecio;
                }
                
                if (btnEl) {
                    btnEl.style.background = '#10b981';
                    btnEl.innerHTML = '✅ Listo';
                    setTimeout(() => {
                        btnEl.style.background = '';
                        btnEl.innerHTML = originalBtnHtml;
                        btnEl.disabled = false;
                    }, 2000);
                } else {
                    alert('¡Precio actualizado correctamente!');
                }
            } catch(e) {
                console.error(e);
                alert('Error al guardar en Firebase: ' + e.message);
                if (btnEl) {
                    btnEl.innerHTML = originalBtnHtml;
                    btnEl.disabled = false;
                }
            }
        };
        // ==========================================
"""

pattern_js = re.compile(r'// ==========================================\s*// MÓDULO MANO DE OBRA \(MDO\).*?// ==========================================', re.DOTALL)
if pattern_js.search(content):
    content = pattern_js.sub(lambda m: updated_js.strip(), content, count=1)
    print("JS de MDO actualizado con trigger automático")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fix aplicado con éxito")
