import re

with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Fix the button injection
sidebar_html = """                  <button class="nav-item" data-module="ordenes">
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                          stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                          <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2" />
                          <rect x="8" y="2" width="8" height="4" rx="1" ry="1" />
                          <path d="M12 11h4" />
                          <path d="M12 16h4" />
                          <path d="M8 11h.01" />
                          <path d="M8 16h.01" />
                      </svg>
                      <span>Órdenes Trabajo</span>
                  </button>
                  
                  <button class="nav-item" data-module="tareas">
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                          stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                          <path d="M9 11l3 3L22 4"></path>
                          <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>
                      </svg>
                      <span>Tareas</span>
                  </button>"""

# We look for Órdenes Trabajo instead
c = re.sub(r'<button class="nav-item" data-module="ordenes">[\s\S]*?<span>[Ó]rdenes Trabajo</span>\s*</button>', sidebar_html, c)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(c)

print("Button injected!")
