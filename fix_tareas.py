import re

with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# 1. Update addTareaItem styles
new_add_tarea_item = r'''        window.addTareaItem = function() {
            const row = document.createElement('div');
            row.className = 'tarea-item-row';
            row.style.cssText = 'display:flex; gap:10px; align-items:center;';
            row.innerHTML = `<input type="text" class="tarea-item-input" required placeholder="Nuevo ítem..." style="flex:1; padding: 10px; background: var(--bg-input); border: 1px solid var(--border-color); color: var(--text-primary); border-radius: 6px;"><button type="button" onclick="this.parentElement.remove()" style="color:var(--color-red); background:none; border:none; cursor:pointer; font-size:20px; display:flex; align-items:center; justify-content:center; width:30px; height:30px;">&times;</button>`;
            document.getElementById('tarea-items-container').appendChild(row);
        }'''

c = re.sub(r'window\.addTareaItem = function\(\) \{.*?\}', new_add_tarea_item, c, flags=re.DOTALL)

# 2. Add unsubscribeTareas variable
c = c.replace("let unsubscribePlanillas = null;", "let unsubscribePlanillas = null;\n        let unsubscribeTareas = null;")

# 3. Add listener setup logic for Tareas inside initLocalStorage / realtime setup block
tareas_listener_setup = r'''
            // Activar sincronización de tareas en tiempo real desde Firestore
            if (!unsubscribeTareas) {
                unsubscribeTareas = db.collection('tareas').onSnapshot((querySnapshot) => {
                    const updatedTareas = [];
                    querySnapshot.forEach((doc) => {
                        const data = doc.data();
                        data.id = doc.id;
                        updatedTareas.push(data);
                    });
                    tareas = updatedTareas;
                    localStorage.setItem('electrofrio_tareas', JSON.stringify(tareas));
                    updateTablesAndViews(); // Refresh view
                });
            }
'''

c = c.replace("if (!unsubscribePlanillas) {", tareas_listener_setup + "\n            if (!unsubscribePlanillas) {")

# 4. Add listener cleanup logic
tareas_listener_cleanup = r'''
            if (unsubscribeTareas) {
                unsubscribeTareas();
                unsubscribeTareas = null;
            }
'''
c = c.replace("if (unsubscribePlanillas) {", tareas_listener_cleanup + "\n            if (unsubscribePlanillas) {")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(c)

print("Listener and styles fixed!")
