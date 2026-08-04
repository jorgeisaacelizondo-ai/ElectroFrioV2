import re

with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

save_func = '''
        window.savePlanillaManual = async function(planillaId) {
            const pIndex = planillas.findIndex(p => p.id === planillaId);
            if (pIndex > -1) {
                const btn = document.getElementById('btn-save-' + planillaId);
                if (btn) btn.innerHTML = '⏳';
                try {
                    if (typeof db !== 'undefined') {
                        // Forzar el guardado del objeto completo en Firebase
                        await db.collection('planillas').doc(planillaId).set(planillas[pIndex]);
                    }
                    if (btn) {
                        btn.innerHTML = '✅';
                        setTimeout(() => { if(document.getElementById('btn-save-' + planillaId)) document.getElementById('btn-save-' + planillaId).innerHTML = '💾'; }, 2000);
                    }
                } catch (e) {
                    console.error('Error al guardar planilla manual', e);
                    if (btn) btn.innerHTML = '❌';
                }
            }
        };
'''

c = c.replace('window._pendingPlanillaUpdates = {};', save_func + '\n        window._pendingPlanillaUpdates = {};')

button_html = "${role === 'Administrador' ? `<button id=\"btn-save-${p.id}\" class=\"action-icon-btn\" onclick=\"savePlanillaManual('${p.id}')\" title=\"Guardar Cambios\" style=\"background-color: #2e7d32; border: 1px solid #1b5e20; border-radius: 6px; width: 32px; height: 32px; display: inline-flex; align-items: center; justify-content: center; font-size: 15px; cursor: pointer; transition: all 0.2s ease;\">💾</button>` : ''}\n                              <button class=\"action-icon-btn\" onclick=\"printPlanilla('${p.id}')\""

c = c.replace("<button class=\"action-icon-btn\" onclick=\"printPlanilla('${p.id}')\"", button_html)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(c)

print("Done")
