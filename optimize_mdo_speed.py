import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Instant loading + LocalStorage Cache + Silent background synchronization
new_js = """
        // ==========================================
        // MÓDULO MANO DE OBRA (MDO) - CARGA INSTANTÁNEA & CACHÉ LOCAL
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

        // Pre-cargar en segundo plano al iniciar sesión
        window.addEventListener('load', () => {
            setTimeout(() => {
                cargarFiltrosMDO(true); // silent background load
            }, 1000);
        });

        async function cargarFiltrosMDO(isBackground = false) {
            if (mdoIsLoading) return;

            const selectRubro = document.getElementById('mdoFilterRubro');
            const selectSistema = document.getElementById('mdoFilterSistema');
            const checkContainer = document.getElementById('mdoCheckboxesContainer');
            const tbody = document.getElementById('tbodyMDO');
            const loadingBanner = document.getElementById('mdoLoadingBanner');
            const loadingTitle = document.getElementById('mdoLoadingTitle');
            const loadingSub = document.getElementById('mdoLoadingSub');
            const loadingBadge = document.getElementById('mdoLoadingBadge');
            const spinner = document.getElementById('mdoSpinner');

            // 1. CARGA ULTRA RÁPIDA DESDE CACHÉ LOCAL (0.01 segundos)
            if (window.mdoData.length === 0) {
                try {
                    const cached = localStorage.getItem('electrofrio_mdo_cache');
                    if (cached) {
                        const parsed = JSON.parse(cached);
                        if (Array.isArray(parsed) && parsed.length > 0) {
                            window.mdoData = parsed;
                            mdoEquiposLoaded = true;
                            renderizarTodoMDO();
                            if (loadingBanner) {
                                loadingTitle.innerHTML = '⚡ Catálogo listo desde memoria local';
                                loadingSub.innerHTML = `Mostrando <b>${window.mdoData.length}</b> tareas. Verificando actualizaciones con Firebase...`;
                                loadingBadge.innerHTML = `${window.mdoData.length} Tareas`;
                                loadingBadge.style.color = '#10b981';
                                loadingBadge.style.background = 'rgba(16, 185, 129, 0.15)';
                                loadingBadge.style.borderColor = 'rgba(16, 185, 129, 0.3)';
                                if (spinner) spinner.style.display = 'none';
                            }
                        }
                    }
                } catch(e) {
                    console.warn("Error leyendo caché local MDO:", e);
                }
            } else if (!isBackground) {
                ejecutarBusquedaMDO();
                return;
            }

            // 2. DESCARGA EN SEGUNDO PLANO O CARGA INICIAL
            mdoIsLoading = true;
            try {
                if (window.mdoData.length === 0 && loadingBanner && !isBackground) {
                    loadingBanner.style.display = 'flex';
                    loadingTitle.innerHTML = '⏳ Descargando base de datos inicial...';
                    loadingSub.innerHTML = 'Sincronizando el catálogo completo desde Firebase por primera vez...';
                    loadingBadge.innerHTML = 'Conectando...';
                    loadingBadge.style.color = 'var(--color-blue, #0076e5)';
                }

                const firestoreDb = (typeof db !== 'undefined' && db) ? db : firebase.firestore();
                const snapshot = await firestoreDb.collection('mano_de_obra').get();

                if (!snapshot.empty) {
                    const freshData = [];
                    snapshot.forEach(doc => {
                        const d = doc.data();
                        d.id = doc.id;
                        freshData.push(d);
                    });

                    window.mdoData = freshData;
                    // Guardar en almacenamiento local para que la próxima vez cargue instantáneamente
                    try {
                        localStorage.setItem('electrofrio_mdo_cache', JSON.stringify(freshData));
                    } catch (storageErr) {
                        console.warn("No se pudo guardar caché completo en localStorage:", storageErr);
                    }

                    mdoEquiposLoaded = true;
                    renderizarTodoMDO();

                    if (loadingBanner) {
                        loadingTitle.innerHTML = '✅ Base de datos sincronizada con éxito';
                        loadingSub.innerHTML = `Se sincronizaron <b>${window.mdoData.length}</b> tareas en tiempo real desde la nube.`;
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
                        }, 3000);
                    }
                }
            } catch (error) {
                console.error("Error sincronizando MDO:", error);
                if (window.mdoData.length === 0) {
                    if (loadingBanner) {
                        loadingTitle.innerHTML = '❌ Error al conectar con Firebase';
                        loadingSub.innerHTML = 'No se pudo descargar la base de datos: ' + error.message;
                        loadingBadge.innerHTML = 'Error';
                        loadingBadge.style.color = '#ef4444';
                    }
                    if (tbody) {
                        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; padding: 40px; color: #ef4444;">Error al conectar con Firebase. Revisa tu conexión a internet.</td></tr>';
                    }
                }
            } finally {
                mdoIsLoading = false;
            }
        }

        function renderizarTodoMDO() {
            const selectRubro = document.getElementById('mdoFilterRubro');
            const selectSistema = document.getElementById('mdoFilterSistema');
            const checkContainer = document.getElementById('mdoCheckboxesContainer');

            const rubros = new Set();
            const equipos = new Set();
            const sistemas = new Set();

            window.mdoData.forEach(d => {
                if(d.rubro) rubros.add(d.rubro);
                if(d.equipo) equipos.add(d.equipo);
                if(d.sistema) sistemas.add(d.sistema);
            });

            // Poblar Rubros si está vacío
            if (selectRubro && selectRubro.children.length <= 1) {
                selectRubro.innerHTML = '<option value="">Todos los Rubros</option>';
                Array.from(rubros).sort().forEach(r => {
                    selectRubro.innerHTML += `<option value="${r}">${r}</option>`;
                });
                selectRubro.onchange = () => {
                    window.mdoLimit = 30;
                    actualizarCheckboxesCategorias();
                    ejecutarBusquedaMDO();
                };
            }

            // Poblar Subcategorías si está vacío
            if (selectSistema && selectSistema.children.length <= 1) {
                selectSistema.innerHTML = '<option value="">Todas las Subcategorías</option>';
                Array.from(sistemas).sort().forEach(s => {
                    selectSistema.innerHTML += `<option value="${s}">${s}</option>`;
                });
                selectSistema.onchange = () => {
                    window.mdoLimit = 30;
                    ejecutarBusquedaMDO();
                };
            }

            function actualizarCheckboxesCategorias() {
                if (!checkContainer) return;
                const rubroSeleccionado = selectRubro ? selectRubro.value : '';
                
                const equiposDisponibles = new Set();
                window.mdoData.forEach(d => {
                    if (!rubroSeleccionado || d.rubro === rubroSeleccionado) {
                        if (d.equipo) equiposDisponibles.add(d.equipo);
                    }
                });

                checkContainer.innerHTML = '';
                Array.from(equiposDisponibles).sort().forEach(eq => {
                    const label = document.createElement('label');
                    label.style.cssText = 'display: flex; align-items: center; gap: 8px; font-size: 13px; color: var(--text-primary); cursor: pointer; padding: 6px 10px; background: var(--bg-hover, rgba(255,255,255,0.03)); border: 1px solid var(--border-color); border-radius: 6px; transition: all 0.15s ease; user-select: none;';
                    label.className = 'mdo-cat-chip';
                    
                    label.innerHTML = `
                        <input type="checkbox" class="mdo-cat-checkbox" value="${eq}" style="cursor: pointer; width: 15px; height: 15px; accent-color: var(--color-blue, #0076e5);">
                        <span style="font-weight: 500;">${eq}</span>
                    `;
                    
                    const chk = label.querySelector('input');
                    chk.addEventListener('change', () => {
                        label.style.borderColor = chk.checked ? 'var(--color-blue, #0076e5)' : 'var(--border-color)';
                        label.style.background = chk.checked ? 'rgba(0, 118, 229, 0.12)' : 'var(--bg-hover, rgba(255,255,255,0.03))';
                        window.mdoLimit = 30;
                        ejecutarBusquedaMDO();
                    });
                    
                    checkContainer.appendChild(label);
                });
            }

            actualizarCheckboxesCategorias();

            // Botones Marcar / Desmarcar
            const btnAll = document.getElementById('btnMdoSelectAllCats');
            if (btnAll) {
                btnAll.onclick = () => {
                    document.querySelectorAll('.mdo-cat-checkbox').forEach(chk => {
                        chk.checked = true;
                        const parent = chk.closest('label');
                        if (parent) {
                            parent.style.borderColor = 'var(--color-blue, #0076e5)';
                            parent.style.background = 'rgba(0, 118, 229, 0.12)';
                        }
                    });
                    window.mdoLimit = 30;
                    ejecutarBusquedaMDO();
                };
            }

            const btnNone = document.getElementById('btnMdoDeselectAllCats');
            if (btnNone) {
                btnNone.onclick = () => {
                    document.querySelectorAll('.mdo-cat-checkbox').forEach(chk => {
                        chk.checked = false;
                        const parent = chk.closest('label');
                        if (parent) {
                            parent.style.borderColor = 'var(--border-color)';
                            parent.style.background = 'var(--bg-hover, rgba(255,255,255,0.03))';
                        }
                    });
                    window.mdoLimit = 30;
                    ejecutarBusquedaMDO();
                };
            }

            // Input Búsqueda
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

            // Limpiar Filtros
            const btnLimpiar = document.getElementById('btnMdoLimpiarFiltros');
            if (btnLimpiar) {
                btnLimpiar.onclick = () => {
                    if (searchInput) searchInput.value = '';
                    if (clearSearchBtn) clearSearchBtn.style.display = 'none';
                    if (selectRubro) selectRubro.value = '';
                    if (selectSistema) selectSistema.value = '';
                    document.querySelectorAll('.mdo-cat-checkbox').forEach(chk => {
                        chk.checked = false;
                        const parent = chk.closest('label');
                        if (parent) {
                            parent.style.borderColor = 'var(--border-color)';
                            parent.style.background = 'var(--bg-hover, rgba(255,255,255,0.03))';
                        }
                    });
                    actualizarCheckboxesCategorias();
                    window.mdoLimit = 30;
                    ejecutarBusquedaMDO();
                };
            }

            // Paginación
            const btnMas = document.getElementById('btnMdoMostrarMas');
            if (btnMas) {
                btnMas.onclick = () => {
                    window.mdoLimit += 30;
                    ejecutarBusquedaMDO(false);
                };
            }

            const btnTodo = document.getElementById('btnMdoMostrarTodo');
            if (btnTodo) {
                btnTodo.onclick = () => {
                    window.mdoLimit = 9999;
                    ejecutarBusquedaMDO(false);
                };
            }

            ejecutarBusquedaMDO();
        }
        
        function ejecutarBusquedaMDO(scrollToTop = true) {
            const search = (document.getElementById('mdoSearchText')?.value || '').toLowerCase().trim();
            const rubro = document.getElementById('mdoFilterRubro')?.value || '';
            const sistema = document.getElementById('mdoFilterSistema')?.value || '';
            const tbody = document.getElementById('tbodyMDO');
            const totalCounter = document.getElementById('mdoTotalCounter');
            const showingText = document.getElementById('mdoShowingText');
            const btnMostrarMas = document.getElementById('btnMdoMostrarMas');
            const btnMostrarTodo = document.getElementById('btnMdoMostrarTodo');
            
            if (!tbody) return;

            const selectedCats = new Set();
            document.querySelectorAll('.mdo-cat-checkbox:checked').forEach(chk => {
                selectedCats.add(chk.value);
            });

            let filtrados = window.mdoData || [];
            
            if (rubro) {
                filtrados = filtrados.filter(d => d.rubro === rubro);
            }
            if (selectedCats.size > 0) {
                filtrados = filtrados.filter(d => selectedCats.has(d.equipo));
            }
            if (sistema) {
                filtrados = filtrados.filter(d => d.sistema === sistema);
            }
            if (search) {
                const terms = search.split(' ').filter(t => t.length > 0);
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
                            <div style="font-size: 13px; margin-top: 4px;">Prueba ajustando las casillas de categorías, el rubro o limpiando los filtros.</div>
                        </td>
                    </tr>
                `;
                if (showingText) showingText.innerHTML = 'Mostrando 0 de 0 tareas';
                if (btnMostrarMas) btnMostrarMas.style.display = 'none';
                if (btnMostrarTodo) btnMostrarTodo.style.display = 'none';
                return;
            }

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
                
                const itemIndex = window.mdoData.findIndex(d => d.id === docId);
                if(itemIndex !== -1) {
                    window.mdoData[itemIndex].precio_sugerido = nuevoPrecio;
                    try {
                        localStorage.setItem('electrofrio_mdo_cache', JSON.stringify(window.mdoData));
                    } catch(e) {}
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
    content = pattern_js.sub(lambda m: new_js.strip(), content, count=1)
    print("JS optimizado con caché local inyectado con éxito")
else:
    print("No se encontró el patrón JS")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Optimización de velocidad finalizada")
