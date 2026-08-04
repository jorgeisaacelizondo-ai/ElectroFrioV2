import re

with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Fix 1: Add the sidebar button below ordenes
sidebar_html = """                  <button class="nav-item" data-module="ordenes">
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                          stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                          <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2" />
                          <rect x="8" y="2" width="8" height="4" rx="1" ry="1" />
                          <path d="M12 11h4" />
                          <path d="M12 16h4" />
                          <path d="M8 11h.01" />
                      </svg>
                      <span>Órdenes de Trabajo</span>
                  </button>
                  
                  <button class="nav-item" data-module="tareas">
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                          stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                          <path d="M9 11l3 3L22 4"></path>
                          <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>
                      </svg>
                      <span>Tareas</span>
                  </button>"""
c = re.sub(r'<button class="nav-item" data-module="ordenes">[\s\S]*?<span>Órdenes de Trabajo</span>\s*</button>', sidebar_html, c)

# Fix 2: Add itemTareas to logic
visibility_logic_orig = """                  const itemOrdenes = sidebarNav.querySelector('[data-module="ordenes"]');
                  const itemCalendario = sidebarNav.querySelector('[data-module="calendario"]');"""
visibility_logic_new = """                  const itemOrdenes = sidebarNav.querySelector('[data-module="ordenes"]');
                  const itemTareas = sidebarNav.querySelector('[data-module="tareas"]');
                  const itemCalendario = sidebarNav.querySelector('[data-module="calendario"]');"""
c = c.replace(visibility_logic_orig, visibility_logic_new)

all_items_orig = "itemDashboard, itemOrdenes, itemCalendario, itemMapa,"
all_items_new = "itemDashboard, itemOrdenes, itemTareas, itemCalendario, itemMapa,"
c = c.replace(all_items_orig, all_items_new)

admin_array_orig = """                          itemOrdenes,
                          itemCalendario,"""
admin_array_new = """                          itemOrdenes,
                          itemTareas,
                          itemCalendario,"""
c = c.replace(admin_array_orig, admin_array_new)

premium_array_orig = """                          itemDashboard,
                          itemOrdenes,
                          itemDatabase,"""
premium_array_new = """                          itemDashboard,
                          itemOrdenes,
                          itemTareas,
                          itemDatabase,"""
c = c.replace(premium_array_orig, premium_array_new)

collab_array_orig = """                          itemDashboard,
                          itemOrdenes,
                          itemDatabase,
                          itemFichajes
                      ];"""
collab_array_new = """                          itemDashboard,
                          itemOrdenes,
                          itemTareas,
                          itemDatabase,
                          itemFichajes
                      ];"""
c = c.replace(collab_array_orig, collab_array_new)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(c)

print("Done fixing UI")
