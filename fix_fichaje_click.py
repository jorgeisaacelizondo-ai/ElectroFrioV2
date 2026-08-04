import re

with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

pattern = re.compile(r'if\s*\(btnFicharEntrada\)\s*\{\s*btnFicharEntrada\.addEventListener.*?if\s*\(btnFicharSalida\)\s*\{\s*btnFicharSalida\.addEventListener.*?\n\s*\}\s*\}\s*', re.DOTALL)

replacement = '''if (btnFicharUnico) {
            btnFicharUnico.addEventListener('click', async () => {
                const name = localStorage.getItem('electrofrio_name');
                const username = localStorage.getItem('electrofrio_user') || "";
                
                // Show loading
                const originalText = btnFicharUnico.textContent;
                btnFicharUnico.textContent = 'Validando...';
                btnFicharUnico.disabled = true;

                try {
                    // Strict validation in Firebase
                    const todayStr = getSyncedDate().toISOString().split('T')[0];
                    let intendedType = 'Entrada'; // Default if no records
                    
                    const snapshot = await db.collection('fichajes')
                        .where('date', '==', todayStr)
                        .get();
                    
                    const myDocs = [];
                    snapshot.forEach(doc => {
                        const d = doc.data();
                        if (d.name === name || d.username === username) myDocs.push(d);
                    });
                    myDocs.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
                    
                    const lastType = myDocs.length > 0 ? myDocs[0].type : 'Salida';
                    
                    if (lastType === 'Salida' || myDocs.length === 0) {
                        intendedType = 'Entrada';
                    } else {
                        intendedType = 'Salida';
                    }

                    // Check if it matches what the user thought they were clicking
                    if ((originalText === 'Marcar Entrada' && intendedType !== 'Entrada') ||
                        (originalText === 'Marcar Salida' && intendedType !== 'Salida')) {
                        showToast('Tu estado ya fue actualizado por otra vía.', 'error');
                        btnFicharUnico.disabled = false;
                        btnFicharUnico.textContent = intendedType === 'Entrada' ? 'Marcar Entrada' : 'Marcar Salida';
                        btnFicharUnico.className = intendedType === 'Entrada' ? 'fichaje-btn in' : 'fichaje-btn out';
                        return;
                    }
                    
                    verifyGeolocationAndExecute((collab, userLat, userLng) => {
                        const now = getSyncedDate();
                        const dateVal = now.toISOString().split('T')[0];
                        const timeVal = formatTime12h(now);
                        const timestampStr = now.toISOString();
                        const isVerified = userLat !== null && userLng !== null;

                        const nuevoFichaje = {
                            id: `fichaje-${Date.now()}`,
                            name: name,
                            username: username,
                            date: dateVal,
                            time: timeVal,
                            timestamp: timestampStr,
                            type: intendedType,
                            gps: {
                                lat: userLat !== null ? userLat : 0,
                                lng: userLng !== null ? userLng : 0,
                                verified: isVerified,
                                manual: !isVerified
                            }
                        };

                        // 1. Agregar localmente
                        fichajes.unshift(nuevoFichaje);
                        localStorage.setItem('electrofrio_clockins', JSON.stringify(fichajes));
                        updateTablesAndViews();
                        showToast('¡Se registró con éxito!', 'success');

                        // 2. Grabar de fondo
                        (async () => {
                            try {
                                await db.collection('fichajes').add(nuevoFichaje);
                                if (collab && collab.uid) {
                                    await db.collection('usuarios').doc(collab.uid).update({ status: intendedType === 'Entrada' ? 'online' : 'offline' });
                                }
                            } catch (error) {
                                console.error("Error al registrar: ", error);
                                showToast("Error de sincronización con el servidor", "error");
                            }
                        })();
                    });
                } catch (e) {
                    console.error(e);
                    showToast('Error validando el fichaje.', 'error');
                    btnFicharUnico.disabled = false;
                    btnFicharUnico.textContent = originalText;
                }
            });
        }
'''

new_c = pattern.sub(replacement, c)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(new_c)
print('Replaced successfully:', c != new_c)
