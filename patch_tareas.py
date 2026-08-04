import re

with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# 1. Inject tareas parsing into updateTablesAndViews
c = c.replace(
    "planillas = JSON.parse(localStorage.getItem('electrofrio_worksheets')) || [];",
    "planillas = JSON.parse(localStorage.getItem('electrofrio_worksheets')) || [];\n            tareas = JSON.parse(localStorage.getItem('electrofrio_tareas')) || [];"
)

# 2. Add renderTareas() call inside updateTablesAndViews
render_tareas_injection = r'''
            if (activeModule === 'tareas') {
                renderTareas();
            }
'''
c = c.replace(
    "if (activeModule === 'clientes') {",
    "if (activeModule === 'tareas') {\n                renderTareas();\n            }\n            if (activeModule === 'clientes') {"
)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(c)

print("updateTablesAndViews patched!")
